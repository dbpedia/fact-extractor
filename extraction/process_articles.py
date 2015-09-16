
import click
import re
import os
import json
import sys


def iter_split(iterator, split):
    acc = []
    for item in iterator:
        acc.append(item)
        if split(item):
            yield acc
            acc = []


def process_article(content, soccer_ids, mapping, output_dir):
    """ given a single article as a string checks if its id is contained
    in the soccer_ids set, if so updates the soccer ids and the mappings
    and saves the article in a new file named as the article id

    :param str content: Text of the article including start and end doc tags
    :param set soccer_ids: Set of wikipedia ID
    :param dict mapping: Mapping between wiki ID and title, will be updated
    :return: None
    """
    attrs = dict(re.findall(r'([^\s=]+)="([^"]+)"', content))
    print >> sys.stderr, 'Processing [%s]...\r' % attrs['id'],

    if attrs['id'] not in soccer_ids:
        return
    else:
        soccer_ids.remove(attrs['id'])

    mapping[attrs['id']] = attrs['title']
    fout = os.path.join(output_dir, '%s' % attrs['id'])
    with open(fout, 'w') as f:
        f.write(content.encode('utf8'))

    print >> sys.stderr, '\rFound article [%s] %s' % (attrs['id'], attrs['title'])


@click.command()
@click.argument('soccer_ids', type=click.File('r'))
@click.argument('input_file', type=click.File('r'))
@click.argument('output_dir', type=click.Path(exists=True, file_okay=False))
@click.argument('output_mapping', type=click.File('w'))
def main(soccer_ids, input_file, output_dir, output_mapping):
    """
    this script extracts all the articles whose id is contained in the input list
    (one id per line) and saves each article in a file whose name is the id of
    the article itself.
    the input of this script is a single big file with all the articles
    in the usual format <doc id=.. title=.. url=..> .. </doc>
    """
    soccer_ids = {row.strip().decode('utf8') for row in soccer_ids}

    mapping = {}
    for i, rows in enumerate(iter_split(input_file, lambda row: '</doc>' in row)):
        article = '\n'.join(rows).decode('utf8')
        process_article(article, soccer_ids, mapping, output_dir)

        if len(soccer_ids) == 0:
            break

    json.dump(mapping, output_mapping, indent=2)
    print >> sys.stderr, '\rProcessed %d articles' % i

if __name__ == '__main__':
    main()
