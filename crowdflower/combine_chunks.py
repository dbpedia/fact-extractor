#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import os
if __name__ == '__main__' and __package__ is None:
    os.sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import codecs
import itertools
import json
import os
import re
import sys
import click
from lib import stopwords
from collections import defaultdict


DEBUG = True


# From https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Longest_common_substring#Python2
def longest_common_substring(s1, s2):
    """ finds the longest common substring between two strings """
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


def read_twm_links(f):
    """ reads the links produced by the wiki machine, filtering out italian stopwords

    :param str f: Path of the file containing the links
    :return: Sentence ID and linked chunks
    :rtype: tuple
    """
    links = json.load(codecs.open(f, 'rb', 'utf-8'))
    sentence, val = links.items()[0]

    link_chunks = dict()
    for diz in val:
        chunk = diz['chunk']
        if chunk.lower() not in stopwords.StopWords.words('italian'):
            link_chunks[chunk] = {
                'start': diz['start'],
                'end': diz['end'],
            }

    return sentence, link_chunks


def read_ngrams(f):
    """ read the ngrams from the json file filtering out italian stopwords

    :param file f: Path to the file containing the ngrmams
    :return: the ngram chunks
    :rtype: dict
    """
    ngrams = json.load(codecs.open(f, 'rb', 'utf-8'))

    ngram_chunks = dict()
    for val in ngrams.values():
        for diz in val:
            chunk = diz['chunk']
            if chunk.lower() not in stopwords.StopWords.words('italian'):
                ngram_chunks[chunk] = {
                    'start': diz['start'],
                    'end': diz['end'],
                }

    return ngram_chunks


def read_tp_chunks(f):
    """ reads the chunks produced by textpro

    :param str f: Path to the file containing the chunks
    :return: The loaded chunks as map ngram -> {}
    :rtype: dict 
    """
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
    return {' '.join(chunk): {} for chunk in tmp_tp_chunks}


def load_chunks(path):
    """
    loads all chunks contained in the given path
    chunk type is determined only from the path of the file, 'twm-links',
    'twm-ngrams' and 'textpro-chunks', the name of the file must be a
    two digits number (the sentence id) and an optional extension

    :param str path: Path containing all the files
    :return: The chunks for each sentence
    :rtype: dict
    """
    all_chunks = defaultdict(lambda: dict())

    for path, _, files in os.walk(path):
        for name in files:
            f = os.path.join(path, name)
            filename, ext = os.path.splitext(name)

            # Skip unwanted files
            match = re.match(r'^\d+$', filename)
            if not match:
                continue

            sentence_id = '%03d' % int(match.group(0))
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
    removes from second all the chunks which completely include,
    or is completely included in, some other chunk first

    :param set first: First set of chunks
    :param set second: Second set of chunks
    :return: None
    """
    to_remove = set()

    for a, b in itertools.product(first, second):
        if a in b or b in a:
            to_remove.add(b)
            if DEBUG:
                print 'Removing "%s" because it overlaps with "%s"' % (b, a)

    for chunk in to_remove:
        second.pop(chunk)


def combine_priority(link_chunks, ngram_chunks, tp_chunks):
    """ combine chunks according to priority link_chunks > ngram_chunks > tp_chunks
    
    :param set link_chunks: Set of chunks coming from entity linking
    :param set ngram_chunks: Set of ngram chunks
    :param set tp_chunks: Set of chunks coming from textpro
    :return: The combined chunks
    :rtype: set
    """
    priority_update(link_chunks, ngram_chunks)
    priority_update(link_chunks, tp_chunks)
    priority_update(ngram_chunks, tp_chunks)

    combined = dict()
    combined.update(link_chunks)
    combined.update(ngram_chunks)
    combined.update(tp_chunks)

    return combined


def combine_overlapping(chunks):
    """ Combine overlapping chunks

    :param list chunks: List of string with all the chunks
    :return: The list with overlapping chunks combined
    :rtype: list
    """
    pairs = itertools.combinations(chunks, 2)
    for p1, p2 in pairs:
        if not p1 in chunks or not p2 in chunks:
            continue

        words1, words2 = p1.split(), p2.split()
        common = longest_common_substring(words1, words2)
        if common:
            word_common = ' '.join(common)
            index1, index2 = p1.index(word_common), p2.index(word_common)

            #             v index1
            #    +--------|-common-|------------+          p1
            #          +--|-common-|-------------------+   p2
            #             ^ index2
            #    +-------------------------------------+    total
            if index1 < index2:
                (p1, index1), (p2, index2) = (p2, index2), (p1, index1)
            total = p1[:index1] + p2[index2:]

            if DEBUG:
                print 'Merging (overlap) "%s" and "%s" to "%s"' % (p1, p2, total)

            p1 = chunks.pop(p1)
            p2 = chunks.pop(p2)
            chunks[total] = {
                'start': p1.get('start', -1),
                'end': p2.get('end', -1),
            }

    return chunks 


def combine_contiguous(combined):
    """ Combine contiguous chunks

    :param list combined: List of the combined chunks
    :return: A list with combined chunks merged
    """

    def contiguous(c1, c2):
        return c1['end'] + 1 == c2['start']

    final = list()

    # order by start
    chunks = sorted(({'chunk': k, 'start': v.get('start', -1), 'end': v.get('end', -1)}
                         for k, v in combined.iteritems()),
                    key=lambda x: x.get('start', -1))
    i = 0
    while i < len(chunks):
        if chunks[i]['start'] < 0:
            final.append(chunks[i])
            i += 1
        else:
            # start from this chunk and find all the contiguous ones
            j = i
            while j < len(chunks) - 1 and contiguous(chunks[j], chunks[j + 1]):
                j += 1

            # merge them
            total = ' '.join(c['chunk'] for c in chunks[i:j + 1])
            final.append({
                'chunk': total,
                'start': chunks[i]['start'],
                'end': chunks[j]['end']
            })

            if j > i and DEBUG:
                print 'Merging (contiguous) chunks %d to %d to %s' % (i, j, total)

            i = j + 1

    return final


def combine_chunks(sentence_id, values):
    """
    combine the chunks of each sentence
    if chunks overlap, prefer links > ngrams > chunker
    if chunks still overlap after this merge them, i.e. "la Nazionale" and
    "Nazionale Under-21" would be merged into "la Nazionale Under-21"
    finally, merge contiguous chunks into a single bigger one

    :param str sentence_id: ID of the sentence being processed
    :param dict values: Chunks coming from different sources
    :return: Dictionary with combined chunks, keys: id, sentence, chunks
    :rtype: dict
    """

    link_chunks = values.get('twm-links', dict())
    ngram_chunks = values.get('twm-ngrams', dict())
    tp_chunks = values.get('textpro-chunks', dict())

    if DEBUG:
        print '--- PROCESSING SENTENCE', sentence_id
        print values['sentence']
        print 'LINKS', link_chunks
        print 'NGRAMS', ngram_chunks
        print 'TEXTPRO', tp_chunks

    chunks_p = combine_priority(link_chunks, ngram_chunks, tp_chunks)
    chunks_o = combine_overlapping(chunks_p)
    final = combine_contiguous(values['sentence'], chunks_o)

    return {
        'id': sentence_id,
        'sentence': values['sentence'],
        'chunks': list(x['chunk'] for x in final),
    }


@click.command()
@click.argument('chunks-path', type=click.Path(exists=True, file_okay=False))
@click.argument('combined_out')
@click.option('--debug/--no-debug', default=False)
def main(chunks_path, combined_out, debug):
    """ combines the chunks found by three different chunking strategies
    """
    global DEBUG
    DEBUG = debug

    path = sys.argv[1]
    all_chunks = load_chunks(chunks_path)

    all_combined = []
    for sentence_id, values in all_chunks.iteritems():
        combined = combine_chunks(sentence_id, values)
        all_combined.append(combined)
        if debug:
            print 'RESULT', combined

    with codecs.open(combined_out, 'wb', 'utf8') as f:
        json.dump(all_combined, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()
