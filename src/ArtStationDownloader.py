#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = "0.0.2"
# $Source$

import argparse

from app import App
from console import Console


def main():
    parser = argparse.ArgumentParser(
        prog='FK_ArtStation下载器',
        description='FK_ArtStation下载器是对ArtStation网站资源根据用户名进行下载的小工具')
    parser.add_argument('--version', action='version',
                        version='%(prog)s '+__version__)
    parser.add_argument('-u', '--username',
                        help='进行下载的用户名，可用逗号 , 分隔', nargs='*')
    parser.add_argument('-d', '--directory', help='下载文件夹')
    args = parser.parse_args()

    if args.username:
        if args.directory:
            console = Console()
            console.download_by_usernames(args.username, args.directory, args.type)
        else:
            print("请设置输出文件夹。可使用 -d 参数。")
    else:
        app = App(version=__version__)
        app.mainloop()  # 进入主循环，程序运行


if __name__ == '__main__':
    main()
