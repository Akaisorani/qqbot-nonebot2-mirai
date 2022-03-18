#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import nonebot
from nonebot.adapters.mirai2 import Adapter as MIRAI2Adapter

# Custom your logger
# 
# from nonebot.log import logger, default_format
# logger.add("error.log",
#            rotation="00:00",
#            diagnose=False,
#            level="ERROR",
#            format=default_format)

# You can pass some keyword args config to init function
nonebot.init()
app = nonebot.get_asgi()

driver = nonebot.get_driver()
driver.register_adapter(MIRAI2Adapter)

config = driver.config
# add myconfig
import myconfig
config.__dict__.update(dict([(cfg_name, cfg_value) for cfg_name, cfg_value in myconfig.__dict__.items() if cfg_name[:2]!="__"]))
import apikeys
config.__dict__.update(dict([(cfg_name, cfg_value) for cfg_name, cfg_value in apikeys.__dict__.items() if cfg_name[:2]!="__"]))

# nonebot.load_builtin_plugins("single_session")
nonebot.load_builtin_plugins("echo")
# nonebot.load_plugin("akaisora_nonebot.plugins.arknights_tag")
# nonebot.load_plugin("akaisora_nonebot.plugins.hello")

# Please DO NOT modify this file unless you know what you are doing!
# As an alternative, you should use command `nb` or modify `pyproject.toml` to load plugins
nonebot.load_from_toml("pyproject.toml")

# Modify some config / config depends on loaded configs
# 
# config = driver.config
# do something...


if __name__ == "__main__":
    nonebot.logger.warning("Always use `nb run` to start the bot instead of manually running!")
    nonebot.run(app="__mp_main__:app")
