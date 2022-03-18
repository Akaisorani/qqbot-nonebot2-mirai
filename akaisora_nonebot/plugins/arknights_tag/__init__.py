from nonebot import on_message, on_command, on_regex, get_driver, require
from nonebot.rule import to_me, startswith
from nonebot.matcher import Matcher
from nonebot.adapters import Message
from nonebot.adapters.mirai2 import MessageSegment
from nonebot.params import Arg, CommandArg, ArgPlainText, RegexMatched, EventMessage
from nonebot.typing import T_State

from .util import rule_recommend_tags_groups
from .recommend_tags import Tags_recom

cfg=get_driver().config
scheduler = require("nonebot_plugin_apscheduler").scheduler

tags_recom=Tags_recom(recomtag_data_path=cfg.recomtag_data_path, 
                        baidu_aip_key={'APP_ID':cfg.APP_ID,
                                        'API_KEY':cfg.API_KEY,
                                        'SECRET_KEY':cfg.SECRET_KEY})

# 明日方舟公开招募助手
recommend_tags=on_message(rule=rule_recommend_tags_groups, priority=10)

@recommend_tags.handle()
async def handle_first_receive(matcher: Matcher, state: T_State, message: Message = EventMessage()):
    # print(message)

    text=message.extract_plain_text()
    tags_list=text.split() if text else []
    image=message["Image"][0].data["url"] if message["Image"] else None
    
    ret=tags_recom.recom(tags_list, image)

    if not ret: return

    await recommend_tags.finish(ret)

# 明日方舟查询干员/敌人
tell=on_command("tell", rule=rule_recommend_tags_groups, aliases={"查询干员"}, priority=1)

@tell.handle()
async def handle_first_receive(matcher: Matcher, state: T_State, args: Message = CommandArg()):
    plain_text = args.extract_plain_text()
    # print("+"+plain_text+"+")
    if not plain_text: return
    ret=tags_recom.char_data.get_peo_info(plain_text)
    # print(ret)

    if not ret: return
    if isinstance(ret, str):
        await tell.finish(ret)
    else:
        msg=Message([
            MessageSegment.image(url=ret["head_pic"]),
            MessageSegment.plain("\n"),
            MessageSegment.plain(ret["description"])
        ])
        await tell.finish(msg)

# 明日方舟爬取干员/敌人数据
update_data=on_command("update_data", rule=rule_recommend_tags_groups & to_me(), priority=1)

@update_data.handle()
async def handle_first_receive():

    tags_recom.char_data.update()

    ret="更新完成"+"\n{0} 干员, {1} 敌人".format(len(tags_recom.char_data.char_data),len(tags_recom.char_data.enemy_data))
    print(ret)

    await update_data.finish(ret)

@scheduler.scheduled_job("cron", hour="16", minute='35', id="update_data")
async def update_characters():
    tags_recom.char_data.update()