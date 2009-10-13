#!/bin/bash

if [ $# -ne 1 ]
then
    echo "Please state one tex file for a word count."
else
    detex $1 | tr -cd '0-9A-Z a-z\n' | wc -w
fi