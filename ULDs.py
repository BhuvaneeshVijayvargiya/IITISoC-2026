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
    

    #this is the uld class file with id,dimension,max weight variables.
    """z is the heightmap variable,we also have variables to track the curr weight packed in the uld(currweight),
    the respective extreme points generated(extr),the list of packages in the uld(packaged)."""
    #volume function returns the volume of the uld.
