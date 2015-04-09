#!/usr/bin/env python
# encoding: utf-8

import codecs
import json
import os
import sys

for path, subdirs, files in os.walk(sys.argv[1]):
  for name in files:
    f = os.path.join(path, name)
    DO STUFF

ngrams = json.load(codecs.open('/home/fox/srl/soccer/training/07042015/twm-ngrams/0.json'))
links = json.load(codecs.open('/home/fox/srl/soccer/training/07042015/twm-links/0.json'))
fsssasdadsadsdadas= codecs.open('/home/fox/srl/soccer/training/07042015/textpro/00', 'rb', 'utf-8')
tp = [l.strip() for l in f.readlines()]

tmp_tp_chunks = []
for line in tp:
    if line.startswith('#'): continue
    items = line.split('\t')
    token = items[0]
    tag = items[3]
    if tag == 'B-NP': chunk = [token]
    elif tag == 'I-NP': chunk.append(token)
    else: continue
    tmp_tp_chunks.append(chunk)

tp_chunks = []
for chunk in tmp_tp_chunks:
    if chunk not in tp_chunks: tp_chunks.append(chunk)
tp_chunks = set([' '.join(chunk) for chunk in tp_chunks])

ngram_chunks = set()
for val in ngrams.values():
    for diz in val:
        ngram_chunks.add(diz['chunk'])

print 'NGRAMS'
print ngram_chunks

link_chunks = set()
for val in links.values():
    for diz in val:
        link_chunks.add(diz['chunk'])

print 'LINKS'
print link_chunks

# If chunks overlap, prefer links > ngrams > chunker
to_remove = set()
for link_chunk in link_chunks:
    for ngram_chunk in ngram_chunks:
        if link_chunk in ngram_chunk:
            to_remove.add(ngram_chunk)
ngram_chunks.difference_update(to_remove)

print 'NGRAMS PRUNED FROM LINKS'
print ngram_chunks

print 'TEXTPRO'
print tp_chunks

to_remove = set()
for link_chunk in link_chunks:
    for tp_chunk in tp_chunks:
        if link_chunk in tp_chunk:
            to_remove.add(tp_chunk)
tp_chunks.difference_update(to_remove)

print 'TEXTPRO PRUNED FROM LINKS'
print tp_chunks

to_remove = set()
for ngram_chunk in ngram_chunks:
    for tp_chunk in tp_chunks:
        if ngram_chunk in tp_chunk:
            to_remove.add(tp_chunk)
tp_chunks.difference_update(to_remove)

print 'TEXTPRO PRUNED FROM NGRAMS'
print tp_chunks

all_chunks = tp_chunks.union(ngram_chunks, link_chunks)

print 'FINAL'
print all_chunks
