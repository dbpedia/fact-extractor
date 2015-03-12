#!/bin/bash

set -e

cd ..

# Check if the argument is null
if [ ! -n "$1" ] ;then
    echo "No language code entered!"
    echo "Usage:"
    echo "./extract_verbs.sh languageCode(e.g it OR italian for Italian)"   
    exit
fi
# Get the entered language code
LANGCODE=$1
# Get the right tree-tagger file and abbreviative language code based on the input 
case $LANGCODE in
	[iI][tT] | [iI][tT][aA][lL][iI][aA][nN] )
		LANGCODE="it"
		TREETAGGER="tree-tagger-italian";;
	[zZ][hH] | [cC][hH][iI][nN][eE][sE][eE] )
		LANGCODE="zh"
		TREETAGGER="tree-tagger-chinese";;
	[eE][nN] | [eE][nN][gG][lL][iI][sS][hH] )
		LANGCODE="en"
		TREETAGGER="tree-tagger-english";;
	[bB][gG] | [bB][uU][lL][gG][aA][rR][iI][aA][nN] )
		LANGCODE="bg"
		TREETAGGER="tree-tagger-bulgarian";;
	[nN][lL] | [dD][uU][tT][cC][hH] )
		LANGCODE="nl"
		TREETAGGER="tree-tagger-dutch";;
	[eE][tT] | [eE][sS][tT][oO][nN][iI][aA][nN] )
		LANGCODE="et"
		TREETAGGER="tree-tagger-estonian";;
	[fF][iI] | [fF][iI][nN][nN][iI][sS][hH] )
		LANGCODE="fi"
		TREETAGGER="tree-tagger-finnish";;
	[fF][rR] | [fF][rR][eE][nN][cC][hH] )
		LANGCODE="fr"
		TREETAGGER="tree-tagger-french";;
	[gG][lL] | [gG][aA][lL][iI][cC][iI][aA][nN] )
		LANGCODE="gl"
		TREETAGGER="tree-tagger-galician";;
	[dD][eE] | [gG][eE][rR][mM][aA][nN] )
		LANGCODE="de"
		TREETAGGER="tree-tagger-german";;
	[lL][aA] | [lL][aA][tT][iI][nN] )
		LANGCODE="la"
		TREETAGGER="tree-tagger-latin";;
	[pP][lL] | [pP][oO][lL][iI][sS][hH] )
		LANGCODE="pl"
		TREETAGGER="tree-tagger-polish";;
	[rR][uU] | [rR][uU][sS][sS][iI][aA][nN] )
		LANGCODE="ru"
		TREETAGGER="tree-tagger-russian";;
	[sS][kK] | [sS][lL][oO][vV][aA][kK] )
		LANGCODE="sk"
		TREETAGGER="tree-tagger-slovak";;
	[eE][sS] | [sS][pP][aA][nN][iI][sS][hH] )
		LANGCODE="es"
		TREETAGGER="tree-tagger-spanish";;
	[sS][wW] | [sS][wW][aA][hH][iI][lL][iI] )
		LANGCODE="sw"
		TREETAGGER="tree-tagger-swahili";;
	*) echo "Invalid input OR Not supported language for now"
    	exit;;
esac
# Generate the Wikipedia dump URL
WIKIDUMPURL="http://download.wikimedia.org/"$LANGCODE"wiki/latest/"$LANGCODE"wiki-latest-pages-articles.xml.bz2"
# Download latest Wikipedia dump
wget $WIKIDUMPURL
# Extract text
if [ ! -d "extracted/"]; then
  mkdir "extracted/"
fi
bzcat "$LANGCODE"wiki-latest-pages-articles.xml.bz2 | scripts/lib/WikiExtractor.py -o extracted/
# Split extraction by article
if [ ! -d "corpus/"]; then
  mkdir "corpus/"
fi
cat extracted/*/* | csplit --suppress-matched -z -f 'corpus/doc_' - '/</doc>/' {*}
# Build a single big file
find extracted -type f -exec cat {} \; > all-extracted.txt
# Extract verbs with TreeTagger
# N.B. treetagger segfaults with the single big file, run it over each article instead
#cat all-extracted.txt | treetagger/cmd/tree-tagger-chinese | grep VER | sort -u > verbi.txt
find extracted -type f -exec bash -c "cat '{}' | treetagger/cmd/$TREETAGGER | grep VER >> verbi.txt" \;
sort -u verbi.txt > unique-sorted-verbs.txt
# Extract vocabulary
python scripts/bag_of_words.py all-extracted.txt
# POS tagging + chunker with TextPro
perl textpro.pl -verbose -html -l ita -c token+sentence+pos+chunk -o . ~/srl/training/"$LANGCODE"wiki/gold
