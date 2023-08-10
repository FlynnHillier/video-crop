import pygame
import cv2 
from Component import Component,Coordinate
from CropOverlay import CropOverlay

from events import EVENT_FRAME_SKIP,EVENT_PAUSE,EVENT_PLAY


class VideoPlayer(Component):
    def __init__(self,
        dimensions:Coordinate, # the display dimensions we are working with
        position:Coordinate,
        video:cv2.VideoCapture,
        show_crop_overlay:bool,
        bg_colour = (0,0,0),
        parent:None | Component = None,
    ):
        #super
        super().__init__(
            dimensions=dimensions,
            position=position,
            parent=parent,
        )

        self.bg_colour = bg_colour

        #READING FRAMES / DISPLAY
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

        #CROP OVERLAY
        self.component_crop_overlay = CropOverlay(
            dimensions=self.frame.get_dimensions(),
            position=(0,0),
            parent=self.frame,

            initial_selection_dimensions=(90,160),
            handle_width=2,
            max_selection=(2000,2000),
            min_selection=(90,160),
            aspect_ratio=self.aspect_ratio,
            bg_alpha=128,
        )


        #BOOLEAN
        self.show_crop_overlay = show_crop_overlay
        self.paused = False
    


    ### DRAW ###

    def draw(self) -> None:
        self.surface.fill(self.bg_colour)

        #resize frame to fit display
        resized_frame = cv2.resize(self.current_frame_image,self.frame.get_dimensions())

        frame_image_surface = pygame.image.frombuffer(resized_frame.tobytes(),resized_frame.shape[1::-1],"BGR")

        self.frame.set_surface(frame_image_surface)

        if self.show_crop_overlay:
            self.frame.surface.blit(self.component_crop_overlay.surface,self.component_crop_overlay.get_position())

        self.surface.blit(self.frame.surface,self.frame.get_position())


    
    ### EVENTS ###
    
    #handle resize
    def resize(self,xy:tuple[int,int]):
        self.surface = pygame.Surface(xy)

        #UPDATE FRAME DIMENSIONS
        self.frame.set_dimensions(self._gen_frame_dimensions_maintaining_aspect_ratio_to_fit_surface())
        
        #UPDATE FRAME POS
        self.frame.set_position(self._gen_frame_position_center_in_surface())

        #UPDATE CROP OVERLAY
        self.component_crop_overlay.resize(self.frame.get_dimensions())

        #redisplay current frame onto new surface
        self.draw()

    def _handle_event(self,event):
        #pass of events to children
        if self.show_crop_overlay:
            self.component_crop_overlay._handle_event(event)

        #handle native
        if event.type == pygame.KEYDOWN:
            self._handle_event_key_down(event)
        elif event.type == EVENT_FRAME_SKIP:
            self.jump_to_frame(frame_indx=event.frame_index)
        elif event.type == EVENT_PAUSE:
            self.pause()
        elif event.type == EVENT_PLAY:
            self.play()

    def _handle_event_key_down(self,event:pygame.event.Event):
        #post event that toggles pause
        if event.key == pygame.K_SPACE:
            if self.paused:
                pygame.event.post(pygame.event.Event(EVENT_PLAY))
            else:
                pygame.event.post(pygame.event.Event(EVENT_PAUSE))





    ### SETTERS ###

    #set current frame
    def set_current_frame(self,frame) -> None:
        self.current_frame_image = frame

        # #update display
        # self.draw()

    

    ### GETTERS ###
    def get_crop_selection(self) -> (Coordinate,Coordinate):
        if not self.show_crop_overlay:
            return None
        
        selection = self.component_crop_overlay.get_selection()


        height_multi = self.video.get(cv2.CAP_PROP_FRAME_HEIGHT) / self.component_crop_overlay.surface.get_height()
        width_multi = self.video.get(cv2.CAP_PROP_FRAME_WIDTH) / self.component_crop_overlay.surface.get_width()

        #adjust selection (given in window size dimensions) to be relative to real frame size (account for window resize)
        x1 = round(selection[0][0] * width_multi)
        x2 = round(selection[0][1] * width_multi)

        h1 = round(selection[1][0] * height_multi)
        h2 = round(selection[1][1] * height_multi)

        return ((x1,x2),(h1,h2))




    #FRAME POSITIONING/DIMENSIONS
    
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



    ### VIDEO INTERACTION ###
    
    #toggle pause
    def toggle_pause(self) -> bool:
        self.paused = not self.paused
        return self.paused
    
    def pause(self):
        self.paused = True

    def play(self):
        self.paused = False



    # to be called on each tick of the loop
    def tick(self) -> tuple[bool,bool]: #return true if end of video
        """returns booleans ( isPlaying , isEndOfVideo )"""
        isEndOfVideo = False
        isPlaying = not self.paused
        
        if not self.paused:
            success,frame = self.video.read()
            
            if not success:
                self.jump_to_frame(0)
                isEndOfVideo =  True
            else:
                self.set_current_frame(frame)

        #update display on every tick (possible inefficiency)
        self.draw()

        return (isPlaying,isEndOfVideo)
    

    #return true if successfully jumped, return false if out of range of frames
    def jump_to_frame(self,frame_indx:int) -> bool:
        max_frame = self.video.get(cv2.CAP_PROP_FRAME_COUNT)

        #invalid frame
        if frame_indx > max_frame or frame_indx < 0:
            return False
        
        self.video.set(cv2.CAP_PROP_POS_FRAMES,frame_indx)
        success,frame = self.video.read()

        if not success:
            raise Exception("unexpected error, unable to read frame when jumping to frame.")

        self.set_current_frame(frame)