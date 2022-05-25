import os
from grepper import setupGrepFiltering
from helpers import clearScrn, shellCMDLst, makeLtrRankDictionary, showThisWordList, makeRankedFilteredResultDictionary
from helpers import getWordListPathName, getRawWordCount, getResultsWordList

clearScrn()

# variables
ranked_wrds_dict ={} # dictionary of ranked words resulting from grep filtering

wrdListFileName = getWordListPathName('worddata/wo_nyt_wordlist.txt')
# wrdListFileName = getWordListPathName('worddata/nyt_wordlist.txt')

rankFile = 'worddata/letter_ranks.txt' # rankFile is the letter ranking textfile
ltr_rank_dict = makeLtrRankDictionary(rankFile)  # ltr_rank_dict is the rank dictionary

# Initialize and setup the shellCMDLst class instance that is used to hold the
# grep filtering command stack. Guessing because it is a class instance is why it
# can be passed around as a global variable where it gets modified along the way.
thisShCMDLst = shellCMDLst(wrdListFileName)
setupGrepFiltering(thisShCMDLst) # fills the stack with grep assignments

# Get word count
raw_cnt = getRawWordCount(thisShCMDLst)

# Get results words list
wrds = getResultsWordList(thisShCMDLst)

# Ranking and filtering the words into a dictionary
# Set noDups to prevent letters from occurring more than once
# noDups = False
noDups = True 
ranked_wrds_dict = makeRankedFilteredResultDictionary(wrds,ltr_rank_dict,noDups)

showThisWordList(ranked_wrds_dict)
print()
print('Showing word list of ' + str(len(ranked_wrds_dict)) + " from raw list of " + raw_cnt + " having duplicates.")
print()

print(thisShCMDLst.fullCMD())
print()