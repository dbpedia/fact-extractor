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


def read_twm_links_and_ngrams(f):
    links = json.load(codecs.open(f, 'rb', 'utf-8'))
    sentence, val = links.items()[0]

    link_chunks = set()
    for diz in val:
        chunk = diz['chunk']
        if chunk.lower() not in stopwords.StopWords.words('italian'):
            link_chunks.add(chunk)

    return sentence, link_chunks


def read_ngrams(f):
    ngrams = json.load(codecs.open(f, 'rb', 'utf-8'))

    ngram_chunks = set()
    for val in ngrams.values():
        for diz in val:
            chunk = diz['chunk']
            if chunk.lower() not in stopwords.StopWords.words('italian'):
                ngram_chunks.add(chunk)

    return ngram_chunks


def read_tp_chunks(f):
    with codecs.open(f, 'rb', 'utf-8') as i:
        tp = [l.strip() for l in i.readlines()]

    tmp_tp_chunks, current_chunk = [], []
    for line in tp:
        if line.startswith('#'):
            continue

        items = line.split('\t')
        token = items[0]
        tag = items[3]

        if tag == 'B-NP':
            if current_chunk:
                tmp_tp_chunks.append(current_chunk)
            current_chunk = [token]
        elif tag == 'I-NP':
            if not current_chunk:
                print 'WARNING missing starting token:', f  # FIXME might be symptom of error
                current_chunk = []
            current_chunk.append(token)
        else:
            print 'WARNING ignoring token "%s" with tag "%s" in file "%s"' % (
                  token, tag, f)

    if current_chunk:
        tmp_tp_chunks.append(current_chunk)
    return set(' '.join(chunk) for chunk in tmp_tp_chunks)


def load_chunks(path):
    """
    loads all chunks contained in the given path

    chunk type is determined only from the path of the file, 'twm-links',
    'twm-ngrams' and 'textpro-chunks', the name of the file must be a
    two digits number (the sentence id) and an optional extension
    """
    all_chunks = defaultdict(lambda: dict())

    for path, _, files in os.walk(path):
        for name in files:
            f = os.path.join(path, name)
            filename, ext = os.path.splitext(name)

            # Skip unwanted files
            match = re.match(r'^\d{2}$', filename)
            if not match:
                continue

            sentence_id = '%02d' % int(match.group(0))
            if 'twm-links' in path:
                sentence, link_chunks = read_twm_links(f)
                all_chunks[sentence_id]['sentence'] = sentence
                all_chunks[sentence_id]['twm-links'] = link_chunks
            elif 'twm-ngrams' in path:
                all_chunks[sentence_id]['twm-ngrams'] = read_ngrams(f)
            elif 'textpro-chunks' in path:
                all_chunks[sentence_id]['textpro-chunks'] = read_tp_chunks(f)

    return all_chunks


def priority_update(first, second):
    """
    removes from second all the items which completely include, or are completely
    included in, some item in first
    """
    to_remove = set()

    for a, b in itertools.product(first, second):
        if a in b or b in a:
            to_remove.add(b)
            if debug:
                print 'Removing "%s" because it overlaps with "%s"' % (b, a)

    second.difference_update(to_remove)


def combine_chunks(sentence_id, values):
    """
    combine the chunks of each sentence
    if chunks overlap, prefer links > ngrams > chunker
    if chunks still overlap after this merge them, i.e. "la Nazionale" and
    "Nazionale Under-21" would be merged into "la Nazionale Under-21"
    """

    link_chunks = values.get('twm-links', set())
    ngram_chunks = values.get('twm-ngrams', set())
    tp_chunks = values.get('textpro-chunks', set())

    if debug:
        print '--- PROCESSING SENTENCE', sentence_id
        print 'LINKS', link_chunks
        print 'NGRAMS', ngram_chunks
        print 'TEXTPRO', tp_chunks

    priority_update(link_chunks, ngram_chunks)
    priority_update(link_chunks, tp_chunks)
    priority_update(ngram_chunks, tp_chunks)

    combined = tp_chunks.union(ngram_chunks, link_chunks)
    if debug:
        print 'COMBINED CHUNKS', combined

    pairs = itertools.combinations(combined, 2)
    for p1, p2 in pairs:
        if not p1 in combined or not p2 in combined:
            continue

        words1, words2 = p1.split(), p2.split()
        common = longest_common_substring(words1, words2)
        if common:
            word_common = ' '.join(common)
            index1, index2 = p1.index(word_common), p2.index(word_common)

            if index1 > index2:
                total = p1[:index1] + p2[index2:]
            else:
                total = p2[:index2] + p1[index1:]

            if debug:
                print 'Merging "%s" and "%s" to "%s"' % (p1, p2, total)

            combined.remove(p1)
            combined.remove(p2)
            combined.add(total)

    return {
        'id': sentence_id,
        'sentence': values['sentence'],
        'chunks': list(combined),
    }


def main():
    path = sys.argv[1]
    all_chunks = load_chunks(path)

    all_combined = []
    for sentence_id, values in all_chunks.iteritems():
        combined = combine_chunks(sentence_id, values)
        all_combined.append(combined)
        if debug:
            print 'RESULT', combined

    json.dump(all_combined, codecs.open('chunks.json', 'wb', 'utf-8'),
              ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()
