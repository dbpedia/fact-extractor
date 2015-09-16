import click
import re
import os
import json
import sys


def _iter_split(iterator, split):
    acc = []
    for item in iterator:
        acc.append(item)
        if split(item):
            yield acc
            acc = []


def process_article(content, tokens, sentence_wid, output_dir, min_words, max_words):
    """
    processes an article with format <doc id=... title=... url=...> ... </doc>
    and extracts all the sentences whose length is between min_words and max_words
    and contains at least one token in the specified set
    sentences are split by a dot followed by at least one space

    :param str content: Text of the article including start and end doc tags
    :param set token: Set of tokens
    :param dict sentence_wid: Mapping between sentence and wikipedia ID
    :param str output_dir: Directory where to save the sentences
    :param int min_words: Only consider sentences longer than this
    :param int max_words: Only consider sentence shorter than this
    """
    attrs = dict(re.findall(r'([^\s=]+)="([^"]+)"', content))

    i = 0
    for row in content.split('\n')[1:-1]:
        all_sentences = re.split(r'\.\s+', row)
        for sentence in all_sentences:
            snt_tokens = sentence.split()
            if min_words < len(snt_tokens) < max_words and \
                    any(token in snt_tokens for token in tokens):

                wid = '%s.%d' % (attrs['id'], i)
                norm = ''.join(c for c in sentence if c.isalnum())
                sentence_wid[norm] = wid
                fout = os.path.join(output_dir, wid)
                with open(fout, 'w') as f:
                    f.write(sentence.encode('utf8'))
                i += 1

    print >> sys.stderr, "%10s %30s %5d sentences%s" % (
                         attrs['id'], attrs['title'], i,
                         ' (skipped)' if i == 0 else '')
    return i


@click.command()
@click.argument('input_file', type=click.File('r'))
@click.argument('token_list', type=click.File('r'))
@click.argument('sentence-to-wid', type=click.File('w'))
@click.argument('output_dir', type=click.Path(exists=True, file_okay=False))
@click.option('--min-words', default=5)
@click.option('--max-words', default=25)
def main(input_file, token_list,sentence_to_wid, output_dir, min_words, max_words):
    """
    this script extracts all the sentences of a certain length from a file
    containing wikipedia articles one after the other contained
    inside <doc>...</doc> xml tags
    """
    tokens = {row.strip().decode('utf8') for row in token_list}

    mapping, count = {}, 0
    for i, rows in enumerate(_iter_split(input_file, lambda row: '</doc>' in row)):
        article = '\n'.join(rows).decode('utf8')
        count += process_article(article, tokens, mapping, output_dir,
                                 min_words, max_words)
    json.dump({k.encode('utf8'): v for k, v in mapping.iteritems()},
               sentence_to_wid, indent=2)
    print >> sys.stderr, 'Processed %d articles, extracted %d sentences' % (i, count)


if __name__ == '__main__':
    main()
