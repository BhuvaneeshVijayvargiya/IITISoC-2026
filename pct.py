class PCT:
    def __init__(self, package, uld, ep, ori, score=0):
        self.package=package
        self.uld=uld
        self.ep=ep
        self.ori=ori
        self.score=score

        self.x,self.y,self.z=ep
        self.l,self.w,self.h=ori
