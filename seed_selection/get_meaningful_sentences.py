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
    filtered = []
    for sentence_id, data in pos_data.iteritems():
        result = chunker.parse(data)
        good_one = False
        if 'CHUNK' in [s.label() for s in result.subtrees()]:
            for t in result.subtrees(lambda result: result.label() == 'CHUNK'):
                for token, pos in t.leaves():
                    if pos.find('VER') != -1 and token in tokens: good_one = True
                if good_one:
                    filtered.append(' '.join([item[0] for item in data]))
    return filtered


@click.command()
@click.argument('tagged-dir', type=click.Path(exists=True, file_okay=False))
@click.argument('tokens', type=click.File('r'))
@click.argument('outfile', default='gold', type=click.File('w'))
def main(tagged_dir, tokens, outfile):
    pos_data = load_pos_data(tagged_dir)
    tokens = [l.strip() for l in tokens]
    sentences = filter_sentences_by_chunk(pos_data, tokens)
    outfile.write('\n'.join(sentences).encode('utf8'))


if __name__ == "__main__":
    main()
