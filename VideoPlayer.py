import pygame
import cv2 

class VideoPlayer:
    def __init__(self,dimensions:tuple[int,int],video:cv2.VideoCapture):
        self.surface = pygame.Surface(dimensions)

        self.video = video
        self.current_frame = None
        
        self.paused = False

    #handle resize
    def resize(self,xy:tuple[int,int]):
        self.surface = pygame.Surface(xy)

        #redisplay current frame onto new surface
        self.display_frame(self.current_frame)

    #resize frame to fit display
    def resize_frame_to_fit_display(self,frame): #-> frame
        return cv2.resize(frame,(self.surface.get_width(),self.surface.get_height()))
    
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
            frame = self.resize_frame_to_fit_display(frame) #resize frame to fit window dimensions
            return True,frame
        else:
            return False,None
    
    #display frame in window
    def display_frame(self,frame) -> None:
        fitted_frame = self.resize_frame_to_fit_display(frame)
        frame_surface = pygame.image.frombuffer(fitted_frame.tobytes(),fitted_frame.shape[1::-1],"BGR")
        self.current_frame = frame

        #write frame to window
        self.surface.blit(frame_surface,(0,0))