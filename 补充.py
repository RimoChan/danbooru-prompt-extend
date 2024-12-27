import re

from PIL import Image

import mllm


def 物件计数(image: Image.Image, tags: list[str]) -> list[str]:
    所有计数目标 = {'chair', 'desk', 'table', 'bed', 'sofa', 'couch', 'bookshelf', 'fireplace', 'cabinet', 'teapot', 'teacup', 'cup', 'handbag', 'bag', 'school_bag', 'plastic_bag', 'backpack', 'book', 'duster', 'phone', 'smartphone', 'bucket', 'box', 'mug', 'pen', 'paintbrush', 'coffee_mug', 'tissue_box', 'clock', 'flower', 'fruit', 'stuffed_toy', 'stuffed_animal', 'lamp', 'hair_dryer', 'game_controller', 'ice_cream', 'computer_keyboard', 'computer_mouse', 'couch', 'microphone', 'pillow', 'bird', 'cat', 'dog', 'rabbit', 'candle', 'poker_chip', 'can', 'energy_drink', 'vase', 'bowl', 'pot', 'cooking_pot', 'tray', 'mop', 'card', 'soda_bottle', 'cake', 'pancake', 'bread', 'locker', 'guitar', 'bottle', 'wine_bottle', 'water_bottle', 'tree', 'sunflower', 'snowman', 'sword', 'penguin', 'road_sign', 'bamboo', 'swim_ring', 'drinking_glass', 'fird', 'frog', 'railing', 'balloon', 'ball', 'lantern', 'building', 'inflatable_toy', 'mushroom', 'lamppost', 'potted_plant', 'tent', 'towel', 'butterfly', 'boat', 'car', 'bicycle', 'pillar', 'chandelier'}
    结果 = []
    for i in 所有计数目标 & set(tags):
        n = mllm.超问(image, f'How many {i} are in the image? Please answer with one number.', max_new_tokens=4)
        if n.isdigit() and int(n) > 1:
            结果.append(f'{n}{i}s')
    return 结果


def 物件上色(image: Image.Image, tags: list[str]) -> list[str]:
    所有上色目标 = {'curtains', 'chair', 'desk', 'table', 'bed', 'sofa', 'couch', 'bathtub', 'bookshelf', 'fireplace', 'cabinet', 'teapot', 'teacup', 'cup', 'handbag', 'bag', 'school_bag', 'plastic_bag', 'backpack', 'book', 'duster', 'phone', 'smartphone', 'bucket', 'box', 'mug', 'pen', 'paintbrush', 'coffee_mug', 'tissue_box', 'clock', 'flower', 'fruit', 'stuffed_toy', 'stuffed_animal', 'lamp', 'hair_dryer', 'game_controller', 'ice_cream', 'computer_keyboard', 'computer_mouse', 'couch', 'microphone', 'pillow', 'bird', 'cat', 'dog', 'rabbit', 'candle', 'poker_chip', 'can', 'energy_drink', 'vase', 'bowl', 'pot', 'cooking_pot', 'tray', 'rope', 'mop', 'card', 'soda_bottle', 'cake', 'pancake', 'bread', 'locker', 'guitar', 'bottle', 'house', 'brick_wall', 'petals', 'swim_ring', 'drinking_glass', 'fird', 'frog', 'railing', 'balloon', 'ball', 'lantern', 'building', 'inflatable_toy', 'mushroom', 'lamppost', 'potted_plant', 'tent', 'towel', 'butterfly', 'boat', 'car', 'bicycle', 'pillar', 'chandelier'}
    结果 = []
    for i in 所有上色目标 & set(tags):
        color = mllm.超问(image, f'What is the color of the {i} in the image? Please answer with one word.', max_new_tokens=4)
        if 'no' in color.split():
            continue
        结果.append(f'{color}_{i}')
    return 结果


def 发现家具(image: Image.Image, tags: list[str]) -> list[str]:
    所有家具 = {'curtains', 'chair', 'desk', 'table', 'bed', 'sofa', 'couch', 'bathtub', 'bookshelf', 'fireplace', 'cabinet'}
    结果 = re.sub('(,|\.) *', ' ', mllm.超问(image, 'What furniture items appear in the image? Please provide the names of the furniture, separated by spaces. Furniture includes table, chair, bed, cabinet, sofa, curtains, etc.', max_new_tokens=16)).split()
    结果 = set(结果) & 所有家具
    出现的家具 = 所有家具 & (set(tags) | 结果)
    for i in 出现的家具:
        color = mllm.超问(image, f'What is the color of the {i} in the image? Please answer with one word.', max_new_tokens=4)
        if 'no' in color.split():
            if i in 结果:
                结果.remove(i)
            continue
        结果.add(f'{color}_{i}')
    return list(结果)


def 发现地板(image: Image.Image) -> list[str]:
    a = mllm.超问(image, "Is the room's floor visible in the image? Please answer yes or no.", max_new_tokens=4)
    if 'yes' in a:
        material = mllm.超问(image, "What's the material of the floor in the picture? Please answer with one word, such as wooden.", max_new_tokens=4)
        if material == 'carpet':
            return [f'{material}']
        else:
            return [f'{material}_floor']
    return []


def 发现门(image: Image.Image) -> list[str]:
    a = mllm.超问(image, "Is the room's door visible in the image? Please answer yes or no.", max_new_tokens=4)
    if 'yes' in a:
        color = mllm.超问(image, "What color is the door in the picture? Please answer with one word.")
        return ['door', f'{color}_door']
    return []
