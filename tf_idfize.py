#!/usr/bin/env python
# coding: utf-8

import os
import sys
import tfidf
import codecs
import numpy
import json
import regex
from collections import Counter, OrderedDict

STOPWORDS = ["ad", "al", "allo", "ai", "agli", "all", "agl", "alla", "alle", "con", "col", "coi", "d", "da", "dal", "dallo", "dai", "dagli", "dall", "dagl", "dalla", "dalle", "di", "del", "dello", "dei", "degli", "dell", "degl", "della", "delle", "in", "nel", "nello", "nei", "negli", "nell", "negl", "nella", "nelle", "su", "sul", "sullo", "sui", "sugli", "sull", "sugl", "sulla", "sulle", "per", "tra", "contro", "io", "tu", "lui", "lei", "noi", "voi", "loro", "mio", "mia", "miei", "mie", "tuo", "tua", "tuoi", "tue", "suo", "sua", "suoi", "sue", "nostro", "nostra", "nostri", "nostre", "vostro", "vostra", "vostri", "vostre", "mi", "ti", "ci", "vi", "lo", "la", "li", "le", "gli", "ne", "il", "un", "uno", "una", "ma", "ed", "se", "perché", "anche", "come", "dov", "dove", "che", "chi", "cui", "non", u"più", "quale", "quanto", "quanti", "quanta", "quante", "quello", "quelli", "quella", "quelle", "questo", "questi", "questa", "queste", "si", "tutto", "tutti", "a", "c", "e", "i", "l", "o", "ho", "hai", "ha", "abbiamo", "avete", "hanno", "abbia", "abbiate", "abbiano", u"avrò", "avrai", u"avrà", "avremo", "avrete", "avranno", "avrei", "avresti", "avrebbe", "avremmo", "avreste", "avrebbero", "avevo", "avevi", "aveva", "avevamo", "avevate", "avevano", "ebbi", "avesti", "ebbe", "avemmo", "aveste", "ebbero", "avessi", "avesse", "avessimo", "avessero", "avendo", "avuto", "avuta", "avuti", "avute", "sono", "sei", u"è", "siamo", "siete", "sia", "siate", "siano", u"sarò", "sarai", u"sarà", "saremo", "sarete", "saranno", "sarei", "saresti", "sarebbe", "saremmo", "sareste", "sarebbero", "ero", "eri", "era", "eravamo", "eravate", "erano", "fui", "fosti", "fu", "fummo", "foste", "furono", "fossi", "fosse", "fossimo", "fossero", "essendo", "faccio", "fai", "facciamo", "fanno", "faccia", "facciate", "facciano", u"farò", "farai", u"farà", "faremo", "farete", "faranno", "farei", "faresti", "farebbe", "faremmo", "fareste", "farebbero", "facevo", "facevi", "faceva", "facevamo", "facevate", "facevano", "feci", "facesti", "fece", "facemmo", "faceste", "fecero", "facessi", "facesse", "facessimo", "facessero", "facendo", "s", "sto", "stai", "sta", "stiamo", "stanno", "stia", "stiate", "stiano", u"starò", "starai", u"starà", "staremo", "starete", "staranno", "starei", "staresti", "starebbe", "staremmo", "stareste", "starebbero", "stavo", "stavi", "stava", "stavamo", "stavate", "stavano", "stetti", "stesti", "stette", "stemmo", "steste", "stettero", "stessi", "stesse", "stessimo", "stessero", "stando"]


def compute_tfidf_matrix(corpus_dir):
    t = tfidf.tfidf()
    for path, subdirs, files in os.walk(sys.argv[1]):
        for name in files:
            f = os.path.join(path, name)
            with codecs.open(f, 'rb', 'utf-8') as i:
                tokens = []
                lines = i.readlines()
                for l in lines:
                    # Skip <doc> tags
                    if not regex.match(ur'</?doc', l):
                        l_tokens = regex.split(ur'[^\p{L}]+', l.lower())
                        tokens += [token for token in l_tokens if token and token not in STOPWORDS]
                t.addDocument(f, tokens)
    return t


def get_distributions(lemmas, tfidf_matrix, threshold=0.75):
    variances = {}
    stdevs = {}
    threshold_rank = {}
    for lemma in lemmas:
        relevance = 0
        ranking = tfidf_matrix.similarities([lemma])
        scores = [pair[1] for pair in ranking]
        variances[lemma] = numpy.var(scores)
        stdevs[lemma] = numpy.std(scores)
        for score in scores:
            if score > threshold:
                relevance += 1
        threshold_rank[lemma] = relevance
    return variances, stdevs, threshold_rank


def parse_tokens(infile):
    with codecs.open(infile, 'rb', 'utf-8') as i:
        return [token.strip() for token in i.readlines()]


if __name__ == "__main__":
    print "Loading tokens from %s" % sys.argv[2]
    tokens = parse_tokens(sys.argv[2])
    print "Building TF/IDF matrix against corpus %s ..." % sys.argv[1]
    t = compute_tfidf_matrix(sys.argv[1])
    print "Computing variance, standard deviation, and ranking with threshold = .75 ..."
    variances, stdevs, threshold_rank = get_distributions(tokens, t)
    print "Dumping results to JSON ..."
    json.dump(variances, open('variances.json', 'wb'), indent = 2)
    json.dump(stdevs, open('stdevs.json', 'wb'), indent = 2)
    json.dump(threshold_rank, open('threshold_rank.json', 'wb'), indent = 2)


