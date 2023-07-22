import pygame
import cv2
from CropOverlay import CropOverlay

def main():
    v = VideoCrop("sample.mp4")
    v.start()


class VideoCrop:
    def __init__(self,fp:str) -> None:
        self.video = cv2.VideoCapture(fp)

        if self.video.isOpened() == False:
            raise Exception(f"video '{fp}' could not be opened.")

        self.v_dimensions_width = int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.v_dimensions_height = int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.v_fps = self.video.get(cv2.CAP_PROP_FPS)
        
        self.current_frame = None

        self.clock = pygame.time.Clock()
        self.window = pygame.display.set_mode(self.get_dimensions(),pygame.RESIZABLE)

        self.video_surface = pygame.Surface(self.get_dimensions()) #resize this in future to not fill whole window (if add playback bar for example)

        self.crop_overlay = CropOverlay(self.get_dimensions(),(100,100),10)

        self.shown = False
        self.paused = False
        self.thread = None
        self.running = True



    ### USER-EXPOSED INTERACTION METHODS ###


    #hide window (not tested)
    def hide(self) -> None:
        pygame.display.set_mode((100,100),flags=pygame.HIDDEN)
        self.shown = False
    
    #show window (not tested)
    def show(self) -> None:
        pygame.display.set_mode(self.get_dimensions(),pygame.RESIZABLE)
        self.shown = True
    
    #pause video playback
    def pause(self) -> None:
        self.paused = True
    
    #unpause video playback
    def unpause(self) -> None:
        self.paused = False
    
    #toggle pause
    def toggle_pause(self) -> bool:
        self.paused = not self.paused
        return self.paused
    
    #start
    def start(self) -> None:
        self.show()
        self._start_event_loop()

    #quit
    def quit(self) -> None:
        self.running = False



    ### UTILITY METHODS ###


    #resize frame to fit fit window
    def resize_frame_to_window_dimensions(self,frame): #-> frame
        return cv2.resize(frame,self.get_dimensions())
    
    #get dimensions
    def get_dimensions(self) -> tuple[int,int]:
        return (self.v_dimensions_width,self.v_dimensions_height)
    
    
    
    ### VIDEO DISPLAY ###


    #fetch next frame from video
    def next_frame(self) -> tuple[bool,any]:
        success,frame = self.video.read()
        if success:
            frame = self.resize_frame_to_window_dimensions(frame) #resize frame to fit window dimensions
            return True,frame
        else:
            return False,None
    
    #display frame in window
    def display_frame(self,frame) -> None:
        frame_surface = pygame.image.frombuffer(frame.tobytes(),frame.shape[1::-1],"BGR")

        self.current_frame = frame

        #write frame to window
        self.video_surface.blit(frame_surface,(0,0))


    #resizes window and frame displayed
    def resize_window(self,xy:tuple[int,int]):
        width,height = xy
        
        self.v_dimensions_width = width
        self.v_dimensions_height = height

        self.window = pygame.display.set_mode(self.get_dimensions(),pygame.RESIZABLE)

        #redisplay current frame onto new surface
        frame = self.resize_frame_to_window_dimensions(self.current_frame)
        self.display_frame(frame)



    ### EVENTS ###

    def _handle_event(self,event) -> None:
        match event.type:
            #handle user quit window
            case pygame.QUIT:
                self.quit()
            
            #handle resize
            case pygame.VIDEORESIZE:
                self.resize_window((event.w,event.h))

            #handle keypress
            case pygame.KEYDOWN:
                self._handle_event_key_down(event)


            ## MOUSE ##

            case pygame.MOUSEBUTTONDOWN:
                self._handle_event_mouse_down(event)
                
    
    def _handle_event_key_down(self,event) -> None:
        match event.key:
            #quit on escape key press (for dev testing purposes)
            case pygame.K_ESCAPE:
                self.quit()
            
            #toggle pause video
            case pygame.K_SPACE:
                self.toggle_pause()


    def _handle_event_mouse_down(self,event) -> None:
        match event.button:
            case 1: #LMB
                self.crop_overlay.move_selection_area((100,100))





    ### LOOP ###

    #loop pygame to handle events and render new frames on tick
    def _start_event_loop(self) -> None:
        clock = pygame.time.Clock()

        while self.running:
            clock.tick(self.v_fps)
            
            #handle events
            for event in pygame.event.get():
                self._handle_event(event)


            if not self.paused:
                #read next frame
                success,frame = self.next_frame()

                if success:
                    self.display_frame(frame)
                else:
                    #no more frames left to read.
                    self.quit()
            
            self.window.blit(self.video_surface,(0,0))
            self.window.blit(self.crop_overlay.get_surface(),(0,0))
            
            pygame.display.flip()

if __name__ == "__main__":
    main()