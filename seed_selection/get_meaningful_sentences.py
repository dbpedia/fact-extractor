#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import os
import sys
from collections import defaultdict
from nltk import RegexpParser

CHUNKER_GRAMMAR = r"""
    SN: {<PRO.*|DET.*|>?<ADJ>*<NUM>?<NOM|NPR>+<NUM>?<ADJ|VER:pper>*}
    CHUNK: {<SN><VER.*>+<SN>}
    """


def load_tokens(tokens_file):
    with codecs.open(tokens_file, 'rb', 'utf-8') as i:
        tokens = [l.strip() for l in i.readlines()]
    return tokens if tokens else False


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


def write_sentences(sentences, outfile='gold'):
    with codecs.open(outfile, 'wb', 'utf-8') as o:
        o.writelines([s + '\n' for s in sentences])
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 4:
        pos_data = load_pos_data(sys.argv[1])
        tokens = load_tokens(sys.argv[2])
        outfile = sys.argv[3]
        sentences = filter_sentences_by_chunk(pos_data, tokens)
        write_sentences(sentences, outfile)
        sys.exit(0)
    elif len(sys.argv) == 3:
        pos_data = load_pos_data(sys.argv[1])
        tokens = load_tokens(sys.argv[2])
        sentences = filter_sentences_by_chunk(pos_data, tokens)
        write_sentences(sentences)
        sys.exit(0)
    else:
        print "Usage: python %s <POS_DATA_DIR> <TOKENS_FILE> [OUTPUT_FILE]" % __file__
        sys.exit(1)
