#!/bin/bash

# a rather noisy script to run latex

echo -e 'Writing proposal pdf'
pdflatex proposal.tex

# this could be smarter, but assume the size of the header is constant
echo -e 'Generating proposal include'
tail --lines=+10 proposal.tex | head --lines=-1 >proposal_include.tex

echo -e 'Writing dissertation pdf'
pdflatex dissertation.tex