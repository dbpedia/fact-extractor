#!/usr/bin/env python
# encoding: utf-8

import codecs
import itertools
import json
import os
import re
import sys
import stopwords
from collections import defaultdict

debug = True
all_chunks = defaultdict(lambda: dict())

# From https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Longest_common_substring#Python2
def longest_common_substring(s1, s2):
    m = [[0] * (1 + len(s2)) for i in xrange(1 + len(s1))]
    longest, x_longest = 0, 0
    for x in xrange(1, 1 + len(s1)):
        for y in xrange(1, 1 + len(s2)):
            if s1[x - 1] == s2[y - 1]:
                m[x][y] = m[x - 1][y - 1] + 1
                if m[x][y] > longest:
                    longest = m[x][y]
                    x_longest = x
            else:
                m[x][y] = 0
    return s1[x_longest - longest: x_longest]

# Loop over the dirs containing the chunks
for path, subdirs, files in os.walk(sys.argv[1]):
    for name in files:
        f = os.path.join(path, name)
        # Skip unwanted files
        if not re.match('^[0-9]', name): continue 
        # Standard sentence ID
        sentence_id = '%02d' % int(os.path.splitext(name)[0])
        # links
        if 'twm-links' in path:
            links = json.load(codecs.open(f, 'rb', 'utf-8'))
            link_chunks = set()
            for sentence, val in links.iteritems():
                all_chunks[sentence_id]['sentence'] = sentence
                for diz in val:
                    # Skip chunks if they are in a stopwords list
                    chunk = diz['chunk']
                    if chunk.lower() in stopwords.StopWords.words('italian'): continue
                    link_chunks.add(chunk)
            all_chunks[sentence_id]['twm-links'] = link_chunks
        # n-grams
        elif 'twm-ngrams' in path:
            ngrams = json.load(codecs.open(f, 'rb', 'utf-8'))
            ngram_chunks = set()
            for val in ngrams.values():
                for diz in val:
                    # Skip chunks if they are in a stopwords list
                    chunk = diz['chunk']
                    if chunk.lower() in stopwords.StopWords.words('italian'): continue
                    ngram_chunks.add(diz['chunk'])
            all_chunks[sentence_id]['twm-ngrams'] = ngram_chunks
        # TextPro
        elif 'textpro-chunks' in path:
            with codecs.open(f, 'rb', 'utf-8') as i:
                tp = [l.strip() for l in i.readlines()]
            tmp_tp_chunks = []
            # Parse TextPro format
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
            all_chunks[sentence_id]['textpro-chunks'] = tp_chunks

if debug:
    print all_chunks

all_combined = []

# Combine results
for sentence_id, values in all_chunks.iteritems():
    current = {'id': sentence_id, 'sentence': values['sentence']}
    # If chunks overlap, prefer links > ngrams > chunker
    link_chunks = values.get('twm-links', set())
    ngram_chunks = values.get('twm-ngrams', set())
    tp_chunks = values.get('textpro-chunks', set())
    if debug:
        print 'LINKS', link_chunks
        print 'NGRAMS', ngram_chunks
        print 'TEXTPRO', tp_chunks

    # Prune ngrams from links
    to_remove = set()
    for link_chunk in link_chunks:
        for ngram_chunk in ngram_chunks:
            # Prune whether the link is an ngram substring or viceversa
            if link_chunk in ngram_chunk or ngram_chunk in link_chunk:
                print 'Removing "%s" because it overlaps with "%s"' % (ngram_chunk, link_chunk)
                to_remove.add(ngram_chunk)
    ngram_chunks.difference_update(to_remove)

    # Prune TextPro chunks from links
    to_remove = set()
    for link_chunk in link_chunks:
        for tp_chunk in tp_chunks:
            # Prune whether the link is a TextPro chunk substring or viceversa
            if link_chunk in tp_chunk or tp_chunk in link_chunk:
                print 'Removing "%s" because it overlaps with "%s"' % (tp_chunk, link_chunk)
                to_remove.add(tp_chunk)
    tp_chunks.difference_update(to_remove)

    # Prune TextPro chunks from ngrams
    to_remove = set()
    for ngram_chunk in ngram_chunks:
        for tp_chunk in tp_chunks:
            # Prune whether the ngram is TextPro chunk substring or viceversa
            if ngram_chunk in tp_chunk or tp_chunk in ngram_chunk:
                print 'Removing "%s" because it overlaps with "%s"' % (tp_chunk, ngram_chunk)
                to_remove.add(tp_chunk)
    tp_chunks.difference_update(to_remove)

    combined = tp_chunks.union(ngram_chunks, link_chunks)
    print 'REMAINING CHUNKS', combined


    # Merge chunks in case of common words
    pairs = itertools.combinations(combined, 2)
    for p1, p2 in pairs:
        """
        if not p1 in combined or not p2 in combined:
            continue
        """

        words1, words2 = p1.split(), p2.split()
        common = longest_common_substring(words1, words2)
        if common:
            word_common = ' '.join(common)
            index1, index2 = p1.index(word_common), p2.index(word_common)

            if index1 > index2:
                total = p1[:index1] + p2[index2:]
            else:
                total = p2[:index2] + p1[index1:]

            print 'Merging "%s" and "%s" to "%s"' % (p1, p2, total)

            combined.remove(p1)
            combined.remove(p2)
            combined.add(total)

    # Cast to list for json serialization
    current['chunks'] = list(combined)
    all_combined.append(current)
    print 'COMBINED', current

if debug:
    print all_combined

json.dump(all_combined, codecs.open('chunks.json', 'wb', 'utf-8'), ensure_ascii=False, indent=2)
