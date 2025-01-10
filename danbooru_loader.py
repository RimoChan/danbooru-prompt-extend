import re
import os
import pickle
import tarfile
from pathlib import Path

import orjson
from tqdm import tqdm
from PIL import Image
from rimo_storage.cache import disk_cache


danbooru2023_path = Path('R:/danbooru2023')
读取失败 = tqdm(desc='读取失败')


def _拆分() -> dict:
    os.makedirs('tags缓存', exist_ok=True)
    res = {}
    with open(danbooru2023_path/'metadata/posts.json', encoding='utf8') as f:
        for line in tqdm(f, desc='拆分tags'):
            d = orjson.loads(line)
            n = d['id'] % 1000
            res.setdefault(n, {})[d['id']] = d
    for k, v in res.items():
        with open(f'tags缓存/{k}.pickle', 'wb') as f:
            f.write(pickle.dumps(v))


def _源(子包, id范围, fav_count范围, 要的tags):
    def 标签过滤(tags: list[str]):
        if {'comic', 'monochrome', 'sketch', 'speech_bubble', 'furry'} & set(tags):
            return False
        for tag in 要的tags:
            if tag in tags:
                return True
        return False
    if not Path(f'tags缓存/{子包}.pickle').is_file():
        _拆分()
    d = pickle.load(open(f'tags缓存/{子包}.pickle', 'rb'))
    t = tarfile.open(danbooru2023_path/f'original/data-{str(子包).zfill(4)}.tar')
    for i in t.getmembers():
        if i.name.endswith('.png') or i.name.endswith('.jpg'):
            n = int(re.findall('\d+', i.name)[0])
            if n not in d:
                读取失败.update(1)
                continue
            if n in id范围 and d[n]['fav_count'] in fav_count范围:
                if not 标签过滤(d[n]['tag_string_general'].split()):
                    continue
                try:
                    image = Image.open(t.extractfile(i))
                    image.thumbnail((1024, 1024))
                    image.load()
                except Exception:
                    读取失败.update(1)
                else:
                    yield i.name.removeprefix('./'), image, d[n]


@disk_cache(serialize='pickle')
def 源(子包, id范围, fav_count范围, 要的tags):
    return [*_源(子包, id范围, fav_count范围, 要的tags)]


def 超源(子包范围, id范围, fav_count范围, 要的tags):
    for 子包 in tqdm(子包范围, desc='子包', ncols=60):
        yield from 源(子包, id范围, fav_count范围, 要的tags)
