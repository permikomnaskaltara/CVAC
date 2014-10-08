
from __future__ import print_function

'''
    Misc utility functions. 
    Some for handling directories and files into labelables
'''

import os
import cvac
import easy


def getImageExtensions():
    return ["bmp","dib","jpeg","jpg","jpe","jp2", \
            "png","pbm","pgm","ppm","sr","ras", \
            "tiff","tif","gif","giff","emf","pct", \
            "pcx","pic","pix","vga","wmf"];

def getVideoExtensions():
    return ["mpg","mpeg","avi","wmv","wmp","wm", \
            "asf","mpe","m1v","m2v","mpv2","mp2v", \
            "dat","ts","tp","tpr","trp","vob","ifo", \
            "ogm","ogv","mp4","m4v","m4p","m4b","3gp", \
            "3gpp","3g2","3gp2","mkv","rm","ram", \
            "rmvb","rpm","flv","swf","mov","qt", \
            "amr","nsv","dpg","m2ts","m2t","mts", \
            "k3g","skm","evo","nsr","amv","divx","webm"];

'''
Return the directory name with the CVAC_DataDir stripped off
if its appended to the front of the directory.
'''
def stripCVAC_DataDir(mydir):
    # make both CVAC_DataDir and mydir absolute and then strip off
    absCVAC = os.path.abspath(easy.CVAC_DataDir)
    absdir = os.path.abspath(mydir)
    if absdir.startswith(absCVAC):
        absdir = absdir[len(absCVAC + '/'):]
        return absdir
    return mydir   # Noth9ing to strip so return original

'''
Return the FilePath with the CVAC_DataDir stripped off
if its appended to the front of the directory.
'''
def stripCVAC_DataDir_from_FilePath(mypath):
    mydir = mypath.directory.relativePath + '/' + mypath.filename;
    resdir = stripCVAC_DataDir(mydir)
    if resdir != mydir:
        # We got stripped so now we have a relative directory without data
        resdirOnly = resdir.rsplit('/',2)
        mypath.directory.relativePath = resdirOnly[0]
    return mypath

'''
  Add a labelable to the set for the given file.  Use the last directory as
  the label name ane previous directories as labelproperties
'''
def addFileToLabelableSet(lset, ldir, lfile, video=True, image=True):
    isVideo = False
    isImage = False
    if '.' not in lfile:
        return  # No extension so don't add it
    #see if we have a video or image file if not just skip it
    name, ext = lfile.rsplit('.',1)
    extLower = ext.lower()
    if extLower in getVideoExtensions():
        isVideo = True
    elif extLower in getImageExtensions():
        isImage = True
    else:
        return
    if isVideo and video == False:
        return
    if isImage and image == False:
        return
    # strip off cvac data dir
    ldir = stripCVAC_DataDir(ldir)
    
    props = {}
    # last directory is the label name
    idx = ldir.rfind("/")
    lastIdx = len(ldir)
    labelName = None
    if idx == -1:
        # at top level directory use directory name as labelName
        labelName = ldir
        lastIdx = 0
    while idx != -1:
        nextdir = ldir[idx+1:lastIdx]
        if labelName == None:
            labelName = nextdir
        else:
            props[nextdir] = ""
        lastIdx = idx
        if idx > 0:
            idx = ldir.rfind("/", 0, idx-1)
        else:
            break
    # add final property
    if lastIdx > 0:
        nextdir = ldir[0:lastIdx]
        props[nextdir] = ""
    dirpath = cvac.DirectoryPath(ldir)
    fpath = cvac.FilePath(dirpath,lfile)
    sub = cvac.Substrate(isImage, isVideo, fpath, 0, 0)
    lab = cvac.Label(True, labelName, props, cvac.Semantics(""))
    lset.append(cvac.Labelable(0.0, lab, sub))
    
'''
    Search a directory optionally recursively adding the correct 
    file types to a labelable set
'''
def searchDir(lset, ldir, recursive=True, video=True, image=True):
    flist = os.listdir(ldir)
    for f in flist:
        if os.path.isdir(ldir + '/' + f) and recursive:
            searchDir(lset, ldir + '/' + f)
        else:
            addFileToLabelableSet(lset, ldir, f, video, image)
