LANGCODE=it
LANGUAGE=italian
WORK_DIR=./workspace-$(LANGCODE)
PAGES_DIR=$(WORK_DIR)/pages
PAGES_DIR=$(WORK_DIR)/pages
SOCCER_DIR=$(WORK_DIR)/soccer
SENTENCES_DIR=$(WORK_DIR)/sentences
TAGGED_DIR=$(WORK_DIR)/tagged
GOLD_DIR=$(WORK_DIR)/gold
TREETAGGER_HOME=../tree-tagger
TREETAGGER=$(TREETAGGER_HOME)/cmd/tree-tagger-$(LANGUAGE)
SOCCER_IDS=extraction/resources/soccer_ids
GOLD_LU_NUM=10
DUMP=../$(LANGCODE)wiki-latest-pages-articles.xml.bz2
CL_MAIN_PACKAGE=org.fbk.cit.hlt.dirha
CL_JAVA_OPTS=-Dlog-config=supervised/classifier/log-config.txt -Xmx2G -Dfile.encoding=UTF-8 -cp supervised/classifier/target/fatJar.jar
CL_TRAINING_SET=supervised/resources/training.sample
CL_GAZETTEER=supervised/resources/it/soccer-gaz.tsv
CL_EVAL_OUTPUT=/tmp/classifierEvaluationOutput
CL_SENTENCES_FILE=$(WORK_DIR)/sample-50.txt
CL_OUTPUT=$(WORK_DIR)/sample-50-classified.txt
CL_CONF_OUTPUT=$(WORK_DIR)/sample-50-confidences.txt
CL_ANNOTATED_GOLD=
LINK_MODE=twm  # twm or nex
CF_RESULTS=resources/crowdflower-results.sample
SCORING_TYPE=f-score
FE_SCORE=both
SCORING_CORE_WEIGHT=2

default:
	@echo "Ciao"

extract-pages:
	mkdir -p $(WORK_DIR)
	bzcat $(DUMP) | python lib/WikiExtractor.py -o $(PAGES_DIR)
	find $(PAGES_DIR)/*/* -type f -exec cat '{}' \; > $(WORK_DIR)/all-articles.txt

extract-soccer:
	mkdir -p $(SOCCER_DIR)
	python extraction/get_soccer_ids.py $(SOCCER_IDS) --lang $(LANGCODE)
	python extraction/process_articles.py $(SOCCER_IDS) \
		$(WORK_DIR)/all-articles.txt $(SOCCER_DIR) \
		$(WORK_DIR)/wiki-id-to-title-mapping.json
	find $(SOCCER_DIR)/* -type f -exec cat '{}' \; > $(WORK_DIR)/all-soccer.txt

extract-verbs:
	cat $(WORK_DIR)/all-soccer.txt | $(TREETAGGER) | grep VER | grep -v '<unknown>' | \
		cut -f 1,3 | tr '[:upper:]' '[:lower:]' > $(WORK_DIR)/raw-verbs.txt
	sort -u $(WORK_DIR)/raw-verbs.txt -o $(WORK_DIR)/token2lemma.txt
	cut -f 1 $(WORK_DIR)/token2lemma.txt > $(WORK_DIR)/tokens.txt
	cut -f 2 $(WORK_DIR)/token2lemma.txt | sort -u -o $(WORK_DIR)/lemmas.txt
	python extraction/bag_of_words.py $(WORK_DIR)/all-soccer.txt \
		$(WORK_DIR)/vocabulary.txt

extract-sentences:
	mkdir -p $(SENTENCES_DIR) $(TAGGED_DIR)
	python extraction/extract_sentences.py $(WORK_DIR)/all-soccer.txt \
		resources/tokens.list $(WORK_DIR)/sentence-to-wikiid.json $(SENTENCES_DIR)
	find $(SENTENCES_DIR) -type f -exec sh -c 'echo $$1 && cat "$$1" | \
		$(TREETAGGER) > $(TAGGED_DIR)/$$(basename $$1) 2> /dev/null' 'extract' {} \;

rank-verbs:
	cut -f 2 $(WORK_DIR)/token2lemma.txt | python verb_ranking/make_lemma_freq.py - \
		$(WORK_DIR)/lemma-freq.json
	cut -d '"' -f 2 workspace-it/lemma-freq.json | grep -vP	\
		'avere|essere|fare|potere|volere|dovere' | sed -n '2,52'p | sort \
		> $(WORK_DIR)/top-50-lemmas.txt
	grep -wf $(WORK_DIR)/top-50-lemmas.txt $(WORK_DIR)/token2lemma.txt | sort -u \
		> $(WORK_DIR)/top-50-tokens.txt
	grep -wf $(WORK_DIR)/top-50-lemmas.txt $(WORK_DIR)/token2lemma.txt \
		> $(WORK_DIR)/top-50-token2lemma.txt
	python verb_ranking/tf_idfize.py $(SOCCER_DIR) $(WORK_DIR)/top-50-tokens.txt \
		--variance-out $(WORK_DIR)/verbs-variance.json \
		--stdevs-out $(WORK_DIR)/verbs-stdev.json \
		--threshold-rank-out $(WORK_DIR)/verbs-rank-threshold.json \
		--tfidf-rank-out $(WORK_DIR)/verbs-tfidf-rank.json
	python verb_ranking/compute_stdev_by_lemma.py $(WORK_DIR)/top-50-token2lemma.txt \
		$(WORK_DIR)/verbs-stdev.json $(WORK_DIR)/lemma-stdev.json

gold-add:
	mkdir -p $(GOLD_DIR)/$(LU)/sentences $(GOLD_DIR)/$(LU)/gold
	grep -w $(LU) $(WORK_DIR)/top-50-token2lemma.txt | cut -f 1 \
		> $(GOLD_DIR)/$(LU)/tokens.txt
	python extraction/extract_sentences.py $(WORK_DIR)/all-soccer.txt \
		$(GOLD_DIR)/$(LU)/tokens.txt $(GOLD_DIR)/$(LU)/sentences \
		--min-words 5 --max-words 15
	python seed_selection/get_meaningful_sentences.py $(TAGGED_DIR) \
		$(GOLD_DIR)/$(LU)/tokens.txt $(GOLD_DIR)/$(LU)/gold

gold-finalize:
	mkdir -p $(GOLD_DIR)/sentences
	find $(GOLD_DIR)/*/gold/* | shuf | head -n $(GOLD_LU_NUM) | xargs -i cp {} \
		$(GOLD_DIR)/sentences/
	find $(GOLD_DIR)/gold/* -type f -exec sh -c 'echo $$(basename $$1); cat $$1; echo' \
        _ "{}" \; | head -n 100 > $(WORK_DIR)/sample-50.txt

supervised-build-classifier:
	cd supervised/classifier && mvn compile assembly:assembly

supervised-learn-roles:
	java $(CL_JAVA_OPTS) $(CL_MAIN_PACKAGE).SpreadSheetToRoleTrainingSet \
		-t $(CL_TRAINING_SET)
	java $(CL_JAVA_OPTS) $(CL_MAIN_PACKAGE).RoleTrainingSetToLibsvm \
		-t $(CL_TRAINING_SET).iob2 -g $(CL_GAZETTEER)
	svm-train -t 0 -m 10000 $(CL_TRAINING_SET).iob2.svm $(CL_TRAINING_SET).iob2.model

supervised-learn-frames:
	java $(CL_JAVA_OPTS) $(CL_MAIN_PACKAGE).SpreadSheetToFrameTrainingSet \
		-t $(CL_TRAINING_SET) 
	java $(CL_JAVA_OPTS) $(CL_MAIN_PACKAGE).FrameTrainingSetToLibsvm \
		-t $(CL_TRAINING_SET).frame -g $(CL_GAZETTEER)
	svm-train -t 0 -m 10000 $(CL_TRAINING_SET).frame.svm $(CL_TRAINING_SET).frame.model

supervised-run-interactive:
	java $(CL_JAVA_OPTS) -Dtreetagger.home=$(TREETAGGER_HOME) \
		$(CL_MAIN_PACKAGE).Annotator -g $(CL_GAZETTEER) -m $(CL_TRAINING_SET) \
		-l $(LANGCODE) -i

supervised-run-batch:
	java $(CL_JAVA_OPTS) -Dtreetagger.home=$(TREETAGGER_HOME) \
		$(CL_MAIN_PACKAGE).Annotator -g $(CL_GAZETTEER) -m $(CL_TRAINING_SET) \
		-l $(LANGCODE) -r $(CL_EVAL_OUTPUT)  -a $(CL_SENTENCES_FILE) \
		-o $(CL_OUTPUT) -c $(CL_CONF_OUTPUT)

supervised-evaluate:
	ifndef CL_ANNOTATED_GOLD $(error CL_ANNOTATED_GOLD is not set) endif
	java $(CL_JAVA_OPTS) -Dtreetagger.home=$(TREETAGGER_HOME) \
		$(CL_MAIN_PACKAGE).Annotator -g $(CL_GAZETTEER) -m $(CL_TRAINING_SET) \
		-l $(LANGCODE) -r $(CL_EVAL_OUTPUT) -a $(CL_SENTENCES_FILE) \
		-e $(CL_ANNOTATED_GOLD)

supervised-results-to-assertions:
	python supervised/produce_triples.py $(CL_OUTPUT) \
		$(WORK_DIR)/sentence-to-wikiid.json $(WORK_DIR)/wiki-id-to-title-mapping.json \
		$(WORK_DIR)/supervised-triples.nt $(WORK_DIR)/supervised-scores.nt --format nt \
        --sentence-score $(SCORING_TYPE) --core-weight $(SCORING_CORE_WEIGHT) \
        --score-fes --fe-score $(FE_SCORE) --format nt


crowdflower-create-input:
	# TODO generate twm ngrams and textpro chunks somehow
	mkdir -p $(WORK_DIR)/linked
	python lib/entity_linking.py $(LINK_MODE) $(GOLD_DIR)/sentences $(WORK_DIR)/linked
	python unsupervised/produce_labeled_data.py $(WORK_DIR)/linked \
		$(WORK_DIR)/labeled_data.json
	# TODO change combine_chunks so that you can specify where to get individual parts
	mv $(WORK_DIR)/linked resources/twm-links
	python crowdflower/combine_chunks.py resources/ $(WORK_DIR)/chunks.json
	python crowdflower/create_crowdflower_input.py resources/labeled_data.sample \
		$(WORK_DIR)/chunks.json -o $(WORK_DIR)/crowdflower_input.csv
	python crowdflower/generate_crowdflower_interface_template.py \
		$(WORK_DIR)/crowdflower_input.csv $(WORK_DIR)/crowdflower_template.html

crowdflower-to-training:
	python crowdflower/crowdflower_results_into_training_data.py $(CF_RESULTS) \
		$(TAGGED_DIR) $(WORK_DIR)/training-data.tsv

run-unsupervised:
	# you need to run extract-soccer before
	mkdir -p $(WORK_DIR)/unsupervised/linked
	python lib/entity_linking.py $(LINK_MODE) $(SOCCER_DIR) \
		$(WORK_DIR)/unsupervised/linked
	python unsupervised/produce_labeled_data.py $(WORK_DIR)/unsupervised/linked \
		$(WORK_DIR)/labeled_data.json --score $(SCORING_TYPE) \
        --core-weight $(SCORING_CORE_WEIGHT) --score-fes
	python unsupervised/labeled_to_assertions.py $(WORK_DIR)/labeled_data.json \
		$(WORK_DIR)/wiki-id-to-title-mapping.json $(WORK_DIR)/unsupervised/processed \
		$(WORK_DIR)/unsupervised/discarded $(WORK_DIR)/unsupervised/dataset.nt
