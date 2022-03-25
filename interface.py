"""
This file allow to connect this program with different type of data classification system.
You can edit it in order to allow the program to treat your data.

This file must contain at leat the following functions:
- connectData : allow to create objects with basic informations (id, path to data)
- getBlock, getTriplet, getShot, getCCD : allow to fill all the informations of the object using the basic information already available in these objects

All the data cannot be stored entirely in the RAM, so each object will load data when needed by using these get functions.
"""

##################################################
DATA_ROOT = "D:/Lab_Project/OSSOS/dbimages/Triplets"
DATA_LIST = "rsrc/All_triplets"
OUTPUT = "./results/"
##################################################

from block import Block
from triplet import Triplet
from shot import Shot
from ccd import CCD
import os
from astropy.io import fits
from numpy import *
from utils.term import *

#    _____      _      ____  _     _           _         _      _     _   
#   / ____|    | |    / __ \| |   (_)         | |       | |    (_)   | |  
#  | |  __  ___| |_  | |  | | |__  _  ___  ___| |_ ___  | |     _ ___| |_ 
#  | | |_ |/ _ \ __| | |  | | '_ \| |/ _ \/ __| __/ __| | |    | / __| __|
#  | |__| |  __/ |_  | |__| | |_) | |  __/ (__| |_\__ \ | |____| \__ \ |_ 
#   \_____|\___|\__|  \____/|_.__/| |\___|\___|\__|___/ |______|_|___/\__|
#                                _/ |                                     
#                               |__/                                     
                                       
def connectData(verbose=False):
    """This function allow to create instances of all objects that will be used by the program. These informations can be incomplete (only containing the name/id of each object)"""
    reading = ""

    # Reading All_triplets file
    with open(DATA_LIST) as file:
        if verbose == True: print("Scanning data...",end="\r")
        if verbose == 2: print("Scanning data...")
        for line in file:

            if line == "\n":
                continue

            #__________________________________________________
            # Reading headers (blocks and triplets)

            if "#" in line:
                if line[1:-5] not in Block.all:
                    currentBlock = Block(id=line[1:-5])
                    if verbose == 2: print(f"   Block {line[1:-5]}")
                else: currentBlock = Block.all[line[1:-5]] # Just to be sure to have the correct block

                currentTriplet = Triplet(id=line[1:-1], block=currentBlock)
                currentBlock.tripletList.append(currentTriplet)
                if verbose == 2: print(f"      Triplet {line[1:-1]}")
            
            # __________________________________________________
            # Reading all shots and associated CCDs

            else:
                currentShot = Shot(id=line[:-1].replace(" ",""),triplet=currentTriplet,block=currentBlock, dataPath=os.path.join(DATA_ROOT,str(int(line[:-1]))))
                for i in os.listdir(currentShot.dataPath):
                    path = os.path.join(currentShot.dataPath,i)
                    if os.path.isdir(path) and i[:3] == "ccd":
                        currentShot.ccdList.append(CCD(id=i[3:], dataPath=path, shot=currentShot, triplet=currentShot.triplet, block=currentShot.block))
                currentTriplet.shotList.append(currentShot)
                if verbose == 2: print(f"         Shot {line[:-1]} with {len(currentShot.ccdList)} CCDs")
    
    if verbose == True: print("Scanning data... Done")
    if verbose: print(f"-> Found {len(Block.all)} blocks, {len(Triplet.all)} triplets, {len(Shot.all)} shots and {len(CCD.all)} CCDs")

    

#    _____                      _      _          ____  _     _           _       
#   / ____|                    | |    | |        / __ \| |   (_)         | |      
#  | |     ___  _ __ ___  _ __ | | ___| |_ ___  | |  | | |__  _  ___  ___| |_ ___ 
#  | |    / _ \| '_ ` _ \| '_ \| |/ _ \ __/ _ \ | |  | | '_ \| |/ _ \/ __| __/ __|
#  | |___| (_) | | | | | | |_) | |  __/ ||  __/ | |__| | |_) | |  __/ (__| |_\__ \
#   \_____\___/|_| |_| |_| .__/|_|\___|\__\___|  \____/|_.__/| |\___|\___|\__|___/
#                        | |                                _/ |                  
#                        |_|                               |__/                                                                                                                                                                                                                        

def loadBlock(block):
    """This function use the informations contained in the block object to find the corresponding data and fill the missing parts"""
    return block

def loadTriplet(triplet):
    """This function use the informations contained in the triplet object to find the corresponding data and fill the missing parts"""
    return triplet

def loadShot(shot, verbose=False, prefix=""):
    """This function use the informations contained in the shot object to find the corresponding data and fill the missing parts"""
    hdul = fits.open(os.path.join(shot.dataPath,f"{shot.id}p.fits.fz"))

    if verbose: print(f"{prefix}Getting data for shot {shot.id}...")    
    for i in range(len(hdul)-1):
        if verbose: progressbar(i/(len(hdul)-2),prefix=f"{prefix}   ")
        for ccd in shot.ccdList:
            if i == int(ccd.id):
                ccd.data = hdul[i+1].data
    return shot

def loadCCD(ccd):
    """This function use the informations contained in the CCD object to find the corresponding data and fill the missing parts"""

    if ccd.data is None:
        hdul = fits.open(os.path.join(ccd.shot.dataPath,f"{ccd.shot.id}p.fits.fz"))
        for i in range(len(hdul)-1):
            if i == int(ccd.id):
                ccd.data = hdul[i].data

    ccd.fwhm = loadtxt(os.path.join(ccd.dataPath,f"{ccd.uid}.fwhm"))
    print(f"CCD{ccd.id} FWHM={ccd.fwhm}")

    apcor = loadtxt(os.path.join(ccd.dataPath,f"{ccd.uid}.apcor"))
    ccd.apcor_inner_radius = apcor[0]
    ccd.apcor_outer_radius = apcor[1]
    ccd.apcor_factor       = apcor[2]
    ccd.apcor_uncertainty  = apcor[3]
    
    return ccd

# if __name__ == "__main__":
#     connectData(verbose=False)

    
# #   __  __ _         _                   _       _        
# #  |  \/  (_)       (_)                 | |     | |       
# #  | \  / |_ ___ ___ _ _ __   __ _    __| | __ _| |_ __ _ 
# #  | |\/| | / __/ __| | '_ \ / _` |  / _` |/ _` | __/ _` |
# #  | |  | | \__ \__ \ | | | | (_| | | (_| | (_| | || (_| |
# #  |_|  |_|_|___/___/_|_| |_|\__, |  \__,_|\__,_|\__\__,_|
# #                             __/ |                       
# #                            |___/                       


#     with open("listFWHM","w+") as file, open("listAPCOR","w+") as file2, open("listZEROPOINT","w+") as file3:
#         count = 0
#         count2 = 0
#         count3 = 0
#         incomplet = []
#         for ccd in CCD.all.values():
#             if not os.path.isfile(os.path.join(ccd.dataPath,f"{ccd.shot.id}p{ccd.id}.fwhm")):
#                 if ccd not in incomplet:
#                     incomplet.append(ccd)
#                 file.write(ccd.uid + "\n")
#                 print(os.path.join(ccd.dataPath,f"{ccd.shot.id}p{ccd.id}.fwhm"))
#                 count += 1
#             if not os.path.isfile(os.path.join(ccd.dataPath,f"{ccd.shot.id}p{ccd.id}.apcor")):
#                 if ccd not in incomplet:
#                     incomplet.append(ccd)
#                 file2.write(ccd.uid + "\n")
#                 print(os.path.join(ccd.dataPath,f"{ccd.shot.id}p{ccd.id}.apcor"))
#                 count2 += 1
        
#             if not os.path.isfile(os.path.join(ccd.dataPath,f"{ccd.shot.id}p{ccd.id}.zeropoint.used")):
#                 if ccd not in incomplet:
#                     incomplet.append(ccd)
#                 file3.write(ccd.uid + "\n")
#                 print(os.path.join(ccd.dataPath,f"{ccd.shot.id}p{ccd.id}.zeropoint.used"))
#                 count3 += 1

#         for ccd in incomplet:
#             print(f"{ccd.uid}")
#             if not os.path.isdir(f"D:\Lab_Project/incomplet/{ccd.shot.id}/"): os.makedirs(f"D:\Lab_Project/incomplet/{ccd.shot.id}/")
#             os.rename(ccd.dataPath, f"D:\Lab_Project/incomplet/{ccd.shot.id}/ccd{ccd.id}")

#     print(count)
#     print(count2)
#     print(count3)