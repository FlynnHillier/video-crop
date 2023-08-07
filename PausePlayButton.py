import pygame
from Button import Button
from Component import Coordinate,Component


class PausePlayButton(Button):
    def __init__(self,
        dimensions:Coordinate,
        position:Coordinate,
        parent:Component | None = None,
    ):
        state_displays = {
            1:pygame.image.load("media\\play.png"),
            2:pygame.image.load("media\\pause.png")
        }

        onClick = lambda state : print(state)


        super().__init__(
            dimensions=dimensions,
            color=(255,255,255),
            position=position,
            onClick=onClick,
            start_state=1,
            state_count=2,
            state_displays=state_displays,
            surface_args=[pygame.SRCALPHA,32], #transparent
            parent=parent,
        )