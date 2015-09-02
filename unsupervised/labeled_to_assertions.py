#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import os
if __name__ == '__main__' and __package__ is None:
    os.sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import click
import codecs
import json
from rdflib.namespace import Namespace, NamespaceManager
from rdflib import Graph, URIRef
from lib.to_assertions import to_assertions

@click.command()
@click.argument('labeled')
@click.argument('wid-title-mapping', type=click.File('r', 'utf8'))
@click.argument('scores', default='scores.nt', type=click.File('w'))
@click.argument('processed_out', default='processed')
@click.argument('discarded_out', default='discarded')
@click.argument('dataset', default='dataset.nt')
@click.option('--format', default='nt')
@click.option('--resource-namespace', default='http://it.dbpedia.org/resource/')
@click.option('--fact-namespace', default='http://dbpedia.org/fact-extraction/')
@click.option('--ontology-namespace', default='http://dbpedia.org/ontology/')
def main(labeled, wid_title_mapping, scores, processed_out, discarded_out, dataset, format,
         resource_namespace, fact_namespace, ontology_namespace):
    """
    this script converts the labeled data produced by the unsupervised approach into
    actual triples in nt format
    """

    mapping = json.load(wid_title_mapping)
    with codecs.open(labeled, 'rb', 'utf8') as f:
        labeled = json.load(f)

    processed, discarded = to_assertions(labeled, mapping, score_dataset=scores,
                                         outfile=dataset, format=format)
    with codecs.open(processed_out, 'wb', 'utf8') as f:
        f.writelines('\n'.join(processed))

    with codecs.open(discarded_out, 'wb', 'utf8') as f:
        f.writelines('\n'.join(discarded))


if __name__ == '__main__':
    main()
