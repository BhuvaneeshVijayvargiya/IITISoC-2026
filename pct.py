#this defines the pct class
class PCT:

    def __init__(self, package, uld, ep, ori,support,direction=(1, 1, 1), score=0):
        self.package = package
        self.uld = uld
        self.ep = ep
        self.ori = ori
        self.direction = direction
        self.score = score

        self.x, self.y, self.z = ep
        self.l, self.w, self.h = ori

        
        self.cx = self.x + self.l / 2
        self.cy = self.y + self.w / 2
        self.cz = self.z + self.h / 2
        self.support=support

