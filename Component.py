import pygame

Coordinate = tuple[int,int]

class Component:
    def __init__(self,dimensions:tuple[int,int],position:tuple[int,int],parent = None,surface_args = []):
        self.surface_args = surface_args
        
        self.surface : pygame.Surface = pygame.Surface(dimensions,*surface_args)
        
        self.position = position #position relative to parent surface
        self.parent : Component | None = parent
    

    ### SETTERS ###

    def set_position(self,position:Coordinate):
        self.position = position

    def set_dimensions(self,dimensions:Coordinate):
        self.surface = pygame.Surface(dimensions,*self.surface_args)

        #redraw children to surface on resize
        self.draw()

    #manually override surface
    def set_surface(self,surface:pygame.Surface):
        self.surface = surface

    
    ## GETTERS ###

    def get_position(self) -> Coordinate:
        return self.position
    
    def get_dimensions(self) -> Coordinate:
        return (self.surface.get_width(),self.surface.get_height())
    
    #used for determining wether collision has occured with window bound positions
    def get_position_relative_to_window(self) -> Coordinate:
        left,top = self.get_position()

        if self.parent != None:
            parent_left,parent_top = self.parent.get_position_relative_to_window()

            left += parent_left
            top += parent_top
        
        return (left,top)
    

    def convert_window_position_to_relative_to_surface(self,window_pos:Coordinate) -> Coordinate:
        arg_pos_left,arg_pos_top = window_pos
        left,top = self.get_position_relative_to_window()
        
        return (
            arg_pos_left - left,
            arg_pos_top - top,
        )


    ## DISPLAY UPDATES ##

    #draw should append all children to the surface
    def draw(self):
        #if inherited from Component:
        #print("REDEFINE DRAW FUNCTION IF INHERITING FROM COMPONENT CLASS")
        pass