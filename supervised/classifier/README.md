# Supervised classifier
The [Makefile](../../Makefile) is responsible for handling all the tasks, from compilation to evaluation.
Just make sure you are in the project root directory!

## Installation
First check if you have installed [libsvm](http://www.csie.ntu.edu.tw/~cjlin/libsvm/), then:
```
make supervised-build-classifier
```

## Training set format
A TSV file as per [the sample](../resources/training.sample):
```
1200	0	Cresciuto	VER:pper	crescere	Attività	O
1200	1	nel	PRE:det	nel	Attività	O
1200	2	Como	NPR	Como	Attività	Squadra
1200	3	dove	PRO:rela	dove	Attività	O
1200	4	esordisce	VER:pres	esordire	Attività	LU
1200	5	in	PRE	in	Attività	O
1200	6	Serie C1	ENT	Serie C1	Attività	Competizione
1200	7	a	PRE	a	Attività	O
1200	8	17	NUM	@card@	Attività	O
1200	9	anni	NOM	anno	Attività	O
1200	10	nella	PRE:det	nel	Attività	O
1200	11	stagione	NOM	stagione	Attività	O
1200	12	1999-2000	NUM	@card@	Attività	O
1200	13	.	SENT	.	Attività	O
```

## Train
**N.B.:** If no training set file is specified with the `CL_TRAINING_SET` variable, it will train with [this sample](../resources/training.sample).

1. Learn roles
```
make supervised-learn-roles
```
2. Learn frames
```
make supervised-learn-frames
```

## Run
**N.B.:** If no training set file is specified with the `CL_TRAINING_SET` variable, it will use the model trained with [this sample](../resources/training.sample).
1. Interactive mode: type a sentence and classify it
```
make supervised-run-interactive
```

2. Batch mode: classify a set of sentences, given one per line in a plain text file
```
make supervised-run-batch CL_SENTENCES_FILE=your_sentences_file_here
```

## Evaluate against the [gold-standard](../../resources/gold-standard.final)
```
make supervised-evaluate
```
