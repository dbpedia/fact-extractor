#######################
# Verb extraction
#######################
# A random sample of 1k verbs
shuf true-positives.txt | head -1000 > 1ktest
# Cut out entries identified as verbs with unknown lemma (probably errors)
grep -v unknown all.txt > true-positives.txt
# Lemma list
cut -f 3 true-positives.txt | sort -u > lemmas.txt
# Frequency dict
python make_lemma_freq.py
# 100 most frequent
grep -P '\d{3},' frequencies.json | cut -d '"' -f 2 > over-100-occurrencies
# Top 50 without auxiliar/modal verbs (very frequent of course)
grep -vP 'avere|essere|fare|potere|volere|dovere' frequencies.json | sed -n '2,52'p > top-50
# Top 50 lemmas with grep magic
grep -Po '"\K[^"]+(?=")' top-50 | sort -u > top-50-sorted-lemmas
# Get tokens from the top 50 lemmas
grep -wf top-50-sorted-lemmas true-positives | cut -f 1 | perl -ne 'print lc' | sort -u > top-50-sorted-tokens

######################
# Crowdsourcing data building
######################
# very rough grep on selected lexical units (infinite tense only)
for lu in {nascere,dare,uccidere,dire,morire}; do grep -rhw $lu ../../corpus/ | sed "s/$lu/<strong>$lu<\/strong>/gi" > $lu/tagged; done
# get the token list from a verb
grep -P '^(mor|muo)' ../../verbs/top-50-sorted-tokens
# better grep using a token list (all tense occurrencies)
grep -rhwf tokens ../../../corpus/ > raw-sentences
# surround lexical units with a <strong> tag
sed -r 's/(mor[^ ]+|muo[^ ]+)/<strong>\1<\/strong>/gi' raw-sentences > tagged-sentences
# get sentences with less than 15 words
while read f; do words=$(echo $f | wc -w); if [ $words -lt 15 ]; then echo $f >> short; fi; done < tagged-sentences
# gold creation: 10 random sentences for each lexical unit
for lu in {nascere,dare,uccidere,dire,morire}; do shuf -n 10 $lu/tagged > $lu/gold; cat $lu/gold >> gold; done
# split into sentences
python split_sentence.py
# link entities
python entity_linking.py ../../training/itwiki/clean-gold && mkdir ../../training/itwiki/linked-gold && mv *.json ../../training/itwiki/linked-gold
# POS tag sentences
i=0; while read f; do echo $f | treetagger/cmd/tree-tagger-italian > training/itwiki/pos-tagged-gold/$i; let i++; done < training/itwiki/clean-gold
# build crowdflower input csv
python create_crowdflower_input.py ../training/itwiki/partecipare/linked-gold/ ../training/itwiki/partecipare/pos-tagged-gold/

#######################
# Intersect with Evalita 2008 frame annotation dataset and get what matches
#######################
# SRL annotation
cat ILC/ILC_Sample_*.sem FBK/FBK_Sample.sem >> annotated
# LUs evoking frames
grep Target annotated > lus
# LUs + frames
cut -f 2,4 lus > frames
# Unique + sorted LUs
# N.B. manually removed 'a'
cut -f 1 lexical-units/frames | sort -u > lexical-units/unique-sorted

# POS tagging
cat ILC/ILC_Sample_*.synt FBK/FBK_Sample.synt >> pos-tagged
# Verbs + lemmas
grep -P '\tV\t' pos-tagged | cut -f 2,3 | grep -v '<unknown>' > lexical-units/verb-lemmas
# Intersect LUs with verbs + lemmas 
grep -wf lexical-units/unique-sorted lexical-units/verb-lemmas > intersection
# Intersect with our list of verbs
# N.B. Seems to yield the same set
grep -wf ../verbs/unique-sorted-lemmas intersection > ../matching/all
# Verb lexicalizations
cut -f 1 ../matching/all > ../matching/verbs
# Verbs + frames
grep -wf ../matching/verbs with-frames > ../matching/verbs-frames
# Final set of frames (with frequencies) in the Italian Wikipedia that appear in the annotated dataset
python ../../scripts/make_frames_freq.py verbs-frames
