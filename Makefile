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
	cat $(WORK_DIR)/all-soccer.txt | $(TREETAGGER) | grep VER | \
		tr '[:upper:]' '[:lower:]' > $(WORK_DIR)/temp-ver.txt
	cut -f 1 $(WORK_DIR)/temp-ver.txt > $(WORK_DIR)/all-verbs.txt
	cut -f 3 $(WORK_DIR)/temp-ver.txt > $(WORK_DIR)/verb-lemmas.txt
	sort -u $(WORK_DIR)/verb-lemmas.txt -o $(WORK_DIR)/verb-lemmas.txt
	rm $(WORK_DIR)/temp-ver.txt
