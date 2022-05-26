# ----------------------------------------------------------------
# greppers AKS 5/2022
# ----------------------------------------------------------------
from helpers import ShellCmdList


# grep filtering builder
def setup_grep_filtering(this_sh_cmd_lst):
    # post first pick always exclusions
    # format is => this_sh_cmd_lst.add_excl_any_cmd('l|s')
    this_sh_cmd_lst.add_excl_any_cmd('l|h|c|o|r|n')

    # post first pick temporary exclusions
    # format is => this_sh_cmd_lst.add_excl_any_cmd('l|s')
    # make sure to remove any position rules for these 
    # this_sh_cmd_lst.add_excl_any_cmd('a|t|e')

    # Low rank exclusions
    # add back in at some point
    # this_sh_cmd_lst.add_cmd('grep -vE \'b|f|k|w\'')
    # this_sh_cmd_lst.add_cmd('grep -vE \'v|x|z|q|j\'')

    # Midrank inclusions
    # this_sh_cmd_lst.add_cmd('grep -E \'u|c|y|h|d|p|g|m\'')

    # Exclude all midrank inclusions
    # this_sh_cmd_lst.add_cmd('grep -vE \'u|c|y|h|d|p|g|m\'')

    # Require a single random midrank inclusion
    # randMidrank = random.choice('ucyhdpgm')
    # this_sh_cmd_lst.add_cmd('grep -E \'' + randMidrank + '\'')

    # randMidrank = this_sh_cmd_lst.add_rand_incl_frm_cmd('ucyhdpgm')

    # # post first pick required non positions
    # # format is => this_sh_cmd_lst.add_excl_pos_cmd('l',p)
    this_sh_cmd_lst.add_excl_pos_cmd('s',1)
    this_sh_cmd_lst.add_excl_pos_cmd('a',2)
    this_sh_cmd_lst.add_excl_pos_cmd('t',3)
    this_sh_cmd_lst.add_excl_pos_cmd('e',5)

    # # post first pick required positions
    # # format is => this_sh_cmd_lst.add_incl_pos_cmd('l',p)
    # this_sh_cmd_lst.add_incl_pos_cmd('t',5)
    # this_sh_cmd_lst.add_incl_pos_cmd('u',3)
    # this_sh_cmd_lst.add_incl_pos_cmd('c',4)
    # this_sh_cmd_lst.add_incl_pos_cmd('h',5)
    # this_sh_cmd_lst.add_incl_pos_cmd('r',1)
    # this_sh_cmd_lst.add_incl_pos_cmd('s',5)

    # # post first pick Low rank inclusions
    # this_sh_cmd_lst.add_cmd('grep -E \'b|f|k|w\'')
    # this_sh_cmd_lst.add_cmd('grep -E \'v|x|z|q|j\'')

    pass  # Required to avoid error when no statements are made in here.
