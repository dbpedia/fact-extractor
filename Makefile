LANGCODE=it
LANGUAGE=italian
WORK_DIR=./workspace-$(LANGCODE)
PAGES_DIR=$(WORK_DIR)/pages
SOCCER_DIR=$(WORK_DIR)/soccer
SENTENCES_DIR=$(WORK_DIR)/sentences
TAGGED_DIR=$(WORK_DIR)/tagged
SAMPLE_DIR=$(WORK_DIR)/samples
TREETAGGER_HOME=../tree-tagger
TREETAGGER=$(TREETAGGER_HOME)/cmd/tree-tagger-$(LANGUAGE)
SOCCER_IDS=extraction/resources/soccer_ids
SAMPLE_LU_NUM=10
SENTENCES_MIN_WORDS=5
SENTENCES_MAX_WORDS=25
DUMP=../$(LANGCODE)wiki-latest-pages-articles.xml.bz2
CL_MAIN_PACKAGE=org.fbk.cit.hlt.dirha
CL_JAVA_OPTS=-Dlog-config=supervised/classifier/log-config.txt -Xmx2G -Dfile.encoding=UTF-8 -cp supervised/classifier/target/fatJar.jar
CL_TRAINING_SET=supervised/resources/training.sample
CL_GAZETTEER=supervised/resources/it/dbpedia-gaz.tsv
CL_SENTENCES_FILE=$(WORK_DIR)/sample-50.txt
CL_OUTPUT=$(WORK_DIR)/sample-50-classified.txt
CL_ANNOTATED_GOLD=resources/gold-standard.final
CL_SVM_TRAIN_ARGS=-b 1 -t 0 -m 6000 -s 0
LINK_MODE=twm  # twm or nex
MIN_LINK_CONFIDENCE=0.01
CF_RESULTS=resources/crowdflower-results.sample
SCORING_TYPE=weighted-mean
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
		resources/tokens.list $(WORK_DIR)/sentence-to-wikiid.json $(SENTENCES_DIR) \
        --min-words $(SENTENCES_MIN_WORDS) --max-words $(SENTENCES_MAX_WORDS)
	find $(SENTENCES_DIR) -type f | xargs -I{} -P 4 sh -c \
		'echo {} && $(TREETAGGER) {} > $(TAGGED_DIR)/$$(basename {}) 2> /dev/null';

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

sample-add:
	if [ -z "$(LU)" ]; then echo "Error: LU not set" && exit 1; fi
	mkdir -p $(SAMPLE_DIR)/$(LU)/all-sentences $(SAMPLE_DIR)/$(LU)/tagged \
		$(SAMPLE_DIR)/$(LU)/meaningful
	grep -w $(LU) $(WORK_DIR)/top-50-token2lemma.txt | cut -f 1 \
		> $(SAMPLE_DIR)/$(LU)/tokens.txt
	python extraction/extract_sentences.py $(WORK_DIR)/all-soccer.txt \
		$(SAMPLE_DIR)/$(LU)/tokens.txt $(SAMPLE_DIR)/$(LU)/title-to-wid.json \
		$(SAMPLE_DIR)/$(LU)/all-sentences --min-words $(SENTENCES_MIN_WORDS) \
		--max-words $(SENTENCES_MAX_WORDS)
	python seed_selection/get_meaningful_sentences.py $(TAGGED_DIR) \
		$(SAMPLE_DIR)/$(LU)/tokens.txt $(SAMPLE_DIR)/$(LU)/meaningful
	find $(SAMPLE_DIR)/$(LU)/all-sentences -type f | xargs -I{} -P 4 sh -c 'echo {} && \
		$(TREETAGGER) {} > $(SAMPLE_DIR)/$(LU)/tagged/$$(basename {}) 2> /dev/null';


sample-finalize:
	mkdir -p $(SAMPLE_DIR)/sentences
	find $(SAMPLE_DIR)/*/sample/* | shuf | head -n $(SAMPLE_LU_NUM) | xargs -i cp {} \
		$(SAMPLE_DIR)/sentences/
	find $(SAMPLE_DIR)/*/sample/* -type f | head -n 100 | xargs -I{} sh -c \
		'echo $$(basename {}); cat {}; echo' > $(WORK_DIR)/sample-50.txt

supervised-build-classifier:
	cd supervised/classifier && mvn compile assembly:assembly

supervised-learn-roles:
	java $(CL_JAVA_OPTS) $(CL_MAIN_PACKAGE).RoleTrainingSetToLibSvm \
		-t $(CL_TRAINING_SET) -g $(CL_GAZETTEER)
	svm-train $(CL_SVM_TRAIN_ARGS) $(CL_TRAINING_SET).iob2.svm \
        $(CL_TRAINING_SET).iob2.model

supervised-learn-frames:
	java $(CL_JAVA_OPTS) $(CL_MAIN_PACKAGE).FrameTrainingSetToLibSvm \
		-t $(CL_TRAINING_SET) -g $(CL_GAZETTEER)
	svm-train $(CL_SVM_TRAIN_ARGS) $(CL_TRAINING_SET).frame.svm \
        $(CL_TRAINING_SET).frame.model

supervised-run-interactive:
	java $(CL_JAVA_OPTS) -Dtreetagger.home=$(TREETAGGER_HOME) \
		$(CL_MAIN_PACKAGE).Annotator -g $(CL_GAZETTEER) -m $(CL_TRAINING_SET) \
		-l $(LANGCODE) -i -n

supervised-run-batch:
	python date_normalizer/rpc.py 2>/dev/null &
	java $(CL_JAVA_OPTS) -Dtreetagger.home=$(TREETAGGER_HOME) \
		$(CL_MAIN_PACKAGE).Annotator -g $(CL_GAZETTEER) -m $(CL_TRAINING_SET) \
		-l $(LANGCODE) -r $(CL_SENTENCES_FILE).eval  -a $(CL_SENTENCES_FILE) \
		-o $(CL_OUTPUT) -n

supervised-evaluate:
	python date_normalizer/rpc.py 2>/dev/null &
	java $(CL_JAVA_OPTS) -Dtreetagger.home=$(TREETAGGER_HOME) \
		$(CL_MAIN_PACKAGE).Annotator -g $(CL_GAZETTEER) -m $(CL_TRAINING_SET) \
		-l $(LANGCODE) -r $(CL_ANNOTATED_GOLD).report \
        -a $(CL_ANNOTATED_GOLD).sentences -e $(CL_ANNOTATED_GOLD) \
        -r $(CL_ANNOTATED_GOLD).report -o $(CL_ANNOTATED_GOLD).classified -n

supervised-results-to-assertions:
	python supervised/produce_triples.py $(CL_OUTPUT) \
        $(WORK_DIR)/wiki-id-to-title-mapping.json $(CL_OUTPUT).triples.nt \
        $(CL_OUTPUT).triples.scores.nt --format nt --sentence-score $(SCORING_TYPE) \
        --core-weight $(SCORING_CORE_WEIGHT) --fe-score $(FE_SCORE) --format nt

supervised-plot-results:
	python supervised/plot.py $(CL_ANNOTATED_GOLD).report.frames.confusion.csv roc &
	python supervised/plot.py $(CL_ANNOTATED_GOLD).report.frames.confusion.csv confpr &
	python supervised/plot.py $(CL_ANNOTATED_GOLD).report.roles.confusion.csv roc &
	python supervised/plot.py $(CL_ANNOTATED_GOLD).report.roles.confusion.csv confpr &

crowdflower-create-input:
	# TODO generate twm ngrams and textpro chunks somehow
	mkdir -p $(WORK_DIR)/linked
	python lib/entity_linking.py $(LINK_MODE) $(SAMPLE_DIR)/sentences $(WORK_DIR)/linked
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
		$(TAGGED_DIR) $(WORK_DIR)/training-data.tsv -d

run-unsupervised:
	# you need to run extract-soccer before
	mkdir -p $(WORK_DIR)/unsupervised/linked
	python lib/entity_linking.py -d -c $(MIN_LINK_CONFIDENCE) $(LINK_MODE) $(SOCCER_DIR) \
		$(WORK_DIR)/unsupervised/linked
	python unsupervised/produce_labeled_data.py $(WORK_DIR)/unsupervised/linked \
		$(WORK_DIR)/labeled_data.json --score $(SCORING_TYPE) \
        --core-weight $(SCORING_CORE_WEIGHT) --score-fes
	python unsupervised/labeled_to_assertions.py $(WORK_DIR)/labeled_data.json \
		$(WORK_DIR)/wiki-id-to-title-mapping.json $(WORK_DIR)/unsupervised/processed \
		$(WORK_DIR)/unsupervised/discarded $(WORK_DIR)/unsupervised/dataset.nt

evaluate-unsupervised:
	mkdir -p $(WORK_DIR)/unsupervised/evaluation/{linked,sentences}
	i=0; while read f; do printf -v j "%04d" $$i; echo $$f > $(WORK_DIR)/unsupervised/evaluation/sentences/$$j; let i++; done < $(GOLD_SENTENCES)
	python lib/entity_linking.py -d -c $(MIN_LINK_CONFIDENCE) $(LINK_MODE) \
		$(WORK_DIR)/unsupervised/evaluation/sentences \
		$(WORK_DIR)/unsupervised/evaluation/linked
	python unsupervised/produce_labeled_data.py $(WORK_DIR)/unsupervised/evaluation/linked \
		$(WORK_DIR)/unsupervised/evaluation/test_data.json --score $(SCORING_TYPE) \
        --core-weight $(SCORING_CORE_WEIGHT) --score-fes
	python unsupervised/evaluate.py $(WORK_DIR)/unsupervised/evaluation/test_data.json $(GOLD_STANDARD) --partial
