import HTMLParser
import csv
import re


def read_full_results(results_file):
    """ Reads and aggregates the results

    :param file results_file: an open file with the CSV data
    :return: a dictionary with data for every sentence
    :rtype: dict
    """
    h = HTMLParser.HTMLParser()
    processed = {}

    # TODO csv lib doesn't handle unicode
    results = csv.DictReader(results_file)
    fields = results.fieldnames
    fe_amount = len([f for f in fields if re.match(r'fe[0-9]{2}$', f)])

    # Include gold
    for row in results:
        # Uncomment the following line to skip gold
        # if row['_golden'] == 'true': continue
        # Avoid Unicode encode/decode exceptions
        for k, v in row.iteritems():
            row[k] = v.decode('utf-8') if v else u''
        sentence_id = row['id']
        sentence = h.unescape(row['sentence'])

        # initialize data structure with sentence, frame, lu and entity list
        if sentence_id not in processed:
            processed[sentence_id] = dict()
            processed[sentence_id]['sentence'] = sentence
            processed[sentence_id]['frame'] = row['frame']
            processed[sentence_id]['lu'] = row['lu']
            for n in xrange(0, fe_amount):
                entity = row['orig_fe%02d' % n]
                if entity:
                    processed[sentence_id][entity] = {
                        'judgments': 0,
                        'answers': list()
                    }

        # update judgments for each entity
        for n in xrange(0, fe_amount):
            entity = row['orig_fe%02d' % n]
            answer = row.get('fe%02d' % n)
            if entity and answer:
                processed[sentence_id][entity]['judgments'] += 1
                processed[sentence_id][entity]['answers'].append({
                    'answer': answer,
                    'trust': row.get('_trust', row.get('fe%02d:confidence' % n))
                })

    return processed


def computeFleissKappa(mat):
    """
    Computes the Fleiss' Kappa value as described in (Fleiss, 1971) 
    https://en.wikibooks.org/wiki/Algorithm_Implementation/Statistics/Fleiss%27_kappa#Python
    """

    n = sum(mat[0])  # PRE : every line count must be equal to n
    assert all(sum(line) == n for line in mat[1:]), "Line count != %d (n value)." % n
    N = len(mat)
    k = len(mat[0])
    
    # Computing p[]
    p = [0.0] * k
    for j in xrange(k):
        p[j] = 0.0
        for i in xrange(N):
            p[j] += mat[i][j]
        p[j] /= N*n
    
    # Computing P[]    
    P = [0.0] * N
    for i in xrange(N):
        P[i] = 0.0
        for j in xrange(k):
            P[i] += mat[i][j] * mat[i][j]
        P[i] = (P[i] - n) / (n * (n - 1))
    
    # Computing Pbar
    Pbar = sum(P) / N
    
    # Computing PbarE
    PbarE = 0.0
    for pj in p:
        PbarE += pj * pj
    
    kappa = (Pbar - PbarE) / (1 - PbarE)
    return kappa
