class PCT:
    def __init__(self, package, uld, ep, ori, score=0):
        self.package=package
        self.uld=uld
        self.ep=ep
        self.ori=ori
        self.score=score

        self.x,self.y,self.z=ep
        self.l,self.w,self.h=ori
#each node has following:package(the package we looking at),uld(uld it will be stored in),ep(extreme points(for next node)),ori(orientation of package),score(will be used later)
