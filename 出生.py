import os
import random
import hashlib
from pathlib import Path
from datetime import datetime

from tqdm import tqdm

import 补充
from danbooru_loader import 超源


def 人数标签(s: str):
    if s in ('1girl', '1boy'):
        return True
    if s.endswith('girls') or s.endswith('boys'):
        return True
    return False


def 时间标签(iso_time: str):
    year = datetime.fromisoformat(iso_time).year
    year_tag = 'newest'
    for t, y in [('oldest', 2017), ('old', 2019), ('modern', 2020), ('recent', 2022)]:
        if year <= y:
            year_tag = t
            break
    res = [f'year {year}', year_tag]
    random.shuffle(res)
    return res


if __name__ == '__main__':
    random.seed(1)
    tq_img = tqdm(desc='写入图片')
    tq_tag = tqdm(desc='写入tags')
    os.makedirs('output/1_A', exist_ok=True)
    for name, image, meta in 超源(子包范围=range(0, 49), id范围=range(2000000, 9999999), fav_count范围=range(5, 9999999)):
        原始tags = meta['tag_string_general'].split()
        tags = 原始tags.copy()

        if 'indoors' in tags:
            tags.extend(补充.发现地板(image))
            tags.extend(补充.发现门(image))
        tags.extend(补充.物件上色(image, 原始tags))
        tags.extend(补充.物件计数(image, 原始tags))

        差tags = set(tags) - set(原始tags)
        if len(差tags) >= 2:
            人 = [i for i in 原始tags if 人数标签(i)]
            剩下的 = [i for i in 原始tags if not 人数标签(i)]
            if len(剩下的) > 14:
                限制标签数 = random.randint(14, (14 + len(剩下的))//2)
                剩下的 = random.sample(剩下的, 限制标签数)
            剩下的 = 剩下的 + list(差tags)
            random.shuffle(剩下的)
            新tags = 人 + meta['tag_string_character'].split() + 剩下的 + meta['tag_string_artist'].split() + 时间标签(meta['created_at'])
            新tags = [i.replace('_', ' ') for i in 新tags]
            s = ', '.join(新tags)
            # 人数 ||| 角色名称 ||| 一般标签 ||| 艺术家  ||| 年份修饰语
            # 这里的prompt格式为https://arxiv.org/html/2409.19946v1的prompt的子序列
            打散 = hashlib.md5(s.encode('utf8')).hexdigest()[:3]
            image.save(f'output/1_A/{打散}_{name}')
            with open(f'output/1_A/{打散}_{Path(name).stem}.txt', 'w', encoding='utf8') as f:
                f.write(s)
            tq_img.update(1)
            tq_tag.update(len(差tags))
