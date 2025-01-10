import os
import random
os.environ['ONNX_MODE'] = 'CUDA'

from PIL import Image
from rimo_storage.cache import disk_cache
from imgutils.detect import detect_person
from imgutils.tagging.mldanbooru import get_mldanbooru_tags

from 标签处理 import 分离人数标签


detect_person = disk_cache(serialize='pickle')(detect_person)
get_mldanbooru_tags = disk_cache(serialize='pickle')(get_mldanbooru_tags)


def iou(boxA, boxB):
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
    interArea = max(0, xB - xA) * max(0, yB - yA)
    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
    iou = interArea / (boxAArea + boxBArea - interArea)
    return iou


def 切人(image):
    全box = sorted([i[0] for i in detect_person(image)])
    if len(全box) <= 1 or len(全box) >= 5:
        return
    for box1 in 全box:
        for box2 in 全box:
            if box1 is not box2 and iou(box1, box2) > 0.4:
                return
    面积 = [(c-a)*(d-b) for a, b, c, d in 全box]
    if min(面积) < max(面积) / 4:
        return
    for box in 全box:
        yield image.crop(box)


def 分离每个人tags(image: Image.Image, 原始tags: list[str]) -> tuple[list[str], list[list[str]], list[str]]:
    切 = [*切人(image)]
    人, 剩下的 = 分离人数标签(原始tags)
    if not 切:
        return 人, [], 剩下的
    每个人的tags = []
    for i, 人图 in enumerate(切人(image)):
        检测tags = get_mldanbooru_tags(人图, threshold=0.4)
        if 检测tags.get('2girls', 0) > 0.8 or 检测tags.get('3girls', 0) > 0.8:
            return 人, [], 剩下的
        每个人的tags.append({*检测tags})
    公交 = {*每个人的tags[0]}
    for tags in 每个人的tags:
        公交 &= tags
    for tags in 每个人的tags:
        tags -= 公交
        tags &= {*剩下的}
    剩下的剩下的 = {*剩下的}
    for tags in 每个人的tags:
        剩下的剩下的 -= tags
    公交 = {*每个人的tags[0]}
    for tags in 每个人的tags:
        公交 &= tags
    for tags in 每个人的tags:
        tags -= 公交
        tags &= {*剩下的}
    剩下的剩下的 = {*剩下的}
    for tags in 每个人的tags:
        剩下的剩下的 -= tags
    每个人的tags = [[*i] for i in 每个人的tags]
    for i in 每个人的tags:
        random.shuffle(i)
    剩下的剩下的 = [*剩下的剩下的]
    random.shuffle(剩下的剩下的)
    return 人, 每个人的tags, 剩下的剩下的
