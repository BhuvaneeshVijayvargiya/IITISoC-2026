class Package:

    def __init__(self, id, length, width, height,weight, category, delay_cost):

        self.id=id
        self.length=length
        self.width=width
        self.height=height
        self.weight=weight
        self.category=category
        self.delay_cost=delay_cost

    def volume(self):

        return (self.length*self.width*self.height)

    def __str__(self):
        return f"{self.id}:({self.length},{self.width},{self.height})"