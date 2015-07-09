#!/usr/bin/env python
# coding: utf-8
from collections import Counter, OrderedDict
import codecs
import json
import sys
import click


@click.command()
@click.argument('verb-lemmas', type=click.File('r'))
@click.argument('freq-out', type=click.File('w'))
def main(verb_lemmas, freq_out):
    freq = Counter([l.strip() for l in verb_lemmas])
    voc = OrderedDict(sorted(freq.items(), key=lambda x: x[1], reverse=True))
    json.dump(voc, freq_out, ensure_ascii=False, indent=2)


if __name__ == '__main__':
	main()
