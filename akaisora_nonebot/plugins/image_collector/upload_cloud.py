import requests
import urllib
from html import unescape

from requests.api import head
from lxml import html, etree
import os, sys, re
import io
import json
import pytz
from datetime import datetime, timedelta
from io import BytesIO
import traceback

o_path = os.getcwd()
# sys.path.append(o_path)
# sys.path.append(o_path+"/plugins/")

path_prefix="plugins/"

# import myconfig

class Cloud(object):
    def __init__(self, repo_link="", repo_upload_link="", repo_download_link=""):
        self.repo_link=repo_link
        self.repo_upload_link=repo_upload_link
        self.repo_download_link=repo_download_link
        self.repo_id=""
        self.session=requests.session()

    def get_repo_id(self):
        result=re.search(r"cloud\.tsinghua\.edu\.cn/library/(.+?)/", self.repo_link)
        if result:
            self.repo_id=result.group(1)
        else:
            self.repo_id=""
        
        return self.repo_id


    def get_upload_link(self):
        r=self.session.get(self.repo_upload_link)
        # print(r.status_code)

        headers=self.session.headers
        headers["x-requested-with"]="XMLHttpRequest"
        if not self.repo_id: self.get_repo_id()
        param={
            'r':self.repo_id
        }
        upload_link_id=re.search(r"cloud\.tsinghua\.edu\.cn/u/d/(.+?)/", self.repo_upload_link).group(1)
        upload_pre="https://cloud.tsinghua.edu.cn/ajax/u/d/{0}/upload/".format(upload_link_id)
        r=self.session.get(upload_pre, params=param, headers=headers)
        # print(r.text)
        # print(r.status_code)

        js=r.json()

        self.file_upload_link=js["url"]

        return self.file_upload_link

    def upload_file(self, file_upload_link, file_path=None, file_like=None, rel_path=""):
        headers=self.session.headers
        # with open(file_path,'rb') as fp:
        #     file_content=fp.read()
        # fp=io.BytesIO(file_content)
        # fp.name="kkk.png"
        if file_path:
            files = {'file': open(file_path,'rb')}
        elif file_like:
            files = {'file': file_like}
        if rel_path and rel_path[-1]!="/":
            rel_path=rel_path+"/"
        data={
            "parent_dir": "/",
            "relative_path":rel_path
        }
        r=self.session.post(file_upload_link, data=data, files=files, headers=headers)
        # print("upload result", r.text)
        filename=r.json()[0]["name"]

        return r.json()

    def upload(self, file_path=None, file_like=None, rel_path=""):
        file_upload_link=self.get_upload_link()
        result=self.upload_file(file_upload_link, file_path, file_like, rel_path)

        return result

        # print(filename)


if __name__=="__main__":
    repo_link=myconfig.repo_link
    repo_upload_link=myconfig.repo_upload_link
    repo_download_link=myconfig.repo_download_link
    cloud=Cloud(repo_link, repo_upload_link, repo_download_link)


    cloud.upload(path_prefix+"image.jpg")