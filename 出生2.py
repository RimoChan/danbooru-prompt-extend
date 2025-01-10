import os
import random
import hashlib
from pathlib import Path

from tqdm import tqdm

from danbooru_loader import 超源
from 标签处理 import 时间标签
from 分离 import 分离每个人tags


更好图 = tqdm(desc='更好图')


rating = {
    's': 'sensitive',
    'g': 'general',
    'q': 'questionable',
    'e': 'explicit',
}
jj = []

random.seed(1)
os.makedirs('output/1_A', exist_ok=True)
for name, image, meta in tqdm(超源(子包范围=range(0, 110), id范围=range(500000, 9999999), fav_count范围=range(2, 9999999), 要的tags=['2girls', '3girls'])):
    原始tags = meta['tag_string_general'].split()
    if ('boys ' in ' '.join(原始tags)) or '1boy' in 原始tags:
        continue

    人, 每个人的tags, 剩下的剩下的 = 分离每个人tags(image, 原始tags)
    if not 每个人的tags or min([len(i) for i in 每个人的tags]) <= 1:
        continue
    print(人, 每个人的tags, 剩下的剩下的)

    剩下的改 = []
    啊 = 'αβγδε'
    for i, tags in enumerate(每个人的tags):
        剩下的改 += [f'{啊[i]} {j}' for j in tags]
    剩下的改 += [*剩下的剩下的]

    新tags = 人 + meta['tag_string_character'].split() + [rating[meta['rating']]] + 剩下的改 + meta['tag_string_artist'].split() + 时间标签(meta['created_at'])
    新tags = [i.replace('_', ' ') for i in 新tags]
    assert len(新tags) == len({*新tags})
    s = ', '.join(新tags)
    打散 = hashlib.md5(s.encode('utf8')).hexdigest()[:4]
    image.save(f'output/1_A/{打散}_{name}')
    with open(f'output/1_A/{打散}_{Path(name).stem}.txt', 'w', encoding='utf8') as f:
        f.write(s)

    jj.append(name)
    if len(jj) > 100:
        print('\n\n\n', jj)
        exit()
    更好图.update(1)
