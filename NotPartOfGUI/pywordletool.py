# ----------------------------------------------------------------
# pywordletool AKS 5/2022
# ----------------------------------------------------------------

# temporary path environment to find helpers.py
import sys
import helpers
import grepper

sys.path.append('/Users/aks/Documents/GitHub/pywordletool/')

data_path = './worddata/'  # path from here to data folder

# Set allow_dups to prevent letters from occurring more than once
# First pick should not use duplicates, later picks should consider them.
# allow_dups = False
no_dups = True

rank_mode = 1

helpers.clear_scrn()  # clears terminal

# initialize the wordletool
wordletool = helpers.ToolResults(data_path, 'wo_nyt_wordlist.txt', 'letter_ranks.txt', no_dups, rank_mode)

# # variables
# ranked_wrds_dict = {}  # dictionary of ranked words resulting from grep filtering
#
# wrdListFileName = helpers.get_word_list_path_name(data_path + 'wo_nyt_wordlist.txt')
# # wrdListFileName = helpers.get_word_list_path_name(data_path + 'nyt_wordlist.txt')

# rankFile = data_path + 'letter_ranks.txt'  # rankFile is the letter ranking textfile
# ltr_rank_dict = helpers.make_ltr_rank_dictionary(rankFile)  # ltr_rank_dict is the rank dictionary

# Initialize and set up the ShellCmdList class instance that is used to hold the
# grep filtering command stack. Guessing because it is a class instance is why it
# can be passed around as a global variable where it gets modified along the way.
# tool_command_list = helpers.ShellCmdList(wrdListFileName)
# tool_command_list = wordletool.tool_command_list
grepper.setup_grep_filtering(wordletool.tool_command_list)  # fills the stack with grep assignments
#
# # Get word count
# raw_cnt = helpers.get_raw_word_count(tool_command_list)
#
# # Get results words list
# wrds = helpers.get_results_word_list(tool_command_list)
#
# # Ranking and filtering the words into a dictionary
# ranked_wrds_dict = helpers.make_ranked_filtered_result_dictionary(wrds, ltr_rank_dict, allow_dups)

# helpers.print_this_word_list(ranked_wrds_dict, 6)

wordletool.print_col_format_ranked_list(6)

print(wordletool.get_status())

print(wordletool.get_full_cmd())

# print()
# print('Showing word list of ' + str(len(ranked_wrds_dict)) + " from raw list of " + raw_cnt + " having duplicates.")
# print()

# print(tool_command_list.full_cmd())
# print()
