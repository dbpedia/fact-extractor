#!/bin/bash

set -e

usage="Usage: $(basename "$0") <DBPEDIA_CLASS>"
if [[ $# -lt 1 ]]; then
    echo $usage
    exit 1
fi

DBPEDIA_CLASS=$1

# Query Virtuoso
isql-vt 1111 dba spazio1999dba exec="sparql select ?s where {?s a <http://dbpedia.org/ontology/${DBPEDIA_CLASS}> .}" > results

# Output filename is the lowercased DBpedia class
outfile=$(echo ${DBPEDIA_CLASS} | tr '[:upper:]' '[:lower:]')-gaz.tsv

# Feature name is the uppercased DBpedia class
feature=$(echo ${DBPEDIA_CLASS} | tr '[:lower:]' '[:upper:]')
printf "$feature\t" > $outfile

# Post-process result set to populate the gaz
grep 'resource' results | sed 's/http:\/\/it.dbpedia.org\/resource\///' | sed 's/_/ /g' | perl -ne 'print lc' | tr '\n' '\t' >> $outfile

rm results

exit 0
