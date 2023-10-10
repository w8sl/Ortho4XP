import re
import os

def replace_all(contents, dic):
    for i, j in dic.items():
        contents = contents.replace(i, j)
    return contents

f_dic = {"nvcompress.app":"nvcompress","moulinette.app":"moulinette","triangle.app":"triangle","Triangle4XP.app":"Triangle4XP","DSFTool.app":"DSFTool"}

def name_fix(file_py):

   with open(file_py,'r') as f:
       contents=f.read()
       contents=replace_all(contents,f_dic)
       contents=re.sub(r'PROD\s(?=[1-9])',r'PROD',contents)
   with open(file_py,'w') as w:
       w.write(contents)

name_fix("./src/O4_Imagery_Utils.py")
name_fix("./src/O4_Mesh_Utils.py")
name_fix("./src/O4_Overlay_Utils.py")

os.rename("./Utils/moulinette","./Utils/moulinetteLin")
os.rename("./Utils/moulinette.app","./Utils/moulinette")
os.rename("./Utils/triangle","./Utils/triangleLin")
os.rename("./Utils/triangle.app","./Utils/triangle")
os.rename("./Utils/triangle4XP","./Utils/triangle4XPLin")
os.rename("./Utils/triangle4XP.app","./Utils/triangle4XP")
os.rename("./Utils/DSFTool","./Utils/DSFToolLin")
os.rename("./Utils/DSFTool.app","./Utils/DSFTool")
os.rename("./Utils/nvcompress/nvcompress.app","./Utils/nvcompress/nvcompress")
