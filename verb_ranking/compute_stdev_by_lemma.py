# coding: utf-8

import sys
import codecs
import json
import click
from collections import defaultdict, OrderedDict


@click.command()
@click.argument('token-lemma-map', type=click.File('r'))
@click.argument('token-stdev', type=click.File('r'))
@click.argument('stdev-lemma-out', type=click.File('w'))
def main(token_lemma_map, token_stdev, stdev_lemma_out):
    lemma_token_map = defaultdict(list)
    for line in token_lemma_map:
        token, lemma = line.strip().split('\t')
        lemma_token_map[lemma].append(token)
        
    jg = {}
    token_stdev = json.load(token_stdev, encoding='utf8')
    for lemma, tokens in lemma_token_map.iteritems():
        jg[lemma] = sum(token_stdev.get(t, 0.0) for t in tokens)

    d = OrderedDict(sorted(jg.items(), key=lambda x: x[1], reverse=True))
    json.dump(d, stdev_lemma_out, ensure_ascii=False, indent=2)


if __name__ == '__main__':
	main()
