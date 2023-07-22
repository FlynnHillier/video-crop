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



    def update(self):
        self.surface.fill((255,255,255,0)) #erase previous rects
        pygame.draw.rect(self.surface,(255,0,0),self.handle_rect)
        pygame.draw.rect(self.surface,(0,255,0),self.body_rect)

    def get_surface(self):
        self.update()
        return self.surface
    
    def move_selection_area(self,vector:tuple[int,int]):
        self.handle_rect = self.handle_rect.move(vector[0],vector[1])
        self.body_rect = self.body_rect.clamp(self.handle_rect)
        self.body_rect.top += self.handle_width
        self.body_rect.left += self.handle_width
        
