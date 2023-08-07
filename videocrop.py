import pygame
import cv2
from CropOverlay import CropOverlay
from VideoPlayer import VideoPlayer
from PlayBar import PlayBar

def main():
    v = VideoCrop("sample.mp4")
    v.start()


class VideoCrop:
    def __init__(self,fp:str) -> None:
        self.video = cv2.VideoCapture(fp)

        if self.video.isOpened() == False:
            raise Exception(f"video '{fp}' could not be opened.")

        #video metadata
        self.v_dimensions_width = int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.v_dimensions_height = int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.v_fps = self.video.get(cv2.CAP_PROP_FPS)

        #display proportions
        self.display_video_coverage_h = 0.9 #the amount of screen in the y-direction to be covered by the video
        self.display_play_bar_coverage_h = 0.1 #the amount of screen in the y-direction to be covered by the play bar

        #display
        self.clock = pygame.time.Clock()
        self.window = pygame.display.set_mode(self.get_video_dimensions(),pygame.RESIZABLE)

        #video player
        self.video_player = VideoPlayer(
            dimensions=(self.gen_dimensions_video_surface()),
            position=self.gen_position_video_surface(),
            video=self.video,
            show_crop_overlay=True,
        )



        self.play_bar = PlayBar(
            dimensions=self.gen_dimensions_playbar_surface(),
            position=self.gen_position_playbar_surface(),
            fps=self.v_fps,
            frame_count=self.video.get(cv2.CAP_PROP_FRAME_COUNT)
        )

        #display variables
        self.shown = False
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
    
    #start
    def start(self) -> None:
        self._start_event_loop()

    #quit
    def quit(self) -> None:
        self.running = False

    #resizes window and frame displayed
    def resize_window(self,xy:tuple[int,int]):
        self.window = pygame.display.set_mode(xy,pygame.RESIZABLE)
        
        #video player
        self.video_player.resize(self.gen_dimensions_video_surface())
        self.video_player.set_position(self.gen_position_video_surface())
        
        #playbar
        self.play_bar.set_position(self.gen_position_playbar_surface())
        self.play_bar.resize(self.gen_dimensions_playbar_surface())



    ### UTILITY METHODS ###
    
    #get dimensions
    def get_video_dimensions(self) -> tuple[int,int]:
        return (self.v_dimensions_width,self.v_dimensions_height)
    
    #generate video surface display dimensions/position based on window size
    def gen_dimensions_video_surface(self) -> tuple[int,int]:
        return (self.window.get_width(),self.window.get_height() - 200)
    
    def gen_position_video_surface(self) -> tuple[int,int]:
        return (0,0)
    
    #generate video surface display dimensions/position based on window size
    def gen_dimensions_playbar_surface(self) -> tuple[int,int]:
        return (self.window.get_width(),200)
    
    def gen_position_playbar_surface(self) -> tuple[int,int]:
        return (0,self.gen_dimensions_video_surface()[1])



    ### VIDEO WRITE ###

    # crop the video 

    def video_crop(self):
        selection = self.video_player.get_crop_selection()

        if selection == None:
            return
        
        x_range,y_range = selection


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
        self.video_player._handle_event(event)
        self.play_bar._handle_event(event)
        
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
                
    
    def _handle_event_key_down(self,event) -> None:
        match event.key:
            #quit on escape key press (for dev testing purposes)
            case pygame.K_ESCAPE:
                self.quit()

            #save video
            case pygame.K_RETURN:
                self.video_crop()




    ### LOOP ###

    #loop pygame to handle events and render new frames on tick
    def _start_event_loop(self) -> None:
        clock = pygame.time.Clock()

        while self.running:
            clock.tick(self.v_fps)
            
            #handle events
            for event in pygame.event.get():
                self._handle_event(event)


            isPlaying,isEndOfVideo = self.video_player.tick()

            if isPlaying:
                if not isEndOfVideo:
                    self.play_bar.next_frame()
                else:
                    self.play_bar.set_current_frame_index(0)    

            
            self.window.blit(self.video_player.surface,self.video_player.get_position())
            self.window.blit(self.play_bar.surface,self.play_bar.get_position())
            
            pygame.display.flip()

if __name__ == "__main__":
    main()