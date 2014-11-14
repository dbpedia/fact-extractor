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
# N.B. modal + auxiliar verbs commented by hand
# Intersect with Saccarosio's frame annotation dataset and get matching sentence IDs
# FIXME no lemmas in annotation, change matching strategy
grep -wf ../verbs/over-100-occurrencies FBK/ita_gold.xml | grep -oP 'id="[^"]+"' | sed 's/id="//' | sed 's/"//' > FBK/matching-ids

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
grep -f ../verbs/unique-lemmas.txt intersection | cut -f 2 | sort -u > matching-lemmas
# Final set of frames in the Italian Wikipedia that appear in the annotated dataset
cut -f 2 frames | sort -u > unique-sorted-frames
