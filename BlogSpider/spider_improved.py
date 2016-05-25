#!/usr/bin/env python3
# -*-coding: utf-8-*-
# Author : Chris
# Blog   : http://blog.chriscabin.com
# GitHub : https://www.github.com/chrisleegit
# File   : spider_improved.py
# Date   : 16-5-22
# Version: 0.1
# Description: BUILD FAILED! THE SEVER WILL SHUTDOWN, TOO MANY REQUESTS AT A TIME!!!!!

# 主线程使用页面作为分析处理单元，得到页面对应所有文章的链接；子线程负责处理所有文章链接
# 并完成PDF转换工作
from threading import current_thread, Thread
import datetime
import requests
import sys
from bs4 import BeautifulSoup, Tag
import os
import pdfkit

# 代理设置
PROXIES = {
    "http": "http://223.3.45.6:1088",
    "https": "https://223.3.45.6:1088"
}

# 控制PDF输出格式
OPTIONS = {
    'page-size': 'Letter',
    'margin-top': '0.75in',
    'margin-right': '0.75in',
    'margin-bottom': '0.75in',
    'margin-left': '0.75in',
    'encoding': 'UTF-8',
    'proxy': PROXIES['http'],
    'quiet': ''
}


# 所有正在运行的线程
THREADS = []

# 所有处理过的URL
BLOG_URLS = []


def get_valid_name(name):
    """
    过滤掉名称中不适合作为文件名的字符，用空格替代
    """
    invalid_chars = ("\\", "/", ":", "?", "*", "<", ">", "|")
    for x in invalid_chars:
        if x in name:
            name = name.replace(x, ' ')
    return name


def get_pure_article(content):
    if isinstance(content, Tag):
        # 构建新的文章，只包括文章内容
        new_soup = BeautifulSoup('''<html  lang="zh-CN">
            <head><meta http-equiv="content-type" content="text/html;charset=utf-8"></head>
            <body></body></html>''', 'lxml')
        new_soup.body.append(content)
        return str(new_soup)
    else:
        return None


def get_article_title(content):
    if isinstance(content, Tag):
        return content.header.h1.text
    else:
        return '未命名'


def get_article_category(content):
    if isinstance(content, Tag):
        return content.header.div.span.text.split('->')[-1].strip()
    else:
        return '未分类'


def save_article(html):
    soup = BeautifulSoup(html, 'lxml')
    if isinstance(soup, BeautifulSoup):
        # 获得文章内容
        content = soup.find('article')

        # 得到文章标题名称
        title = get_article_title(content)

        # 得到文章的分类信息
        category = get_article_category(content)

        # 创建存放文章的分类目录
        if not os.path.exists(os.path.join('archives', category)):
            os.mkdir(os.path.join('archives', category))

        # 实际保存后的文件名称
        name = '{}'.format(get_valid_name('{}'.format(title)))

        try:
            print('正在生成文件：{}.pdf...'.format(title))
            article = get_pure_article(content)
            if article:
                # 生成PDF文件，这里的css文件是博客使用的样式
                pdfkit.from_string(article, os.path.join('archives', category, '{}.pdf'.format(name)),
                                   options=OPTIONS, css='style.css')

            return True
        except Exception as e:
            print(str(e))
            return False

    return False


def get_html(url):
    """
    获取指定URL的UTF-8编码的文本HTML
    """
    if isinstance(url, str):
        print('GET: {}'.format(url))
        return requests.get(url, proxies=PROXIES).content.decode('utf-8')
    else:
        return ''


def process_blog(blog_url):
    """
    处理单独的博客，由单独的线程来执行，加速处理过程
    """
    if isinstance(blog_url, str):
        print('线程{}正在处理博客，'.format(current_thread().getName(), blog_url), end='')
        save_article(get_html(blog_url))
    else:
        return


def process_page(page_url):
    """
    处理单个页面，由一个子线程执行
    """
    if isinstance(page_url, str):
        print('线程{}正在处理页面，'.format(current_thread().getName(), page_url), end='')
        # 下载页面
        page_html = get_html(page_url)
        if page_url != '':
            # 找到页面所有文章的入口URL
            url_list = (x.header.h2.a['href'] for x
                        in BeautifulSoup(page_html, 'lxml').find_all('article'))
            for url in url_list:
                BLOG_URLS.append(url)
                # process_blog(url)
                thr = Thread(target=process_blog, args=(url, ))
                THREADS.append(thr)
                thr.start()
    else:
        return


def main():
    # 主站的URL
    main_url = 'http://blog.chriscabin.com'

    # 指定总共有多少页博客（这样不用程序去分析页面找到页面链接，节省时间）
    blog_page_total = 11

    start = datetime.datetime.now()

    print('开始整理博客，请稍等...')
    # 主线程启动后台线程下载每页对应的页面
    for index in range(1, blog_page_total + 1):
        process_page(os.path.join(main_url, 'page', str(index)))

    # 等待所有线程结束
    for x in THREADS:
        if isinstance(x, Thread):
            x.join()

    end = datetime.datetime.now()

    print('任务完成，共计{}篇文章，耗时{:}秒'.format(len(BLOG_URLS),
                                        (end - start).total_seconds()))

if __name__ == '__main__':
    main()
