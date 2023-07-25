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
        self.window = pygame.display.set_mode(self.get_video_dimensions(),pygame.RESIZABLE)

        self.video_surface = pygame.Surface(self.get_video_dimensions()) #resize this in future to not fill whole window (if add playback bar for example)

        self.crop_overlay = CropOverlay(
            bg_dimensions=self.get_video_dimensions(),
            initial_rect_dimensions=(90,160),
            handle_width=5,
            max_selection=(608,1080),
            min_selection=(50,50),
            aspect_ratio=9/16
        )

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
        pygame.display.set_mode((self.v_dimensions_width,self.v_dimensions_height),pygame.RESIZABLE)
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
        return cv2.resize(frame,(self.video_surface.get_width(),self.video_surface.get_height()))
    
    #get dimensions
    def get_video_dimensions(self) -> tuple[int,int]:
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
        self.window = pygame.display.set_mode(xy,pygame.RESIZABLE)

        self.crop_overlay.resize(xy)
        self.video_surface = pygame.Surface(xy)



        #redisplay current frame onto new surface
        frame = self.resize_frame_to_window_dimensions(self.current_frame)
        self.display_frame(frame)


    ### VIDEO WRITE ###

    # crop the video 
    def crop_area_selection(self):
        #retrieve selection
        selection = self.crop_overlay.get_selection()

        height_multi = self.v_dimensions_height / self.crop_overlay.get_surface().get_height()
        width_multi = self.v_dimensions_width / self.crop_overlay.get_surface().get_width()

        #adjust selection (given in window size dimensions) to be relative to real frame size (account for window resize)
        x1 = round(selection[0][0] * width_multi)
        x2 = round(selection[0][1] * width_multi)

        h1 = round(selection[1][0] * height_multi)
        h2 = round(selection[1][1] * height_multi)

        self.video_crop((x1,x2),(h1,h2))




    def video_crop(self,x_range:tuple[int,int],y_range:tuple[int,int]):
        #cropped frame size
        frame_w = x_range[1] - x_range[0]
        frame_h = y_range[1] - y_range[0]

        #codec
        fourcc = cv2.VideoWriter.fourcc(*"mp4v")
        
        #video writer constructor
        out = cv2.VideoWriter("out.mp4",fourcc,self.v_fps,(frame_w,frame_h)) 

        #read from new videocapture
        cap = cv2.VideoCapture("sample.mp4")

        #read each frame of video
        while cap.isOpened():
            success,frame = cap.read()

            if success:
                cropped_frame = frame[ y_range[0]:y_range[1], x_range[0]:x_range[1] ] #write colum first and width after? seems to work.
                out.write(cropped_frame)
            else:
                cap.release()
        
        out.release()




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
            case pygame.MOUSEBUTTONUP:
                self._handle_event_mouse_up(event)
            case pygame.MOUSEMOTION:
                self.crop_overlay.on_mouse_motion(event)
                
    
    def _handle_event_key_down(self,event) -> None:
        match event.key:
            #quit on escape key press (for dev testing purposes)
            case pygame.K_ESCAPE:
                self.quit()
            
            #toggle pause video
            case pygame.K_SPACE:
                self.toggle_pause()

            #save video
            case pygame.K_RETURN:
                self.crop_area_selection()
                
    def _handle_event_mouse_down(self,event) -> None:
        match event.button:
            case 1: #LMB
                mouse_pos = pygame.mouse.get_pos()
                self.crop_overlay.on_lmb_down(mouse_pos)

    def _handle_event_mouse_up(self,event) -> None:
        match event.button:
            case 1: #LMB
                self.crop_overlay.on_lmb_up()
            
            





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