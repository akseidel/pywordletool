#!/bin/bash
# akseidel 12/06/22
# https://github.com/akseidel/
# A script automating the steps to run groupdrilling.py
#
# To use from the residing folder:
# First mark as executable with "chmod +x start-groupdrilling.command".
# In OSX run by entering "./start-groupdrilling.command".
# In Linux run by entering "./start-groupdrilling.command"
#
# Script arguments:
# none

# globals
s=0 # proceed flag 0=yes, 1=no

# print name header if needed
doheader(){
        doline
        printf "                         start-groupdrilling                          \n"
}

doline(){
        printf "======================================================================\n"
}

doerror(){
        printf "    Not starting the groupdrilling! Some required parts were not found.      \n"
        doline
        printf "%s " "Press return to close."
        read -r ans
}

# check for python3 on this system
# note to file: 2> suppresses the assertion error but does not discard the
# standard output. sh in linux kde required the 2 instead of &
chk4python3(){
  printf " Checking for python3"
  if ! python3 -c 'import sys; assert sys.version_info >= (3, )' 2> /dev/null;
  then
      printf "\n======================================================================\n"
      printf " ! A problem. Python3 is required for groupdrilling to work.\n"
      printf " Search the internet for how to install it for your computer.\n"
      printf "======================================================================\n"
      s=1
  else
    printf " .... found "
    python3 --version
  fi
}

# initial cleanup
initclean(){
    reset
    clear
    cd -- "$(dirname "$0")" || return
}

# checking for needed parts
chk4parts(){

  printf " Checking for ./worddata/letter_ranks.txt"
  file='./worddata/letter_ranks.txt'
  if [ ! -f "$file" ]
  then
      notfound $file 0
  else
      printf " .... found.\n"
  fi

  printf " Checking for ./groupdrilling.py"
  file='./groupdrilling.py'
  if [ ! -f "$file" ]
  then
      notfound $file 1
      s=1
  else
      printf " .... found.\n"
  fi

  printf " Checking for ./helpers.py"
  file='./helpers.py'
  if [ ! -f "$file" ]
  then
      notfound $file 1
      s=1
  else
      printf " .... found.\n"
  fi

  printf " Checking for ./worddata/nyt_wordlist.txt"
  file='./worddata/nyt_wordlist.txt'
  if [ ! -f "$file" ]
  then
      notfound $file 1
      s=1
  else
      printf " .... found.\n"
  fi

}

notfound(){
  f=$1
  n=$2
  printf "\n   %s not found." "${f}"
  if [ "$n" -eq 0 ]
  then
    printf "  It is not needed.\n"
  else
    printf "  It is needed.\n"
  fi
}

startitup(){
  sleep 1
  cd -- "$(dirname "$0")" || exit
  if [ $s -eq 0 ]
  then
    python3 groupdrilling.py &
  else
    doerror
  fi
}

# program section
initclean
doheader
doline
chk4python3
chk4parts
doline
startitup
# end
