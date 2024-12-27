import re
import os
import pickle
import tarfile
from pathlib import Path

import orjson
from tqdm import tqdm
from PIL import Image
from rimo_storage.cache import disk_cache


danbooru2023_path = Path('S:/danbooru2023')


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


def _源(子包, id范围, fav_count范围):
    def 标签过滤(tags: list[str]):
        if {'comic', 'monochrome', 'sketch', 'speech_bubble', 'furry'} & set(tags):
            return False
        if 'indoors' in tags or 'outdoors' in tags:
            return True
        return False
    if not Path(f'tags缓存/{子包}.pickle').is_file():
        _拆分()
    d = pickle.load(open(f'tags缓存/{子包}.pickle', 'rb'))
    t = tarfile.open(danbooru2023_path/f'original/data-{str(子包).zfill(4)}.tar')
    for i in t.getmembers():
        if i.name.endswith('.png') or i.name.endswith('.jpg'):
            n = int(re.findall('\d+', i.name)[0])
            if n in id范围 and d[n]['fav_count'] in fav_count范围:
                if not 标签过滤(d[n]['tag_string_general'].split()):
                    continue
                try:
                    image = Image.open(t.extractfile(i))
                    image.thumbnail((1024, 1024))
                except Exception:
                    pass
                else:
                    yield i.name.removeprefix('./'), image, d[n]


@disk_cache(serialize='pickle')
def 源(子包, id范围, fav_count范围):
    return [*_源(子包, id范围, fav_count范围)]


def 超源(子包范围, id范围, fav_count范围):
    for 子包 in 子包范围:
        yield from 源(子包, id范围, fav_count范围)
