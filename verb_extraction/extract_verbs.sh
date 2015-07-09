#!/bin/bash
# Call this script with the language you want to work with
# sh extract_verbs.sh english

set -e

cd ..

if [[ $# -ne 2 ]]; then
    echo "Usage: sh $(basename "$0") <LANGUAGE> <SENTENCES_DIR>"
	exit 1
fi

find $2 -type f -exec bash -c "cat '{}' | treetagger/cmd/tree-tagger-"$1" | grep VER >> verbs" \;
sort -u verbs > unique-sorted-verbs
# Extract vocabulary
python bag_of_words.py all-extracted.txt
# POS tagging + chunker with TextPro
perl textpro.pl -verbose -html -l ita -c token+sentence+pos+chunk -o . ~/srl/training/"$LANGCODE"wiki/gold

### Extract chunks from TextPro
perl textpro.pl -verbose -html -l ita -c token+sentence+pos+chunk -o ~/srl/soccer/training/07042015/textpro/ ~/srl/soccer/training/07042015/sentences.curated
# Manually curate in case of end-of-sentence errors
# Split into one sentence per file
cat full.curated | csplit --suppress-matched -z -f '' - '/<eos>/' {*}
# Extract Noun Phrases only
ls | grep [0-9] | xargs -I {} sh -c "egrep '(B|I)\-NP' {} > ../textpro-chunks/{}"
