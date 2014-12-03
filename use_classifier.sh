# Tokenize + POS tag a file with raw sentences into a tsv ready for annotation
java -Dfile.encoding=UTF-8 -Dtreetagger.home=/home/fox/srl/treetagger -Dtreetagger.model=/home/fox/srl/treetagger/lib/italian-utf8.par -cp fatJar.jar org.fbk.cit.hlt.dirha.SentencesToSpreadSheet ../../training/itwiki/gold test.out 0 10
# Translate a tsv annotation file into IOB2 format
java -Dfile.encoding=UTF-8 -cp target/fatJar.jar org.fbk.cit.hlt.dirha.SpreadSheetToRoleTrainingSet -t data/whole-train/20140616/whole-train.tab
# Produce role training data for libsvm
java -Dfile.encoding=UTF-8 -cp target/fatJar.jar org.fbk.cit.hlt.dirha.RoleTrainingSetToLibsvm -t data/whole-train/20140616/whole-train.tab.iob2 -g resources/gazetteer.tsv
# Translate a tsv annotation file into text categorization format
java -Dfile.encoding=UTF-8 -cp target/fatJar.jar org.fbk.cit.hlt.dirha.SpreadSheetToFrameTrainingSet -t data/whole-train/whole-train.tab
# Produce frame training data for libsvm
java -Dfile.encoding=UTF-8 -cp target/fatJar.jar org.fbk.cit.hlt.dirha.FrameTrainingSetToLibsvm -t data/whole-train/whole-train.tab.frame -g resources/gazetteer.tsv
# Train role classifier
svm-train -t 0 -m 10000 data/whole-train/20140616/whole-train.tab.svm data/whole-train/20140616/whole-train.tab.model
#Train frame classifier
svm-train -t 0 -m 10000 data/whole-train/20140821/whole-train.tab.frame.svm data/whole-train/20140821/whole-train.tab.frame.model
# Run classifier in Italian, interactive mode
java -Dfile.encoding=UTF-8 -Dtreetagger.home=/home/fox/srl/treetagger -cp target/fatJar.jar org.fbk.cit.hlt.dirha.Annotator -g resources/it/gazetteer.tsv -m data/whole-train/20140616/whole-train.tab -i -l it
