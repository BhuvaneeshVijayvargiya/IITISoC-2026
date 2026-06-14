import numpy as np
class UlDs:

    def __init__(self, id, length, width,height, max_weight):

        self.id=id
        self.length=length
        self.width=width
        self.height=height
        self.max_weight=max_weight
        self.z=np.zeros((length,width))
        self.currweight=0
        self.extr=[(0,0,0)]
        self.packaged=[]

    def volume(self):

        return (self.length*self.width*self.height)
    

    
