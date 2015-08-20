# -*- encoding: utf-8 -*-

import os
if __name__ == '__main__' and __package__ is None:
    os.sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import click
import json
from lib.to_assertions import to_assertions
from collections import defaultdict
from date_normalizer import DateNormalizer
from lib.scoring import compute_score, AVAILABLE_SCORES


def read_sentences(rows):
    sentences = defaultdict(list)
    for row in rows:
        cols = row[:-1].decode('utf8').split('\t')
        if cols[0]:
            sentences[cols[0]].append(cols)
    return sentences


def score_fe(fe_format, fe_score_type, frame_conf, role_conf, link_conf):
    if fe_score_type == 'nothing':
        return 

    if fe_format == 'uri':
        if fe_score_type == 'svm':
            return role_conf
        elif fe_score_type == 'link':
            return link_conf
        elif fe_score_type == 'both':
            return 2 * (role_conf * link_conf) / (role_conf + link_conf)
    else:
        return role_conf


def to_labeled(sentences, fe_score_type):
    normalizer = DateNormalizer()
    labeled = []
    for sentence_id, rows in sentences.iteritems():
        lu = [x for x in rows if x[6] == 'LU']
        if len(lu) == 0:
            print 'Could not find LU for sentence %s' % sentence_id
        elif len(lu) > 1:
            print 'More than 1 LU for sentence %s, taking first' % sentence_id
            lu = lu[0]
        else:
            lu = lu[0]
        
        if sentence_id == '1115184.2':
            import pdb; pdb.set_trace()

        fe_list = []
        for _, _, token, pos, lemma, frame, role, frame_c, role_c, link_c, uri in rows:

            if role not in {'O', 'LU'}:
                fe_format = 'uri' if uri.startswith('http://') else 'literal'
                score = score_fe(fe_format, fe_score_type, float(frame_c),
                                 float(role_c), float(link_c))

                fe_list.append({
                    'chunk': token,
                    'type': 'core',
                    fe_format: uri if fe_format == 'uri' else lemma,
                    'FE': role,
                    'score': float(score) if score is not None else None
                })

        sentence = ' '.join(x[2] for x in rows)
        labels = {
            'id': sentence_id,
            'frame': frame,
            'lu': lu[2] if lu else None,
            'sentence': sentence,
            'FEs': fe_list,
        }

        # normalize and annotate numerical expressions
        for (start, end), tag, norm in normalizer.normalize_many(sentence):
            labels['FEs'].append({
                'chunk': sentence[start:end],
                'FE': tag,
                'type': 'extra',
                'literal': norm
            })

        labeled.append(labels)
    return labeled


@click.command()
@click.argument('classified-output', type=click.File('r'))
@click.argument('id-to-title', type=click.File('r'))
@click.argument('output-file', type=click.File('w'))
@click.argument('triple-scores', type=click.File('w'))
@click.option('--sentence-score', type=click.Choice(['arithmetic-mean', 'weighted-mean',
                                                     'f-score', 'nothing']),
              default='weighted-mean')
@click.option('--fe-score', type=click.Choice(['svm', 'link', 'both', 'nothing']),
              default='nothing')
@click.option('--core-weight', default=2)
@click.option('--format', default='nt')
def main(classified_output, output_file, id_to_title, triple_scores, \
         format, sentence_score, core_weight, fe_score):

    sentences = read_sentences(classified_output)
    labeled = to_labeled(sentences, fe_score)

    if sentence_score != 'nothing':
        for sentence in labeled:
            sentence['score'] = compute_score(sentence, sentence_score, core_weight)

    mapping = json.load(id_to_title)
    processed, discarded = to_assertions(labeled, mapping, output_file,
                                         triple_scores, format)


if __name__ == '__main__':
    main()
