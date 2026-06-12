import pandas as pd
from packages import Package
from ULDs import UlDs
def pack():
    df=pd.read_csv(r"")
    packlist=[]
    for ind,row in df.iterrows():
        p=Package(row["Package_ID"],row["Length"],row["Width"],row["Height"],row["Weight"],row["Category"],row["Delay Cost"])
        packlist.append(p)
    return packlist
def ulds():
    df=pd.read_csv(r"")
    uldlist=[]
    for ind,row in df.iterrows():
        u=UlDs(row["ULD_ID"],row["Length"],row["Width"],row["Height"],row["MaxWeight"])
        uldlist.append(u)
    return uldlist
