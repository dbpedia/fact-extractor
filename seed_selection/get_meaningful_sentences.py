#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import os
import sys
import click
from collections import defaultdict
from nltk import RegexpParser


CHUNKER_GRAMMAR = r"""
    SN: {<PRO.*|DET.*|>?<ADJ>*<NUM>?<NOM|NPR>+<NUM>?<ADJ|VER:pper>*}
    CHUNK: {<SN><VER.*>+<SN>}
    """


def load_pos_data(dir):
    """ walks the directory and loads the sentence's POS tagged data

    :param str dir: The directory with the POS data
    :return: Dictionary with POS data for each file
    :rtype: dict
    """
    pos_data = defaultdict(list)
    for path, subdirs, files in os.walk(dir):
        for name in files:
            f = os.path.join(path, name)
            data = codecs.open(f, 'rb', 'utf-8')
            tokens = data.readlines()
            for line in tokens:
                parts = line.split('\t')
                if len(parts) > 1:
                    (token, pos) = (parts[0], parts[1])
                    pos_data[name].append((token, pos))
    return pos_data


def filter_sentences_by_chunk(pos_data, tokens):
    chunker = RegexpParser(CHUNKER_GRAMMAR)
    filtered = {}
    for sentence_id, data in pos_data.iteritems():
        result = chunker.parse(data)
        good_one = False
        if 'CHUNK' in [s.label() for s in result.subtrees()]:
            for t in result.subtrees(lambda result: result.label() == 'CHUNK'):
                for token, pos in t.leaves():
                    if pos.find('VER') != -1 and token in tokens: good_one = True
                if good_one:
                    filtered[sentence_id] = ' '.join(item[0] for item in data)
    return filtered


def save_sentences(sentences, outdir):
    """ saves the sentences (dictionary id -> text) one per file
    into the given directory

    :param dict sentences: Dictionary with sentence ID and sentence text
    :param str outdir: Where to save the sentences
    :return: None
    """
    for sentence_id, text in sentences.iteritems():
        with open(os.path.join(outdir, sentence_id), 'w') as f:
            f.write(text.encode('utf8'))


@click.command()
@click.argument('tagged-dir', type=click.Path(exists=True, file_okay=False))
@click.argument('tokens', type=click.File('r'))
@click.argument('outdir', default='gold', type=click.Path(exists=True, file_okay=False))
def main(tagged_dir, tokens, outdir):
    """ this script extracts meaningful sentences based on a simple grammar
    """
    pos_data = load_pos_data(tagged_dir)
    tokens = [l.strip().decode('utf8') for l in tokens]
    sentences = filter_sentences_by_chunk(pos_data, tokens)
    save_sentences(sentences, outdir)


if __name__ == "__main__":
    main()
