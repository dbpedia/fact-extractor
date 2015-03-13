#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import requests
import json
import sys


ENDPOINT = 'http://it.dbpedia.org/sparql'
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
    processed = {}
    for result in endpoint_response['results']['bindings']:
        # Get rid of URI namespace
        entity = result['resource']['value'][31:]
        vars = result.keys()
        vars.remove('resource')
        # Deduplication hack
        processed[entity] = list(set([result[var]['value'] for var in vars]))
    return processed


def write_lexicalizations_list(results, outfile):
    """Write a grep-friendly list of lexicalizations, one per line"""
    with codecs.open(outfile, 'wb', 'utf-8') as o:
        for entity, lexicalizations in results.iteritems():
            o.writelines([l + '\n' for l in lexicalizations])
    return 0


if __name__ == "__main__":
    all_results = {}
    for entity_type in sys.argv[1:]:
        response = query_endpoint(QUERY, entity_type)
        all_results.update(process_response(response))
    write_lexicalizations_list(all_results, 'lexicalizations')

