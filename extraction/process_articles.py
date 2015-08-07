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


def process_article(content, soccer_ids, mapping, output_dir, max_words):
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
@click.option('--max-words', default=25)
def main(soccer_ids, input_file, output_dir, output_mapping, max_words):
    soccer_ids = {row.strip().decode('utf8') for row in soccer_ids}

    mapping = {}
    for i, rows in enumerate(iter_split(input_file, lambda row: '</doc>' in row)):
        article = '\n'.join(rows).decode('utf8')
        process_article(article, soccer_ids, mapping, output_dir, max_words)

        if len(soccer_ids) == 0:
            break

    json.dump(mapping, output_mapping, indent=2)
    print >> sys.stderr, '\rProcessed %d articles' % i

if __name__ == '__main__':
    main()
