#!/bin/bash

set -e

cd ..
# Download latest Wikipedia dump in language of choice
echo "Enter wikipedia dump language e.g. en OR english"
read LANGCODE
#convert lnaguge code to lower case
LANGCODE="$(echo $LANGCODE | tr '[A-Z]' '[a-z]')"

#looping to select language
case $LANGCODE in
	"english" | "en" )
		LANGSHORTCODE="en"
		TAGGER="tree-tagger-english"
		;;

	"french" | "fr" )
		LANGSHORTCODE="fr"
		TAGGER="tree-tagger-french"
		;;

	"german" | "de" )
		LANGSHORTCODE="de"
		TAGGER="tree-tagger-german"
		;;

	"bulgarian" | "bg" )
		LANGSHORTCODE="bg"
		TAGGER="tree-tagger-bulgarian"
		;;

	"dutch" | "nl" )
		LANGSHORTCODE="nl"
		TAGGER="tree-tagger-dutch"
		;;

	"estonian" | "et" )
		LANGSHORTCODE="et"
		TAGGER="tree-tagger-estonian"
		;;

	"finnish" | "fi" )
		LANGSHORTCODE="fi"
		TAGGER="tree-tagger-finnish"
		;;

	"galician" | "gl" )
		LANGSHORTCODE="gl"
		TAGGER="tree-tagger-galician"
		;;

	"italian" | "it" )
		LANGSHORTCODE="it"
		TAGGER="tree-tagger-italian"
		;;

	"latin" | "la" )
		LANGSHORTCODE="la"
		TAGGER="tree-tagger-latin"
		;;

	"polish" | "pl" )
		LANGSHORTCODE="pl"
		TAGGER="tree-tagger-polish"
		;;

	"russian" | "ru" )
		LANGSHORTCODE="ru"
		TAGGER="tree-tagger-russian"
		;;

	"slovak" | "sk" )
		LANGSHORTCODE="sk"
		TAGGER="tree-tagger-slovak"
		;;

	"spanish" | "es" )
		LANGSHORTCODE="es"
		TAGGER="tree-tagger-spanish"
		;;

	*)
		echo "Entered language is not yet supported in this script! EXIT from script"
		exit
		;;
esac

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
