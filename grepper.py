#----------------------------------------------------------------
# greppers AKS 5/2022
#----------------------------------------------------------------
from helpers import shellCMDLst

# grep filtering builder
def setupGrepFiltering(thisShCMDLst):
    
    # post first pick always exclusions
    # format is => thisShCMDLst.addExclAnyCMD('l|s')
    # thisShCMDLst.addExclAnyCMD('a|s|p|l|r|t|e')

    # post first pick temporary exclusions
    # format is => thisShCMDLst.addExclAnyCMD('l|s')
    # make sure to remove any position rules for these 
    # thisShCMDLst.addExclAnyCMD('c')

    # Low rank exclusions
    # add back in at some point
    # thisShCMDLst.addCMD('grep -vE \'b|f|k|w\'')
    #thisShCMDLst.addCMD('grep -vE \'v|x|z|q|j\'')

    # Midrank inclusions
    # thisShCMDLst.addCMD('grep -E \'u|c|y|h|d|p|g|m\'')

    # Exclude all midrank inclusions
    # thisShCMDLst.addCMD('grep -vE \'u|c|y|h|d|p|g|m\'')

    # Require a single random midrank inclusion
    # randMidrank = random.choice('ucyhdpgm')
    # thisShCMDLst.addCMD('grep -E \'' + randMidrank + '\'')

    # randMidrank = thisShCMDLst.addRandInclFrmCMD('ucyhdpgm')

    # # post first pick required non positions
    # # format is => thisShCMDLst.addExclPosCMD('l',p)
    # thisShCMDLst.addExclPosCMD('c',1)
    # thisShCMDLst.addExclPosCMD('o',4)
    # thisShCMDLst.addExclPosCMD('u',4)
    # thisShCMDLst.addExclPosCMD('m',2)

    # # post first pick required positions
    # # format is => thisShCMDLst.addInclPosCMD('l',p)
    # thisShCMDLst.addInclPosCMD('o',2)
    # thisShCMDLst.addInclPosCMD('u',3)
    # thisShCMDLst.addInclPosCMD('c',4)
    # thisShCMDLst.addInclPosCMD('h',5)
    # thisShCMDLst.addInclPosCMD('r',1)
    # thisShCMDLst.addInclPosCMD('s',5)

    # # post first pick Low rank inclusions
    # thisShCMDLst.addCMD('grep -E \'b|f|k|w\'')
    # thisShCMDLst.addCMD('grep -E \'v|x|z|q|j\'')


    pass # Required to avoid error when no statements are made in here.
