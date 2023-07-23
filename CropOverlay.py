import pygame

class CropOverlay:
    def __init__(self,
            bg_dimensions:tuple[int,int],
            initial_rect_dimensions:tuple[int,int],
            handle_width:int,
        ):
        self.handle_width = handle_width

        self.bg_w = bg_dimensions[0]
        self.bg_h = bg_dimensions[1]

        self.rect_handle_w = initial_rect_dimensions[0]
        self.rect_handle_h = initial_rect_dimensions[1]

        self.rect_body_w = initial_rect_dimensions[0] - (2 * handle_width)
        self.rect_body_h = initial_rect_dimensions[1] - (2 * handle_width)

        initial_rect_left = int((self.bg_w  - self.rect_handle_w) / 2)
        initial_rect_top = int((self.bg_h  - self.rect_handle_h) / 2)

        self.handle_rect = pygame.Rect(initial_rect_left,initial_rect_top,self.rect_handle_w,self.rect_handle_h)
        self.body_rect = pygame.Rect(initial_rect_left + self.handle_width,initial_rect_top + self.handle_width,self.rect_body_w,self.rect_body_h)

        self.surface = pygame.Surface((self.bg_w,self.bg_h),pygame.SRCALPHA,32) #transparent surface
        
        self.drag_offset_x = 0 #how much to offset position based on mouse location on selection
        self.drag_offset_y = 0 #how much to offset position based on mouse location on selection

        self.is_moving = False
        self.is_resizing = False

    #draw rectangles to surface
    def update(self):
        self.surface.fill((255,255,255,0)) #erase previous rects
        pygame.draw.rect(self.surface,(255,0,0),self.handle_rect)
        pygame.draw.rect(self.surface,(0,255,0),self.body_rect)

    #update and return the surface
    def get_surface(self):
        self.update()
        return self.surface
    
    #move the selection rectangle to the position specified
    def move_selection_area(self,pos:tuple[int,int]):
        self.handle_rect.left = pos[0]
        self.handle_rect.top = pos[1]
        self.combine_rects()


    #ensure body rect is contained centrally within handle rect
    def combine_rects(self):
        self.body_rect.top = self.handle_rect.top + self.handle_width
        self.body_rect.left = self.handle_rect.left + self.handle_width


    #generate the position the rectangle should be placed at, factoring in the initial offset, based on the passed pos (typically passed pos will be mouse_pos)
    def _generate_pos_factoring_drag_offset(self,pos:tuple[int,int]) -> tuple[int,int]:
        return ( pos[0] + self.drag_offset_x , pos[1] + self.drag_offset_y )


    #return boolean regarding wether passes position collides with handle of area rectangle
    def is_handle_collide(self,pos:tuple[int,int]) -> bool:
        return self.handle_rect.collidepoint(pos) and not self.body_rect.collidepoint(pos)
    
    #return boolean regarding wether passes position collides with body of area rectangle
    def is_body_collide(self,pos):
        return self.body_rect.collidepoint(pos)
    
    #to run when lmb down event occurs
    def on_lmb_down(self,pos):
        if self.is_body_collide(pos):
            self.is_moving = True
            pos_x,pos_y = pos
            self.drag_offset_x = self.handle_rect.left - pos_x
            self.drag_offset_y = self.handle_rect.top - pos_y
        
        if self.is_handle_collide(pos):
            self.is_resizing = True

    #to run on mouse motion event
    def on_mouse_motion(self,event):
        if self.is_moving:
            self.move_selection_area(self._generate_pos_factoring_drag_offset(event.pos))
        
        if self.is_resizing:
            #calculate wether user is resizing from the left/right & top/bottom
            is_right_side_select =(event.pos[0] - self.handle_rect.left) - ( self.handle_rect.w  / 2) > 0
            is_top_side_select = (event.pos[1] - self.handle_rect.top) - ( self.handle_rect.h  / 2) > 0

            #get change relative to which direction the user is moving relative to the edges of the rectangle
            change_x = event.rel[0] if is_right_side_select else event.rel[0] * -1
            change_y = event.rel[1] if is_top_side_select else event.rel[1] * -1

            #inflate by scale factor 2 of change to ensure border of rectangle tracks mouse.
            self.handle_rect.inflate_ip(change_x * 2,change_y * 2)
            self.body_rect.inflate_ip(change_x * 2,change_y * 2)


    #to run on lmb up event
    def on_lmb_up(self):
        if self.is_moving:
            self.is_moving = False
            self.drag_offset_x = 0
            self.drag_offset_y = 0
        
        if self.is_resizing:
            self.is_resizing = False
