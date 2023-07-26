from typing import TypedDict

#return type within formatter
class ElementInfo(TypedDict):
    dimensions:tuple[int,int]
    position:tuple[int,int]



#handles relative sizing
class Percentage:
    def __init__(self,
        percentage:float,
        min:int | None = None,
        max:int | None = None,
    ):
        self.percentage = percentage
        self.min = min
        self.max = max

        
    def get(self,anchor_value:int):
        organic_val = self.percentage * anchor_value

        if self.max != None and anchor_value > self.max:
            return self.max
        elif self.min != None and anchor_value < self.min:
            return self.min
        else:
            return organic_val




#represents an entry to the Formatter class
class Element:
    def __init__(self,
        id:str,
        order:tuple[int,int], #where the element should lie on the x-axis & y-axis with respect to other elements
        width:Percentage | int, 
        height:Percentage | int,
        margin:dict[str,Percentage | int] | None = None, #right,left,top,bottom
    ):
        self.id = id
        self.order = order
        self.width = width
        self.height = height
        self.parent_dimensions = None

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
    
    
    #update parent dimensions used for relative calculations when using Percentage values
    def set_parent_dimensions(self,xy:tuple[int,int]):
        self.parent_dimensions = xy

    
    #get margins

    def get_margin_right(self):
        return self._get_absolute(self.margin_right,self.parent_dimensions[0])
    
    def get_margin_left(self):
        return self._get_absolute(self.margin_left,self.parent_dimensions[0])
    
    def get_margin_top(self):
        return self._get_absolute(self.margin_top,self.parent_dimensions[1])
    
    def get_margin_bottom(self):
        return self._get_absolute(self.margin_bottom,self.parent_dimensions[1])


    #get orders
    
    def get_order_x(self) -> int:
        return self.order[0]
    
    def get_order_y(self) -> int:
        return self.order[1]
    

    # get dimensions

    def get_width(self):
        return self._get_absolute(self.width,self.parent_dimensions[0])
        
    def get_height(self):
        return self._get_absolute(self.height,self.parent_dimensions[1])
    

    #choose correct value, allow for usage of absolute values aswell as implict percentage values
    def _get_absolute(self,v:Percentage | int,anchor_val:int) -> int:
        if type(v) == int:
            return v
        elif type(v) == Percentage:
            return int(v.get(anchor_val))
        



# pass all previously constructed 'Element' classes to 'Formatter' class in array.
# Then on resize call Formatter.update_parent_dimensions
# Then update each element, using the Formatter.get_element_info method

class Formatter:
    def __init__(self,
        parent_dimensions:tuple[int,int],
        elements:list[Element],             
    ):
        #define constructor arguments
        self.parent_dimensions = parent_dimensions
        self.elements = elements

        #set parent dimensions for each element
        self.update_parent_dimensions(parent_dimensions)

        #retrieve order ranges (it is assumed order begins at 0, therefore no need for min)
        self.order_max_x = 0
        self.order_max_y = 0
        for element in elements:
            self.order_max_x = element.order[0] if element.order[0] > self.order_max_x else self.order_max_x
            self.order_max_y = element.order[1] if element.order[1] > self.order_max_y else self.order_max_y

        #check for collisions in positions
        for y in range(self.order_max_y + 1):
            existing_x = []
            for element in self._get_elements_by_y(y):
                x = element.order[0]
                if x in existing_x:
                    raise ValueError(f"coordinate collision at [{x},{y}]")
                existing_x.append(x)

        for x in range(self.order_max_x + 1):
            existing_y = []
            for element in self._get_elements_by_x(x):
                y = element.order[1]
                if y in existing_y:
                    raise ValueError(f"coordinate collision at [{x},{y}]")
                existing_x.append(y)


        #ordered rows (each row has same y)
        self.rows : list[Element] = []
        for y in range(self.order_max_y + 1):
            elements = self._get_elements_by_y(y)    
            elements.sort(key=lambda element: element.order[0])
            self.rows.append(elements)

        #ordered colums (each row has same x)
        self.colums : list[Element] = []
        for x in range(self.order_max_x + 1):
            elements = self._get_elements_by_x(x)
            elements.sort(key=lambda element: element.order[1])
            self.colums.append(elements)

    
    ### USER EXPOSED ###
    
    #returns the position (<left>,<top>)
    def get_element_info(self,elementID) -> ElementInfo:
        target_element = next((element for element in self.elements if element.id == elementID), None)

        if target_element == None:
            raise Exception(f"an element with id: '{elementID}' does not exist.")

        position = self._gen_position_from_order(target_element.order)
        width = target_element.get_width()
        height = target_element.get_height()

        return {
            "position":position,
            "dimensions":(width,height)
        }

    def update_parent_dimensions(self,xy:tuple[int,int]):
        for element in self.elements:
            element.set_parent_dimensions(xy)


    ### SEGMENTING ###

    #returns the elements within the colum specified by index 'x'
    def _get_elements_by_x(self,index:int) -> list[Element]:
        if index > self.order_max_x:
            raise ValueError(f"cannot fetch elements outside range of order. tried fetching index '{index}', order max is {self.order_max_x}")

        return list(filter(lambda element: element.order[0] == index ,self.elements))
    
    #returns the elements within the row specificied by index 'y'
    def _get_elements_by_y(self,index:int) -> list[Element]:
        if index > self.order_max_y:
            raise ValueError(f"cannot fetch elements outside range of order. tried fetching index '{index}', order max is {self.order_max_y}")

        return list(filter(lambda element: element.order[1] == index ,self.elements))


    def _get_element_by_order(self,order:tuple[int,int]) -> Element:
        target_colum = self.colums[order[0]]

        target_element = next((element for element in target_colum if element.order[1] == order[1]), None)


        return target_element


    ### POSITION CALCULATION ###

    #gen position (<left>,<top>)
    def _gen_position_from_order(self,order:tuple[int,int]) -> tuple[int,int]:
        left = 0
        top = 0

        target_element = self._get_element_by_order(order)


        #calculate left position based on previous elements in colum
        previous_elements_in_colum : list[Element] = self.colums[order[0]][:order[1]]

        for element in previous_elements_in_colum:
            left += element.get_width()
            left += element.get_margin_right()
            left += element.get_margin_left()
        
        left += target_element.get_margin_left()
        
        #calculate top position based on previous elements in row
        previous_elements_in_row : list[Element] = self.rows[order[1]][:order[0]]

        for element in previous_elements_in_row:
            top += element.get_height()
            top += element.get_margin_top()
            top += element.get_margin_bottom()
        
        top += target_element.get_margin_top()

        return (int(left),int(top))







