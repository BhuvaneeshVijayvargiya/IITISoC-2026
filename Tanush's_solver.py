"""Here the code for finding the space for the next space for the package will come"""
from input import pack,ulds
from pct import PCT

packages_list=pack()
ulds_list=ulds()
def place(package,x,y,z,uld,ori,ep):
    uld.currweight+=package.weight
    uld.extr.remove(ep)
    uld.packaged.append(package)
    l,w,h=ori
    se=set(uld.extr)
    se.add((x+l,y,z))
    se.add((x,y+w,z))
    se.add((x,y,z+h))
    uld.extr=list(se)
    for i in range(x,x+l):
        for j in range(y,y+w):
            uld.z[i][j]=z+h
    package.uld=uld
    package.pos=(x,y,z)
    package.ori=ori
def check_coll(x, y, z, l, w, h, packaged):
    pass  #need to be implemented...


def generate_pct(package, ulds_list):
    leaves=[]

    for uld in ulds_list:
        if uld.currweight+package.weight>uld.max_weight:
            continue

        for ep in uld.extr:
            x,y,z=ep

            for ori in package.orie():
                l,w,h=ori

                if x+l<=uld.length and y+w<=uld.width and z+h<=uld.height:
                    coll_free = True
                    for packaged in uld.packaged:
                        if check_coll(x,y,z,l,w,h,packaged):
                            coll_free=False
                            break

                    if coll_free:
                        node=PCT(package, uld, ep, ori)
                        leaves.append(node)

    return leaves
#place method is for placing package in the end
#check_coll is to check for collision with already packed packages
#generate_pct generated a depth-1 PCT.



    


    
