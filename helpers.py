# ----------------------------------------------------------------
# helpers AKS 5/2022
# ----------------------------------------------------------------
import sys
import os
import random

# Returns the wordle word list full pathname
# Exits program if not found
def getWordListPathName(localPathFileName):
    fullPathName = os.path.join(os.path.dirname(__file__), localPathFileName)
    if os.path.exists(fullPathName):
        print("Using " + localPathFileName)
        return fullPathName
    else:
        print(
            "Stopping here, wordle word list file "
            + localPathFileName
            + " was not found."
        )
        print("Expected here: " + fullPathName)
        print()
        sys.exit()


# Make and return the letter ranking dictionary
def makeLtrRankDictionary(localPathRankFile):
    fullPathName = os.path.join(os.path.dirname(__file__), localPathRankFile)
    ltr_rank_dict = {}  # ltr_rank_dict will be the rank dictionary
    if os.path.exists(fullPathName):
        print("Using " + localPathRankFile)
        with open(fullPathName) as f:
            for l in f:
                l = l.split(":")
                ltr_rank_dict[l[0]] = float(l[1])
    else:
        print(
            "Letter ranking file "
            + localPathRankFile
            + " not found. Switching to built in letter ranking."
        )
        ltr_rank_dict = {
            "e": 39.0,
            "a": 33.6,
            "r": 30.9,
            "o": 24.9,
            "t": 24.7,
            "i": 23.9,
            "l": 23.9,
            "s": 22.9,
            "n": 20.3,
            "u": 16.9,
            "c": 16.5,
            "y": 15.4,
            "h": 14.0,
            "d": 13.7,
            "p": 12.8,
            "g": 11.1,
            "m": 11.0,
            "b": 9.9,
            "f": 7.6,
            "k": 7.5,
            "w": 7.1,
            "v": 5.5,
            "x": 1.4,
            "z": 1.3,
            "q": 1.1,
            "j": 1.0,
        }
    return ltr_rank_dict


# Returns a word's letter frequency ranking
def wrd_rank(wrd, ltr_rank_dict):
    r = 0
    for x in wrd:
        r = r + ltr_rank_dict[x]
    return r


# Returns true if word has duplicate letters
def wrdHasDuplicates(wrd):
    ltrD = {}
    for l in wrd:
        ltrD[l] = l
    return len(ltrD) < len(wrd)


# List out the ranked word list
def showThisWordList(theWordList):
    print("Word  : Rank")
    for key, value in theWordList.items():
        msg = key + " : " + str(value)
        print(msg)


# Ranking and filtering the words into a dictionary
def makeRankedFilteredResultDictionary(wrds, ltr_rank_dict, noDups):
    wrds_dict = {}
    for w in wrds:
        if len(w) == 5:
            if noDups == True:
                if wrdHasDuplicates(w) != True:
                    wrds_dict[w] = "{:05.1f}".format(wrd_rank(w, ltr_rank_dict))
            else:
                wrds_dict[w] = "{:05.1f}".format(wrd_rank(w, ltr_rank_dict))

    # sorting the ranked word list into a dictionary
    # return dict(sorted(wrds_dict.items(), reverse=True,key= lambda x:x[1]))
    return dict(sorted(wrds_dict.items(), reverse=False, key=lambda x: x[1]))


# Returns the number of matching words
def getRawWordCount(thisShCMDLst):
    shCMD_cnt = thisShCMDLst.fullCMD() + " | wc -l"
    return os.popen(shCMD_cnt).read().strip()


# Returns the results words list
def getResultsWordList(thisShCMDLst):
    result = os.popen(thisShCMDLst.fullCMD()).read()
    return result.split("\n")


# Clears the console
def clearScrn():
    os.system("cls" if os.name == "nt" else "clear")


# A class used for holding list stack of the shell commands
# It has functions that build greps related to filtering wordle
# letter conditions.
class shellCMDLst:
    shCMDlist = list()

    def __init__(self, listFileName):
        self.shCMDlist.append("cat " + listFileName)

    def addCMD(self, s):
        self.shCMDlist.append(s)

    # word includes random letter from list lst
    # returns the random pick letter
    def addRandInclFrmCMD(self, lst):
        randFrmL = random.choice(lst)
        self.shCMDlist.append("grep -E '" + randFrmL + "'")
        return randFrmL

    # word requires this letter l
    def addRequireCMD(self, l):
        self.shCMDlist.append("grep -E '" + l + "'")

    # word excludes this letter l
    def addExclAnyCMD(self, l):
        self.shCMDlist.append("grep -vE '" + l + "'")

    # word excludes letter from position number
    def addExclPosCMD(self, l, p):
        # can have letter
        self.shCMDlist.append("grep -E '" + l + "'")
        # but not in this position
        if p == 1:
            self.shCMDlist.append("grep -vE '" + l + "....'")
        elif p == 2:
            self.shCMDlist.append("grep -vE '." + l + "...'")
        elif p == 3:
            self.shCMDlist.append("grep -vE '.." + l + "..'")
        elif p == 4:
            self.shCMDlist.append("grep -vE '..." + l + ".'")
        elif p == 5:
            self.shCMDlist.append("grep -vE '...." + l + "'")

    # word includes letter in position number
    def addInclPosCMD(self, l, p):
        # Have letter in this position
        if p == 1:
            self.shCMDlist.append("grep -E '" + l + "....'")
        elif p == 2:
            self.shCMDlist.append("grep -E '." + l + "...'")
        elif p == 3:
            self.shCMDlist.append("grep -E '.." + l + "..'")
        elif p == 4:
            self.shCMDlist.append("grep -E '..." + l + ".'")
        elif p == 5:
            self.shCMDlist.append("grep -E '...." + l + "'")

    def fullCMD(self):
        pc = " | "
        thisCMD = ""
        for w in self.shCMDlist[:-1]:
            thisCMD = thisCMD + w + pc
        thisCMD = thisCMD + self.shCMDlist[-1]
        return thisCMD
