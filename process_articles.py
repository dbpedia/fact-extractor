import click
import re
import os
import json
import sys


DEBUG = True


def iter_split(iterator, split):
    acc = []
    for item in iterator:
        acc.append(item)
        if split(item):
            yield acc
            acc = []


def process_article(content, soccer_ids, tokens, mapping, output_dir, max_words):
    attrs = dict(re.findall(r'([^\s=]+)="([^"]+)"', content))
    if attrs['id'] not in soccer_ids:
        return
    else:
        soccer_ids.remove(attrs['id'])

    mapping[attrs['id']] = attrs['url']
    all_sentences = re.split(r'\.\s+', content)

    i = 0
    for sentence in all_sentences:
        if len(sentence.split(' ')) < max_words and \
                any(token in sentence for token in tokens):

            fout = os.path.join(output_dir, '%s.%d' % (attrs['id'], i))
            with open(fout, 'w') as f:
                f.write(sentence.encode('utf8'))
            i += 1

    if DEBUG:
        print >> sys.stderr, "%6d %10s %30s %5d sentences%s" % (
                len(soccer_ids), attrs['id'], attrs['title'], i,
                ' (skipped)' if i == 0 else '')


@click.command()
@click.argument('soccer_ids', type=click.File('r'))
@click.argument('input_file', type=click.File('r'))
@click.argument('token_list', type=click.File('r'))
@click.argument('output_dir', type=click.Path(exists=True, file_okay=False))
@click.argument('output_mapping', type=click.File('w'))
@click.option('--max-words', default=25)
def main(soccer_ids, input_file, token_list, output_dir, output_mapping, max_words):
    soccer_ids = {row.strip().decode('utf8') for row in soccer_ids}
    tokens = {row.strip().decode('utf8') for row in token_list}

    mapping = {}
    for i, rows in enumerate(iter_split(input_file, lambda row: '</doc>' in row)):
        article = '\n'.join(rows).decode('utf8')
        process_article(article, soccer_ids, tokens, mapping, output_dir, max_words)

        if len(soccer_ids) == 0:
            break

    json.dump(mapping, output_mapping, indent=2)

    if DEBUG:
        print >> sys.stderr, 'Processed %d articles' % i

if __name__ == '__main__':
    main()
