# coding: utf-8

import codecs
import pickle
import click
import os
import re
from nltk.tokenize.punkt import PunktSentenceTokenizer


@click.command()
@click.argument('serialized-tokenizer', type=click.File('r'))
@click.argument('input-dir', type=click.Path(exists=True, file_okay=False))
@click.argument('output-dir', type=click.Path(exists=True, file_okay=False))
@click.option('--min-length', '-l', default=25, help='Min length in chars')
def main(serialized_tokenizer, input_dir, output_dir, min_length):
    """
    this script walks a directory and splits the articles found into sentences
    using the nltk punkt tokenizer
    assumes one article per file, the sentences are saved one per file
    with name 'original_article_file_name.incremental_id'
    """
    tokenizer = pickle.load(serialized_tokenizer)
    for path, subdirs, files in os.walk(input_dir):
        for name in files:
            with open(os.path.join(path, name)) as f:
                rows = [x for x in f if '<doc' not in x and '</doc>' not in x]
                text = ''.join(rows).decode('utf8')

            sentences = [s for s in tokenizer.tokenize(text) if len(s) > min_length]
            print name, 'found', len(sentences), 'sentences'

            for i, sent in enumerate(sentences):
                with open(os.path.join(output_dir, '%s.%d' % (name, i)), 'w') as f:
                    f.write(sent.encode('utf8'))


if __name__ == '__main__':
    main()
