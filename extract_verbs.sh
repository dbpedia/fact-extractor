#!/bin/bash

set -e

cd ..
# Download latest Italian Wikipedia dump
#wget http://download.wikimedia.org/itwiki/latest/itwiki-latest-pages-articles.xml.bz2
# Extract text
#bzcat itwiki-latest-pages-articles.xml.bz2 | scripts/WikiExtractor.py
# Build a single big file
find extracted -type f -exec cat {} \; > all-extracted.txt
# Extract verbs with TreeTagger
cat all-extracted.txt | treetagger/cmd/tree-tagger-italian | grep VER | sort -u > verbi.txt
# Extract vocabulary
python scripts/bag_of_words.py all-extracted.txt
