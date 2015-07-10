# coding: utf-8
import codecs
from sys import argv, exit

from nltk.tokenize.punkt import PunktTrainer, PunktSentenceTokenizer

if len(argv) != 3:
    print "Usage: %s <TRAINING_CORPUS> <SENTENCES_TO_SPLIT>" % __file__
    exit(1)

training = ''.join(codecs.open(argv[1], 'rb', 'utf-8').readlines())
trainer = PunktTrainer()
trainer.train(training, verbose=True)
tokenizer = PunktSentenceTokenizer(trainer.get_params(), verbose=True)
text = ''.join(codecs.open(argv[2], 'rb', 'utf-8').readlines())
sentences = tokenizer.tokenize(text)
codecs.open('split', 'wb', 'utf-8').writelines([s + '\n' for s in sentences])
