import os, sys
import requests
from . import pixiv_crawler as pc

o_path = os.getcwd()

# path_prefix="./akaisora/plugins/"


class Pixivsetu(object):
    def __init__(self, username=None, password=None, setu_data_path = "./data/setu"):
        pc.set_value("username",username)
        pc.set_value("password",password)
        pc.set_value("local_save_root",setu_data_path)
        pc.set_value("chrome","/root/chromedriver")
        pc.set_value("cookies_file",setu_data_path+"/cookies.txt")
        # pc.set_value("phantomjs","D:/tectree/Code/phantomjs-2.1.1-windows/bin/phantomjs.exe")
        # pc.set_value('socks','127.0.0.1:21474')
        # self.classi_lis=["normalrank"]
        self.farthest_exist_time=0
        # self.jdtuc=Jd_tuchuang()
        self.maxitems=100
        self.local_save_root=setu_data_path

    def get_setu(self, tags=None):
        if not tags or tags=="normalrank":
            classi="normalrank"
            label=None
        elif tags.split(" ")[0]=="user":
            classi="illustrator"
            label=tags.split(" ")[1]
        else:
            classi="tag"
            label=tags

        self.check_tempfile_overflow()
        setu_path=pc.random_one_by_classfi(classi, label)

        if isinstance(setu_path, list):
            ret_msg=[]
            text_lis=["{0}({1})".format(user[0],user[1]) for user in setu_path]
            text="\n".join(text_lis)
            return text
        else:

            # setu_path="./default_save/75568889_p0.png"
            if not setu_path:return None

            return {"image":setu_path}

        # return ret_msg

        

    def upload_tuc(self, img_path):
        UPLOAD_URL = "https://sm.ms/api/upload"
        if not os.path.isfile(img_path):
            print('要上传的文件不存在')
            return None
        data = {'smfile': open(img_path, 'rb')}
        r = requests.post(UPLOAD_URL, files=data)
        js=r.json()
        print(js)
        if js["code"]=="error":
            print("图床err: "+js["msg"])
            return None

        img_url=js["data"]["url"]

        # delete old img
        time_expr=20*60
        self.del_old_imgurl(js["data"]["timestamp"]-time_expr)
        
        return img_url

    def del_old_imgurl(self, time_bound):
        LIST_URL = "https://sm.ms/api/list"
        params = {'ssl': 0, 'format': 'json'}
        r = requests.get(LIST_URL, params)
        history_lis=r.json()
        if history_lis["code"]!="success":
            print("get upload history failed")
            return
        for img in history_lis["data"]:
            if img["timestamp"]<time_bound and img["timestamp"]>self.farthest_exist_time:
                r=requests.get(img["delete"])
                if "success" in r.text or "already" in r.text:
                    print("DELETE RESULT SUCCESS")
                    self.farthest_exist_time=max(self.farthest_exist_time, img["timestamp"])
                else:
                    print("DELETE RESULT FAIL")
    
    def check_tempfile_overflow(self):
        if not os.path.exists(self.local_save_root) : os.makedirs(self.local_save_root)
        temp_file_list=os.listdir(self.local_save_root)

        if(len(temp_file_list)>self.maxitems):
            for filename in temp_file_list:os.remove(self.local_save_root+"/"+filename)
            print("cleared local_save_root")

        



        
if __name__=="__main__":
    pixiv_setu=Pixivsetu()
    # img_url=pixiv_setu.get_setu("德克萨斯")
    img_url=pixiv_setu.get_setu()
    print(img_url)
    