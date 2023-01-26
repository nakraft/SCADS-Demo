class sorter(): 

    def __init__(self, arr): 
        self.arr = arr

    def find_position(self, new_ele): 
        s = 0
        e = len(self.arr)
        insert_index = None

        while e - s > 1 and insert_index == None: 
            split = int((e + s) / 2)
            if new_ele < self.arr[split]: 
                e = split
            elif new_ele > self.arr[split]: 
                s = split
            else: 
                insert_index = split 

        if insert_index == None: 
            if self.arr[s] > new_ele: 
                insert_index = s
            elif self.arr[e - 1] < new_ele: 
                insert_index = e
            else: 
                insert_index = e-1

        return insert_index