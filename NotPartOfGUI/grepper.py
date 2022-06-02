# ----------------------------------------------------------------
# greppers AKS 5/2022
# ----------------------------------------------------------------


# grep filtering builder
def setup_grep_filtering(this_sh_cmd_lst):

    # post first pick always exclusions
    # format is => tool_command_list.add_excl_any_cmd('ltr|s')
    # tool_command_list.add_excl_any_cmd('a|s|b|i|e')

    # post first pick temporary exclusions
    # format is => tool_command_list.add_excl_any_cmd('ltr|s')
    # make sure to remove any position rules for these 
    # tool_command_list.add_excl_any_cmd('e|t|r')

    # Low rank exclusions
    # add back in at some point
    # this_sh_cmd_lst.add_cmd('grep -vE \'b|f|k|w\'')
    # this_sh_cmd_lst.add_cmd('grep -vE \'v|x|z|q|j\'')

    # Midrank inclusions
    # tool_command_list.add_cmd('grep -E \'u|c|y|h|d|p|g|m\'')

    # Exclude all midrank inclusions
    # tool_command_list.add_cmd('grep -vE \'u|c|y|h|d|p|g|m\'')

    # Require a single random midrank inclusion
    # randMidrank = random.choice('ucyhdpgm')
    # tool_command_list.add_cmd('grep -E \'' + randMidrank + '\'')

    # randMidrank = tool_command_list.add_rand_incl_frm_cmd('ucyhdpgm')

    # # post first pick required non positions
    # # format is => tool_command_list.add_excl_pos_cmd('ltr',p)
    # tool_command_list.add_excl_pos_cmd('r',4)
    # tool_command_list.add_excl_pos_cmd('e',2)
    # tool_command_list.add_excl_pos_cmd('t',1)
    # tool_command_list.add_excl_pos_cmd('c',4)
    # tool_command_list.add_excl_pos_cmd('e',4)
    # tool_command_list.add_excl_pos_cmd('p',5)

    # # post first pick required positions
    # # format is => tool_command_list.add_incl_pos_cmd('ltr',p)
    # tool_command_list.add_incl_pos_cmd('c',1)
    # tool_command_list.add_incl_pos_cmd('r',2)
    # tool_command_list.add_incl_pos_cmd('c',3)
    # tool_command_list.add_incl_pos_cmd('e',4)
    # tool_command_list.add_incl_pos_cmd('p',5)

    # # post first pick Low rank inclusions
    # tool_command_list.add_cmd('grep -E \'b|f|k|w\'')
    # tool_command_list.add_cmd('grep -E \'v|x|z|q|j\'')

    pass  # Required to avoid error when no statements are made in here.
