#!/usr/bin/env python3
# -*-coding: utf-8-*-
# Author : Chris
# Blog   : http://blog.chriscabin.com
# GitHub : https://www.github.com/chrisleegit
# File   : PSpider.py
# Date   : 16-5-21
# Version: 0.1
# Description: 从鸟哥的网站获取所有的基础篇的内容，并生成PDF文件保存；每一章都单独存到一个文件中

import pdfkit
import requests
from bs4 import BeautifulSoup
from threading import *
import  datetime
import os

# 控制PDF生成的格式
OPTIONS = {
    'page-size': 'Letter',
    'margin-top': '0.75in',
    'margin-right': '0.75in',
    'margin-bottom': '0.75in',
    'margin-left': '0.75in',
    'encoding': 'UTF-8',
    'quiet': ''
}


# 鸟哥的网站主页
ROOT_URL = 'http://linux.vbird.org'

# 基础篇教程基本URL
BASIC_URL = 'http://linux.vbird.org/linux_basic'

# 存放所有处理页面线程
PROC_THREADS = list()


def get_valid_name(name):
    """
    过滤掉名称中不适合作为文件名的字符，用空格替代
    """
    assert isinstance(name, str)
    invalid_chars = ("\\", "/", ":", "?", "*", "<", ">", "|")
    for x in invalid_chars:
        if x in name:
            name = name.replace(x, ' ')
    return name.strip()


def get_first_url():
    return 'http://linux.vbird.org/linux_basic/0105computers.php'


def get_next_url(html):
    if isinstance(html, str):
        try:
            return os.path.join(BASIC_URL,
                                BeautifulSoup(html, 'lxml').find('div',
                                                                 {'class': 'rightarea'}).a['href'])
        except Exception as e:
            # print('错误：{}'.format(str(e)))
            return ''

    return ''


def save2pdf(title, html):
    """
    把HTML保存成为PDF
    """
    title = get_valid_name(title)
    print('线程：{}，正在生成 {}.pdf，请耐心等待...'.format(current_thread().getName(), title))
    try:
        pdfkit.from_string(html, os.path.join('archives', '{}.pdf'.format(title)),
                           options=OPTIONS, css='style.css')
    except Exception as e:
        print('错误：{}'.format(str(e)))


def download_page(url):
    """
    下载指定URL的HTML格式源文，返回转为UTF-8编码的HTML文本
    """
    if isinstance(url, str):
        print('正在下载网页：{}，请稍等...'.format(url))
        return requests.get(url).content.decode('utf-8')
    else:
        return ''


def process_page(count, url, html):
    """
    处理下载好的文档，并启动保存成PDF线程
    """
    global SAVE_THREADS
    if isinstance(html, str):
        if str != '':
            print('线程：{}，正在处理来自{}的页面...'.format(current_thread().getName(), url))
            soup = BeautifulSoup(html, 'lxml')

            # 找到所有block元素，主体内容都在这些标签中
            blocks = soup.find_all('div', {'class': 'block1'})

            # 获取文章的标题
            title = '{}. {}'.format(count, blocks[0].h1.text)

            # 构建新的只包含主体部分的HTML
            soup = BeautifulSoup(
                '''
                <html lang="zh-TW">
                    <head>
                        <meta charset="utf-8" />
                    </head>
                    <body><div></div></body>
                </html>
                ''', 'lxml')

            tmp = BeautifulSoup('<p>本文由PSpider自动生成，原文链接：<a href="{}" style="margin: 10px">{}</a></p>'.format(url, url), 'lxml')

            container = soup.html.body.div
            container.append(tmp)

            for block in blocks[:-1]:
                # 需要注意的是，必须把所有img元素src属性设置为绝对路径，否则生成pdf会丢失图片
                for img in block.find_all('img'):
                    if img['src'].startswith('/'):
                        img['src'] = ROOT_URL + img['src']

                container.append(block)
           
            save2pdf(title, str(soup))


def main():
    global PROC_THREADS

    print('开始整理，请耐心等待...')
    start = datetime.datetime.now()

    count = 0
    url = get_first_url()
    while url != '':
        count += 1
        print(count, end=': ')
        html = download_page(url)

        # 启动线程处理网页，并保存文件为PDF
        thr = Thread(target=process_page, args=(count, url, html))
        PROC_THREADS.append(thr)
        thr.start()

        # 获取到下个URL
        url = get_next_url(html)

    # 等待所有的线程运行完毕
    for x in PROC_THREADS:
        x.join()

    print('任务完成!耗时：{}s'.format((datetime.datetime.now() - start).total_seconds()))

if __name__ == '__main__':
    main()
