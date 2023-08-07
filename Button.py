import pygame
from Component import Component,Coordinate
from typing import Dict,Callable

class Button(Component):
    def __init__(self,
        dimensions:Coordinate,
        position:Coordinate,
        
        onClick:Callable[[int],any] = lambda : None, #argument is the new state
        
        color: tuple[int,int,int,int] | None = None, # None means transparent
        start_state = 1,
        state_count = 2,
        state_displays: Dict[int,None | pygame.Surface] = {} , # a dict which contains a surface that shows what 

        parent:Component | None = None,
        surface_args:list = []
    ):
        super().__init__(
            dimensions=dimensions,
            position=position,
            parent=parent,
            surface_args=surface_args,
        )

        self._cb_onclick = onClick

        self.color = color

        self.state_displays = state_displays 
        self.state_count = state_count
        self.state = start_state 

        if self.state_count <= 0:
            raise ValueError(f"invalid state count '{state_count}', minimum 1 state")
        
        if self.state > self.state_count:
            raise ValueError(f"invalid starting state '{start_state}', state_count is '{state_count}'")
        

        self.isHeld = False #if
        self.isHovered = False
        
        self.draw()



    def draw(self):
        if self.color != None:
            self.surface.fill(self.color)
        
        target_display_surface = self.state_displays.get(self.state)

        if target_display_surface != None:
            #resize image to fit surface if larger
            actual_width = target_display_surface.get_width()
            actual_height = target_display_surface.get_height()

            max_width = self.surface.get_width()
            max_height = self.surface.get_height()

            if actual_height > max_height and actual_width > max_width:
                target_display_surface = pygame.transform.scale(target_display_surface,(max_width,max_height))
            elif actual_height > max_height:
                target_display_surface = pygame.transform.scale(target_display_surface,(actual_width,max_height))
            elif actual_width > max_width:
                target_display_surface = pygame.transform.scale(target_display_surface,(max_width,actual_height))


            #center image on surface
            s_width = target_display_surface.get_width()
            s_height = target_display_surface.get_height()

            left = round((self.surface.get_width() - s_width) / 2)
            top = round((self.surface.get_height() - s_height) / 2)

            self.surface.blit(target_display_surface,(left,top))

    
    def resize(self,dimensions:Coordinate):
        self.set_dimensions(dimensions)



    ### EVENTS ###
    def _handle_default(self,event):
        if event.type == pygame.MOUSEMOTION:
            original_hover_status = self.isHovered
            self.isHovered = self.get_is_hovered()

            ## update cursor
            if original_hover_status and not self.isHovered:
                #was hovered and no longer is
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            elif not original_hover_status and self.isHovered:
                #was not hovered and now is
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: #LMB
                if self.isHovered:
                    #button clicked
                    self.isHeld = True
                    self.next_state()
                    self._cb_onclick(self.state)


        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1: #LMB
                if self.isHeld:
                    self.isHeld = False
            

    #to be overwritten in child class.
    def _handle_event(self,event:pygame.event.Event):
        self._handle_default(event)



    ### STATE HANDLING ###

    def next_state(self) -> int:
        if self.state + 1 > self.state_count:
            self.set_state(1)
        else:
            self.set_state(self.state + 1)
        
        return self.state

    def set_state(self,state:int) -> bool:
        #invalid state arg
        if state <= 0 or state > self.state_count:
            return False
        
        self.state = state
        self.draw()
        return True



    ### UTILITY ###

    def get_is_hovered(self):
        mouse_pos = pygame.mouse.get_pos()

        relative_mouse_pos = self.convert_window_position_to_relative_to_surface(mouse_pos)

        return self.surface.get_rect().collidepoint(*relative_mouse_pos)