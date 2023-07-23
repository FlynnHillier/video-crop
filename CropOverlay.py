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

        self.rect_pos_x = int((self.bg_w  - self.rect_handle_w) / 2)
        self.rect_pos_y = int((self.bg_h  - self.rect_handle_h) / 2)

        self.handle_rect = pygame.Rect(self.rect_pos_x,self.rect_pos_y,self.rect_handle_w,self.rect_handle_h)
        self.body_rect = pygame.Rect(self.rect_pos_x + self.handle_width,self.rect_pos_y + self.handle_width,self.rect_body_w,self.rect_body_h)

        self.surface = pygame.Surface((self.bg_w,self.bg_h),pygame.SRCALPHA,32) #transparent surface

        
        self.drag_offset_x = 0 #how much to offset position based on mouse location on selection
        self.drag_offset_y = 0 #how much to offset position based on mouse location on selection

        self.is_moving = False
        self.is_resizing = False

    def update(self):
        self.surface.fill((255,255,255,0)) #erase previous rects
        pygame.draw.rect(self.surface,(255,0,0),self.handle_rect)
        pygame.draw.rect(self.surface,(0,255,0),self.body_rect)

    def get_surface(self):
        self.update()
        return self.surface
    
    def move_selection_area(self,pos:tuple[int,int]):
        self.handle_rect.left = pos[0]
        self.handle_rect.top = pos[1]

        # self.body_rect = self.body_rect.clamp(self.handle_rect)
        self.body_rect.top = pos[1] + self.handle_width
        self.body_rect.left = pos[0] + self.handle_width

    
    def _generate_pos_factoring_drag_offset(self,pos:tuple[int,int]) -> tuple[int,int]:
        return ( pos[0] + self.drag_offset_x , pos[1] + self.drag_offset_y )



    def is_handle_collide(self,pos):
        return self.handle_rect.collidepoint(pos) and not self.body_rect.collidepoint(pos)
    
    def is_body_collide(self,pos):
        return self.body_rect.collidepoint(pos)
    
    def on_lmb_down(self,pos):
        if self.is_body_collide(pos):
            self.is_moving = True
            pos_x,pos_y = pos
            self.drag_offset_x = self.handle_rect.left - pos_x
            self.drag_offset_y = self.handle_rect.top - pos_y

    def on_mouse_motion(self,pos):
        if self.is_moving:
            self.move_selection_area(self._generate_pos_factoring_drag_offset(pos))

    def on_lmb_up(self):
        if self.is_moving:
            self.is_moving = False
            self.drag_offset_x = 0
            self.drag_offset_y = 0
