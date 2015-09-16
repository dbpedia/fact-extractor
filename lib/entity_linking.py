#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
this script performs the entity linking with optional disambiguation. it takes as input
a directory with sentences to link, one per file, and the output directory where
linked sentences are put (one per file). links with a confidence lower than a given
threshold are discarded
"""

import argparse
import codecs
import json
import sys
import requests
import os
import secrets

# Some soccer-specific words to constrain TWM towards the domain
SOCCER_WORDS = ' calcio ronaldo attaccante beckham gol totti'

### BEGIN API parameters
## BEGIN The Wiki Machine
# /annotate API params:
# text TEXT_TO_ANNOTATE [REQUIRED]
# -- boolean --
# abstract -> abstract text
# class -> override named/non-named entity info with DBpedia ontology classes (URI-stolen airpedia)
# cross -> Wikipedia interlanguage links
# dbpedia -> ???
# disambiguation [default OFF] -> guess the best sense
# form -> all surface forms (lexicalizations) of each keyword
# image -> image + thumb URLs
# include_text -> input text
# link -> external URLs (Wikipedia/DBpedia)
# nbest_filter [default ON] -> ???
# overlapping_filter [default ON] -> skip overlapping n-grams
# person_filter -> ???
# topic -> topic categorization
# type -> ???
# type_filter -> ???
# -- string --
# lang -> input language
# target_lang -> ???
# -- number --
# category int DEPTH [default 0] -> Wikipedia category tree with given depth
# min_weight double WEIGHT [default 0.25] -> minimum threshold for confidence score (i.e., 'rel' field in JSON response)

TWM_URL = secrets.TWM_URL
TWM_DATA = {
    'app_id': secrets.TWM_APPID,
    'app_key': secrets.TWM_APPKEY,
    'lang': 'it'
}

# Dandelion APIs
NEX_URL = secrets.NEX_URL
NEX_DATA = {
    '$app_id': secrets.NEX_APPID,
    '$app_key': secrets.NEX_APPKEY,
    'lang': 'it',
    'include': 'types'
    }
### END API parameters


def twm_link_articles(raw_articles):
  """Run Machine Linking on a list of raw text articles

  :param list raw_articles: List of dictionaries with info about each article,
   should have keys url, title and text
  :return: The articles with the TWM linked entities, a new list of dictionaries
   with the same keys as raw_articles plus an 'entitites' list
  :rtype: list
  """
  articles = []
  for raw in raw_articles:
    linked = {'url': raw['url'], 'title': raw['title']}
    TWM_DATA['text'] = raw['text']
    r = requests.post(TWM_URL, data=TWM_DATA)
    mids = []
    for entity in twm_extract_entities(r.json()):
      mid = lookup_mid(entity)
      if mid:
        mids.append(mid)
    linked['entities'] = mids
    articles.append(linked)
  return articles


def twm_extract_entities(twm_json, disambiguation, debug):
    """Extract the list of entities from a Machine Linking JSON response

    :param dict twm_json: The response from TWM
    :param bool disambiguation: Include disambiguation
    :param bool debug: Print debug aids
    :return: The entities extracted
    :rtype: list
    """
    entities = []
    for keyword in twm_json['annotation']['keyword']:
        entity = {}
        entity['score'] = keyword['rel']
        if disambiguation:
            if keyword.get('sense'): entity['uri'] = u'http://it.dbpedia.org/resource/' + keyword['sense']['page']
            # Replace stolen URIs
            entity['types'] = [t['url'].replace('www.airpedia.org/ontology/class', 'dbpedia.org/ontology') for t in keyword['class']]
        for ngram in keyword['ngram']:
            # Skip appended soccer words
            if SOCCER_WORDS.find(ngram['form']) != -1:
                continue
            entity['chunk'] = ngram['form']
            span = ngram['span']
            entity['start'] = span['start']
            entity['end'] = span['end']
            entities.append(entity)
            if debug:
                print 'EXTRACTED ENTITY:'
                print entity
    return entities


def twm_link(text, disambiguation, debug):
    """Run Machine linking on raw text

    :param str text: The text in which to extract entities
    :param bool disambiguation: Perform entity disambiguation
    :param bool debug: Print debugging aids
    :return: The entities extracted
    :rtype: list
    """
    #  Constrain the context to the soccer domain by appending dummy words
    text += SOCCER_WORDS
    TWM_DATA['text'] = text
    response = None
    while response is None:
        try:
            r = requests.get(TWM_URL, params=TWM_DATA)
            r.raise_for_status()
            response = r.json()
        except requests.exceptions.RequestException:
            pass

    if debug:
        print 'URL SENT:'
        print r.url
        print 'TEXT SENT:'
        print text
        print 'THE WIKI MACHINE RESPONSE:'
        print response
    return twm_extract_entities(response, disambiguation, debug)


def nex_link(text):
    """Run using the Dandelion APIs on raw text

    :param str text: The text used to perform linking
    :return: The entities extracted
    :rtype: list
    """
    NEX_DATA['text'] = text
    r = requests.post(NEX_URL, data=NEX_DATA)
    print r.json()
    print text
    return nex_extract_entities(r.json())


def nex_extract_entities(nex_response_json):
    """Extract the list of entities from the Dandelion APIs JSON response

    :param dict nex_response_json: The response of The Dandelion APIs
    :return: The extracted entities, containing uri, types, start and end
    :rtype: list
    """
    entities = []
    for annotation in nex_response_json['annotations']:
        entities.append({k: v for k, v in annotation.iteritems() if k in ['uri', 'types', 'start', 'end']})
    return entities


def create_cli_parser():
    parser = argparse.ArgumentParser(description='Run an entity linking service of your choice against a set of sentences')
    parser.add_argument('service', choices=['twm', 'nex'], help='Entity linking service to use. Allowed values are "twm" (the Wiki Machine) or "nex" (Dandelion APIs)')
    parser.add_argument('input_dir', help='Input directory with sentences to link, one per file')
    parser.add_argument('output_dir', help='Linked files will be placed here')
    parser.add_argument('-d', '--disambiguation', action='store_true', help='Toggle disambiguation (twm ONLY)')
    parser.add_argument('-c', '--min-confidence', type=float, default=0.25, help='Minimum confidence score (default 0.25)')
    parser.add_argument('--debug', action='store_true', help='Toggle debug mode')
    return parser


if __name__ == '__main__':
    cli = create_cli_parser()
    args = cli.parse_args()

    sentences = {}
    for path, dirs, files in os.walk(args.input_dir):
        for name in files:
            f = os.path.join(path, name)
            with codecs.open(f, 'rb', 'utf-8') as i:
                sentences[name] = i.read()

    # Work with the Wiki Machine
    if args.service == 'twm':
        TWM_DATA['min_weight'] = args.min_confidence
        disambiguation = args.disambiguation
        # If disambiguation is enabled, so are DBpedia ontology types (see quick doc above)
        TWM_DATA['disambiguation'] = TWM_DATA['class'] = int(disambiguation)

        for _id, sentence in sentences.iteritems():
            json.dump({sentence: twm_link(sentence, disambiguation, args.debug)},
                      codecs.open(os.path.join(args.output_dir, _id), 'wb', 'utf-8'),
                      indent=2)

    # Work with dataTXT-NEX
    else:
        NEX_DATA['min_confidence'] = args.min_confidence
        for _id, sentence in sentences.iteritems():
            json.dump({sentence: nex_link(sentence)},
                      codecs.open(os.path.join(args.output_dir, _id), 'wb', 'utf-8'),
                      ensure_ascii=False, indent=2)
