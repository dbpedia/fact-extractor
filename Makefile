LANGCODE=it
LANGUAGE=italian
WORK_DIR=./workspace-$(LANGCODE)
PAGES_DIR=$(WORK_DIR)/pages
PAGES_DIR=$(WORK_DIR)/pages
SOCCER_DIR=$(WORK_DIR)/soccer
SENTENCES_DIR=$(WORK_DIR)/sentences
TREETAGGER=../tree-tagger/cmd/tree-tagger-$(LANGUAGE)
SOCCER_IDS=../soccer_ids
DUMP=../$(LANGCODE)wiki-latest-pages-articles.xml.bz2

default:
	@echo "Ciao"

clean:
	rm -rf $(WORK_DIR)
	mkdir -p $(WORK_DIR)

get-soccer-ids-sample:
	curl -g -H 'Accept: text/csv' 'http://$(LANGCODE).dbpedia.org/sparql?query=SELECT%20?id%20WHERE%20{%20?player%20a%20%3Chttp://dbpedia.org/ontology/SoccerPlayer%3E%20.%20?player%20dbpedia-owl:wikiPageID%20?id%20}' | tail -n +2 > $(SOCCER_IDS)

extract-pages:
	mkdir -p $(WORK_DIR)
	bzcat $(DUMP) | python lib/WikiExtractor.py -o $(PAGES_DIR)
	find $(PAGES_DIR)/*/* -type f -exec cat '{}' \; > $(WORK_DIR)/all-articles.txt

extract-soccer:
	mkdir -p $(SOCCER_DIR)
	python verb_extraction/process_articles.py $(SOCCER_IDS) \
		$(WORK_DIR)/all-articles.txt $(SOCCER_DIR) \
		$(WORK_DIR)/wiki-id-to-title-mapping.json
	find $(SOCCER_DIR)/* -type f -exec cat '{}' \; > $(WORK_DIR)/all-soccer.txt

extract-verbs:
	cat $(WORK_DIR)/all-soccer.txt | $(TREETAGGER) | grep VER | grep -v '<unknown>' | \
		cut -f 1,3 | tr '[:upper:]' '[:lower:]' > $(WORK_DIR)/raw-verbs.txt
	sort -u $(WORK_DIR)/raw-verbs.txt -o $(WORK_DIR)/token2lemma.txt
	cut -f 1 $(WORK_DIR)/token2lemma.txt > $(WORK_DIR)/tokens.txt
	cut -f 2 $(WORK_DIR)/token2lemma.txt | sort -u -o $(WORK_DIR)/lemmas.txt
	python verb_extraction/bag_of_words.py $(WORK_DIR)/all-soccer.txt \
		$(WORK_DIR)/vocabulary.txt

extract-sentences:
	mkdir -p $(SENTENCES_DIR)
	python verb_extraction/extract_sentences.py $(WORK_DIR)/all-soccer.txt \
		resources/tokens.list $(SENTENCES_DIR)

rank-verbs:
	cut -f 2 $(WORK_DIR)/token-lemma.txt | python verb_ranking/make_lemma_freq.py - \
		$(WORK_DIR)/lemma-freq.json
	cut -d '"' -f 2 workspace-it/lemma-freq.json | grep -vP	\
		'avere|essere|fare|potere|volere|dovere' | sed -n '2,52'p | sort \
		> $(WORK_DIR)/top-50-lemmas.txt
	grep -wf $(WORK_DIR)/top-50-lemmas.txt $(WORK_DIR)/token-lemma | sort -u \
		> $(WORK_DIR)/top-50-tokens.txt
	grep -wf $(WORK_DIR)/top-50-lemmas.txt > $(WORK_DIR)/top-50-token2lemma.txt
	python verb_ranking/tf_idfize.py $(SOCCER_DIR) $(WORK_DIR)/top-50-tokens.txt \
		--variance-out $(WORK_DIR)/verbs-variance.json \
		--stdevs-out $(WORK_DIR)/verbs-stdev.json \
		--threshold-rank-out $(WORK_DIR)/verbs-rank-threshold.json \
		--tfidf-rank-out $(WORK_DIR)/verbs-tfidf-rank.json
	python verb_ranking/compute_stdev_by_lemma.py $(WORK_DIR)/top-50-token2lemma.txt \
		$(WORK_DIR)/verbs-stdev.json $(WORK_DIR)/lemma-stdev.json
