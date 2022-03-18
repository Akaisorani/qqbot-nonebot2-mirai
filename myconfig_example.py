["bot"]

qq = 1234567890 # 字段 qq 的值
authKey = '' # 字段 authKey 的值
mirai_api_http_locate = 'localhost:8099/ws' # httpapi所在主机的地址端口,如果 setting.yml 文件里字段 "enableWebsocket" 的值为 "true" 则需要将 "/" 换成 "/ws", 否则将接收不到消息.

["test"]

test_group_list=[87654321]
test_friend_list=[87654321]

["hourcall"]

group_medi_id_list=[87654321]
group_mrfz_cake_id_list=[87654321, 87654321]

["weibo"]

group_mrfz_weibo_id_list=[87654321, 87654321]
# group_mrfz_weibo_id_list=[696694875]

["heartbeat"]
group_heartbeat_list=[87654321]

["pic_collect"]
group_pic_collect_list=[87654321, 87654321, 87654321, 87654321]


["share"]

app = None
scheduler = None

["memo"]

memo_dir = "./plugins/memo_data/data"
memo_index_path = "./plugins/memo_data/memo_index.json"
memo_index = None


["sanity"]

sanity_data_path = "./plugins/sanity_data.json"


["setu"]
pixiv_username = ""
pixiv_password = ""
setu_data_path = "./data/setu"
group_setu_id_list=[87654321, 87654321, 87654321]


["msglog"]

msglog={"group":{}}


["recomtag"]

recomtag_data_path = "./data/recomtag"
cookies_prts = "./cookies_prts.txt"
group_recomtag_id_list=[87654321, 87654321, 87654321]

["pic_collector"]

repo_link=""
repo_upload_link=""
repo_download_link=""

["monitor"]
monitor_report_groups_id_list=[87654321]