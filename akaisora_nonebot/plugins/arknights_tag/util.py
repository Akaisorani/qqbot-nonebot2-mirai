from nonebot import get_driver
from nonebot.rule import Rule

import requests

cfg=get_driver().config

def recommend_tags_groups_checker(bot, event):
    if event.type=="GroupMessage":
        if event.sender.group.id in cfg.group_recomtag_id_list:
        # if event.sender.group.id in cfg.test_group_list:    # for test
            return True
        else:
            return False
    else:
        return True

rule_recommend_tags_groups=Rule(recommend_tags_groups_checker)



def get_bytes_image_from_url(url):
    r=requests.get(url,timeout=30)
    buffer=r.content
    return buffer