import re
import random
from datetime import datetime


def 人数标签(s: str) -> bool:
    if s in ('1girl', '1boy'):
        return True
    return bool(re.fullmatch('[0-9](girl|boy)s$', s))


def 分离人数标签(原始tags: list[str]) -> tuple[list[str], list[str]]:
    人 = [i for i in 原始tags if 人数标签(i)]
    剩下的 = [i for i in 原始tags if not 人数标签(i)]
    return 人, 剩下的


def 时间标签(iso_time: str) -> list[str]:
    year = datetime.fromisoformat(iso_time).year
    year_tag = 'newest'
    for t, y in [('oldest', 2017), ('old', 2019), ('modern', 2020), ('recent', 2022)]:
        if year <= y:
            year_tag = t
            break
    res = [f'year {year}', year_tag]
    random.shuffle(res)
    if random.random() > 0.5:
        return res
    else:
        return [res[0]]
