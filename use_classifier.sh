#!/bin/bash

set -e

usage="Usage: $(basename "$0") <> <> <>"
if [[ $# -ne 3 ]]; then
    echo $usage
    exit 1;
fi

TREETAGGER_HOME=$1
TREETAGGER_MODEL=$1/lib/italian-utf8.par
ANNOTATION_FILE=$2
JAVA_OPTS="-Dfile.encoding=UTF-8 -cp target/fatJar.jar"
MAIN_PACKAGE="org.fbk.cit.hlt.dirha"
GAZETTEER_FILE="resources/it/gazetteer.tsv"

# Tokenize + POS tag a file with raw sentences into a tsv ready for annotation
#java -Dfile.encoding=UTF-8 -Dtreetagger.home=$TREETAGGER_HOME -Dtreetagger.model=$TREETAGGER_MODEL -cp target/fatJar.jar $MAIN_PACKAGE.SentencesToSpreadSheet ../../training/itwiki/gold test.out 0 10
echo "Learning roles ..."
# Translate a tsv annotation file into IOB2 format
java $JAVA_OPTS ${MAIN_PACKAGE}.SpreadSheetToRoleTrainingSet -t $ANNOTATION_FILE
# Produce role training data for libsvm
java $JAVA_OPTS ${MAIN_PACKAGE}.RoleTrainingSetToLibsvm -t ${ANNOTATION_FILE}.iob2 -g $GAZETTEER_FILE
# Train role classifier
svm-train -t 0 -m 10000 ${ANNOTATION_FILE}.svm ${ANNOTATION_FILE}.model
echo "Learning frames ..."
# Translate a tsv annotation file into text categorization format
java $JAVA_OPTS ${MAIN_PACKAGE}.SpreadSheetToFrameTrainingSet -t $ANNOTATION_FILE 
# Produce frame training data for libsvm
java $JAVA_OPTS ${MAIN_PACKAGE}.FrameTrainingSetToLibsvm -t ${ANNOTATION_FILE}.frame -g $GAZETTEER_FILE
# Train frame classifier
svm-train -t 0 -m 10000 ${ANNOTATION_FILE}.frame.svm ${ANNOTATION_FILE}.frame.model
echo "Done! Launching classifier ..."
# Run classifier in Italian, interactive mode
java $JAVA_OPTS $TREETAGGER_HOME ${MAIN_PACKAGE}.Annotator -g $GAZETTEER_FILE -m ${ANNOTATION_FILE} -l it -i
