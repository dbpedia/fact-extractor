# coding: utf-8
import codecs
import sys

from nltk.tokenize.punkt import PunktTrainer, PunktSentenceTokenizer
training = ''.join(codecs.open('IT-TrainingCorpus.txt', 'rb', 'utf-8').readlines())
trainer = PunktTrainer()
trainer.train(training, verbose=True)
tokenizer = PunktSentenceTokenizer(trainer.get_params(), verbose=True)
text = ''.join(codecs.open(sys.argv[1], 'rb', 'utf-8').readlines())
sentences = tokenizer.tokenize(text)
clean = [s for s in sentences if s.find('<strong>') != -1]
codecs.open('clean-gold', 'wb', 'utf-8').writelines([s + '\n' for s in clean])
