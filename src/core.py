# -*- coding: utf-8 -*-

import os
import re
from concurrent import futures
from multiprocessing import cpu_count
from urllib.parse import urlparse

import requests


class Core:
    total_download_count = 0

    def log(self, message):
        print(message)

    def __init__(self, log_print=None):
        if log_print:
            global print
            print = log_print
        max_workers = cpu_count()*4
        self.executor = futures.ThreadPoolExecutor(max_workers)
        self.executor_video = futures.ThreadPoolExecutor(1)
        self.root_path = None
        self.futures = []
        self.session = requests.session()

    def download_file(self, url, file_path, file_name, title):
        file_fill_name = title + "_" + file_name
        file_full_path = os.path.join(file_path, file_fill_name)
        if os.path.exists(file_full_path):
            self.log('[重复] [{}]'.format(file_full_path))
        else:
            r = self.session.get(url)
            os.makedirs(file_path, exist_ok=True)
            with open(file_full_path, "wb") as code:
                code.write(r.content)
            self.total_download_count += 1
            self.log('[成功] 下载第{}张图：[{}]'.format(self.total_download_count, file_fill_name))

    def download_project(self, hash_id):
        url = 'https://www.artstation.com/projects/{}.json'.format(hash_id)
        r = self.session.get(url)
        j = r.json()
        assets = j['assets']
        title = j['slug'].strip()
        username = j['user']['username']
        for asset in assets:
            assert(self.root_path)
            user_path = os.path.join(self.root_path, username)
            os.makedirs(user_path, exist_ok=True)
            if asset['has_image']:  # 包含图片
                url = asset['image_url']
                file_name = urlparse(url).path.split('/')[-1]
                try:
                    self.futures.append(self.executor.submit(self.download_file,
                                                             url, user_path, file_name, title))
                except Exception as e:
                    print(e)

    def get_projects(self, username):
        data = []
        if username is not '':
            page = 0
            while True:
                page += 1
                url = 'https://www.artstation.com/users/{}/projects.json?page={}'.format(
                    username, page)
                r = self.session.get(url)
                if not r.ok:
                    err = "[错误] [{} {}] ".format(r.status_code, r.reason)
                    if r.status_code == 403:
                        self.log(err + " 因下载次数过多，您的IP被ArtStation封锁了。请明天再尝试。")
                    elif r.status_code == 404:
                        self.log(err + " 您输入的用户名不存在。")
                    else:
                        self.log(err + " 出现了未知错误，请联系开发人员。duzhi5368@gmail.com")
                    break
                j = r.json()
                total_count = int(j['total_count'])
                if total_count == 0:
                    self.log("[错误] 该用户名可能不存在数据或被封锁，请检查用户名正确性。")
                    break
                if page is 1:
                    self.log('\n========== 开始分析 [{}] 用户数据=========='.format(username))
                data_fragment = j['data']
                data += data_fragment
                self.log('\n========== 当前在统计 [{}] 第 {}/{} 页数据=========='.format(username, page, total_count // 50 + 1))
                
                if page > total_count / 50:
                    break
        return data

    def download_by_username(self, username):
        data = self.get_projects(username)
        if len(data) is not 0:
            future_list = []
            self.log('\n========== [{}] 该用户的项目总数为 {} =========='.format(username, len(data)))
            for project in data:
                future = self.executor.submit(
                    self.download_project, project['hash_id'])
                future_list.append(future)
            futures.wait(future_list)

    def download_by_usernames(self, usernames):
        # 去重与处理网址
        username_set = set()
        for username in usernames:
            username = username.strip().split('/')[-1]
            if username not in username_set:
                username_set.add(username)
                self.download_by_username(username)
        futures.wait(self.futures)
        self.log('\n========== 用户 [{}] 数据 [{}] 张图下载完成 =========='.format(username, self.total_download_count))
