from itertools import permutations
class Package:

    def __init__(self, id, length, width, height,weight, category, delay_cost):

        self.id=id
        self.length=length
        self.width=width
        self.height=height
        self.weight=weight
        self.category=category
        if(self.category=="Economy"):
            self.delay_cost=delay_cost
        else:
            self.delay_cost=delay_cost
            self.delay_cost=None
        self.uld=None
        self.pos=None
        self.ori=None

    def volume(self):

        return (self.length*self.width*self.height)

    def __str__(self):
        return f"{self.id}:({self.length},{self.width},{self.height})"
    
    def orie(self):
        dims=(self.length,self.width,self.height)
        return list(set(permutations(dims,3)))

#this is the Package class with id,dimension,weight,category,delay cost attributes.
#uld,pos,ori will store the final uld,position coordinates(left bottom front corner) and orientation of the package when packed.
#volume function returns volume of package
#__str__ is a dunder method that returns a string of id,length,width,height of package separated by commas(will be used in output)
#orie function generated all the 6 possible orientations.
