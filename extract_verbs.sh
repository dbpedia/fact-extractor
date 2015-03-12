#!/bin/bash
# Call this script with the language you want to work with
# The accepted argument can be a language or a language code, e.g., 'en' OR 'english'
# sh extract_verbs.sh english

set -e

cd ..

if [[ $# -ne 1 ]]; then
    echo "Usage: sh $(basename "$0") <LANGUAGE>"
	exit 1
fi

# Lowercase argument
LANGCODE="$(echo $1 | tr '[:upper:]' '[:lower:]')"

# Switch statement to select language
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
		echo "Invalid or not supported language for now! QUITTING ..."
		exit 1
		;;
esac

# Form Wikipedia dump URL
URL="http://download.wikimedia.org/"$LANGSHORTCODE"wiki/latest/"$LANGSHORTCODE"wiki-latest-pages-articles.xml.bz2"
echo "Downloading dump from: $URL"
wget $URL
# Extract text
if [ ! -d "extracted"]; then
    mkdir extracted
fi
bzcat "$LANGCODE"wiki-latest-pages-articles.xml.bz2 | scripts/lib/WikiExtractor.py -o extracted
# Split extraction by article
if [ ! -d "corpus"]; then
    mkdir corpus
fi
cat extracted/*/* | csplit --suppress-matched -z -f 'corpus/doc_' - '/</doc>/' {*}
# Build a single big file
find extracted -type f -exec cat {} \; > all-extracted.txt
# Extract verbs with TreeTagger
# N.B. treetagger segfaults with the single big file, run it over each article instead
#cat all-extracted.txt | treetagger/cmd/tree-tagger-italian | grep VER | sort -u > verbi.txt
find extracted -type f -exec bash -c "cat '{}' | treetagger/cmd/$TAGGER | grep VER >> verbs" \;
sort -u verbs > unique-sorted-verbs
# Extract vocabulary
python scripts/bag_of_words.py all-extracted.txt
# POS tagging + chunker with TextPro
perl textpro.pl -verbose -html -l ita -c token+sentence+pos+chunk -o . ~/srl/training/"$LANGSHORTCODE"wiki/gold
