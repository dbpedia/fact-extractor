import click
import csv
import os
import json
import sys


@click.command()
@click.argument('cf-results', type=click.File('r'))
@click.argument('sentence-to-wid', type=click.File('r'))
@click.argument('outfile', type=click.File('w'))
def main(cf_results, sentence_to_wid, outfile):
    writer = None
    sentence_to_wid = json.load(sentence_to_wid)
    for row in csv.DictReader(cf_results):
        if not writer:
            writer = csv.DictWriter(outfile, fieldnames=row.keys())
            writer.writeheader()

        sentence = row['sentence'].decode('utf8')
        if sentence not in sentence_to_wid:
            print row['id'], 'not resolved\r',
        else:
            print 'Sentence %s maps to wikipedia ID %s\r' % (row['id'],
                                                             sentence_to_wid[sentence]),
            row['id'] = sentence_to_wid[sentence]
            writer.writerow(row)


if __name__ == '__main__':
    main()
