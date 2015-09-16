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
from resources.soccer_lu2frame_dbtypes import LU_FRAME_MAP


_frame_map = defaultdict(dict)
def _get_fe_type(frame_name, fe_name):
    """ Given a frame and a frame element returns the type of the fe (code/extra)

    :param str frame_name: Name of the frame
    :param str fe_name: Name of the FE
    :return: The type of the FE
    :rtype: str
    """
    if not _frame_map:
        for lu in LU_FRAME_MAP:
            for frame in lu['lu']['frames']:
                for fe in frame['FEs']:
                    _frame_map[frame['frame']][fe.keys()[0]] = fe.values()[0]

    return _frame_map.get(frame_name, {}).get(fe_name)

def read_sentences(rows):
    """ Aggregates a sequence of rows of tab-separated fields by its first value

    :param list rows: List of rows
    :return: A dictionary with first field -> all rows with that field as first
    :rtype: dict
    """
    sentences = defaultdict(list)
    for row in rows:
        cols = row[:-1].decode('utf8').split('\t')
        if cols[0]:
            sentences[cols[0]].append(cols)
    return sentences


def score_fe(fe_format, fe_score_type, frame_conf, role_conf, link_conf):
    """ computes the score for the given frame element

    :param str fe_format: Format of the FE, uri or literal
    :param float role_conf: Confidence for the role (coming from the SVM)
    :param float frame_conf: Confidence for the frame (coming from the SVM)
    :param float link_conf: Confidence for the link (if the format is uri)
    :param str fe_score_type: Which score to use for uris: svm, link or both (f1)
    """
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
    """ Transform the sentences into labeled data ready to be serialized into triples

    :param dict sentences: Labeled data for each sentence
    :param str fe_score_type: Which score to use for uris: svm, link or both (f1)
    """
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
        
        fe_dict = {}
        for _, _, token, pos, lemma, frame, role, frame_c, role_c, link_c, uri in rows:

            if role not in {'O', 'LU'}:
                fe_format = 'uri' if uri.startswith('http://') else 'literal'
                score = score_fe(fe_format, fe_score_type, float(frame_c),
                                 float(role_c), float(link_c))

                fe_dict[token] = {
                    'chunk': token,
                    'type': _get_fe_type(frame, role) or 'out_of_frame',
                    fe_format: uri if fe_format == 'uri' else lemma,
                    'FE': role,
                    'score': float(score) if score is not None else None
                }

        sentence = ' '.join(x[2] for x in rows)

        # normalize and annotate numerical expressions
        for (start, end), tag, norm in normalizer.normalize_many(sentence):
            chunk = sentence[start:end]
            for existing in fe_dict.keys():
                 if existing == chunk:  # was normalized by classifier
                    fe_dict[existing]['literal'] = norm
                    break
            else:
                fe_dict[chunk] = {
                    'chunk': chunk,
                    'FE': tag,
                    'type': _get_fe_type(frame, tag) or 'extra',
                    'literal': norm
                }

        labeled.append({
            'id': sentence_id,
            'frame': frame,
            'lu': lu[2] if lu else None,
            'sentence': sentence,
            'FEs': fe_dict.values(),
        })

    return labeled


@click.command()
@click.argument('classified-output', type=click.File('r'))
@click.argument('id-to-title', type=click.File('r'))
@click.argument('output-file', type=click.File('w'))
@click.argument('triple-scores', type=click.File('w'))
@click.option('--sentence-score', type=click.Choice(['arithmetic-mean', 'weighted-mean',
                                                     'f-score', 'nothing']),
              default='weighted-mean',
              help='How to combine FEs scores into a sentence score')
@click.option('--fe-score', type=click.Choice(['svm', 'link', 'both', 'nothing']),
              default='nothing', help='How to score FEs')
@click.option('--core-weight', default=2, help='Weight of core FEs wrt extra FEs')
@click.option('--format', default='nt')
def main(classified_output, output_file, id_to_title, triple_scores, \
         format, sentence_score, core_weight, fe_score):
    """
    serializes the classification result into triples
    optionally scoring sentences and/or frame elements
    """

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
