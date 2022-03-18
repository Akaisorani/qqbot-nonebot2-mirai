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
from .characters import Character
from .ocr_tool import Ocr_tool
# from .util import get_bytes_image_from_url

o_path = os.getcwd()

# cfg=get_driver().config


class Tags_recom(object):
    def __init__(self, recomtag_data_path = "./data/recomtag", baidu_aip_key={}):
        self.char_data=Character()
        self.char_data.extract_all_char()
        self.all_tags={
        '狙击', '术师', '特种', '重装', '辅助', '先锋', '医疗', '近卫',
        '减速', '输出', '生存', '群攻', '爆发', '召唤', '快速复活','费用回复',
        '新手', '治疗', '防护', '位移', '削弱', '控场', '支援',
        '支援机械', "机械",
        '近战位', '远程位',
        '近战', '远程',
        '资深干员','高级资深干员', '高级资深',
        '资深','高资', 
        #'女', '男',
        #'女性', '男性',
        '狙击干员', '术师干员', '特种干员', '重装干员', '辅助干员', '先锋干员', '医疗干员', '近卫干员',
        #'女性干员', '男性干员',
        # flags
        '全部'
        }
        self.data_path=recomtag_data_path
        if not os.path.exists(self.data_path): os.makedirs(self.data_path)
        
        self.ocr_tool=Ocr_tool(**baidu_aip_key)
        self.record=Record(self.data_path+"/"+"record_tags.txt",writecnt=50)
        
    def recom_tags(self, tags, flags={}):
        tags=self.strip_tags(tags)
    
        itertag=self.iter_all_combine(tags)
        if itertag is None:return []
        cob_lis=list(itertag)
        cob_lis.remove([])
        cob_lis=[(tags_lis, list(self.char_data.filter(tags_lis, flags))) for tags_lis in cob_lis]
        cob_lis=[x for x in cob_lis if x[1]!=[]]
        # print(cob_lis)
        # char_data[name]
        
        # print("")
        # for x in cob_lis:
            # print(x)
        
        # remove same result
        for i in range(0,len(cob_lis)):
            for j in range(0,len(cob_lis)):
                if i==j:continue
                if set(cob_lis[i][1])==set(cob_lis[j][1]):
                    if set(cob_lis[i][0]).issubset(set(cob_lis[j][0])):
                        cob_lis[j]=(cob_lis[j][0],[])
        cob_lis=[x for x in cob_lis if x[1]!=[]]
        # print("")
        # for x in cob_lis:
            # print(x)
   
        # special remove
        if ('show_all' not in flags or flags['show_all']==False):
            for i in range(len(cob_lis)):
                if self.is_special_rm(cob_lis[i]):
                    cob_lis[i]=(cob_lis[i][0],[])
            cob_lis=[x for x in cob_lis if x[1]!=[]]
            # print("")
            # for x in cob_lis:
                # print(x)   

        # sort
        cob_lis.sort(key=self.avg_rank, reverse=True)
        for tags_lis, lis in cob_lis:
            lis.sort(key=lambda x:self.char_data.char_data[x]["rank"], reverse=True)
        # print("")
        # for x in cob_lis:
            # print(x)
            
        # for x in cob_lis:
            # print(self.avg_rank(x))
            
        # # build reverse index
        # char_dic=dict()
        # for i in range(len(cob_lis)):
            # for name in cob_lis[i][1]:
                # if name not in char_dic:
                    # char_dic[name]=[i]
                # else:
                    # char_dic[name].append(i)
        # # print("")
        # # print(char_dic)
        
        # # remove duplicate
        # min_size_id=dict()
        # for name, lis in char_dic.items():
            # if len(lis)>1:
                # min_size_id[name]=lis[0]
                # for id in lis:
                    # if len(cob_lis[id][1])<len(cob_lis[min_size_id[name]][1]):
                        # min_size_id[name]=id
                        
        # for name, lis in char_dic.items():
            # if len(lis)>1:                        
                # for id in lis:
                    # if id!=min_size_id[name]:
                        # cob_lis[id][1].remove(name)
        # cob_lis=[x for x in cob_lis if x[1]!=[]]
        # # print("")
        # # for x in cob_lis:
            # # print(x)
        
        #merge less rank 3
        if ('show_all' not in flags or flags['show_all']==False):
            tag_cnt=0
            max_num_until_del=30
            for tags_lis, lis in cob_lis:
                cnt=0
                sp_lis=[]
                while len(lis)>0 and self.char_data.char_data[lis[-1]]["rank"]<="3":
                    res=lis.pop()
                    if res in ["Castle-3","Lancet-2","THRM-EX"]:
                        sp_lis.append(res)
                    else:
                        cnt+=1
                
                if len(sp_lis)>0:
                    lis.extend(sp_lis)
                if cnt>0 and len(lis)>0:
                    lis.append("...{0}".format(cnt))
                    # delete all contain <=3
                    if tag_cnt+len(lis)>max_num_until_del:
                        lis.clear()
                        max_num_until_del=-1
                tag_cnt+=len(lis)
            cob_lis=[x for x in cob_lis if x[1]!=[]]
            
        return cob_lis
        # print("")
        # for x in cob_lis:
            # print(x)        
                
        
    
    def is_special_rm(self, cob_i):
        if set(cob_i[0])==set(["女"]):
            return True
        # if set(cob_i[0])==set(["男"]):
            # return True
        return False
        
    def avg_rank(self, cob_i):
        rank_map={1:0.5, 2:1, 3:10, 4:2, 5:0.5, 6:3}
        rank_list=list(map(lambda x:int(self.char_data.char_data[x]["rank"]),cob_i[1]))
        sum_score=0
        sum_cnt=0
        for i in range(1,7):
            sum_score+=rank_list.count(i)*rank_map[i]*i
            sum_cnt+=rank_list.count(i)*rank_map[i]
        if sum_cnt==0:return 0
        else: return sum_score/sum_cnt
    
    def strip_tags(self, tags):
        restags=[]
        for tag in tags:
            if tag in ["高级资深干员","高资","高级资深"]:
                restags.append("高级资深干员")
            elif tag in ["资深干员","资深"]:
                restags.append("资深干员")
            elif tag in ["近战","远程"]:
                restags.append(tag+"位")
            elif tag in ["机械"]:
                restags.append(tag+"支援机械")
            # elif tag in ["男性","女性"]:
            #     tag=tag.replace("性","")
            #     restags.append(tag)              
            # elif "性干员" in tag:
            #     tag=tag.replace("性干员","")
            #     restags.append(tag)
            elif "干员" in tag:
                tag=tag.replace("干员","")
                restags.append(tag)
            else:
                restags.append(tag)
        return restags
        
    def iter_all_combine(self, tags):
        if len(tags)==0:
            yield []
            return
        tag=tags[0]
        new_tags=tags[:]
        new_tags.remove(tag)
        for x in self.iter_all_combine(new_tags):
            yield [tag]+x
        for x in self.iter_all_combine(new_tags):
            yield x
    
    def check_legal_tags(self, tags):
        if not tags: return False
        for tag in tags:
            if tag not in self.all_tags:
                return False
        return True


    def split_tags(self, t_tag):
        rest_tag=t_tag[:]
        flag=True
        tag_lis=[]
        for tag in self.all_tags:
            if rest_tag==tag:
                return [tag]
        for tag in self.all_tags:
            if tag in rest_tag:
                res=self.split_tags(rest_tag.replace(tag,""))
                if res:
                    return [tag]+res
        return []
        
    def filter_legal_tags(self, tags):
        if not tags: return []
        new_tags=[]
        for tag in tags:
            split_res=self.split_tags(tag)
            new_tags.append(tag)
            if len(split_res)>1:new_tags.extend(split_res)
        tags=new_tags
        # print(new_tags)
        res=[]
        for tag in tags:
            if tag in self.all_tags:
                res.append(tag)
        return res

    def split_flags(self, tags):
        if not tags: return [],{}
        tags=list(set(tags))
        flags={}
        if '全部' in tags:
            flags['show_all']=True
            tags.remove('全部')
        else:
            flags['show_all']=False

        return tags, flags



    def record_tags(self, tags):
        for tag in tags:
            self.record.add(tag)


    def recom(self, tags=None, image=None):
        if not tags:
            if image:
                tags=self.get_tags_from_image(image)
                if not tags:
                    print("MYDEBUG image checkfail {0}".format(image))
                    return None
            else:
                return None
        
        tags, flags=self.split_flags(tags)
        # print(tags, flags)

        if not self.check_legal_tags(tags):
            print("MYDEBUG no legal tags")
            return None

        self.record_tags(tags)
        cob_lis=self.recom_tags(tags, flags)
        if not cob_lis:
            return "没有"
        line_lis=[]
        for tags_lis, lis in cob_lis:
            new_lis=[]
            for x in lis:
                if x in self.char_data.char_data:
                    new_lis.append(x+"★"+self.char_data.char_data[x]["rank"])
                else:
                    new_lis.append("★1~3"+x)
            lef='【'+'+'.join(tags_lis)+"】:\n"
            rig=', '.join(new_lis)
            line_lis.append(lef+rig)
        res="\n\n".join(line_lis)
        return res
    
    def get_tags_from_image(self, image):
        tags=self.ocr_tool.get_tags_from_url(image)
        print(tags)
        tags=self.filter_legal_tags(tags)
        tags=list(set(tags))
        print("ocr res=",tags)
        if len(tags)>=2 and len(tags)<=8:
            return tags
        else:
            return []


if __name__=="__main__":
    tags_recom=Tags_recom()

    res2=tags_recom.char_data.get_peo_info("艾斯戴尔")
    print(res2)
    # tags_recom.char_data.fetch_data()
    # tags_recom.char_data.extract_all_char()
    res2=tags_recom.char_data.get_peo_info("法术大师A2")
    print(res2)
    
    res=tags_recom.recom(["狙击干员","辅助干员", "削弱", "支援机械", "治疗"])
    
    # res=tags_recom.recom(["近卫", "男", "支援"])
    print(res)
    print("="*15)
    url="https://c2cpicdw.qpic.cn/offpic_new/1224067801//39b40a48-b543-4082-986d-f29ee82645d3/0?vuin=2473990407&amp;amp;term=2"
    url="https://c2cpicdw.qpic.cn/offpic_new/391809494//857ddb74-7a0d-40ae-98db-068f8c733c86/0?vuin=2473990407&amp;amp;term=2"
    url="https://gchat.qpic.cn/gchatpic_new/2465342838/698793878-3133403591-5DB0FBC01E75F719EA8CD107F6416BAA/0?vuin=2473990407&amp;amp;term=2"
    # res=tags_recom.recom(images=[url])
    # print(res)
    
    res=tags_recom.recom(["远程", "支援"])
    print(res)

    res=tags_recom.recom(["支援机械"])
    print(res)