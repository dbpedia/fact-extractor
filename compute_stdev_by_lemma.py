# coding: utf-8

import sys
import codecs
import json
from collections import defaultdict, OrderedDict

#i = codecs.open('top-50-token2lemma.sorted', 'rb', 'utf-8')
i = codecs.open(sys.argv[1], 'rb', 'utf-8')
j = defaultdict(list)
lines = [l.strip() for l in i.readlines()]
for l in lines:
    items = l.split('\t')
    j[items[1]].append(items[0])
    
#g = json.load(codecs.open('/home/fox/srl/ranking/top-50/tokens/stdevs.json', 'rb', 'utf-8'), encoding='utf-8')
g = json.load(codecs.open(sys.argv[2], 'rb', 'utf-8'), encoding='utf-8')
jg = {}
for lemma, tokens in j.iteritems():
    jg[lemma] = 0.0
    for toke in tokens:
        jg[lemma] += g.get(toke, 0.0)
        
d = OrderedDict(sorted(jg.items(), key=lambda x: x[1], reverse=True))
#json.dump(d, open('../ranking/top-50/stdevs-by-lemma.json', 'wb'), ensure_ascii=False, indent=2)
json.dump(d, open('stdevs-by-lemma.json', 'wb'), ensure_ascii=False, indent=2)
