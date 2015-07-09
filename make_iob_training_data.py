#!/usr/bin/python
# -*- coding: utf-8 -*-

###
# Translate sentences that are labeled
# according to the internal specs
# into IOB data for NER training
###

'''
Created on Oct 04, 2013

@author: marco.fossati@maluuba.com
@author: justin@maluuba.com
'''

from collections import defaultdict
import codecs
import re
import sys
import os

## CONFIG
FILEIN = 'all_generated_data.tsv'
FILEOUT_SUFFIX = "company_IOB_gold.txt"
## END CONFIG

DIACRITICS = {
    u'à': 'a',
    u'á': 'a',
    u'â': 'a',
    u'ä': 'a',
    u'å': 'a',
    u'À': 'A',
    u'Á': 'A',
    u'Â': 'A',
    u'Ã': 'A',
    u'æ': 'ae',
    u'Æ': 'AE',
    u'ç': 'c',
    u'Ç': 'C',
    u'ê': 'e',
    u'é': 'e',
    u'ë': 'e',
    u'è': 'e',
    u'Ê': 'E',
    u'Ë': 'E',
    u'É': 'E',
    u'È': 'E',
    u'ï': 'i',
    u'í': 'i',
    u'î': 'i',
    u'ì': 'i',
    u'Í': 'I',
    u'Ì': 'I',
    u'Î': 'I',
    u'Ï': 'I',
    u'ñ': 'n',
    u'Ñ': 'N',
    u'œ': 'oe',
    u'Œ': 'OE',
    u'ô': 'o',
    u'ö': 'o',
    u'ò': 'o',
    u'õ': 'o',
    u'ó': 'o',
    u'ø': 'o',
    u'Ó': 'O',
    u'Ô': 'O',
    u'Õ': 'O',
    u'Ø': '0',
    u'Ö': 'O',
    u'Ò': 'O',
    u'š': 's',
    u'Š': 'S',
    u'ú': 'u',
    u'ü': 'u',
    u'û': 'u',
    u'ù': 'u',
    u'Ù': 'U',
    u'Ú': 'U',
    u'Ü': 'U',
    u'Û': 'U',
    u'ÿ': 'y',
    u'Ÿ': 'Y',
    u'ý': 'y',
    u'Ý': 'Y',
    u'ž': 'z',
    u'Ž': 'Z',
    u'-':' ',
    u"'":" ",
    u'–':' '   
}


def normalize(chars):
    # Replace ' - / . with space, then lowercase
    chars = re.sub(r'[\'\-/\.]', ' ', chars).lower()
    chars = re.sub(r'\s+', ' ', chars)
    # Remove punctuation and brackets
    chars = re.sub(r'[\'\"\?,;!\(\)]', '', chars)
    # Remove diacritcs
    #for diacritic, plain in DIACRITICS.iteritems():
    #    chars = chars.replace(diacritic, plain)
    return chars


def label_sentence_tokens(entity, entity_label, string_sentence, sentence_tags):
    entity_value = entity
    value_tokens = entity_value.split()
    # Get sentence index of first entity token
    first_entity_token_index = string_sentence.find(entity_value)
    # Write an error if the entity token has not a match in the sentence
    if first_entity_token_index != -1:
        # The number of spaces before the 1st entity token corresponds to
        # the starting index of the sentence tokens that must be labeled
        start_index = string_sentence[:first_entity_token_index].count(' ')
        entity = list()
        # Assign beginning label to first token
        entity.append((value_tokens[0], 'B-' + entity_label))
        # Assign inside labels to remaining tokens
        for token in value_tokens[1:]:
            entity.append((token, 'I-' + entity_label))
            # Update sentence tokens with labeled entities
        sentence_tags[start_index:start_index + len(entity)] = entity
    else:
        sys.stderr.write('Couldn\'t find "%s" in "%s"\n' % (entity_value, string_sentence))
    return 0


def assign_iob_labels(entities, tokens):
    # Rebuild sentence
    sentence = ' '.join(tokens)
    # Assign default outside label to sentence tokens
    structured_sentence = list()
    #for t in tokens:
    #    structured_sentence.append((t, 'O'))
    # Get entities
    for entity_label, entity in entities.iteritems():
        label_sentence_tokens(entity, entity_label, sentence, structured_sentence)
    return structured_sentence


def pre_process(line):
    # Remove extra tabs
    line = re.sub(r'\t+', '\t', line)
    items = line.strip().split('\t')
    # Normalize
    sentence = normalize(items[0])
    # Tokenize on whitespaces
    tokens = sentence.split()
    return items, tokens


def translate_to_iob(filein=FILEIN):
    #result = defaultdict(list)
    result = []
    with codecs.open(filein, 'rb', 'utf-8') as i:
        for line in i.readlines():
            line = line.strip()
            items = line.split('|')
            tokens = items[0].split()
            #items, tokens = pre_process(line)
            # Split on file naming convention
            #primary = os.path.splitext(filein.replace('generated_', '').split('_')[0])[0]
            structured_sentence = assign_iob_labels(items, tokens)
            #result[primary].append(structured_sentence)
            result.append(structured_sentence)
    print result
    return result


#def write_output(data_map, fileout_suffix=FILEOUT_SUFFIX):
#    for primary, data in data_map.iteritems():
#        print "Writing %d queries for %s" %(len(data), primary)
#        output_path = os.path.join(primary.lower(), 'data', fileout_suffix)
#        with codecs.open(output_path, 'wb', 'utf-8') as o:
#            for tagged_query in data:
#                for (token, tag) in tagged_query:
#                    o.write(token + u'\t' + tag + u'\n')
#                o.write(u'\n')
#        print "Done writing queries for %s" % primary
def write_output(data, fileout='porcodio'):
    return 0

if __name__ == "__main__":
    #if len(sys.argv) == 2:
    #    data = translate_to_iob(sys.argv[1])
    #    write_output(data)
    #else:
    #    for domain in ['music', 'finance', 'sports', 'weather']:
    #        data = translate_to_iob(domain + '.tsv')
    #        write_output(data)
    #print "Done"
    data = translate_to_iob(sys.argv[1])
    write_output(data)
