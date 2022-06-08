#!/bin/bash
# akseidel 06/08/22
# https://github.com/akseidel/
# A script automating the steps to run pywordletool
#
# To use from the residing folder:
# First mark as executable with "chmod +x start-pywt.command".
# In OSX run by entering "./start-pywt.command".
# In Linux run by entering "./start-pywt.command"
#
# Script arguments:
# none

# globals
s=0

# print name header if needed
doheader(){
        doline
        printf "                             start-pywt                               \n"
}

doline(){
        printf "======================================================================\n"
}

dotrailer(){
        printf "You may minimize this window, do not close it. The helper will close. \n"
        doline
}

doerror(){
        printf "    Not starting the helper! Some required parts were not found.      \n"
        doline
}

# check for python package customtkinter on this system
chk4customtkinter(){
  printf " Checking for customtkinter"
  if ! pip3 list | grep 'customtkinter' > /dev/null;
  then
      printf "\n======================================================================\n"
      printf " ! A problem. The 'customtkinter' package for python is required\n"
      printf " for pywordletool to work. This package nees to be installed using\n"
      printf " pip. \n"
      printf "\n It can be installed using the command:\n"
      printf "\n     pip3 install customtkinter\n"
      printf "======================================================================\n"
      s=1
      exit 0
  else
    printf " .... found.\n"
  fi
}

# initial cleanup
initclean(){
    reset
    clear
    cd -- "$(dirname "$0")" || return
}

chk4parts(){
  printf " Checking for ./worddata/helpinfo.txt"
  file='./worddata/helpinfo.txt'
  if [ ! -f "$file" ]
  then
      notfound $file 0
  else
      printf " .... found.\n"
  fi

  printf " Checking for ./worddata/letter_ranks.txt"
  file='./worddata/letter_ranks.txt'
  if [ ! -f "$file" ]
  then
      notfound $file 0
  else
      printf " .... found.\n"
  fi

  printf " Checking for ./pywt.py"
  file='./pywt.py'
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

  printf " Checking for ./worddata/wo_nyt_wordlist.txt"
  file='./worddata/wo_nyt_wordlist.txt'
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
  if [ $n -eq 0 ]
  then
    printf "  It is not needed.\n"
  else
    printf "  It is needed.\n"
  fi
}

startitup(){
  cd -- "$(dirname "$0")" || exit
  if [ $s -eq 0 ]
  then
    dotrailer
    python3 pywt.py
  else
    doerror
  fi
}


# program section
initclean
doheader
doline
chk4customtkinter
chk4parts
doline
startitup
# end


#####!/bin/bash
#####cd -- "$(dirname "$0")"
#####python3 pywt.py
