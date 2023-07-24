import pygame

class CropOverlay:
    def __init__(self,
            bg_dimensions:tuple[int,int],
            initial_rect_dimensions:tuple[int,int],
            handle_width:int,
            max_selection:tuple[int,int], #max selection rect x y area
            min_selection:tuple[int,int],
            aspect_ratio:float | None = None, #if aspect ratio is passed, ensure initial dimensions are within said aspect ratio
            bg_alpha:int = 128, #how dark the not selected area of the video should be, 0-255
        ):
        self.aspect_ratio = aspect_ratio

        self.bg_alpha = bg_alpha

        
        self.handle_width = handle_width

        self.bg_w = bg_dimensions[0]
        self.bg_h = bg_dimensions[1]

        self.max_selection = max_selection
        self.min_selection = min_selection

        initial_rect_handle_w = initial_rect_dimensions[0]
        initial_rect_handle_h = initial_rect_dimensions[1]

        initial_rect_body_w = initial_rect_dimensions[0] - (2 * handle_width)
        initial_rect_body_h = initial_rect_dimensions[1] - (2 * handle_width)

        initial_rect_left = int((self.bg_w  - initial_rect_handle_w) / 2)
        initial_rect_top = int((self.bg_h  - initial_rect_handle_h) / 2)

        self.handle_rect = pygame.Rect(initial_rect_left,initial_rect_top,initial_rect_handle_w,initial_rect_handle_h)
        self.body_rect = pygame.Rect(initial_rect_left + self.handle_width,initial_rect_top + self.handle_width,initial_rect_body_w,initial_rect_body_h)

        self.surface = pygame.Surface((self.bg_w,self.bg_h),pygame.SRCALPHA,32) #transparent surface
        
        self.drag_offset_x = 0 #how much to offset position based on mouse location on selection
        self.drag_offset_y = 0 #how much to offset position based on mouse location on selection

        self.is_moving = False
        self.is_resizing = False

    #draw rectangles to surface
    def update(self):
        self.surface.fill((0,0,0,self.bg_alpha)) #erase previous rects
        pygame.draw.rect(self.surface,(255,255,255,255),self.handle_rect,width=self.handle_width)
        pygame.draw.rect(self.surface,(0,0,0,0),self.body_rect)

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

            
            min_w = self.min_selection[0]
            max_w = self.max_selection[0]

            min_h = self.min_selection[1]
            max_h = self.max_selection[1]
            #inflate by scale factor 2 of change to ensure border of rectangle tracks mouse.
            w = self.handle_rect.w
            h = self.handle_rect.h
            
            inflate_by_x = 0
            inflate_by_y = 0

            if self.aspect_ratio != None:
                #manipulate change to maintain aspect ratio, respect the most influential change (either x or y) relative to their weight within the aspect ratio.
                if abs(int(change_x * self.aspect_ratio)) >= abs(change_y): #respect x change, manipulate y based on x movement
                    change_y = round(change_x * (1/self.aspect_ratio))
                else: #respect y change, manipulate x based on y movement
                    change_x = round(change_y * self.aspect_ratio)

            #inflate width
            if (change_x > 0 and w + (change_x * 2) <= max_w) or (change_x < 0 and w + (change_x*2) >= min_w): #check that inflating by the given change_x would not exceed/subceed the max/min value for the width
                inflate_by_x = change_x * 2
            elif (change_x > 0 and w < max_w): #if not yet reached maximum width, but mouse movement relative would result in exceeding maximum, set width to maximum.
                inflate_by_x = max_w - self.handle_rect.w
            elif (change_x < 0 and w > min_w): #if not yet reached minimum width, but mouse movement relative would result in subceeding minimum, set width to minimum.
                inflate_by_x = min_w - self.handle_rect.w
            
            #inflate height
            if (change_y > 0 and h + (change_y * 2) <= max_h) or (change_y < 0 and h + (change_y*2) >= min_h): #check that inflating by the given change_y would not exceed/subceed the max/min value for the height
                inflate_by_y = change_y * 2
            elif (change_y > 0 and h < max_h): #if not yet reached maximum height, but mouse movement relative would result in exceeding maximum, set height to maximum.
                inflate_by_y = max_h - self.handle_rect.h
            elif (change_y < 0 and h > min_h): #if not yet reached minimum height, but mouse movement relative would result in subceeding minimum, set height to minimum.
                inflate_by_y = min_h - self.handle_rect.h



            self.handle_rect.inflate_ip(inflate_by_x,0)
            self.body_rect.inflate_ip(inflate_by_x,0)

            self.handle_rect.inflate_ip(0,inflate_by_y)
            self.body_rect.inflate_ip(0,inflate_by_y)

    #to run on lmb up event
    def on_lmb_up(self):
        if self.is_moving:
            self.is_moving = False
            self.drag_offset_x = 0
            self.drag_offset_y = 0
        
        if self.is_resizing:
            self.is_resizing = False
