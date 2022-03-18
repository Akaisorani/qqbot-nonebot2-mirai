from nonebot import get_driver
from nonebot.rule import Rule

import requests

cfg=get_driver().config

def setu_groups_checker(bot, event):
    if event.type=="GroupMessage":
        if event.sender.group.id in cfg.group_setu_id_list:
        # if event.sender.group.id in cfg.test_group_list:    # for test
            return True
        else:
            return False
    else:
        return True

rule_setu_groups=Rule(setu_groups_checker)