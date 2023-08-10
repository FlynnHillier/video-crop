import pygame
from Formatter import Formatter,Element,Percentage,Span,AspectMultiplier
from Component import Component,Coordinate
from PausePlayButton import PausePlayButton

from events import EVENT_FRAME_SKIP,PostEvent_FrameSkip

#TODO
#PLAN
#generate font rect, maybe create new method to expose row height easily - X
#also create method that allows for updating element dimensions
#then with font rect, create element specfiying absolute dimensions - X
# on resize use newly created method (mentioned previously) and




class PlayBar(Component):
    def __init__(self,
                dimensions:Coordinate,
                position:Coordinate,
                fps:int,
                frame_count:int,
                bg_colour = (0,0,0),
                parent:Component | None = None
            ):
        
        #inheritance
        super().__init__(
            dimensions=dimensions,
            position=position,
            parent=parent,
        )

        self.bg_colour = bg_colour

        # self.surface  = pygame.Surface(dimensions)
        self.surface.fill(self.bg_colour)

    

        self.fps = fps
        self.frame_count = frame_count 

        self.current_frame_index = 0
        
        ## formatting

        self.element_pauseplay = Element(
            "pauseplay",
            order=(0,1),
            width=AspectMultiplier(1),
            height=Percentage(0.4),
        )

        self.element_progress_bar = Element(
            "progress_bar",
            order=(2,1),
            width=Percentage(1),
            height=Percentage(0.4),
        )


        self.formatter = Formatter(
            parent_dimensions=dimensions,
            rows=[
                Percentage(0.2,relative_to_container=False),
                Percentage(0.8,relative_to_container=False),
            ],
            columns=[
                Percentage(0.05,relative_to_container=False),
                Percentage(0.05,relative_to_container=False),
                Percentage(0.85,relative_to_container=False),
            ],
            elements=[
                self.element_pauseplay,
                self.element_progress_bar,
            ]
        )

        ## timestamp

        #timestamp element is defined after formatter initialisation, because the height of the element (the font size) is dependant on the height of the row
        #which is calculated within formatter init
    
        if not pygame.font.get_init(): #initiliase pygame font module if not already initiliased.
            pygame.font.init()

        _timestamp_order = (2,0) #column 1, row 0

        timestamp_row_height = self.formatter.get_row_height(_timestamp_order[1])

        timestamp_font_size = round(timestamp_row_height * 0.6)

        timestamp_font = pygame.font.Font("fonts\\arial.ttf",timestamp_font_size)

        timestamp_text = self.milliseconds_to_timestamp(self.get_video_length())
        timestamp_text_colour = (255,255,255)

        self.surface_timestamp = timestamp_font.render(timestamp_text,True,timestamp_text_colour,self.bg_colour)

        timestamp_width,timestamp_height = self.surface_timestamp.get_rect()[:2]


        self.element_timestamp = Element(
            "timestamp",
            order=_timestamp_order,
            width=timestamp_width,
            height=timestamp_height,
            margin={
                "bottom":Percentage(0),
                "left":Percentage(0)
            },
        )

        self.formatter.add_element(self.element_timestamp)


        #pauseplay button
        pauseplay_pos = self.formatter.get_position("pauseplay")
        pauseplay_dim = self.formatter.get_dimensions("pauseplay")
        self.component_pauseplay_button = PausePlayButton(pauseplay_dim,pauseplay_pos,parent=self)


        #progress bar
        progress_bar_rect_pos = self.formatter.get_position("progress_bar")
        progress_bar_rect_dim = self.formatter.get_dimensions("progress_bar")
        self.rect_progress_bar = pygame.Rect(*progress_bar_rect_pos,1,progress_bar_rect_dim[1])
        
        self.rect_progress_container = pygame.Rect(*progress_bar_rect_pos,*progress_bar_rect_dim)

        #if playbar is being dragged by user
        self.isDraggingBar = False




        self.update_progress_bar()
        self.draw()


    
    ### display changes ###

    #to be ran on each tick
    def tick(self,video_is_playing:bool) -> None:
        if video_is_playing:
            self.next_frame(draw=False)
        
        self.draw()



    #draw rects 
    def draw(self):
        self.surface.fill(self.bg_colour)
        
        #pauseplay button
        self.surface.blit(self.component_pauseplay_button.surface,self.component_pauseplay_button.get_position())
        
        #timestamp
        self.surface.blit(self.surface_timestamp,self.formatter.get_position("timestamp"))


        #progress bar
        pygame.draw.rect(self.surface,(255,255,255),self.rect_progress_container)
        pygame.draw.rect(self.surface,(110,150,200),self.rect_progress_bar)
        pygame.draw.rect(self.surface,(200,200,200),self.rect_progress_container,width=self._get_outline_width())



    def resize(self,xy:tuple[int,int]):
        width,height = xy

        #generate new surface
        self.set_dimensions(xy)
        self.surface.fill((0,255,0))

        self.formatter.resize_parent(width=width,height=height)
        
        #draw pauseplay
        pauseplay_rect_pos = self.formatter.get_position("pauseplay")
        pauseplay_rect_dim = self.formatter.get_dimensions("pauseplay")
        self.rect_pauseplay = pygame.Rect(*pauseplay_rect_pos,*pauseplay_rect_dim)

        #draw progress bar rect
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
        if index > self.frame_count or index < 0:
            raise Exception(f"cannot set frame index to a frame greater than the frame count. Tried setting index '{index}' , frame-count: '{self.frame_count}'")
        
        self.current_frame_index = index
        self.update_progress_bar()
        self.draw()

    
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
        self.component_pauseplay_button._handle_event(event)

        #custom
        if event.type == EVENT_FRAME_SKIP:
            self.set_current_frame_index(event.frame_index)
        
        #vanilla
        else:
            match event.type:
                case pygame.VIDEORESIZE:
                    self.resize((event.w,event.h))
                case pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: #LMB
                        self._handle_event_lmb_down(event)
                case pygame.MOUSEBUTTONUP:
                    if event.button == 1: #LMB
                        self._handle_event_lmb_up(event)
                case pygame.MOUSEMOTION:
                    self._handle_event_mousemotion(event)

    
    # MOUSE
    
    def _handle_event_lmb_down(self,event):        
        if self.playbar_is_hovered(event):
            if not self.isDraggingBar:
                self.isDraggingBar = True

                #post event to indicate to jump to specified location in video
                jump_to_ms = self.get_ms_on_playbar_selection(event)
                jump_to_frame_index = self.frame_indx_at_milliseconds(jump_to_ms)
                pygame.event.post(PostEvent_FrameSkip(jump_to_frame_index).event())

    def _handle_event_lmb_up(self,event):
        if self.isDraggingBar:
            self.isDraggingBar = False

    def _handle_event_mousemotion(self,event):
        if self.isDraggingBar:
            jump_to_ms = self.get_ms_on_playbar_selection(event)
            jump_to_frame_index = self.frame_indx_at_milliseconds(jump_to_ms)
            pygame.event.post(PostEvent_FrameSkip(jump_to_frame_index).event())







    ### PLAY BAR INTERACTION ###

    def playbar_is_hovered(self,event:pygame.event.Event) -> bool:
        return self.rect_progress_container.collidepoint(self.convert_window_position_to_relative_to_surface(event.pos))
    





    ### backend utility ###

    #return millisecond timestamp within video, based on where user clicks on the progress bar
    def get_ms_on_playbar_selection(self,event:pygame.event.Event) -> int:
        if not (event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEMOTION):
            raise Exception("invalid event type to retrieve ms on playbar selection")
        
        relative_mouse_pos = self.convert_window_position_to_relative_to_surface(event.pos)
        relative_progress_bar_pos = self.formatter.get_position("progress_bar")
        
        x_vector_from_playbar_container_start = relative_mouse_pos[0] - relative_progress_bar_pos[0]

        bar_container_width = self.rect_progress_container.w

        #account for dragging past bounds of playbar
        if x_vector_from_playbar_container_start < 0:
            x_vector_from_playbar_container_start = 0
        elif x_vector_from_playbar_container_start > bar_container_width:
            x_vector_from_playbar_container_start = bar_container_width
        
        progress_percentage = x_vector_from_playbar_container_start / bar_container_width

        return round(self.get_video_length() * progress_percentage)

        


    #get length of video in milliseconds
    def get_video_length(self) -> int:
        return round((self.frame_count / self.fps) * 1000)


    #get the duration each frame is present in video for, in milliseconds
    def get_duration_per_frame(self) -> float:
        return 1000 / self.fps

    #get timestamp from frame in milliseconds
    def milliseconds_time_from_frame(self,frame_indx) -> float:
        frame_duration = self.get_duration_per_frame()
        return frame_indx * frame_duration
    
    #convert seconds to timestamp
    def milliseconds_to_timestamp(self,milliseconds:int):
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
    def next_frame(self,draw=True) -> None:
        if self.current_frame_index + 1 > self.frame_count:
            #reset frame index when end of video is reached
            self.set_current_frame_index(0)
        else:
            #if not end of video progress to next frame
            self.set_current_frame_index(self.current_frame_index + 1)

        if draw:
            self.draw()
    


if __name__ == "__main__":
    x = PlayBar((600,200),60,2000)