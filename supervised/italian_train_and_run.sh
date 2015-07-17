#!/bin/bash

set -e

usage="Usage: $(basename "$0") <TRAINING_SET> <GAZETTEER> [SENTENCES_FILE] [ANNOTATED_GOLD_FILE] [EVALUATION_OUTPUT] [TREETAGGER_HOME_DIR]"
if [[ $# -lt 2 ]]; then
    echo $usage
    exit 1
fi

# Ensure all paths are absolute
TRAINING_SET=$(readlink -f "$1")
GAZETTEER=$(readlink -f "$2")
if [[ -n ${3+x} ]]; then
    SENTENCES_FILE=$(readlink -f "$3")
fi
if [[ -n ${4+x} ]]; then
    ANNOTATED_GOLD_FILE=$(readlink -f "$4")
fi
if [[ -n ${5+x} ]]; then
    EVALUATION_OUTPUT=$(readlink -f "$5")
fi
if [[ -n ${6+x} ]]; then
    TREETAGGER_HOME=$(readlink -f "$6")
fi

TREETAGGER_MODEL=${TREETAGGER_HOME}/lib/italian-utf8.par
JAVA_OPTS="-Dlog-config=classifier/log-config.txt -Xmx2G -Dfile.encoding=UTF-8 -cp classifier/target/fatJar.jar"
MAIN_PACKAGE="org.fbk.cit.hlt.dirha"

# Minimal java arguments to launch the classifier
CLASSIFIER_ARGS="-Dtreetagger.home=$TREETAGGER_HOME $JAVA_OPTS ${MAIN_PACKAGE}.Annotator -g $GAZETTEER -m ${TRAINING_SET} -l it "
# Batch mode if a sentences file is provided, otherwise interactive mode
if [[ -n "$SENTENCES_FILE" ]]; then
    CLASSIFIER_ARGS+="-a ${SENTENCES_FILE} "
else
    CLASSIFIER_ARGS+="-i"
fi
# Evaluation if an annotated gold file is provided
if [[ -n "$ANNOTATED_GOLD_FILE" ]] ; then
    CLASSIFIER_ARGS+="-e ${ANNOTATED_GOLD_FILE} "
fi
# Write evaluation report to a specific file if provided
if [[ -n "$EVALUATION_OUTPUT" ]] ; then
    CLASSIFIER_ARGS+="-r ${EVALUATION_OUTPUT}"
fi

echo "training set: $TRAINING_SET"
echo "gazetteer: $GAZETTEER"
echo "sentences file: $SENTENCES_FILE"
echo "annotated gold file: $ANNOTATED_GOLD_FILE"
echo "evaluation output: $EVALUATION_OUTPUT"
echo "treetagger home: $TREETAGGER_HOME"
echo "classifier args: $CLASSIFIER_ARGS"

# Tokenize + POS tag a file with raw sentences into a tsv ready for annotation
#java -Dfile.encoding=UTF-8 -Dtreetagger.home=$TREETAGGER_HOME -Dtreetagger.model=$TREETAGGER_MODEL -cp target/fatJar.jar $MAIN_PACKAGE.SentencesToSpreadSheet ../../training/itwiki/gold test.out 0 10
echo
echo "------------------------------------------"
echo "Learning roles ..."
echo "------------------------------------------"
echo
# Translate a tsv annotation file into IOB2 format
java $JAVA_OPTS ${MAIN_PACKAGE}.SpreadSheetToRoleTrainingSet -t $TRAINING_SET
# Produce role training data for libsvm
java $JAVA_OPTS ${MAIN_PACKAGE}.RoleTrainingSetToLibsvm -t ${TRAINING_SET}.iob2 -g $GAZETTEER
# Train role classifier
svm-train -t 0 -m 10000 ${TRAINING_SET}.iob2.svm ${TRAINING_SET}.iob2.model
echo
echo "------------------------------------------"
echo "Learning frames ..."
echo "------------------------------------------"
echo
# Translate a tsv annotation file into text categorization format
java $JAVA_OPTS ${MAIN_PACKAGE}.SpreadSheetToFrameTrainingSet -t $TRAINING_SET 
# Produce frame training data for libsvm
java $JAVA_OPTS ${MAIN_PACKAGE}.FrameTrainingSetToLibsvm -t ${TRAINING_SET}.frame -g $GAZETTEER
# Train frame classifier
svm-train -t 0 -m 10000 ${TRAINING_SET}.frame.svm ${TRAINING_SET}.frame.model
echo
echo "------------------------------------------"
echo "Done! Launching classifier ..."
echo "------------------------------------------"
echo
java $CLASSIFIER_ARGS

