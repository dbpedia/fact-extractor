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
@click.argument('processed_out', default='processed')
@click.argument('discarded_out', default='discarded')
@click.argument('dataset', default='dataset')
@click.option('--format', default='nt')
@click.option('--resource-namespace', default='http://it.dbpedia.org/resource/')
@click.option('--fact-namespace', default='http://dbpedia.org/fact-extraction/')
@click.option('--ontology-namespace', default='http://dbpedia.org/ontology/')
def main(labeled, wid_title_mapping, processed_out, discarded_out, dataset, format,
         resource_namespace, fact_namespace, ontology_namespace):

    # Namespace prefixes for RDF serialization
    RESOURCE_NS = Namespace(resource_namespace)
    FACT_EXTRACTION_NS = Namespace(fact_namespace)
    ONTOLOGY_NS = Namespace(ontology_namespace)
    NAMESPACE_MANAGER = NamespaceManager(Graph())
    NAMESPACE_MANAGER.bind('resource', RESOURCE_NS)
    NAMESPACE_MANAGER.bind('fact', FACT_EXTRACTION_NS)
    NAMESPACE_MANAGER.bind('ontology', ONTOLOGY_NS)

    mapping = json.load(wid_title_mapping)
    with codecs.open(labeled, 'rb', 'utf8') as f:
        labeled = json.load(f)

    processed, discarded = to_assertions(labeled, mapping, NAMESPACE_MANAGER, {
                                            'ontology': ONTOLOGY_NS,
                                            'resource': RESOURCE_NS,
                                            'fact_extraction': FACT_EXTRACTION_NS,
                                         })
    with codecs.open(processed_out, 'wb', 'utf8') as f:
        f.writelines('\n'.join(processed))

    with codecs.open(discarded_out, 'wb', 'utf8') as f:
        f.writelines('\n'.join(discarded))


if __name__ == '__main__':
    main()
