#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import requests
import json
import sys
import click


ENDPOINT = 'http://it.dbpedia.org/sparql'
LIMIT = 1000
QUERY = """
        SELECT ?resource, ?label, ?name, ?redirect_label
        WHERE
        {{
            ?resource a dbpedia-owl:{type} ;
                rdfs:label ?label .
            OPTIONAL {{ ?resource foaf:name ?name . }} .
            ?redirect dbpedia-owl:wikiPageRedirects ?resource ;
                rdfs:label ?redirect_label .
        }}
        OFFSET {offset}
        LIMIT {limit}
        """


def query_endpoint(query, entity_type):
    """Run a query to a Virtuoso SPARQL endpoint

    :param str query: Template of the query with type, offset and limit as parameters
    :param str entity_type: Type of the entity
    :return: The bindings returned
    :rtype: list
    """
    print 'Getting data for', entity_type
    bindings = []
    finished, offset = False, 0
    while not finished:
        r = requests.get(ENDPOINT, params={
                'format': 'json',
                'query': query.format(type=entity_type, offset=offset, limit=LIMIT),
            })
        if r.ok:
            bindings += r.json()['results']['bindings']
        finished = not r.ok or len(r.json()['results']['bindings']) < LIMIT
        offset += LIMIT

    print len(bindings), 'results'
    return bindings


def process_response(bindings):
    """Process the query result set from the endpoint JSON response

    :param list bindings: Bindings of entities returned by the endpoint
    :return: Data for each entity
    :rtype: dict
    """
    processed = {}
    for result in bindings:
        # Get rid of URI namespace
        entity = result['resource']['value'][31:]
        vars = result.keys()
        vars.remove('resource')
        # Deduplication hack
        processed[entity] = list(set([result[var]['value'] for var in vars]))
    return processed


def write_lexicalizations_patterns(subjects, lus, objects, outfile):
    """Write a grep-friendly file containing lexicalization patterns, one per line"""
    for subj_entity, subj_lexicalizations in subjects.iteritems():
        for lu in lus:
            for obj_entity, obj_lexicalizations in objects.iteritems():
                for subj in subj_lexicalizations:
                    for obj in obj_lexicalizations:
                        # Each lexicalization is separated by '.*' for matching purposes
                        outfile.write(('%s.*%s.*%s\n' % (subj, lu, obj)).encode('utf8'))
    return 0


@click.command()
@click.argument('tokens', type=click.File('r'))
@click.argument('subject-type', type=click.STRING)
@click.argument('object-types', type=click.STRING, nargs=-1)
@click.argument('output', type=click.File('w'), default='lexicalization')
def main(tokens, subject_type, object_types, output):
    objects = {}
    lus = [row.strip().decode('utf8') for row in tokens]
    subjects = process_response(query_endpoint(QUERY, subject_type))
    for entity_type in object_types:
        bindings = query_endpoint(QUERY, entity_type)
        objects.update(process_response(bindings))
    print 'Writing lexicalizations patterns'
    write_lexicalizations_patterns(subjects, lus, objects,output)


if __name__ == "__main__":
    main()
