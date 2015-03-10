#!/bin/bash

set -e

cd ..
# Download latest Wikipedia dump in language of Chioce
echo -n "Enter wikipedia dump URL e.g.  http://download.wikimedia.org/itwiki/latest/itwiki-latest-pages-articles.xml.bz2> "
read URL
echo "Downloading dump from: $URL"
#wget -O [Preferred_Name] [URL]
wget -O wiki-pages-articles.xml.bz2 $URL
# Extract text
bzcat wiki-pages-articles.xml.bz2 | scripts/lib/WikiExtractor.py
# Split extraction by article
cat extracted/*/* | csplit --suppress-matched -z -f 'corpus/doc_' - '/</doc>/' {*}
# Build a single big file
find extracted -type f -exec cat {} \; > all-extracted.txt
# Extract verbs with TreeTagger
# N.B. treetagger segfaults with the single big file, run it over each article instead
#cat all-extracted.txt | treetagger/cmd/tree-tagger-italian | grep VER | sort -u > verbi.txt
echo -n "enter corresponding language tree-tagger path e.g. /home/kasun/tree_tagger/cmd/tree-tagger-italian "
read TAGGERPATH
find extracted -type f -exec bash -c "cat '{}' | $TAGGERPATH | grep VER >> verbi.txt" \;
sort -u verbi.txt > unique-sorted-verbs.txt
# Extract vocabulary
python scripts/bag_of_words.py all-extracted.txt
# POS tagging + chunker with TextPro
perl textpro.pl -verbose -html -l ita -c token+sentence+pos+chunk -o . ~/srl/training/itwiki/gold
