from typing import Any, Dict, List
from nonebot import on_message, on_command, on_regex, get_driver, require, on_notice
from nonebot.rule import to_me, startswith
from nonebot.matcher import Matcher
from nonebot.adapters import Message
from nonebot.adapters.mirai2 import Bot, Event, MessageSegment
from nonebot.adapters.mirai2.event import GroupRecallEvent
from nonebot.params import Arg, CommandArg, ArgPlainText, RegexMatched, EventMessage
from nonebot.typing import T_State, T_CalledAPIHook

driver=get_driver()

msg_ids: Dict[str, List[str]] = {}
max_size = 50

def get_key(msg_type, id):
    return f'{msg_type}_{id}'

@Bot.on_called_api
async def save_msg_id(bot: Bot, e: Exception, api: str, data: Dict[str, Any], result: Any) -> T_CalledAPIHook:

    # print("api\n",api)
    # print("data\n",data)
    # print("result\n",result)
    try:
        if api == 'send_msg':
            msg_type = data['message_type']
            id = data['group'] if msg_type == 'group' else data['target']
        elif api == 'send_friend_message':
            msg_type = 'friend'
            id = data['target']
        elif api == 'send_temp_message':
            msg_type = 'temp'
            id = data['target']
        elif api == 'send_group_message':
            msg_type = 'group'
            id = data['group']
        else:
            return
        key = get_key(msg_type, id)
        msg_id = result['messageId']

        if key not in msg_ids:
            msg_ids[key] = []
        msg_ids[key].append(msg_id)
        if len(msg_ids[key]) > max_size:
            msg_ids[key].pop(0)
    except:
        pass



withdraw = on_command('withdraw', aliases={'撤回'},
                      block=True, rule=to_me(), priority=2)


@withdraw.handle()
async def _(bot: Bot, event: Event, args: Message = CommandArg()):
    
    if event.type=="GroupMessage":
        msg_type = 'group'
        id=event.sender.group.id
    elif event.type=="FriendMessage":
        msg_type = 'friend'
        id=event.sender.id
    elif event.type=="TempMessage":
        msg_type = 'temp'
        id=event.sender.id

    key = get_key(msg_type, id)

    if event.to_quote:
        msg_id = event.quote.id
        try:
            await bot.recall(target=msg_id)
            if msg_id in msg_ids[key]: msg_ids[key].remove(msg_id)
            return
        except:
            await withdraw.finish('撤回失败，可能已超时')

    num = args.extract_plain_text()
    if num and num.isdigit() and 0 <= int(num) < len(msg_ids[key]):
        num = int(num)
    else:
        num = 0

    try:
        idx = -num - 1
        print(msg_ids[key][idx])
        await bot.recall(target=msg_ids[key][idx])
        msg_ids[key].pop(idx)
    except Exception as e:
        print(e)
        await withdraw.finish('撤回失败，可能已超时')


async def _group_recall(bot: Bot, event: Event) -> bool:
    if isinstance(event, GroupRecallEvent) and str(event.author_id) == str(bot.self_id):
        return True
    return False


withdraw_notice = on_notice(_group_recall, priority=10)


@withdraw_notice.handle()
async def _(event: GroupRecallEvent):
    msg_id = int(event.message_id)
    id = event.group.id
    key = get_key('group', id)
    if key in msg_ids and msg_id in msg_ids[key]:
        msg_ids[key].remove(msg_id)