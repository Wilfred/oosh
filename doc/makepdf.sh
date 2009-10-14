#!/bin/bash

# a rather noisy script to run latex

echo -e '\e[0;31mWriting proposal pdf \e[m'
pdflatex proposal.tex

# to include a latex file in another we cannot have the preamble
# this could be smarter, but assume the size of the header is constant
echo -e '\e[0;31mGenerating proposal include \e[m'
tail --lines=+10 proposal.tex | head --lines=-1 >proposal_include.tex

echo -e '\e[0;31mWriting dissertation pdf \e[m'
pdflatex dissertation.tex
