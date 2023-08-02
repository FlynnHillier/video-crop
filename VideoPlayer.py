import pygame
import cv2 
from Component import Component,Coordinate

#TODO
# RESIZE NOW WORKS TO MAINTAIN ASPECT RATIO
# FIT CROP OVERLAY TO ONLY GO OVER VIDEO
# ADJUST OVERLAY AREA SELECTION TO SCALE WITH WINDOW RESIZE
# SET MINIMUM DIMENSIONS




class VideoPlayer(Component):
    def __init__(self,
        dimensions:Coordinate, # the display dimensions we are working with
        position:Coordinate,
        video:cv2.VideoCapture,
        parent:None | Component = None,
    ):
        #super
        super().__init__(
            dimensions=dimensions,
            position=position,
            parent=parent,
        )

        self.video : cv2.VideoCapture = video
        self.current_frame_image = None #in future add logic which reads first frame, then reverts to frame index 0, to display still image on start

        v_height = self.video.get(cv2.CAP_PROP_FRAME_HEIGHT)
        v_width = self.video.get(cv2.CAP_PROP_FRAME_WIDTH)

        self.aspect_ratio = v_width / v_height

        frame_dimensions = self._gen_frame_dimensions_maintaining_aspect_ratio_to_fit_surface()

        self.frame = Component(
            dimensions=frame_dimensions,
            position=self._gen_frame_position_center_in_surface(frame_dimensions=frame_dimensions),
            parent=self,
        )

        self.paused = False
    

    

    #set current frame
    def set_current_frame(self,frame) -> None:
        self.current_frame_image = frame

        #update display
        self.draw()
    
    def draw(self) -> None:
        self.surface.fill((0,0,255))

        #resize frame to fit display
        resized_frame = cv2.resize(self.current_frame_image,self.frame.get_dimensions())

        frame_image_surface = pygame.image.frombuffer(resized_frame.tobytes(),resized_frame.shape[1::-1],"BGR")

        self.frame.set_surface(frame_image_surface)

        self.surface.blit(self.frame.surface,self.frame.get_position())


    
    
    #retrieve video dimensions that maintain aspect ratio and fit height of surface
    def _gen_frame_dimensions_maintaining_aspect_ratio_to_fit_surface(self) -> tuple[int,int]:
        max_width = self.surface.get_width()
        max_height = self.surface.get_height()

        width,height = self.get_dimensions()

        if height * self.aspect_ratio > max_width:
            #adjust for bars on vertical axis
            width = max_width
            height = round(max_width * (1/self.aspect_ratio))
        elif width * (1/self.aspect_ratio) > max_height:
            #adjust for bars on horizontal axis
            height = max_height
            width = round(max_height * self.aspect_ratio)
        else:
            #frame already fits in window dimensions.
            pass

        return (width,height)
    

    #returns position of display frame such that it is centered
    def _gen_frame_position_center_in_surface(self,frame_dimensions:Coordinate | None = None) -> tuple[int,int]:
        if frame_dimensions == None:
            f_width,f_height = self.frame.get_dimensions()
        else:
            f_width,f_height = frame_dimensions

        surface_width = self.surface.get_width()
        surface_height = self.surface.get_height()

        left = round((surface_width - f_width) / 2)
        top = round((surface_height - f_height) / 2)

        return (left,top)



    #handle resize
    def resize(self,xy:tuple[int,int]):
        self.surface = pygame.Surface(xy)

        #UPDATE FRAME DIMENSIONS
        self.frame.set_dimensions(self._gen_frame_dimensions_maintaining_aspect_ratio_to_fit_surface())
        
        #UPDATE FRAME POS
        self.frame.set_position(self._gen_frame_position_center_in_surface())

        #redisplay current frame onto new surface
        self.draw()
    

    #toggle pause
    def toggle_pause(self) -> bool:
        self.paused = not self.paused
        return self.paused

    # to be called on each tick of the loop
    def tick(self) -> bool: #return true if end of video
        if not self.paused:
            success,frame = self.next_frame()
            
            if not success:
                self.jump_to_frame(0)
                return True

            self.set_current_frame(frame)
        else:
            return False
    

    #return true if successfully jumped, return false if out of range of frames
    def jump_to_frame(self,frame_indx:int) -> bool:
        max_frame = self.video.get(cv2.CAP_PROP_FRAME_COUNT)

        #invalid frame
        if frame_indx > max_frame or frame_indx < 0:
            return False
        
        self.video.set(cv2.CAP_PROP_POS_FRAMES,frame_indx)
        success,frame = self.next_frame()

        if not success:
            raise Exception("unexpected error, unable to read frame when jumping to frame.")

        self.set_current_frame(frame)


    #fetch next frame from video
    def next_frame(self) -> tuple[bool,any]:
        success,frame = self.video.read()
        if success:
            return True,frame
        else:
            return False,None