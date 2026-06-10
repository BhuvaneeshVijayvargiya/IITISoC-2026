class UlDs:

    def __init__(self, id, length, width,height, max_weight):

        self.id=id
        self.length=length
        self.width=width
        self.height=height
        self.max_weight=max_weight

    def volume(self):

        return (self.length*self.width*self.height)