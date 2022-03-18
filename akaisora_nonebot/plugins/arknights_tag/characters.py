# from nonebot import get_driver

import requests
import urllib
from html import unescape
from lxml import html
import os, sys, re
import json
import pytz
from datetime import datetime

from .fuzzname import Fuzzname
from .record import Record
# from .util import get_bytes_image_from_url

o_path = os.getcwd()

# cfg=get_driver().config

class Character(object):
    def __init__(self, recomtag_data_path = "./data/recomtag"):
        self.char_data=dict()
        self.enemy_data=dict()
        self.head_data=[]
        self.head_key_map={
            "职业":"job",
            "星级":"rank",
            "性别":"sex",
            "阵营":"affiliation",
            "标签":"tags",
            "获取途径":"obtain_method"
        }
        self.data_path=recomtag_data_path
        if not os.path.exists(self.data_path): os.makedirs(self.data_path)

        self.fuzzname=Fuzzname()
        self.record=Record(self.data_path+"/record_peo.txt")

    def update(self):
        self.fetch_data()
        self.extract_all_char()


    def extract_all_char(self, char_file=None, enemy_file=None):
        if char_file is None:char_file=self.data_path+"/chardata.json"  
        if enemy_file is None:enemy_file=self.data_path+"/enemylist.json"

        if not os.path.exists(char_file) or not os.path.exists(enemy_file):
            self.fetch_data()

        # deal char
        with open(char_file,encoding='UTF-8') as fp:
            self.char_data=json.load(fp)

        # deal enemy
        with open(enemy_file,encoding='UTF-8') as fp:
            self.enemy_data=json.load(fp)
           
        # fuzzy name+pinyin -> name
        self.fuzzname.fit(list(self.char_data.keys())+list(self.enemy_data.keys()))
            
    def filter(self, tags, flags={}):
        tags=tags[:]
        ranks=self.gen_ranks(tags)
        for name, dic in self.char_data.items():
            if set(tags).issubset(set(dic["tags"])): pass
            else: continue
            if dic["rank"] in ranks or ('show_all' in flags and flags['show_all']==True): pass
            else: continue
            if "公开招募" in dic["obtain_method"] or ('show_all' in flags and flags['show_all']==True): pass
            else: continue
                
            yield name
     
    def gen_ranks(self, tags):
        ranks=["1","2","3","4","5","6"]
        for i in range(1,7):
            if ">={0}".format(i) in tags:
                ranks=[x for x in ranks if x>=str(i)]
                tags.remove(">={0}".format(i))
            if "<={0}".format(i) in tags:
                ranks=[x for x in ranks if x<=str(i)]
                tags.remove("<={0}".format(i))
        if "高级资深干员" not in tags:
            ranks.remove("6")
        if "资深干员" in tags:
            ranks=["5"]
        if "高级资深干员" in tags:
            ranks=["6"]
        if "资深干员" in tags and "高级资深干员" in tags:
            ranks=["5", "6"]
        
        return ranks
        
    def get_peo_info(self, name=None):
        if not name: return None
        res="None"
        if name in self.char_data:
            res=self.format_friend_info(name)
            self.record.add("friend/"+name)
        elif name in self.enemy_data:
            res=self.format_enemy_info(name)
            self.record.add("enemy/"+name)
        else:
            res=self.fuzzname.predict(name)
            res="你可能想查 {0}".format(res)
        
        return res

    def format_friend_info(self, name):
        res=[]
        for tp, cont in self.char_data[name]['all'].items():
            if tp:
                # if tp=="干员代号":tp="姓名"
                res.append("{0}: {1}".format(tp,cont))
        url=self.char_data[name]["link"]
        res.append(url)
        res_text="\n".join(res)

        # r=requests.get(self.char_data[name]["head_pic"],timeout=30)
        # buffer=r.content
        # bytes_image=get_bytes_image_from_url(self.char_data[name]["head_pic"])

        # ret_msg=[
        #     Image.fromBytes(bytes_image),
        #     # Image.fromRemote(self.char_data[name]["head_pic"]),
        #     # Image.fromFileSystem("./plugins/image.jpg"),
        #     Plain(text="\n"),
        #     Plain(text=res_text)
        # ]

        friend_info={
            "head_pic":self.char_data[name]["head_pic"],
            "description":res_text
        }

        return friend_info

    def format_enemy_info(self, name):
        res=[name]
        url=self.enemy_data[name]["link"]
        res.append(url)
        res_text="\n".join(res)

        # r=requests.get(self.enemy_data[name]["head_pic"],timeout=30)
        # buffer=r.content
        # bytes_image=get_bytes_image_from_url(self.enemy_data[name]["head_pic"])

        # ret_msg=[
        #     Image.fromBytes(bytes_image),
        #     Plain(text="\n"),
        #     Plain(text=res_text)
        # ]
        enemy_info={
            "head_pic":self.enemy_data[name]["head_pic"],
            "description":res_text
        }

        return enemy_info
        
    def fetch_data(self):
        # self.fetch_character_from_wikijoyme()
        self.fetch_character_from_akmooncell()

        self.fetch_enemy_from_akmooncell()

    def fetch_character_from_akmooncell(self, filename="chardata.json"):
        def fetch_data_with_json_format():
            r=requests.get("http://prts.wiki/load.php?debug=false&lang=zh-cn&modules=ext.gadget.charFilter&skin=vector&version=0vmy0ui")
            if r.status_code!=200: raise IOError("Cannot fetch char from akmooncell")
            rtext=r.text.replace("\n","")
            rtext=re.sub(r"<.*?>","",rtext)
            result=re.search(r"(?<=datalist=)(.*?)(?=;console)",rtext).group(1)
            content=eval(result)
            # print(content)

            char_data=dict()
            for char_tr in content:
                name=char_tr["cn"]
                # if name=="杜宾":
                #     print(char_tr)
                char_data[name]=dict()
                char_data[name]["job"]=char_tr["class"]
                char_data[name]["rank"]=str(int(char_tr["rarity"])+1)
                char_data[name]["sex"]=char_tr["sex"]
                char_data[name]["affiliation"]=char_tr["camp"]
                char_data[name]["tags"]=char_tr["tag"]\
                            +[char_data[name]["job"]]\
                            +[char_tr["position"]]\
                            +(["资深干员"] if char_data[name]["rank"]=="5" else [])\
                            +(["高级资深干员"] if char_data[name]["rank"]=="6" else [])
                char_data[name]["obtain_method"]=char_tr["approach"]
                
                #deal head and data
                char_data[name]["all"]={
                    "姓名":char_tr["cn"],
                    "出身":char_tr["camp"],
                    "种族":','.join(char_tr["race"]),
                    "初始生命":char_tr["oriHp"],
                    "初始攻击":char_tr["oriAtk"],
                    "初始防御":char_tr["oriDef"],
                    "初始法术抗性":char_tr["oriRes"],
                    "初始再部署时间":char_tr["oriDt"],
                    "初始部署费用":char_tr["oriDc"],
                    "初始阻挡数":char_tr["oriBlock"],
                    "初始攻击间隔":char_tr["oriCd"],
                    "标签":','.join(char_tr["tag"]),
                    "特性":char_tr["feature"],
                }

                # link
                char_link_root="http://prts.wiki/w/"
                
                url=char_link_root+urllib.parse.quote(name)
                char_data[name]["link"]=url

                char_data[name]["type"]="friend"
            return char_data

        def fetch_data_with_source():
            r=requests.get("http://prts.wiki/w/干员一览")
            if r.status_code!=200: raise IOError("Cannot fetch char from akmooncell")
            rtext=r.text
            rtext=rtext.replace("\n","")
            rtext=re.sub(r"&lt;span style=&quot;display:none.*?&gt;(.*?)&lt;/span&gt;",r"（\1）",rtext)
            rtext=re.sub(r"&lt;br/&gt;","\n",rtext)
            rtext=re.sub(r"&lt;span.*?&gt;","",rtext)
            rtext=re.sub(r"&lt;/span&gt;","",rtext)
            
            tree=html.fromstring(rtext)
            char_res_lis=tree.xpath("//div[@class='smwdata']")

            char_data=dict()
            for char_a in char_res_lis:
                name=char_a.xpath("./@data-cn")[0]
                char_data[name]=dict()
                char_data[name]["job"]=char_a.xpath("./@data-class")[0]
                char_data[name]["rank"]=str(int(char_a.xpath("./@data-rarity")[0])+1)
                char_data[name]["sex"]=char_a.xpath("./@data-sex")[0]
                char_data[name]["affiliation"]=char_a.xpath("./@data-camp")[0]
                char_data[name]["tags"]=char_a.xpath("./@data-tag")[0].split(" ")\
                            +[char_data[name]["job"]]\
                            +[char_a.xpath("./@data-position")[0]]\
                            +(["资深干员"] if char_data[name]["rank"]=="5" else [])\
                            +(["高级资深干员"] if char_data[name]["rank"]=="6" else [])
                char_data[name]["obtain_method"]=char_a.xpath("./@data-approach")[0].split(", ")
                char_data[name]["head_pic"]="https:"+char_a.xpath("./@data-icon")[0]
                
                
                #deal head and data
                char_data[name]["all"]={
                    "姓名":name,
                    "出身":char_a.xpath("./@data-camp")[0],
                    "种族":char_a.xpath("./@data-race")[0],
                    "初始生命":char_a.xpath("./@data-ori-hp")[0],
                    "初始攻击":char_a.xpath("./@data-ori-atk")[0],
                    "初始防御":char_a.xpath("./@data-ori-def")[0],
                    "初始法术抗性":char_a.xpath("./@data-ori-res")[0],
                    "初始再部署时间":char_a.xpath("./@data-ori-dt")[0],
                    "初始部署费用":char_a.xpath("./@data-ori-dc")[0],
                    "初始阻挡数":char_a.xpath("./@data-ori-block")[0],
                    "初始攻击间隔":char_a.xpath("./@data-ori-cd")[0],
                    "标签":char_a.xpath("./@data-tag")[0],
                    "特性":char_a.xpath("./@data-feature")[0],
                }

                # link
                char_link_root="http://prts.wiki/w/"
                url=char_link_root+urllib.parse.quote(name)
                char_data[name]["link"]=url

                char_data[name]["type"]="friend"
                # if name=="杜宾":
                #     print(char_data[name])
            return char_data

        char_data=fetch_data_with_source()

        with open(self.data_path+"/"+filename,"w",encoding='utf-8') as fp:
            json.dump(char_data, fp)

        return char_data

    def fetch_enemy_from_akmooncell(self, filename="enemylist.json"):
        import threading, time
        def try_enemy_head_pic_path(name, enemy_data):
            def modify_data(url):
                enemy_data_rlock.acquire()
                enemy_data[name]["head_pic"]=url
                enemy_data_rlock.release()
            
            print("%s is trying %s"%(threading.current_thread().name,name))
            try:
                print(name)
                session_requests=requests.session()
                for i in range(256):
                    h=hex(i)[2:]
                    if len(h)==1: h='0'+h
                    url="https://prts.wiki/images/{0}/{1}/头像_敌人_{2}.png".format(h[0],h,name)
                    r=session_requests.get(url, allow_redirects=False)
                    if url=="https://prts.wiki/images/1/1f/头像_敌人_大亚当.png":
                        print('*'*80, r.status_code, r.text)
                    if r.status_code==200:
                        print('SUCCESS %s get %s'%(threading.current_thread().name,url))
                        modify_data(url)
                        return

                print(name, "didnt find right url, return default")
                return modify_data("https://prts.wiki/images/3/3e/头像_敌人_源石虫.png")

            except Exception as e:
                print(e)
                print('FAIL %s error %s'%(threading.current_thread().name,name))                

                return modify_data("https://prts.wiki/images/3/3e/头像_敌人_源石虫.png")
        

        print("begin fetch enemy")

        # get enemy data
        r=requests.get("http://prts.wiki/index.php?title=敌人一览/数据&action=raw")
        if r.status_code!=200: raise IOError("Cannot fetch enemy from akmooncell")
        enemy_data_raw=r.json()
        enemy_data=dict()
        enemy_link_root="http://prts.wiki/w/"
        for enemy_a in enemy_data_raw:
            name=enemy_a["name"]
            # print("===="+name)
            enemy_data[name]=dict()
            link=enemy_link_root+urllib.parse.quote(enemy_a["enemyLink"])


            enemy_data[name]["link"]=link
            enemy_data[name]["type"]="enemy"
            if name in self.enemy_data and "head_pic" in self.enemy_data[name] and (name=="源石虫" or self.enemy_data[name]["head_pic"]!=self.enemy_data["源石虫"]["head_pic"]):
                enemy_data[name]["head_pic"]=self.enemy_data[name]["head_pic"]
            else:
                enemy_data[name]["head_pic"]=""

        enemy_name_lis=list(enemy_data.keys())
        threads=[]
        enemy_data_rlock=threading.RLock()
        for name in enemy_name_lis:
            if not enemy_data[name]["head_pic"]:
                t=threading.Thread(target=try_enemy_head_pic_path,args=(name,enemy_data))
                threads.append(t)
                while sum(map(lambda x:1 if x.is_alive() else 0,threads))>=50 : time.sleep(0.5)
                t.start()
                while not threads[0].is_alive(): threads.pop(0)
        for t in threads :
            if t.is_alive():t.join()
        
        with open(self.data_path+"/"+filename,"w",encoding='utf-8') as fp:
            json.dump(enemy_data, fp)

        print("end fetch enemy")
        return enemy_data


if __name__=="__main__":

    char_data=Character()
    char_data.fetch_data()
    print("fetch_done")
    
    char_data.extract_all_char()
    print(char_data.char_data["艾雅法拉"])