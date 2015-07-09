# coding: utf-8
from collections import Counter, OrderedDict
import codecs
import json
import sys
f = codecs.open(sys.argv[1], 'rb', 'utf-8')
lines = f.readlines()
freq = Counter([l.split('\t')[1].strip() for l in lines])
voc = OrderedDict(sorted(freq.items(), key=lambda x: x[1], reverse=True))
json.dump(voc, codecs.open('frequencies.json', 'wb', 'utf-8'), ensure_ascii=False, indent=2)
