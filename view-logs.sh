#!/bin/bash

if [ $# -lt 1 ]; then
  echo "Usage: $0 <keyword> [<keyword1> <keyword2> ... <keywordN>]"
  exit 1
fi

file_name="./test.log"

pattern=$(echo "$*" | tr ' ' '|')

tail -n 1500 "$file_name" | grep -iE "$pattern"

