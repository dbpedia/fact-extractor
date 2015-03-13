#!/bin/bash
# Seed selection strategies

set -e

### BEGIN baseline ###
# 1. Sentences with LUs lexicalizations (all encountered tokens, not just the lemma)
grep -rhwf tokens ../../../corpus/ > raw-sentences
# 2. Short sentences
while read f; do words=$(echo $f | wc -w); if [ $words -lt 15 ]; then echo $f >> short; fi; done < raw-sentences
# 3. Filter based on synctatic patterns (NP V NP)
python get_meaningful_sentences soccer/training/giocare/pos-tagged soccer/training/giocare/tokens
# 4. Link entities
python entity_linking.py ../../training/itwiki/clean-gold && mkdir ../../training/itwiki/linked-gold && mv *.json ../../training/itwiki/linked-gold
### END baseline ###

### BEGIN Distant supervision with DBpedia ###
# Inspired by http://semantic-web-journal.net/system/files/swj742.pdf
# TODO Raw properties with subject == Soccer Player and object == SoccerPlayer | SportsTeam | SoccerClub | SportsEvent
# TODO Subject + object entities lexicalizations
# 1. Grep-friendly list of soccer-related entity lexicalizations
python extract_lexicalizations.py SoccerPlayer SoccerClub SoccerLeague SoccerTournament SoccerLeagueSeason
sort -u lexicalizations > resources/lexicalizations.sorted
rm lexicalizations
# 3. Match lexicalizations against the corpus
grep -rhwf ~/srl/scripts/resources/lexicalizations.sorted ~/srl/corpora/soccer-players > ~/srl/soccer/training/lexicalizations/raw-sentences
# 4. Positive example: at least 2 entities must match, negative example otherwise

# 5. Ambiguity filtering

### END DBpedia lexicalizations ###

### BEGIN active learning, query-by-committee (QBC) ###
# Inspired by http://nlp.stanford.edu/pubs/2014emnlp-kbpactivelearning.pdf
# TODO
### END active learning ###
