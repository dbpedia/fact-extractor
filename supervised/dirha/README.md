**Installation**
 1. Install the required offline dependency `mvn install:install-file -Dfile=jcore-alone.jar -DgroupId=org.fbk.cit.hlt -DartifactId=core -Dversion=1.0 -Dpackaging=jar -DgeneratePom=true`
 2. Compile and build fat jar `mvn compile assembly:assembly`

**Frames and annotation guidelines**

Frames and annotation guidelines available at https://docs.google.com/spreadsheet/ccc?key=0AoGh3TWKyYNPdHN3bmNTVmZuRGo5M0lYZlRzNDlVZHc&usp=drive_web#gid=15

**Training and test data**

train.tab 550 annotated sentences

test.tab  365 annotated sentences
- clean: `dirha_commands_audio_uniq.txt`
- noisy: `dirha_commands_audio_rec_output_example.txt` and `DIRHA_cmd_rev_noise_ov_Livingroom_SNR_*.out`


**Training**

train.tab + test.tab = 915 annotated sentences


**Sentences to spreadsheet**

This class takes as input a file with a sentence per line and returns
a file with the sentences tokenized/pos tagged/lemmatized that can be
annotated with the guidelines described at https://docs.google.com/spreadsheet/ccc?key=0AoGh3TWKyYNPdHN3bmNTVmZuRGo5M0lYZlRzNDlVZHc&usp=drive_web#gid=6

`java -Dfile.encoding=UTF-8 -Dtreetagger.home=${TREETAGGER_HOME} -Dtreetagger.model={TREETAGGER_MODEL_FILE} -cp target/fatJar.jar org.fbk.cit.hlt.dirha.SentencesToSpreadSheet fin fout start size`

**Sentences to mysql**

This class takes as input a file with a sentence per line and returns
a file with the sentences tokenized/pos tagged/lemmatized that can be
annotated with the guidelines described at https://docs.google.com/spreadsheet/ccc?key=0AoGh3TWKyYNPdHN3bmNTVmZuRGo5M0lYZlRzNDlVZHc&usp=drive_web#gid=6
using the Web interface designed by Alessio Palmero Aprosio.

`java -Dfile.encoding=UTF-8 -cp target/fatJar.jar org.fbk.cit.hlt.dirha.SentencesToMysql fin fout start size`


**Role Training**

This class takes as input a hand-crafted annotated file (*.tab) and returns a
file annotated in IOB2 format (4 columns: term POS lemma label) to train a role annotator.

`java -Dfile.encoding=UTF-8 -cp target/fatJar.jar org.fbk.cit.hlt.dirha.SpreadSheetToRoleTrainingSet -t data/whole-train/whole-train.tab`

This class takes as input a file in IOB2 format and a gazetteer and returns
3 files: (1) the example file in svmlib format; (2) the feature
file in tsv format; (c) the label file in tsv format

`java -Dfile.encoding=UTF-8 -cp target/fatJar.jar org.fbk.cit.hlt.dirha.RoleTrainingSetToLibsvm -t data/whole-train/whole-train.tab.iob2 -g resources/gazetteer.tsv`

Train the svm:

`time ~/Applications/libsvm-2.82/svm-train -t 0 -m 10000 data/whole-train/whole-train.tab.iob2.svm data/whole-train/whole-train.tab.iob2.model`

**Frame Training**

This class takes as input a hand-crafted annotated file (*.tab) and returns a
file annotated in text categorization format (4 colums: label tokenized and lemmatized sentence roles) to train a frame annotator.

`java -Dfile.encoding=UTF-8 -cp target/fatJar.jar org.fbk.cit.hlt.dirha.SpreadSheetToFrameTrainingSet -t data/whole-train/whole-train.tab`

This class takes as input a file in text categorization format and a gazetteer and returns
3 files: (1) the example file in svmlib format; (2) the feature
file in tsv format; (c) the label file in tsv format

`java -Dfile.encoding=UTF-8 -cp target/fatJar.jar org.fbk.cit.hlt.dirha.FrameTrainingSetToLibsvm -t data/whole-train/whole-train.tab.frame -g resources/gazetteer.tsv`


Train the svm:
`time ~/Applications/libsvm-2.82/svm-train -t 0 -m 10000 frasi-complete-0-100-400-100-claudio.tab.frame.svm frasi-complete-0-100-400-100-claudio.tab.frame.mdl`


**Classification and evaluation**

This class can annotate sentences using the two models (role and frame) learnt in the previous steps
It can be used in interactive mode (shell), batch (process a file one sentence per line)

`java -Dfile.encoding=UTF-8 -cp target/fatJar.jar org.fbk.cit.hlt.dirha.Annotator -a dirha/data-train-test/dirha_commands_audio_uniq.txt -g gazetteer.tsv -o nuova-prova.tsv -m dirha/data-train-test/train.tab`

# Italian, interactive
`java -Dfile.encoding=UTF-8 -Dtreetagger.home=${TREETAGGER_HOME} -cp target/fatJar.jar org.fbk.cit.hlt.dirha.Annotator -g resources/it/gazetteer.tsv -m data/whole-train/201406/whole-train.tab -i -l it`

Client/server polibio:

- dirha `java -Dtreetagger.home=/home/giuliano/Applications/treetagger/ -Dfile.encoding=UTF-8 -cp target/fatJar.jar org.fbk.cit.hlt.dirha.Annotator -g resources/gazetteer.tsv -m data/whole-train/whole-train.tab --trace -s`

- dirha-2.0 `java -Dtreetagger.home=/home/giuliano/Applications/treetagger/ -Dfile.encoding=UTF-8 -cp target/fatJar.jar org.fbk.cit.hlt.dirha.Annotator -g resources/gazetteer.tsv -m data/whole-train/20140313/whole-train.tab --trace -s --host polibio --port 8080`

(su hlt-services6)

`java -Dtreetagger.home=/data/dirha/treetagger/ -Dfile.encoding=UTF-8 -cp target/fatJar.jar org.fbk.cit.hlt.dirha.Annotator -g resources/gazetteer.tsv -m data/whole-train/20140616/whole-train.tab --trace -s --port 9999 &> logs-20140617.log &`


de:

`java -Dfile.encoding=UTF-8 -cp target/fatJar.jar org.fbk.cit.hlt.dirha.Annotator -g resources/de/gazetteer.tsv -i -m data/annotation-migration/de/20140930/whole-training.tsv --trace -l de`

pos
`java -Dfile.encoding=UTF-8 -Dtreetagger.home=/data/dirha/treetagger/ -cp target/fatJar.jar org.fbk.cit.hlt.dirha.PosTagger "Noi siamo persone pulite" it`


**Annotation Migration**

`java -Dfile.encoding=UTF-8 -cp target/fatJar.jar org.fbk.cit.hlt.dirha.SpreadSheetToSentencesToBeTranslated ...`
en:

`java -Dfile.encoding=UTF-8 -cp target/fatJar.jar org.fbk.cit.hlt.dirha.TranslatedSentencesToSpreadSheet data/annotation-migration/de/de-sentences-fixed-martin.tsv data/annotation-migration/en/en-unlabelled-whole-training-fixed-claudio.tsv en`

`java -Dfile.encoding=UTF-8 -cp target/fatJar.jar org.fbk.cit.hlt.dirha.AnnotationMigration -l data/annotation-migration/from-it.reference-annotation.tsv -o /dev/null -r data/annotation-migration/en/it-en-terms.tsv -u data/annotation-migration/en/en-unlabelled-whole-training-fixed-claudio.tsv`


de:

`java -Dfile.encoding=UTF-8 -cp target/fatJar.jar org.fbk.cit.hlt.dirha.TranslatedSentencesToSpreadSheet data/annotation-migration/de/de-sentences-fixed-martin.tsv data/annotation-migration/de/de-unlabelled-whole-training-fixed-martin.tsv de`

`java -Dfile.encoding=UTF-8 -cp target/fatJar.jar org.fbk.cit.hlt.dirha.AnnotationMigration -l data/annotation-migration/from-it.reference-annotation.tsv -o data/annotation-migration/de/de-whole-training-fixed-martin.tsv -r data/annotation-migration/de/it-de-terms.tsv -u data/annotation-migration/de/de-unlabelled-whole-training-fixed-martin.tsv --info`
