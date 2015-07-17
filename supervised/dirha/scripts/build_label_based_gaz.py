#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import requests
import json
import sys


ENDPOINT = 'http://localhost:18890/sparql'
QUERY = """
        SELECT ?resource, ?label, ?name, ?redirect_label
        WHERE
        {
            ?resource a dbpedia-owl:$TYPE$ ;
                rdfs:label ?label .
            OPTIONAL { ?resource foaf:name ?name . } .
            ?redirect dbpedia-owl:wikiPageRedirects ?resource ;
                rdfs:label ?redirect_label .
        }
        """


def query_endpoint(query, entity_type):
    """Run a query to a Virtuoso SPARQL endpoint"""
    params = {'query': query.replace('$TYPE$', entity_type), 'format': 'json'}
    r = requests.get(ENDPOINT, params=params)
    return r.json() if r.ok else {'id_error': r.status_code, 'message': r.reason}


def process_response(endpoint_response):
    """Process the query result set from the endpoint JSON response"""
    processed = set()
    for result in endpoint_response['results']['bindings']:
        # Get rid of URI namespace and underscores
        entity = result['resource']['value'][31:].replace('_', ' ')
        processed.add(entity)
        vars = result.keys()
        vars.remove('resource')
        # Deduplication hack
        processed.update(set([result[var]['value'] for var in vars]))
    return sorted(list(processed))


def write_gaz(entries, outfile='gaz.tsv'):
    """Write a gazetteer file where each feature is a DBpedia class"""
    with codecs.open(outfile, 'wb', 'utf-8') as o:
        for feature, entries in entries.iteritems():
            o.write('%s\t%s' % (feature.upper(), '\t'.join([entry.lower() for entry in entries])))
    return 0


if __name__ == "__main__":
    entries = {}
    classes = sys.argv[1:]
    for entity_type in classes:
        response = query_endpoint(QUERY, entity_type)
        entries.update({entity_type: process_response(response)})
    #print json.dumps(entries, indent=2)
    write_gaz(entries)

