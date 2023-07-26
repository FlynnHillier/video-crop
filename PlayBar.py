import pygame

class PlayBar:
    def __init__(self,dimensions,fps:int,frame_count:int):
        self.surface  = pygame.Surface(dimensions)
        self.surface.fill((0,0,0))

        self.fps = fps
        self.frame_count = frame_count 

        self.current_frame_indx = 0

    
    ### display changes ###

    def resize(self,xy:tuple[int,int]):
        self.surface = pygame.Surface(xy)
        self.surface.fill((0,0,0))



    ### backend utility ###

    #get the duration each frame is present in video for
    def get_duration_per_frame(self) -> float:
        return 1 / self.fps

    #get timestamp from frame in milliseconds
    def seconds_time_from_frame(self,frame_indx) -> float:
        frame_duration = self.get_duration_per_frame()
        return frame_indx * frame_duration * 1000
    
    #convert seconds to timestamp
    def seconds_to_timestmap(self,milliseconds:float):
        hr = 60 * 60 * 1000
        mint = 60 * 1000
        sec = 1000
        
        hours = int(milliseconds // hr)
        milliseconds = milliseconds % hr

        minutes = int(milliseconds // mint)
        milliseconds = milliseconds % mint

        seconds = int(milliseconds // sec)
        milliseconds = milliseconds % sec

        milliseconds = int(milliseconds) # round down milliseconds and convert to int

        return f"{hours:02d}:{minutes:02d}:{seconds:02d}:{milliseconds:03d}"
    
    #return frame indx at a given millseconds
    def frame_indx_at_milliseconds(self,milliseconds:int) -> int:
        frame_duration = self.get_duration_per_frame()
        return int(milliseconds // frame_duration)
    

    #return progress percentage based on current index
    def get_progress_percentage(self) -> float:
        return (self.current_frame_indx /  self.frame_count) * 100


    #updates the progress bar on display of next frame
    def next_frame(self) -> None:
        self.current_frame_indx += 1
    