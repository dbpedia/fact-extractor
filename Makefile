WORK_DIR=./workspace
PAGES_DIR=$(WORK_DIR)/sentences
PAGES_DIR=$(WORK_DIR)/pages
SOCCER_DIR=$(WORK_DIR)/soccer
TREETAGGER=../tree-tagger/cmd/tree-tagger-italian
SOCCER_IDS=../soccer_ids
DUMP=../itwiki-latest-pages-articles.xml.bz2

default:
	@echo "Ciao"

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
	sort -u $(WORK_DIR)/raw-verbs.txt -o $(WORK_DIR)/verb-lemma.txt
	cut -f 1 $(WORK_DIR)/verb-lemma.txt > $(WORK_DIR)/verbs.txt
	cut -f 2 $(WORK_DIR)/verb-lemma.txt | sort -u -o $(WORK_DIR)/lemmas.txt
	python verb_extraction/bag_of_words.py $(WORK_DIR)/all-soccer.txt \
		$(WORK_DIR)/vocabulary.txt

rank-verbs:
	python verb_ranking/tf_idfize.py $(SOCCER_DIR) $(WORK_DIR)/verbs.txt \
		--variance-out $(WORK_DIR)/verbs-variance.json \
		--stdevs-out $(WORK_DIR)/verbs-stdev.json \
		--threshold-rank-out $(WORK_DIR)/verbs-rank-threshold.json \
		--tfidf-rank-out $(WORK_DIR)/verbs-tfidf-rank.json
	python verb_ranking/compute_stdev_by_lemma.py $(WORK_DIR)/verb-lemma.txt \
		$(WORK_DIR)/verbs-stdev.json $(WORK_DIR)/lemma-stdev.json
	cut -f 2 $(WORK_DIR)/verb-lemma.txt | python verb_ranking/make_lemma_freq.py - \
		$(WORK_DIR)/lemma-freq.json
