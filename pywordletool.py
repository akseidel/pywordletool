
import grepper
import helpers

helpers.clear_scrn()

# variables
ranked_wrds_dict ={} # dictionary of ranked words resulting from grep filtering

# wrdListFileName = helpers.get_word_list_path_name('worddata/wo_nyt_wordlist.txt')
wrdListFileName = helpers.get_word_list_path_name('worddata/nyt_wordlist.txt')

rankFile = 'worddata/letter_ranks.txt' # rankFile is the letter ranking textfile
ltr_rank_dict = helpers.make_ltr_rank_dictionary(rankFile)  # ltr_rank_dict is the rank dictionary

# Initialize and setup the ShellCmdList class instance that is used to hold the
# grep filtering command stack. Guessing because it is a class instance is why it
# can be passed around as a global variable where it gets modified along the way.
this_sh_cmd_lst = helpers.ShellCmdList(wrdListFileName)
grepper.setup_grep_filtering(this_sh_cmd_lst)  # fills the stack with grep assignments

# Get word count
raw_cnt = helpers.get_raw_word_count(this_sh_cmd_lst)

# Get results words list
wrds = helpers.get_results_word_list(this_sh_cmd_lst)

# Ranking and filtering the words into a dictionary
# Set no_dups to prevent letters from occurring more than once
# First pick should not use duplicates, later picks should consider them.
no_dups = False
# no_dups = True
ranked_wrds_dict = helpers.make_ranked_filtered_result_dictionary(wrds, ltr_rank_dict, no_dups)

helpers.show_this_word_list(ranked_wrds_dict)
print()
print('Showing word list of ' + str(len(ranked_wrds_dict)) + " from raw list of " + raw_cnt + " having duplicates.")
print()

print(this_sh_cmd_lst.full_cmd())
print()
