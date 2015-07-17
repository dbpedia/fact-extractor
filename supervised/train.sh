#!/bin/tcsh

if ($#argv == 0) then
	echo "usage: train.sh dir lang"
	exit(0)
endif

set dir = $argv[1]
set lang = $argv[2]
set libsvm = "libsvm-3.18"

echo "role learning"

echo "java -Dfile.encoding=UTF-8 -cp dist/dirha.jar org.fbk.cit.hlt.dirha.SpreadSheetToRoleTrainingSet -t ${dir}/whole-train.tsv"
time java -Dfile.encoding=UTF-8 -cp dist/dirha.jar org.fbk.cit.hlt.dirha.SpreadSheetToRoleTrainingSet -t ${dir}/whole-train.tsv

echo "java -Dfile.encoding=UTF-8 -cp dist/dirha.jar org.fbk.cit.hlt.dirha.RoleTrainingSetToLibsvm -t ${dir}/whole-train.tsv.iob2 -g resources/${lang}/gazetteer.tsv"
time java -Dfile.encoding=UTF-8 -cp dist/dirha.jar org.fbk.cit.hlt.dirha.RoleTrainingSetToLibsvm -t ${dir}/whole-train.tsv.iob2 -g resources/${lang}/gazetteer.tsv

echo "~/Applications/${libsvm}/svm-train -t 0 -m 10000 ${dir}/whole-train.tsv.iob2.svm ${dir}/whole-train.tsv.iob2.model"
time ~/Applications/${libsvm}/svm-train -t 0 -m 10000 ${dir}/whole-train.tsv.iob2.svm ${dir}/whole-train.tsv.iob2.model


echo "frame learning"

echo "java -Dfile.encoding=UTF-8 -cp dist/dirha.jar org.fbk.cit.hlt.dirha.SpreadSheetToFrameTrainingSet -t ${dir}/whole-train.tsv"
time java -Dfile.encoding=UTF-8 -cp dist/dirha.jar org.fbk.cit.hlt.dirha.SpreadSheetToFrameTrainingSet -t ${dir}/whole-train.tsv

echo "java -Dfile.encoding=UTF-8 -cp dist/dirha.jar org.fbk.cit.hlt.dirha.FrameTrainingSetToLibsvm -t ${dir}/whole-train.tsv.frame -g resources/${lang}/gazetteer.tsv"
time java -Dfile.encoding=UTF-8 -cp dist/dirha.jar org.fbk.cit.hlt.dirha.FrameTrainingSetToLibsvm -t ${dir}/whole-train.tsv.frame -g resources/${lang}/gazetteer.tsv


echo "~/Applications/${libsvm}/svm-train -t 0 -m 10000 ${dir}/whole-train.tsv.frame.svm ${dir}/whole-train.tsv.frame.model"
time ~/Applications/${libsvm}/svm-train -t 0 -m 10000 ${dir}/whole-train.tsv.frame.svm ${dir}/whole-train.tsv.frame.model
