import pygame
import cv2 

#TODO
# RESIZE NOW WORKS TO MAINTAIN ASPECT RATIO
# FIT CROP OVERLAY TO ONLY GO OVER VIDEO
# ADJUST OVERLAY AREA SELECTION TO SCALE WITH WINDOW RESIZE
# SET MINIMUM DIMENSIONS




class VideoPlayer:
    def __init__(self,
                 dimensions:tuple[int,int], # the display dimensions we are working with
                 video:cv2.VideoCapture,
            ):
        self.surface = pygame.Surface(dimensions)

        self.video = video
        self.current_frame = None

        v_height = self.video.get(cv2.CAP_PROP_FRAME_HEIGHT)
        v_width = self.video.get(cv2.CAP_PROP_FRAME_WIDTH)

        self.aspect_ratio = v_width / v_height

        self._maintain_aspect_ratio()
        self._center_frame_in_surface()


        self.paused = False
    

    #display frame in window
    def display_frame(self,frame) -> None:
        self.surface.fill((0,0,255))
        resized_frame = self.resize_frame_to_dimensions(frame)

        frame_surface = pygame.image.frombuffer(resized_frame.tobytes(),resized_frame.shape[1::-1],"BGR")
        self.current_frame = frame

        #write frame to window
        self.surface.blit(frame_surface,self.frame_position)

    
    
    #retrieve video dimensions that maintain aspect ratio and fit height of surface
    def _maintain_aspect_ratio(self) -> tuple[int,int]:
        max_width = self.surface.get_width()
        max_height = self.surface.get_height()

        height = self.surface.get_height()
        width = self.surface.get_width()

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

        self.frame_dimensions = (width,height)
    

    #returns position of display frame such that it is centered
    def _center_frame_in_surface(self) -> tuple[int,int]:
        frame_width = self.frame_dimensions[0]
        frame_height = self.frame_dimensions[1]

        surface_width = self.surface.get_width()
        surface_height = self.surface.get_height()

        left = round((surface_width - frame_width) / 2)
        top = round((surface_height - frame_height) / 2)

        self.frame_position = (left,top)



    #handle resize
    def resize(self,xy:tuple[int,int]):
        self.surface = pygame.Surface(xy)

        ## UPDATE SELF.FRAME_DIMENSIONS
        self._maintain_aspect_ratio()

        ## UPDATE SELF.FRAME_POSITION
        self._center_frame_in_surface()

        #redisplay current frame onto new surface
        self.display_frame(self.current_frame)

    #resize frame to fit display
    def resize_frame_to_dimensions(self,frame): #-> frame
        return cv2.resize(frame,self.frame_dimensions)
    
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

            self.display_frame(frame)
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

        self.display_frame(frame)


    #fetch next frame from video
    def next_frame(self) -> tuple[bool,any]:
        success,frame = self.video.read()
        if success:
            frame = self.resize_frame_to_dimensions(frame) #resize frame to fit window dimensions
            return True,frame
        else:
            return False,None