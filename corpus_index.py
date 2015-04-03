#!/usr/bin/env python
# -*- coding: utf-8 -*-

from whoosh.index import create_in
from whoosh.fields import *
from whoosh.qparser import QueryParser


def create_index(outdir, index_name=None)
    schema = Schema(title=TEXT(stored=True), path=ID(stored=True), content=TEXT)
    ix = create_in(outdir, schema, index_name)
    writer = ix.writer()
    writer.add_document(title=u"First document", path=u"/a",
                     content=u"This is the first document we've added!")
    writer.add_document(title=u"Second document", path=u"/b",
                     content=u"The second one is even more interesting!")
    writer.commit()
    return ix


def query_index(index):
    with index.searcher() as searcher:
        query = QueryParser("content", index.schema).parse("first")
        results = searcher.search(query)
        print results[0]

