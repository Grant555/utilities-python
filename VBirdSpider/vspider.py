#!/usr/bin/env python3
# -*-coding: utf-8-*-
# Author : Chris
# Blog   : http://blog.chriscabin.com
# GitHub : https://www.github.com/chrisleegit
# File   : vspider.py
# Date   : 16-5-21
# Version: 0.1
# Description:
import datetime
from bs4 import BeautifulSoup, Tag
import os
import sys
import pdfkit
import requests


# 控制生成的pdf格式
options = {
    'page-size': 'Letter',
    'margin-top': '0.75in',
    'margin-right': '0.75in',
    'margin-bottom': '0.75in',
    'margin-left': '0.75in',
    'encoding': 'UTF-8',
    'quiet': ''
}

root_url = 'http://linux.vbird.org'
basic_url = 'http://linux.vbird.org/linux_basic'
burl = 'http://linux.vbird.org/linux_basic/0105computers.php'


def foo(url, index=0):
    print('开始下载文档...', end='')
    start = datetime.datetime.now()
    page_html = requests.get(url).content.decode('utf-8')
    print((datetime.datetime.now() - start).total_seconds())

    print('开始处理文档...', end='')
    start = datetime.datetime.now()

    # 获取下一篇文档的链接
    next_url = ''
    try:
        next_url = os.path.join(basic_url,
                                BeautifulSoup(page_html, 'lxml').find('div', {'class': 'rightarea'}).a['href'])
    except Exception as e:
        print(str(e))

    # 重新组建一个只包含文章内容的soup
    soup = BeautifulSoup(
        '''
        <html lang="zh-TW">
            <head>
                <meta charset="utf-8" />
            </head>
            <body><div></div></body>
        </html>
        ''', 'lxml')

    container = soup.html.body.div

    blocks = BeautifulSoup(page_html, 'lxml').find_all('div', {'class': 'block1'})[1:-1]

    for block in blocks:
        # 给所有的图片设置为绝对路径，否则生成的PDF会丢失图片
        for img in block.find_all('img'):
            if img['src'].startswith('/'):
                img['src'] = root_url + img['src']
        container.append(block)

    time = datetime.datetime.now() - start
    print(time.total_seconds())

    print('开始生成PDF文档...{}'.format(index), end='')
    # print(soup.prettify(), file=open('temp.html', 'w'))
    start = datetime.datetime.now()
    pdfkit.from_string(str(soup), 'archives/{}.pdf'.format(index), options=options, css='style.css')
    print((datetime.datetime.now() - start).total_seconds())

    if next_url != '':
        foo(next_url, index=index+1)


def main():
    foo(burl, index=1)


if __name__ == '__main__':
    main()
