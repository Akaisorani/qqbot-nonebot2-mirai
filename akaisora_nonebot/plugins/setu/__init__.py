from nonebot import on_message, on_command, on_regex, get_driver, require
from nonebot.rule import to_me, startswith
from nonebot.matcher import Matcher
from nonebot.adapters import Message
from nonebot.adapters.mirai2 import MessageSegment
from nonebot.params import Arg, CommandArg, ArgPlainText, RegexMatched, EventMessage
from nonebot.typing import T_State

import os
from .util import rule_setu_groups
from .pixiv_setu import Pixivsetu

cfg=get_driver().config

pixiv_setu=Pixivsetu(cfg.pixiv_username, cfg.pixiv_password, cfg.setu_data_path)

# 发送pixiv图片
setu=on_command("setu", rule=rule_setu_groups, aliases={"给我一张色图","给我一份色图","色图 "}, priority=1)

@setu.handle()
async def handle_first_receive(matcher: Matcher, state: T_State, args: Message = CommandArg()):
    plain_text = args.extract_plain_text().strip()

    try:
        ret=pixiv_setu.get_setu(plain_text)
    except Exception as e:
        print(e)
        await setu.finish("涩涩失败")
        return

    # print(ret)


    if not ret: return
    if isinstance(ret, str):
        await setu.finish(ret)
    else:
        filepath=os.path.abspath(ret["image"])
        # print(filepath)
        msg=Message([
            MessageSegment.image(path=filepath)
        ])
        await setu.finish(msg)

