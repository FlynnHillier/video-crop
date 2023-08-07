import pygame
from Button import Button
from Component import Coordinate,Component
from events import EVENT_PAUSE,EVENT_PLAY


class PausePlayButton(Button):
    """states: 1 - paused , 2 - playing"""
    def __init__(self,
        dimensions:Coordinate,
        position:Coordinate,
        start_paused:bool = False,
        parent:Component | None = None,
    ):
        state_displays = {
            1:pygame.image.load("media\\play.png"),
            2:pygame.image.load("media\\pause.png")
        }
        #State 1: paused
        #state 2: playing

        start_state = 1 if start_paused else 2

        super().__init__(
            dimensions=dimensions,
            color=(255,255,255),
            position=position,
            onClick=self._onclick,
            start_state=start_state,
            state_count=2,
            state_displays=state_displays,
            surface_args=[pygame.SRCALPHA,32], #transparent
            parent=parent,
        )

    def _onclick(self,state):
        if state == 1: #post pause
            pygame.event.post(pygame.event.Event(EVENT_PAUSE))
        elif state == 2: #post play
            pygame.event.post(pygame.event.Event(EVENT_PLAY))

    def _handle_event(self, event: pygame.event.Event):
        if event.type == EVENT_PAUSE:
            self.set_state(1)
        elif event.type == EVENT_PLAY:
            self.set_state(2)
        else:
            super()._handle_event(event)


