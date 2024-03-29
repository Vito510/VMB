#select one pack randomly using its weight as a probability

import json
import random

def pick(mode):
    if mode == 0:
        e = '_I'
    elif mode == 1:
        e = '_O'

    pack = select()

    if e[1] in pack['type']:
        with open(pack['dir']+e+'.txt','r', encoding='utf-8') as f:
            lines = f.readlines()
            return random.choice(lines).replace('\n','')
    else:
        return pick(mode)


def select():
    x = json.load(open('./config/config.json','r',encoding='utf-8'))
    x = x['packs']
    total = 0
    for i in x:
        total += i['weight']
    r = random.uniform(0, total)
    for i in x:
        r -= i['weight']
        if r <= 0:
            return i
