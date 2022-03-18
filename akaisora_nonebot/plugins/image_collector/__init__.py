from nonebot import on_message, on_command, on_regex, get_driver, require
from nonebot.rule import to_me, startswith
from nonebot.matcher import Matcher
from nonebot.adapters import Message
from nonebot.adapters.mirai2 import MessageSegment
from nonebot.params import Arg, CommandArg, ArgPlainText, RegexMatched, EventMessage
from nonebot.typing import T_State

import os, io
import requests
import pytz
from datetime import datetime
import imghdr
from .util import image_collector_groups, has_image, get_bytes_image_from_url, get_shape
from .upload_cloud import Cloud

cfg=get_driver().config

cloud=Cloud(cfg.repo_link, cfg.repo_upload_link, cfg.repo_download_link)

# 群聊图片收集并保存云盘
image_collector=on_message(rule=image_collector_groups & has_image, priority=10)

@image_collector.handle()
async def handle_first_receive(event, matcher: Matcher, state: T_State, message: Message = EventMessage()):
    # print(message)

    image_urls=[image.data["url"] for image in message["Image"]]

    for url in image_urls:
        buffer=get_bytes_image_from_url(url)
        width, height=get_shape(buffer)
        if width*height>=1080*720:
            now = datetime.now(pytz.timezone('Asia/Shanghai'))
            date_str=now.strftime('%Y%m%d')
            date_time_str=now.strftime("%Y%m%d-%H%M%S")

            fp=io.BytesIO(buffer)
            ext=imghdr.what(None, buffer)
            fp.name="{0}.{1}".format(date_time_str, ext)

            sub_dir_id=event.sender.group.id if event.type=="GroupMessage" else event.sender.id

            rel_path="{0}/{1}/".format(sub_dir_id, date_str)

            result=cloud.upload(file_like=fp, rel_path=rel_path)
            print(result)

# 返回云盘下载地址
pic_download_link=on_command("pictures", rule=image_collector_groups & to_me(), aliases={"图库"}, priority=1)

@pic_download_link.handle()
async def handle_first_receive(event, matcher: Matcher, state: T_State):

    group_id=event.sender.group.id if event.type=="GroupMessage" else event.sender.id
    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    date_str=now.strftime('%Y%m%d')

    download_link="{0}?p=%2F{1}%2F{2}&mode=grid".format(cloud.repo_download_link, group_id, date_str)

    await pic_download_link.finish(download_link)