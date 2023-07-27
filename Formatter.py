#TODO
# GIVE ABILITY FOR ELEMENTS TO SPAN MULTIPLE COLUMS / ROWS
#IMPLEMENT SOMETHING THAT WILL STOP/WARN IF PERCENTAGES EXCEED MAXIMUM HEIGHT/WIDTH OF ROW/COLUMN
#ADD ON_BIND METHOD TO ROW/COLUM ASWELL AS ON_UNBIND WHICH ADDS ELEMENT TO SELF.ELEMENTS[], (THIS IS A CIRCULAR REFERENCE)


class Span:
    def __init__(self,start:int,end:int | None = None, spread:int | None = None):
        self.start = start
        
        if end != None:
            self.end = end
        elif spread != None:
            self.end = self.start + spread
        else:
            raise ValueError("Span must have atleast one of the keyword arguments 'end' or 'spread' defined.")

    def does_contain(self,index:int) -> bool:
        return index >= self.start and index <= self.end




#handles relative sizing
class Percentage:
    def __init__(self,
        percentage:float,
        relative_to_container:bool = True, #if True percentage should be calculated relative to row/column, if False then instead calculate relative to parent
        min:int | None = None,
        max:int | None = None,
    ):
        self.percentage = percentage
        self.min = min
        self.max = max
        self.relative_to_container = relative_to_container

        
    def get(self,parent_dimension_value:int,container_dimension_value:int):
        
        #calculate relative to what the percentage is in relation to (either parent or container[where container is row/column])
        if self.relative_to_container == True:
            organic_val = self.percentage * container_dimension_value
        else:
            organic_val = self.percentage * parent_dimension_value

        #respect minimum / maximums
        if self.max != None and organic_val > self.max:
            return self.max
        elif self.min != None and organic_val < self.min:
            return self.min
        else:
            return organic_val
        

#UTILITY FUNCTION
#choose correct value, allow for usage of absolute values aswell as implict percentage values
def _get_absolute(v:Percentage | int,parent_dimension_value:int,container_dimension_value:int) -> int:
    if type(v) == int:
        return v
    elif type(v) == Percentage:
        return int(v.get(parent_dimension_value=parent_dimension_value,container_dimension_value=container_dimension_value))
    

#hold parent dimensions in a shared object
class Parent:
    def __init__(self,width:int,height:int):
        self.width:int = width
        self.height:int = height


#handles element verticality
class Row:
    def __init__(self,
        height:int | Percentage,
        parent:Parent,
    ):
        self._height = height
        self.parent = parent


        if self._height.relative_to_container == True:
            raise ValueError(f"row cannot be passed percentage that is relative to container. Only percentage relative to parent.")

    def get_height(self):
        return _get_absolute(v=self._height,
                             parent_dimension_value=self.parent.height,
                             container_dimension_value=0,
                            )
    
    def get_left_pos_in_row(self,element_x):
        #This should be used if element choose to not respect colums and instead position relative to previous elements in row
        pass
    
    #maybe ask elements if they want to fit into just row and ignore colums or if they want to fit into colum and grid, then use those attributes when calculating position within row
        


#handles element horizontal
class Column:
    def __init__(self,
        width:int | Percentage, 
        parent:Parent,
    ):
        self._width = width
        self.parent = parent

        if self._width.relative_to_container == True:
            raise ValueError(f"column cannot be passed percentage that is relative to container. Only percentage relative to parent.")

    def get_width(self) -> int:
        return _get_absolute(v=self._width,
                                parent_dimension_value=self.parent.width,
                                container_dimension_value=0,
                            )
    
    def on_parent_resize(self,parent_width:int):
        self.parent_width = parent_width




#represents an entry to the Formatter class
class Element:
    def __init__(self,
        id:str,
        order:tuple[int | Span, int | Span], #where the element should lie on the x-axis & y-axis with respect to other elements
        width:Percentage | int, 
        height:Percentage | int,
        margin:dict[str,Percentage | int] | None = None, #right,left,top,bottom
        center:bool = True, #if true will ignore margins and auto center in colum/row
    ):
        self.id = id
        self._width = width
        self._height = height

        #format self._order to a tuple[Span,Span] factoring in that arguments may also be passed as an int
        self._order : tuple[Span,Span] = (None,None)
        if type(order[0]) == Span:
            column_span = order[0]
        elif type(order[0]) == int:
            column_span = Span(order[0],spread=0)

        if type(order[1]) == Span:
            row_span = order[1]
        elif type(order[1]) == int:
            row_span = Span(order[1],spread=0)

        self._order = (column_span,row_span)
        
        
        
        #row and column provide references to anchor values such as parent_width and row_height, used for percentage calculations
        self.rows : list[Row] = []
        self.columns : list[Column] = []
        self.parent : Parent | None = None


        self.center = center

        #define margin based on margin values
        if margin != None:
            self.margin_right = margin["right"] if "right" in margin else 0
            self.margin_left = margin["left"] if "left" in margin else 0
            self.margin_top = margin["top"] if "top" in margin else 0
            self.margin_bottom = margin["bottom"] if "buttom" in margin else 0
        else:
            self.margin_right = 0
            self.margin_bottom = 0
            self.margin_left = 0
            self.margin_top = 0
    
    

    ## binds
    def _bind_to_colum(self,column:Column) -> None:
        self.columns.append(column)
    

    def _bind_to_row(self,row:Row) -> None:
        self.rows.append(row)

    def _bind_to_parent(self,parent:Parent) -> None:
        self.parent = parent


    #get cumulative container dimensions (accomodates percentage calculation across mutliple rows/columns )
    
    def _get_cumulative_row_height(self) -> int:
        total = 0
        for row in self.rows:
            total += row.get_height()

        return total
    

    def _get_cumulative_column_width(self) -> int:
        total = 0
        for column in self.columns:
            total += column.get_width()
        
        return total


    
    ## get margins

    def get_margin_right(self):
        self._ensure_has_bound_parent()
        self._ensure_has_bound_column()
        return _get_absolute(self.margin_right,
                                    parent_dimension_value=self.parent.width,
                                    container_dimension_value=self._get_cumulative_column_width(),
                                )
    
    def get_margin_left(self):
        self._ensure_has_bound_parent()
        self._ensure_has_bound_column()
        return _get_absolute(self.margin_left,
                                    parent_dimension_value=self.parent.width,
                                    container_dimension_value=self._get_cumulative_column_width(),
                                )
    
    def get_margin_top(self):
        self._ensure_has_bound_parent()
        self._ensure_has_bound_row()
        return _get_absolute(self.margin_top,
                                    parent_dimension_value=self.parent.height,
                                    container_dimension_value=self._get_cumulative_row_height(),
                                )
    
    def get_margin_bottom(self):
        self._ensure_has_bound_parent()
        self._ensure_has_bound_row()
        return _get_absolute(self.margin_bottom,
                                    parent_dimension_value=self.parent.height,
                                    container_dimension_value=self._get_cumulative_row_height(),
                                )
    
    ## get dimensions

    def get_width(self):
        self._ensure_has_bound_parent()
        self._ensure_has_bound_column()
        return _get_absolute(self._width,
                                  parent_dimension_value=self.parent.width,
                                  container_dimension_value=self._get_cumulative_column_width(),
                                )
        
    def get_height(self):
        self._ensure_has_bound_parent()
        self._ensure_has_bound_row()
        return _get_absolute(self._height,
                                  parent_dimension_value=self.parent.height,
                                  container_dimension_value=self._get_cumulative_row_height(),
                                )
    
    ### WATERFALL HAS OCCURED ASSURANCE ###
    def _ensure_has_bound_column(self) -> None:
        if len(self.columns) <= 0:
            raise Exception("element must be bound to atleast one column")
        
    def _ensure_has_bound_row(self) -> None:
        if len(self.rows) <= 0:
            raise Exception("element must be bound to atleast one row")
        
    def _ensure_has_bound_parent(self) -> None:
        if type(self.parent) != Parent:
            raise Exception("waterfall process has not yet been carried out, element must be bound to a parent before its properties can be accessed.")

        

# pass all previously constructed 'Element' classes to 'Formatter' class in array.
# Then on resize call Formatter.resize_parent
# Then update each element, using Formatter.get_dimensions and Formatter.get_position



class Formatter:
    def __init__(self,
        parent_dimensions:tuple[int,int],
        rows:list[int | Percentage],
        columns:list[int | Percentage],
        elements:list[Element],             
    ):
        #define constructor arguments
        self.parent = Parent(*parent_dimensions)
        self.elements = elements

        # add check for coordinate collisions?

        #bind parent object to each element
        for element in self.elements:
            element._bind_to_parent(self.parent)

        
        #build rows (vertical positioning)
        self.rows : list[Row] = []
        for row_index,row_height in enumerate(rows):
            #filter elements to only those that reside in the target row
            child_elements = list(filter(lambda element: element._order[1].does_contain(row_index) ,self.elements))

            #build row
            row = Row(
                    height=row_height,
                    parent=self.parent,
                    #elements=child_elements,
                )

            #bind to each element
            for element in child_elements:
                element._bind_to_row(row)

            #build row class and append to self
            self.rows.append(row)


        #build colums (horizontal positioning)
        self.columns : list[Column] = []
        for column_index,column_width in enumerate(columns):
            #filter elements to only those that reside in the target column
            child_elements = list(filter(lambda element: element._order[0].does_contain(column_index) ,self.elements))

            #build column
            column = Column(
                    width=column_width,
                    parent=self.parent,
                    #elements=self.elements,
                )
            
            #bind to each element
            for element in child_elements:
                element._bind_to_colum(column)

            self.columns.append(column)

        

    
    ### USER EXPOSED ###
    
    #returns the position (<left>,<top>)
    def get_dimensions(self,elementID:str):
        target_elem = self._get_element_by_id(elementID)

        return self._get_element_dimensions(target_elem)
    
    def get_position(self,elementID:str):
        target_elem = self._get_element_by_id(elementID)

        return self._get_element_position(target_elem)

    #to be called when parent 'container' is resized.
    def resize_parent(self,width:int | None = None,height:int | None = None):
        hasChanged = False
        
        if width != None:
            self.parent.width = width
            hasChanged = True
        
        if height != None:
            self.parent.height = height
            hasChanged = True

        if hasChanged:
            self._update_on_resize()


    ### WATERFALL CHILD ELEMENT UPDATES ###

    #triggers waterfall effect, updating reliant children
    def _update_on_resize(self):
        pass


    
    ### POSITION / DIMENSION CALCULATION

    #gen dimenions (width,height)
    def _get_element_dimensions(self,element:Element) -> tuple[int,int]:
        width = element.get_width()
        height = element.get_height()

        return (width,height)


    
    #gen position (<left>,<top>)
    def _get_element_position(self,element:Element) -> tuple[int,int]:      
        column_start = element._order[0].start
        column_end = element._order[0].end
        
        row_start = element._order[1].start
        row_end = element._order[1].end

        ## TOP
        top = 0

        #get all previous rows
        for row in self.rows[:row_start]:
            top += row.get_height()
        

        if element.center:
            #calculate remaining space in row and divide space by two in order to center (should work even for overflow?)
            remaining_space_in_row_y = element._get_cumulative_row_height() - element.get_height()
            top += round(remaining_space_in_row_y / 2)
        else:
            ## CURRENTLY MARGIN TOP MAY ALLOW FOR ELEMENT TO SPILL OVER TO NEXT ROW
            top += element.get_margin_top()


        ## LEFT
        left = 0

        #all previous columns
        for column in self.columns[:column_start]:
            left += column.get_width()
        
        if element.center:
            #calculate remaining space in column and divide space by two in order to center
            remaining_space_in_column_x = element._get_cumulative_column_width() - element.get_width()
            left += round(remaining_space_in_column_x / 2)
        else:
            ## CURRENTLY MARGIN LEFT MAY ALLOW FOR ELEMENT TO SPILL OVER TO NEXT COLUMN
            left += element.get_margin_left()

        return (left,top)


    ### SEGMENTING ###

    #returns colum at specified index
    def _get_column(self,index:int) -> Column:
        if index >= len(self.columns) or index < 0:
            raise ValueError(f"column indexing error. Tried to fetch column index '{index}' , greatest index is '{len(self.columns) - 1 if len(self.columns) != 0 else 'NO COLUMNS'}'")

        return self.columns[index]
        
    
    #returns row at specified index
    def _get_row(self,index:int) -> Row:
        if index >= len(self.columns) or index < 0:
            raise ValueError(f"row indexing error. Tried to fetch row index '{index}' , greatest index is '{len(self.rows) - 1 if len(self.rows) != 0 else 'NO ROWS'}'")

        return self.rows[index]
    
    ### UTILITY ###
    def _get_element_by_id(self,id:str):
        target_element = next((element for element in self.elements if element.id == id), None)

        if target_element == None:
            raise Exception(f"an element with id: '{id}' does not exist.")
        
        return target_element







