import pygame
from Component import Component

# TODO
# MAKE FRAME SURFACE A COMPONENT
# BIND CROP OVERLAY TO FRAME SURFACE SO POSITIONS ITSELF 0,0 AUTOMATICALLY
# PERHAPS ADD CROP OVERLAY INTO VIDEOPLAYER COMPONENT AND SET A BOOLEAN TO DISPLAY/HIDE OVERLAY - DO THIS #TODO#TODO


class CropOverlay(Component):
    def __init__(self,
        dimensions:tuple[int,int],
        position:tuple[int,int],
        initial_selection_dimensions:tuple[int,int],
        handle_width:int,
        max_selection:tuple[int,int], #max selection rect x y area
        min_selection:tuple[int,int],
        aspect_ratio:float | None = None, #if aspect ratio is passed, ensure initial dimensions are within said aspect ratio
        bg_alpha:int = 128, #how dark the not selected area of the video should be, 0-255
        parent: Component | None = None
    ):
        #SUPER
        super().__init__(
            dimensions=dimensions,
            position=position,
            parent=parent,
            surface_args=[pygame.SRCALPHA,32] #transparent surface
        )
        
        self.aspect_ratio = aspect_ratio

        self.bg_alpha = bg_alpha

        self.handle_width = handle_width

        bg_w = dimensions[0]
        bg_h = dimensions[1]

        self.max_selection = max_selection
        self.min_selection = min_selection

        #build area selection rectangle
        
        initial_rect_handle_w = initial_selection_dimensions[0]
        initial_rect_handle_h = initial_selection_dimensions[1]

        initial_rect_body_w = initial_selection_dimensions[0] - (2 * handle_width)
        initial_rect_body_h = initial_selection_dimensions[1] - (2 * handle_width)

        initial_rect_left = int((bg_w  - initial_rect_handle_w) / 2)
        initial_rect_top = int((bg_h  - initial_rect_handle_h) / 2)

        self.handle_rect = pygame.Rect(initial_rect_left,initial_rect_top,initial_rect_handle_w,initial_rect_handle_h)
        self.body_rect = pygame.Rect(initial_rect_left + self.handle_width,initial_rect_top + self.handle_width,initial_rect_body_w,initial_rect_body_h)

        self.draw()

        # self.surface = pygame.Surface((bg_w,bg_h),pygame.SRCALPHA,32) #transparent surface
        
        #drag offset

        self.drag_offset_x = 0 #how much to offset position based on mouse location on selection
        self.drag_offset_y = 0 #how much to offset position based on mouse location on selection


        #area rect booleans
        self.is_moving = False
        self.is_resizing = False

        self.is_hovering_handle = False
        self.is_hovering_body = False


    ### GETTERS ###

    def get_selection(self):
        return ( (self.body_rect.left , self.body_rect.left + self.body_rect.w) , (self.body_rect.top , self.body_rect.top + self.body_rect.h))


    ### UTILITY ###
    
    #generate the position the rectangle should be placed at, factoring in the initial offset, based on the passed pos (typically passed pos will be mouse_pos)
    def _generate_pos_factoring_drag_offset(self,surface_pos:tuple[int,int]) -> tuple[int,int]:        
        return ( surface_pos[0] + self.drag_offset_x , surface_pos[1] + self.drag_offset_y )


    #return boolean regarding wether passes position collides with handle of area rectangle
    def is_handle_collide(self,surface_pos:tuple[int,int]) -> bool:
        return self.handle_rect.collidepoint(surface_pos) and not self.body_rect.collidepoint(surface_pos)
    
    #return boolean regarding wether passes position collides with body of area rectangle
    def is_body_collide(self,surface_pos):
        return self.body_rect.collidepoint(surface_pos)



    ### DISPLAY MANIPULATION ###

    #draw rectangles to surface
    def draw(self):
        self.surface.fill((0,0,0,self.bg_alpha)) #erase previous rects
        pygame.draw.rect(self.surface,(255,255,255,255),self.handle_rect,width=self.handle_width)
        pygame.draw.rect(self.surface,(0,0,0,0),self.body_rect)
    
    #move the selection rectangle to the position specified
    def move_selection_area(self,pos:tuple[int,int]):
        self.handle_rect.left = pos[0]
        self.handle_rect.top = pos[1]

        self.combine_rects()


    #ensure body rect is contained centrally within handle rect
    def combine_rects(self):
        #resize to fit handle_rect
        self.body_rect.w = self.handle_rect.w - (2 * self.handle_width)
        self.body_rect.h = self.handle_rect.h - (2 * self.handle_width)

        #reposition to fit handle rect centrally
        self.body_rect.top = self.handle_rect.top + self.handle_width
        self.body_rect.left = self.handle_rect.left + self.handle_width



    ### EVENTS ###

    def resize(self,xy:tuple[int,int]):        


        original_window_w = self.surface.get_width()
        original_window_h = self.surface.get_height()

        #resize surface
        self.surface = pygame.Surface(xy,pygame.SRCALPHA,32)

        
        ## maintain relative position/dimensions of area selection rect

        #get relative position of rect based on viewport dimensions
        x_pos_percentage = self.handle_rect.left / original_window_w
        y_pos_percentage = self.handle_rect.top / original_window_h

        #get relaitve dimensions of rect based on viewport dimensions
        x_dim_percentage = self.handle_rect.w / original_window_w
        y_dim_percentage = self.handle_rect.h / original_window_h

        #set relative position based on new viewport
        self.handle_rect.left = round(x_pos_percentage * self.surface.get_width())
        self.handle_rect.top = round(y_pos_percentage * self.surface.get_height())

        #set relative dimensions based on new viewport
        self.handle_rect.w = round(x_dim_percentage * self.surface.get_width())
        self.handle_rect.h = round(y_dim_percentage * self.surface.get_height())

        self.combine_rects()
        self.draw()


    def _handle_event(self,event):
        match event.type:
            case pygame.MOUSEBUTTONDOWN:
                if event.button == 1: #LMB
                    self._handle_event_lmb_down(event)
            case pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self._handle_event_lmb_up(event)
            case pygame.MOUSEMOTION:
                self._handle_event_mouse_motion(event)



    #to run when lmb down event occurs
    def _handle_event_lmb_down(self,event):
        pos = self.convert_window_position_to_relative_to_surface(event.pos)

        if self.is_body_collide(pos):
            self.is_moving = True

            #calculate drag offset based of position of mouse when selecting rect
            pos_x,pos_y = pos
            self.drag_offset_x = self.handle_rect.left - pos_x 
            self.drag_offset_y = self.handle_rect.top - pos_y
        
        if self.is_handle_collide(pos):
            self.is_resizing = True

    #to run on mouse motion event
    def _handle_event_mouse_motion(self,event):
        pos = self.convert_window_position_to_relative_to_surface(event.pos)

        
        ### handle cursor image change
        original_cursor = pygame.mouse.get_cursor()
        new_cursor = None
        
        use_defualt_cursor_on_no_other_changes = False #false because we want to maintain current cursor if it is being dictated by another portion of the program

        #check if ended hovering body
        if self.is_hovering_body and not self.is_body_collide(pos):
            self.is_hovering_body = False
            use_defualt_cursor_on_no_other_changes = True
        #check if started hovering body
        elif not self.is_hovering_body and self.is_body_collide(pos):
            self.is_hovering_body = True
            new_cursor = pygame.SYSTEM_CURSOR_SIZEALL
        
        #check if ended hovering handle
        if self.is_hovering_handle and not self.is_handle_collide(pos):
            self.is_hovering_handle = False
            use_defualt_cursor_on_no_other_changes = True
        #check if started hovering handle
        elif not self.is_hovering_handle and self.is_handle_collide(pos):
            self.is_hovering_handle = True

        if new_cursor != None and new_cursor != original_cursor:
            pygame.mouse.set_cursor(new_cursor)
        elif use_defualt_cursor_on_no_other_changes:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        #select correct cursor image based on position within handle (this can change so is done on every move if hovering)
        if self.is_hovering_handle:
            #get position of mouse relative to the position of the area rect
            pos_x_relative_to_handle = pos[0] - self.handle_rect.left
            pos_y_relative_to_handle = pos[1] - self.handle_rect.top

            is_top_handle = pos_y_relative_to_handle <= self.handle_width
            is_bot_handle = pos_y_relative_to_handle >= self.handle_rect.h - self.handle_width

            is_left_handle = pos_x_relative_to_handle <= self.handle_width
            is_right_handle = pos_x_relative_to_handle >= self.handle_rect.w - self.handle_width

            cursor = None

            if (is_top_handle and is_left_handle) or (is_bot_handle and is_right_handle): #NWSE
                cursor = pygame.SYSTEM_CURSOR_SIZENWSE
            elif (is_top_handle and is_right_handle) or (is_bot_handle and is_left_handle): #NESW
                cursor = pygame.SYSTEM_CURSOR_SIZENESW
            elif is_left_handle or is_right_handle:
                cursor = pygame.SYSTEM_CURSOR_SIZEWE
            elif is_top_handle or is_bot_handle:
                 cursor = pygame.SYSTEM_CURSOR_SIZENS

            if cursor != None:
                pygame.mouse.set_cursor(cursor)
        ###
        
        
        if self.is_moving:
            self.move_selection_area(self._generate_pos_factoring_drag_offset(pos))
        
        if self.is_resizing:
            #calculate wether user is resizing from the left/right & top/bottom
            is_right_side_select =(pos[0] - self.handle_rect.left) - ( self.handle_rect.w  / 2) > 0
            is_top_side_select = (pos[1] - self.handle_rect.top) - ( self.handle_rect.h  / 2) > 0

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
                else: #respect y change, manipulate x based on y movemjlkent
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

        self.handle_rect.clamp_ip(self.surface.get_rect())
        self.combine_rects()

        self.draw()


    #to run on lmb up event
    def _handle_event_lmb_up(self,event):
        if self.is_moving:
            self.is_moving = False
            self.drag_offset_x = 0
            self.drag_offset_y = 0
        
        if self.is_resizing:
            self.is_resizing = False

