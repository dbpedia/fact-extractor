LANGCODE=it
LANGUAGE=italian
WORK_DIR=./workspace-$(LANGCODE)
PAGES_DIR=$(WORK_DIR)/pages
SOCCER_DIR=$(WORK_DIR)/soccer
SENTENCES_DIR=$(WORK_DIR)/sentences
POS_TAGGED_DIR=$(WORK_DIR)/tagged
SUPERVISED_DIR=$(WORK_DIR)/supervised
UNSUPERVISED_DIR=$(WORK_DIR)/unsupervised
SAMPLE_DIR=$(WORK_DIR)/samples
TREETAGGER_HOME=../treetagger
TREETAGGER=$(TREETAGGER_HOME)/cmd/tree-tagger-$(LANGUAGE)
SOCCER_IDS=extraction/resources/soccer_ids
SAMPLE_LU_NUM=10
SENTENCES_MIN_WORDS=5
SENTENCES_MAX_WORDS=25
SPLITTER_MIN_CHARS=25
DUMP=../$(LANGCODE)wiki-latest-pages-articles.xml.bz2
CL_MAIN_PACKAGE=org.fbk.cit.hlt.dirha
CL_JAVA_OPTS=-Dlog-config=supervised/classifier/log-config.properties -Xmx2G -Dfile.encoding=UTF-8 -cp supervised/classifier/target/fatJar.jar
CL_TRAINING_SET=supervised/resources/training.sample
CL_GAZETTEER=supervised/resources/it/dbpedia-gaz.tsv
CL_SENTENCES_FILE=$(SUPERVISED_DIR)/all_sentences
CL_OUTPUT=$(CL_SENTENCES_FILE).classified
CL_ANNOTATED_GOLD=resources/gold-standard.final
CL_SVM_TRAIN_ARGS=-b 1 -t 0 -m 6000 -s 0
LINK_MODE=twm  # twm or nex
MIN_LINK_CONFIDENCE=0.01
CF_RESULTS=resources/crowdflower-results.sample
SCORING_TYPE=weighted-mean
FE_SCORE=both
SCORING_CORE_WEIGHT=2

default:
	@echo "Nothing to do. Please launch me with a target!"

extract-pages:
	mkdir -p $(WORK_DIR)
	bzcat $(DUMP) | python lib/WikiExtractor.py -o $(PAGES_DIR)
	find $(PAGES_DIR)/*/* -type f -exec cat '{}' \; > $(WORK_DIR)/all-articles.txt

extract-soccer:
	# must run extract-pages before
	mkdir -p $(SOCCER_DIR)
	python extraction/get_soccer_ids.py $(SOCCER_IDS) --lang $(LANGCODE)
	python extraction/process_articles.py $(SOCCER_IDS) \
		$(WORK_DIR)/all-articles.txt $(SOCCER_DIR) \
		$(WORK_DIR)/wiki-id-to-title-mapping.json
	find $(SOCCER_DIR)/* -type f -exec cat '{}' \; > $(WORK_DIR)/all-soccer.txt

extract-verbs:
	# must run extract-pages before
	cat $(WORK_DIR)/all-articles.txt | $(TREETAGGER) | grep VER | grep -v '<unknown>' | \
		cut -f 1,3 | tr '[:upper:]' '[:lower:]' > $(WORK_DIR)/raw-verbs.txt
	sort -u $(WORK_DIR)/raw-verbs.txt -o $(WORK_DIR)/token2lemma.txt
	cut -f 1 $(WORK_DIR)/token2lemma.txt > $(WORK_DIR)/tokens.txt
	cut -f 2 $(WORK_DIR)/token2lemma.txt | sort -u -o $(WORK_DIR)/lemmas.txt
	python extraction/bag_of_words.py $(WORK_DIR)/all-articles.txt \
		$(WORK_DIR)/vocabulary.txt

pos-tag:
	mkdir -p $(POS_TAGGED_DIR)
	find $(SENTENCES_DIR) -type f | xargs -I{} -P 4 sh -c 'echo {} && \
		$(TREETAGGER) {} > $(POS_TAGGED_DIR)/$$(basename {}) 2> /dev/null';

extract-sentences-baseline:
	# must run extract-soccer before
	mkdir -p $(SENTENCES_DIR)
	python extraction/extract_sentences.py $(WORK_DIR)/all-soccer.txt \
		resources/tokens.list $(WORK_DIR)/sentence-to-wikiid.json $(SENTENCES_DIR) \
        --min-words $(SENTENCES_MIN_WORDS) --max-words $(SENTENCES_MAX_WORDS)

extract-sentences-synctactic:
	# must run extract-sentences-baseline, pos-tag and rank-verbs before
	mkdir -p $(SENTENCES_DIR)
	python seed_selection/get_meaningful_sentences.py $(POS_TAGGED_DIR) \
		$(WORK_DIR)/top-50-tokens.txt $(SENTENCES_DIR)

extract-sentences-lexical:
	# must run extract-short-sentences and rank-verbs before
	mkdir -p $(SENTENCES_DIR)
	pyhon seed_selection/generate_lexicalizazion_patterns.py \
		$(WORK_DIR)/top-50-tokens.txt SoccerPlayer SoccerClub SoccerLeague \
        SoccerTournament SoccerLeagueSeason $(WORK_DIR)/lexicalizations
	sort -ou $(WORK_DIR)/lexicalizations
	find $(SHORT_DIR) -type f -exec sh -c 'echo $$1 && grep -irhwf \
		$(WORK_DIR)/lexicalizations $$1 | ifne "cat > $(SENTENCES_DIR)/$$(basename $$1)"' \
		'extract-sentences-lexical' '{}' \;

extract-sentences-splitter:
	# must run extract-soccer before
	mkdir -p $(SENTENCES_DIR)
	python seed_selection/split_sentences.py resources/italian-splitter.pickle \
		$(SOCCER_DIR) $(SENTENCES_DIR) --min-length $(SPLITTER_MIN_CHARS)

rank-verbs:
	# must run extract-verbs before
	cut -f 2 $(WORK_DIR)/token2lemma.txt | python verb_ranking/make_lemma_freq.py - \
		$(WORK_DIR)/lemma-freq.json
	cut -d '"' -f 2 workspace-it/lemma-freq.json | grep -vP	\
		'avere|essere|fare|potere|volere|dovere' | sed -n '2,52'p | sort \
		> $(WORK_DIR)/top-50-lemmas.txt
	grep -wf $(WORK_DIR)/top-50-lemmas.txt $(WORK_DIR)/token2lemma.txt | sort -u | \
		cut -f 1 > $(WORK_DIR)/top-50-tokens.txt
	grep -wf $(WORK_DIR)/top-50-lemmas.txt $(WORK_DIR)/token2lemma.txt \
		> $(WORK_DIR)/top-50-token2lemma.txt
	python verb_ranking/tf_idfize.py $(SOCCER_DIR) $(WORK_DIR)/top-50-tokens.txt \
		--variance-out $(WORK_DIR)/verbs-variance.json \
		--stdevs-out $(WORK_DIR)/verbs-stdev.json \
		--threshold-rank-out $(WORK_DIR)/verbs-rank-threshold.json \
		--tfidf-rank-out $(WORK_DIR)/verbs-tfidf-rank.json
	python verb_ranking/compute_stdev_by_lemma.py $(WORK_DIR)/top-50-token2lemma.txt \
		$(WORK_DIR)/verbs-stdev.json $(WORK_DIR)/lemma-stdev.json

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
	mkdir -p $(SUPERVISED_DIR)
	for s in $$(find $(SENTENCES_DIR) -type f); do echo $$(basename $$s) >> $(CL_SENTENCES_FILE); \
		cat $$s >> $(CL_SENTENCES_FILE); echo >> $(CL_SENTENCES_FILE); done
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
	python supervised/plot.py $(CL_ANNOTATED_GOLD).report.frames.confusion.csv \
        precall_bars &
	python supervised/plot.py $(CL_ANNOTATED_GOLD).report.frames.confusion.csv \
        precall_scatter &
	python supervised/plot.py $(CL_ANNOTATED_GOLD).report.frames.confusion.csv confmat &
	python supervised/plot.py $(CL_ANNOTATED_GOLD).report.roles.confusion.csv \
        precall_bars &
	python supervised/plot.py $(CL_ANNOTATED_GOLD).report.roles.confusion.csv \
        precall_scatter &
	python supervised/plot.py $(CL_ANNOTATED_GOLD).report.roles.confusion.csv confmat &

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

unsupervised-run:
	# you need to run extract-sentences-* before
	mkdir -p $(WORK_DIR)/unsupervised/linked
	python lib/entity_linking.py --debug -d -c $(MIN_LINK_CONFIDENCE) $(LINK_MODE) \
		$(SENTENCES_DIR) $(WORK_DIR)/unsupervised/linked
	python unsupervised/produce_labeled_data.py $(WORK_DIR)/unsupervised/linked \
		$(WORK_DIR)/labeled_data.json --score $(SCORING_TYPE) \
        --core-weight $(SCORING_CORE_WEIGHT) --score-fes
	python unsupervised/labeled_to_assertions.py $(WORK_DIR)/labeled_data.json \
		$(WORK_DIR)/wiki-id-to-title-mapping.json $(WORK_DIR)/unsupervised/processed \
		$(WORK_DIR)/unsupervised/discarded $(WORK_DIR)/unsupervised/dataset.nt

unsupervised-evaluate:
	mkdir -p $(WORK_DIR)/unsupervised/evaluation/{linked,sentences}
	i=0; while read f; do \
		printf -v j "%04d" $$i; \
		echo $$f > $(WORK_DIR)/unsupervised/evaluation/sentences/$$j; \
		let i++; \
	done < $(GOLD_SENTENCES)
	python lib/entity_linking.py -d -c $(MIN_LINK_CONFIDENCE) $(LINK_MODE) \
		$(WORK_DIR)/unsupervised/evaluation/sentences \
		$(WORK_DIR)/unsupervised/evaluation/linked
	python unsupervised/produce_labeled_data.py $(WORK_DIR)/unsupervised/evaluation/linked \
		$(WORK_DIR)/unsupervised/evaluation/test_data.json --score $(SCORING_TYPE) \
        --core-weight $(SCORING_CORE_WEIGHT) --score-fes
	python unsupervised/evaluate.py $(WORK_DIR)/unsupervised/evaluation/test_data.json \
		$(GOLD_STANDARD) --partial
