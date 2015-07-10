#!/usr/bin/env python
# coding: utf-8

import click
import os
import sys
import codecs
import numpy
import json
import regex
import tfidf
from collections import Counter, OrderedDict

STOPWORDS = ["ad", "al", "allo", "ai", "agli", "all", "agl", "alla", "alle", "con", "col", "coi", "d", "da", "dal", "dallo", "dai", "dagli", "dall", "dagl", "dalla", "dalle", "di", "del", "dello", "dei", "degli", "dell", "degl", "della", "delle", "in", "nel", "nello", "nei", "negli", "nell", "negl", "nella", "nelle", "su", "sul", "sullo", "sui", "sugli", "sull", "sugl", "sulla", "sulle", "per", "tra", "contro", "io", "tu", "lui", "lei", "noi", "voi", "loro", "mio", "mia", "miei", "mie", "tuo", "tua", "tuoi", "tue", "suo", "sua", "suoi", "sue", "nostro", "nostra", "nostri", "nostre", "vostro", "vostra", "vostri", "vostre", "mi", "ti", "ci", "vi", "lo", "la", "li", "le", "gli", "ne", "il", "un", "uno", "una", "ma", "ed", "se", "perché", "anche", "come", "dov", "dove", "che", "chi", "cui", "non", u"più", "quale", "quanto", "quanti", "quanta", "quante", "quello", "quelli", "quella", "quelle", "questo", "questi", "questa", "queste", "si", "tutto", "tutti", "a", "c", "e", "i", "l", "o", "ho", "hai", "ha", "abbiamo", "avete", "hanno", "abbia", "abbiate", "abbiano", u"avrò", "avrai", u"avrà", "avremo", "avrete", "avranno", "avrei", "avresti", "avrebbe", "avremmo", "avreste", "avrebbero", "avevo", "avevi", "aveva", "avevamo", "avevate", "avevano", "ebbi", "avesti", "ebbe", "avemmo", "aveste", "ebbero", "avessi", "avesse", "avessimo", "avessero", "avendo", "avuto", "avuta", "avuti", "avute", "sono", "sei", u"è", "siamo", "siete", "sia", "siate", "siano", u"sarò", "sarai", u"sarà", "saremo", "sarete", "saranno", "sarei", "saresti", "sarebbe", "saremmo", "sareste", "sarebbero", "ero", "eri", "era", "eravamo", "eravate", "erano", "fui", "fosti", "fu", "fummo", "foste", "furono", "fossi", "fosse", "fossimo", "fossero", "essendo", "faccio", "fai", "facciamo", "fanno", "faccia", "facciate", "facciano", u"farò", "farai", u"farà", "faremo", "farete", "faranno", "farei", "faresti", "farebbe", "faremmo", "fareste", "farebbero", "facevo", "facevi", "faceva", "facevamo", "facevate", "facevano", "feci", "facesti", "fece", "facemmo", "faceste", "fecero", "facessi", "facesse", "facessimo", "facessero", "facendo", "s", "sto", "stai", "sta", "stiamo", "stanno", "stia", "stiate", "stiano", u"starò", "starai", u"starà", "staremo", "starete", "staranno", "starei", "staresti", "starebbe", "staremmo", "stareste", "starebbero", "stavo", "stavi", "stava", "stavamo", "stavate", "stavano", "stetti", "stesti", "stette", "stemmo", "steste", "stettero", "stessi", "stesse", "stessimo", "stessero", "stando"]


def compute_tfidf_matrix(corpus_dir):
    t = tfidf.tfidf()
    for path, subdirs, files in os.walk(corpus_dir):
        for name in files:
            f = os.path.join(path, name)
            with codecs.open(f, 'rb', 'utf-8') as i:
                tokens = []
                for line in i:
                    # Skip <doc> tags
                    if not regex.match(ur'</?doc', line):
                        l_tokens = regex.split(ur'[^\p{L}]+', line.lower())
                        tokens += [token for token in l_tokens
                                         if token and token not in STOPWORDS]
                t.addDocument(f, tokens)
    return t


def dump_tfidf(ranking, outfile='tfidf.json'):
    with open(outfile, 'wb') as f:
        json.dump(ranking, f, indent=2)
    return 0


def get_distributions(tokens, tfidf_matrix, threshold):
    variances = {}
    stdevs = {}
    threshold_rank = {}
    tfidf_ranking = {}
    for token in tokens:
        relevance = 0
        ranking = tfidf_matrix.similarities([token])
        non_null = {doc: score for (doc, score) in ranking if score}
        ordered = OrderedDict(sorted(non_null.items(), key=lambda x: x[1], reverse=True))
        tfidf_ranking[token] = ordered
        scores = [pair[1] for pair in ranking]
        variances[token] = numpy.var(scores)
        stdevs[token] = numpy.std(scores)
        for score in scores:
            if score > threshold:
                relevance += 1
        threshold_rank[token] = relevance

    return (OrderedDict(sorted(variances.items(), key=lambda x: x[1], reverse=True)),
           OrderedDict(sorted(stdevs.items(), key=lambda x: x[1], reverse=True)),
           OrderedDict(sorted(threshold_rank.items(), key=lambda x: x[1], reverse=True)),
           tfidf_ranking)


@click.command()
@click.argument('corpus', type=click.Path(exists=True, file_okay=False))
@click.argument('tokens', type=click.File('r'))
@click.option('--threshold', '-t', default=0.6)
@click.option('--dump-tfidf/--no-dump-tfidf', default=False)
@click.option('--variance-out', type=click.File('w'), default='variances.json')
@click.option('--stdevs-out', type=click.File('w'), default='stdevs.json')
@click.option('--threshold-rank-out', type=click.File('w'), default='threshold_rank.json')
@click.option('--tfidf-rank-out', type=click.File('w'), default='tfidf.json')
def main(corpus, tokens, threshold, dump_tfidf, variance_out, stdevs_out,
         threshold_rank_out, tfidf_rank_out):

    print "Loading tokens..."
    tokens = [token.strip() for token in tokens]

    print "Building TF/IDF matrix against corpus %s ..." % corpus
    t = compute_tfidf_matrix(corpus)

    print "Computing variance, standard deviation, and ranking"
    vars, stdevs, threshold_rank, tfidf_ranking = get_distributions(tokens, t, threshold)

    print "Dumping results to JSON ..."
    json.dump(vars, variance_out, indent=2)
    json.dump(stdevs, stdevs_out, indent=2)
    json.dump(threshold_rank, threshold_rank_out, indent=2)

    if dump_tfidf:
        json.dump(tfidf_ranking, tfidf_rank_out, indent=2)


if __name__ == "__main__":
    main()
