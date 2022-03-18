from nonebot import get_driver
from nonebot.rule import Rule
from nonebot.adapters import Message
from nonebot.params import EventMessage

import io
import requests
from PIL import Image as PImage

cfg=get_driver().config

def image_collector_groups_checker(bot, event):
    if event.type=="GroupMessage":
        if event.sender.group.id in cfg.group_pic_collect_list:
        # if event.sender.group.id in cfg.test_group_list:    # for test
            return True
        else:
            return False
    else:
        return True

image_collector_groups=Rule(image_collector_groups_checker)

def has_image_checker(bot, event, message: Message = EventMessage()):
    if message["Image"]: return True
    else: return False

has_image=Rule(has_image_checker)


def get_bytes_image_from_url(url):
    r=requests.get(url,timeout=30)
    buffer=r.content
    return buffer

def get_shape(buffer):
    im=PImage.open(io.BytesIO(buffer))
    return im.size