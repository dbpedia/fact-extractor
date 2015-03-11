#!/bin/bash

set -e

cd ..
# Download latest Wikipedia dump in language of choice
echo "Enter wikipedia dump language e.g. en OR english"
read LANGCODE
#convert lnaguge code to lower case
LANGCODE="$(echo $LANGCODE | tr '[A-Z]' '[a-z]')"

#looping to select language
if [ "$LANGCODE" = "english" ] || [ "$LANGCODE" = "en" ]; then
	LANGSHORTCODE="en"
	TAGGER="tree-tagger-english"
elif [ "$LANGCODE" = "french" ] || [ "$LANGCODE" = "fr" ]; then
	LANGSHORTCODE="fr"
	TAGGER="tree-tagger-french"
elif [ "$LANGCODE" = "german" ] || [ "$LANGCODE" = "de" ]; then
	LANGSHORTCODE="de"
	TAGGER="tree-tagger-german"
elif [ "$LANGCODE" = "bulgarian" ] || [ "$LANGCODE" = "bg" ]; then
	LANGSHORTCODE="bg"
	TAGGER="tree-tagger-bulgarian"
elif [ "$LANGCODE" = "dutch" ] || [ "$LANGCODE" = "nl" ]; then
	LANGSHORTCODE="nl"
	TAGGER="tree-tagger-dutch"
elif [ "$LANGCODE" = "estonian" ] || [ "$LANGCODE" = "et" ]; then
	LANGSHORTCODE="et"
	TAGGER="tree-tagger-estonian"
elif [ "$LANGCODE" = "finnish" ] || [ "$LANGCODE" = "fi" ]; then
	LANGSHORTCODE="fi"
	TAGGER="tree-tagger-finnish"
elif [ "$LANGCODE" = "galician" ] || [ "$LANGCODE" = "gl" ]; then
	LANGSHORTCODE="gl"
	TAGGER="tree-tagger-galician"
elif [ "$LANGCODE" = "italian" ] || [ "$LANGCODE" = "it" ]; then
	LANGSHORTCODE="it"
	TAGGER="tree-tagger-italian"
elif [ "$LANGCODE" = "latin" ] || [ "$LANGCODE" = "la" ]; then
	LANGSHORTCODE="la"
	TAGGER="tree-tagger-latin"
elif [ "$LANGCODE" = "polish" ] || [ "$LANGCODE" = "pl" ]; then
	LANGSHORTCODE="pl"
	TAGGER="tree-tagger-polish"
elif [ "$LANGCODE" = "russian" ] || [ "$LANGCODE" = "ru" ]; then
	LANGSHORTCODE="ru"
	TAGGER="tree-tagger-russian"
elif [ "$LANGCODE" = "slovak" ] || [ "$LANGCODE" = "sk" ]; then
	LANGSHORTCODE="sk"
	TAGGER="tree-tagger-slovak"
elif [ "$LANGCODE" = "spanish" ] || [ "$LANGCODE" = "es" ]; then
	LANGSHORTCODE="es"
	TAGGER="tree-tagger-spanish"
else
	echo "Entered language is not yet supported in this script! EXIT from script"
	exit
fi

#forming URL
URL="http://download.wikimedia.org/"$LANGSHORTCODE"wiki/latest/"$LANGSHORTCODE"wiki-latest-pages-articles.xml.bz2"
echo "Downloading dump from: $URL"
#wget [URL]
wget $URL
# Extract text
bzcat "$LANGSHORTCODE"wiki-latest-pages-articles.xml.bz2 | scripts/lib/WikiExtractor.py
# Split extraction by article
cat extracted/*/* | csplit --suppress-matched -z -f 'corpus/doc_' - '/</doc>/' {*}
# Build a single big file
find extracted -type f -exec cat {} \; > all-extracted.txt
# Extract verbs with TreeTagger
# N.B. treetagger segfaults with the single big file, run it over each article instead
#cat all-extracted.txt | treetagger/cmd/tree-tagger-italian | grep VER | sort -u > verbi.txt
find extracted -type f -exec bash -c "cat '{}' | treetagger/cmd/$TAGGER | grep VER >> verbi.txt" \;
sort -u verbi.txt > unique-sorted-verbs.txt
# Extract vocabulary
python scripts/bag_of_words.py all-extracted.txt
# POS tagging + chunker with TextPro
perl textpro.pl -verbose -html -l ita -c token+sentence+pos+chunk -o . ~/srl/training/"$LANGSHORTCODE"wiki/gold
