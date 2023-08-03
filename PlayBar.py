import pygame
from Formatter import Formatter,Element,Percentage,Span,AspectMultiplier
from typing import Callable
from Component import Component,Coordinate


#TODO
# 


# ADD PAUSE BUTTON FUNCTIONALITY
# THIN OUT PLAYBAR HEIGHT, ADD MIN MAX
# ADD ABILITY TO MOVE END OF PROGRESS BAR
# BETTER INTEGRATE 'NEXT_FRAME' FUNCTIONALITY INTO VIDEOCROP.PY

# NEXT FRAME AS AN EVENT SO CAN BE HANDLED EASILY THROUGHOUT EACH COMPONENT, ATTR: frame_index
# PAUSE AS AN EVENT SO CAN BE HANDLED EASILY THROUGHOUT EACH COMPONENT, ATTR: state
# FRAME SKIP, ATTR: frame_index (maybe only need this instead of next frame also)


class PlayBar(Component):
    def __init__(self,
                dimensions:Coordinate,
                position:Coordinate,
                fps:int,
                frame_count:int,
                parent:Component | None = None
            ):
        
        #inheritance
        super().__init__(
            dimensions=dimensions,
            position=position,
            parent=parent,
        )

        # self.surface  = pygame.Surface(dimensions)
        self.surface.fill((0,0,0))

    

        self.fps = fps
        self.frame_count = frame_count 

        self.current_frame_index = 0
        #formatting
        self.element_pauseplay = Element("pauseplay",
                                        order=(0,1),
                                        width=AspectMultiplier(1),
                                        height=Percentage(0.4)
                                    )
        
        self.element_progress_bar = Element(
                                    "progress_bar",
                                    order=(1,1),
                                    width=Percentage(0.8),
                                    height=Percentage(0.4),
                                )
        
        self.formatter = Formatter(parent_dimensions=dimensions,
                                   rows=[
                                        Percentage(0.2,relative_to_container=False),
                                        Percentage(0.6,relative_to_container=False)
                                    ],
                                   columns=[
                                       Percentage(0.1,relative_to_container=False),
                                       Percentage(0.9,relative_to_container=False)
                                   ],
                                   elements=[
                                       self.element_pauseplay,
                                       self.element_progress_bar,
                                    ]
                                )


        pauseplay_rect_pos = self.formatter.get_position("pauseplay")
        pauseplay_rect_dim = self.formatter.get_dimensions("pauseplay")
        self.rect_pauseplay = pygame.Rect(*pauseplay_rect_pos,*pauseplay_rect_dim)
        
        progress_bar_rect_pos = self.formatter.get_position("progress_bar")
        progress_bar_rect_dim = self.formatter.get_dimensions("progress_bar")
        self.rect_progress_bar = pygame.Rect(*progress_bar_rect_pos,1,progress_bar_rect_dim[1])
        
        self.rect_progress_container = pygame.Rect(*progress_bar_rect_pos,*progress_bar_rect_dim)

        self.update_progress_bar()


        self.draw()


    
    ### display changes ###

    #draw rects 
    def draw(self):
        self.surface.fill((0,0,0))
        pygame.draw.rect(self.surface,(0,255,255),self.rect_pauseplay)

        pygame.draw.rect(self.surface,(255,255,255),self.rect_progress_container)
        pygame.draw.rect(self.surface,(110,150,200),self.rect_progress_bar)
        pygame.draw.rect(self.surface,(200,200,200),self.rect_progress_container,width=self._get_outline_width())




    def resize(self,xy:tuple[int,int]):
        width,height = xy

        #generate new surface
        self.set_dimensions(xy)
        self.surface.fill((0,255,0))

        self.formatter.resize_parent(width=width,height=height)

        pauseplay_rect_pos = self.formatter.get_position("pauseplay")
        pauseplay_rect_dim = self.formatter.get_dimensions("pauseplay")
        self.rect_pauseplay = pygame.Rect(*pauseplay_rect_pos,*pauseplay_rect_dim)

        progress_bar_rect_pos = self.formatter.get_position("progress_bar")
        progress_bar_rect_dim = self.formatter.get_dimensions("progress_bar")
        self.rect_progress_bar = pygame.Rect(*progress_bar_rect_pos,*progress_bar_rect_dim)
        self.update_progress_bar()


        self.rect_progress_container = pygame.Rect(*progress_bar_rect_pos,*progress_bar_rect_dim)

        self.draw()

    def update_progress_bar(self):
        self.rect_progress_bar.w = int(round(self.rect_progress_container.w * self.get_progress_percentage()))


    ### setters ###

    def set_current_frame_index(self,index) -> None:
        if index > self.frame_count:
            raise Exception(f"cannot set frame index to a frame greater than the frame count. Tried setting index '{index}' , frame-count: '{self.frame_count}'")
        
        self.current_frame_index = index
        self.update_progress_bar()

    
    ### getters ###

    def _get_outline_width(self) -> int:
        max_val = 3
        min_val = 1
        
        return  max(
            min_val,
            min(
                max_val,
                round(self.get_dimensions()[1] * 0.05)
            )
        )


    ### events ###
    def _handle_event(self,event):
        match event.type:
            case pygame.VIDEORESIZE:
                self.resize((event.w,event.h))






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
        return (self.current_frame_index /  self.frame_count)


    #updates the progress bar on display of next frame
    def next_frame(self) -> None:
        self.set_current_frame_index(self.current_frame_index + 1)
        self.draw()
    


if __name__ == "__main__":
    x = PlayBar((600,200),60,2000)