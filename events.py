import pygame

#constructor class for easily constructing events (to be inherited from)
class PostEvent:
    def __init__(self,type:int,attributes = {}):
        self.type = type
        self.attributes = attributes

    def event(self):
        return pygame.event.Event(self.type,self.attributes)


# frame skip
EVENT_FRAME_SKIP = pygame.event.custom_type()

class PostEvent_FrameSkip(PostEvent):
    def __init__(self,frame_index:int):
        args = {
            "frame_index": frame_index
        }
        super().__init__(EVENT_FRAME_SKIP,args)