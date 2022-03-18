from nonebot import on_command, on_regex, get_driver
from nonebot.rule import to_me
from nonebot.matcher import Matcher
from nonebot.adapters import Message, Event
from nonebot.params import Arg, CommandArg, ArgPlainText, RegexMatched, EventMessage
from nonebot.typing import T_State

cfg=get_driver().config

# hello=on_regex(r"hello", rule=None, priority=10)

# @hello.handle()
async def handle_first_receive(matcher: Matcher, event:Event, state: T_State, message: Message = EventMessage()):
    print(type(message))
    print(event)
    print(event.type)
    print(event.sender.group.id)

    print(message["image"])
    print(not message["image"])
    print(len(message["image"]))

    matcher.stop_propagation()

    await hello.finish()

def create_file():
    import os
    o_path = os.getcwd()
    print(o_path)
    with open("abc.txt", "w") as fp:
        fp.write("123")

def get_data():
    print(__package__)
    import pkgutil
    data_bytes = pkgutil.get_data(__package__, 'abc.txt')
    data_str = data_bytes.decode()
    print(data_str)

if __name__=="__main__":
    pass
    
