# Genetic Ranking

* Genetic Rank is a method that was part of the pywt.py at one time. It might have been called “genetic ranking” or “smartest pick”. The idea is given a list, the best pick is a member of the largest subset of words that are most in common with each others’ letters. Any of those words could either rule out the most number of words or rule in the highest number of discovered letters. For example for the word GLIDE, its score or genetic rank is the sum of all the times its letters, G, L, I, D, E show up once in all the words in the given list plus an adjustment equal to the number of times a letter in the subject word (GLIDE) repeats within the subject word.

* Genetic ranking does work rather well. The method was dropped from pywt.py after discovering the groups analysis method was better.

* One can still employ genetic ranking by using one of the spreadsheets GENETICWORD.ods (LibreOffice) or GENETICWORD.xlsm (Excel translation of the LibreOffice version). These spreadsheets were created to test the ranking method before it was implemented in pywt.py.
