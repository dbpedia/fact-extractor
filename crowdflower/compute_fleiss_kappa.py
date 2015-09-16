# -*- encoding: utf-8 -*-

import click
from utils import read_full_results, computeFleissKappa
from os import sys


def compute_matrix(cf_results, num_judgments):
    """ Given the results from crowdflower creates the matrix necessary to compute the
    fleiss agreement

    :param dict cf_results: Results from crowdflower for each sentence
    :param int num_judgments: Consider only the first # answers, skip if not enough
    :return: The matrix as list of lists of ints
    :rtype: list
    """
    categories = set()
    for sentence_id, data in cf_results.iteritems():
        for key, value in data.iteritems():
            if key not in {'frame', 'lu', 'sentence'}:
                categories = categories.union(set(x['answer'] for x in value['answers']))
    categories = list(categories)

    matricione = []
    for sentence_id, data in cf_results.iteritems():
        for key, value in data.iteritems():
            if key in {'frame', 'lu', 'sentence'} or value['judgments'] < num_judgments:
                continue

            answers = sorted(value['answers'], key=lambda x: x['trust'],
                             reverse=True)
            judgments = [0] * len(categories)
            for answer in answers[:num_judgments]:
                judgments[categories.index(answer['answer'])] += 1
            matricione.append(judgments)

    return matricione


@click.command()
@click.argument('crowdflower-output', type=click.File('r'))
@click.option('--num-judgments', default=3,
              help='Consider only this number of results, skip if not enough')
def main(crowdflower_output, num_judgments):
    """
    this script computes the agreement of judgments given in the crowdflower
    job using a metric called Fleiss kappa
    :param file crowdflower_output: CSV file containing the results from crowdflower
    :param int num_judgments: Consider only this number of results, skip if not enough
    """
    cf_results = read_full_results(crowdflower_output)
    mat = compute_matrix(cf_results, num_judgments)
    print computeFleissKappa(mat)


if __name__ == '__main__':
    main()
