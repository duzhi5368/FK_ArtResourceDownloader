# -*- coding: utf-8 -*-

import os
from concurrent import futures

from tkinter import Tk, Frame, Label, Button, Scrollbar, Text, Entry, messagebox, filedialog  # 引入Tkinter工具包
from tkinter import TOP, LEFT, BOTTOM, BOTH, X, Y, END
from tkinter import ttk

import config
from core import Core


class App(Frame):

    def log(self, value):
        self.text.configure(state="normal")
        self.text.insert(END, value + '\n')
        self.text.see(END)
        self.text.configure(state="disabled")

    def download(self):
        self.btn_download.configure(state="disabled")
        username_text = self.entry_filename.get()
        if not username_text:
            messagebox.showinfo(
                title='提示', message='请输入一个或多个用户名')
        else:
            usernames = username_text.split(',')
            if len(usernames) == 0:
                usernames = username_text.split('，') # 兼容全角符号
            self.core.root_path = self.root_path
            self.core.download_by_usernames(usernames)
        self.btn_download.configure(state="normal")

    def browse_directory(self):
        dir = os.path.normpath(filedialog.askdirectory())
        if dir:
            self.root_path = dir
            config.write_config('config.ini', 'Paths',
                                'root_path', self.root_path)
            self.entry_path.delete(0, END)
            self.entry_path.insert(0, self.root_path)

    def createWidgets(self):
        frame_label = Frame(self.window)
        frame_tool = Frame(self.window)
        frame_path = Frame(self.window)
        frame_log = Frame(self.window)
        self.lbl_username = Label(
            frame_tool, text='用户名(多个用户名请用 , 逗号分隔)')
        self.entry_filename = Entry(frame_tool)
        self.btn_download = Button(
            frame_tool, text='开始下载', command=lambda: self.executor_ui.submit(self.download))
        self.lbl_path = Label(frame_path, text='存放路径:')
        self.entry_path = Entry(frame_path)
        self.entry_path.insert(END, self.root_path)
        self.btn_path_dialog = Button(
            frame_path, text="选择下载文件夹", command=lambda: self.browse_directory())
        self.scrollbar = Scrollbar(frame_log)
        self.text = Text(frame_log)
        self.text.configure(state="disabled")
        self.lbl_status = Label(frame_label, text='用户名请输入网址后缀，例如：https://www.artstation.com/robinruan 中的 \"robinruan\" 部分即可，不要输入用户昵称')

        frame_tool.pack(side=TOP, fill=X)
        self.lbl_status.pack(side=LEFT)
        frame_label.pack(side=TOP, fill=X)
        self.lbl_username.pack(side=LEFT)
        self.entry_filename.pack(side=LEFT, fill=X, expand=True)
        self.btn_download.pack(side=LEFT)
        frame_path.pack(side=TOP, fill=X)
        self.lbl_path.pack(side=LEFT)
        self.entry_path.pack(side=LEFT, fill=X, expand=True)
        self.btn_path_dialog.pack(side=LEFT)
        self.text.pack(side=LEFT, fill=BOTH, expand=True)
        self.scrollbar.pack(side=LEFT, fill=Y)
        frame_log.pack(side=TOP, fill=BOTH, expand=True)
        self.scrollbar.config(command=self.text.yview)
        self.text.config(yscrollcommand=self.scrollbar.set)
        self.text.focus()

    def __init__(self, version):
        self.core = Core(self.log)
        master = Tk()
        Frame.__init__(self, master)
        master.title('FK_ArtStation下载器 by FreeKnight 當前版本：' + version)  # 定义窗体标题
        root_path_config = config.read_config(
            'config.ini', 'Paths', 'root_path')
        self.root_path = root_path_config or os.path.join(
            os.path.expanduser("~"), "ArtStation")
        self.executor_ui = futures.ThreadPoolExecutor(1)
        self.window = master
        self.pack()
        self.createWidgets()
