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
LANGUAGE="$(echo $1 | tr '[:upper:]' '[:lower:]')"

# Switch statement to select language
case $LANGUAGE in
	"bulgarian" | "bg")
  		LANGUAGE="bulgarian"
  		LANGCODE="bg"
  		;;
	"chinese" | "zh")
  		LANGUAGE="chinese"
  		LANGCODE="zh"
  		;;
	"dutch" | "nl")
  		LANGUAGE="dutch"
  		LANGCODE="nl"
  		;;
	"english" | "en")
  		LANGUAGE="english"
  		LANGCODE="en"
  		;;
	"estonian" | "et")
  		LANGUAGE="estonian"
  		LANGCODE="et"
  		;;
	"finnish" | "fi")
  		LANGUAGE="finnish"
  		LANGCODE="fi"
  		;;
	"french" | "fr")
  		LANGUAGE="french"
  		LANGCODE="fr"
  		;;
	"galician" | "gl")
  		LANGUAGE="galician"
  		LANGCODE="gl"
  		;;
	"german" | "de")
  		LANGUAGE="german"
  		LANGCODE="de"
  		;;
	"italian" | "it")
  		LANGUAGE="italian"
  		LANGCODE="it"
  		;;
	"latin" | "la")
  		LANGUAGE="latin"
  		LANGCODE="la"
  		;;
	"mongolian" | "mn")
  		LANGUAGE="mongolian"
  		LANGCODE="mn"
  		;;
	"polish" | "pl")
  		LANGUAGE="polish"
  		LANGCODE="pl"
  		;;
	"portuguese" | "pt")
  		LANGUAGE="portuguese"
  		LANGCODE="pt"
  		;;
	"russian" | "ru")
  		LANGUAGE="russian"
  		LANGCODE="ru"
  		;;
	"slovak" | "sk")
  		LANGUAGE="slovak"
  		LANGCODE="sk"
  		;;
	"spanish" | "es")
  		LANGUAGE="spanish"
  		LANGCODE="es"
  		;;
	"swahili" | "sw")
  		LANGUAGE="swahili"
  		LANGCODE="sw"
  		;;
	*)
		echo "Invalid or not supported language for now! QUITTING ..."
		exit 1
		;;
esac

# Form Wikipedia dump URL
URL="http://download.wikimedia.org/"$LANGCODE"wiki/latest/"$LANGCODE"wiki-latest-pages-articles.xml.bz2"
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
find extracted -type f -exec bash -c "cat '{}' | treetagger/cmd/tree-tagger-"$LANGUAGE" | grep VER >> verbs" \;
sort -u verbs > unique-sorted-verbs
# Extract vocabulary
python scripts/bag_of_words.py all-extracted.txt
# POS tagging + chunker with TextPro
perl textpro.pl -verbose -html -l ita -c token+sentence+pos+chunk -o . ~/srl/training/"$LANGCODE"wiki/gold

### Extract chunks from TextPro
perl textpro.pl -verbose -html -l ita -c token+sentence+pos+chunk -o ~/srl/soccer/training/07042015/textpro/ ~/srl/soccer/training/07042015/sentences.curated
# Manually curate in case of end-of-sentence errors
# Split into one sentence per file
cat full.curated | csplit --suppress-matched -z -f '' - '/<eos>/' {*}
# Extract Noun Phrases only
ls | grep [0-9] | xargs -I {} sh -c "egrep '(B|I)\-NP' {} > ../textpro-chunks/{}"
