#!/usr/bin/env python3
# -*-coding: utf-8-*-
# Author : Chris
# Blog   : http://blog.chriscabin.com
# GitHub : https://www.github.com/chrisleegit
# File   : spider.py
# Date   : 16-5-20
# Version: 0.1
# Description: ...
import datetime
import requests
import os
from bs4 import Tag, BeautifulSoup
import pdfkit
import threading


# 控制生成的pdf格式
options = {
    'page-size': 'Letter',
    'margin-top': '0.75in',
    'margin-right': '0.75in',
    'margin-bottom': '0.75in',
    'margin-left': '0.75in',
    'encoding': 'UTF-8'
}


def get_valid_name(name):
    """
    过滤掉名称中不适合作为文件名的字符，用空格替代
    """
    invalid_chars = ("\\", "/", ":", "?", "*", "<", ">", "|")
    for x in invalid_chars:
        if x in name:
            name = name.replace(x, ' ')
    return name


def get_first_url(soup):
    if isinstance(soup, BeautifulSoup):
        return soup.find('article').header.h2.a['href']

    return ''


def get_next_url(soup):
    if isinstance(soup, BeautifulSoup):
        previous = soup.find('div', {'class': 'nav-previous'})
        if previous:
            return previous.a['href']

    return ''


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


def save_article(soup):
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
            print('正在生成文件：{}.pdf，请稍等...'.format(title))
            article = get_pure_article(content)
            if article:
                # 生成PDF文件，这里的css文件是博客使用的样式
                pdfkit.from_string(article, os.path.join('archives', category, '{}.pdf'.format(name)),
                                   options=options, css='style.css')

            return True
        except Exception as e:
            print(str(e))
            return False

    return False


def save_url(name, url):
    with open(name, 'w') as f:
        print(url, file=f, end='')


def read_url(name):
    if os.path.exists(name):
        return open(name).read().strip()
    else:
        return ''


def main():
    """
    测试耗时：211.419346s
    :return:
    """
    start = datetime.datetime.now()
    url = 'http://blog.chriscabin.com'
    print('开始整理：{}，请耐心等待...'.format(url))
    main_page = requests.get(url).text

    # old_url = read_url('first_url')

    # 第一篇文章作为入口，可以依次查找下一篇文章
    url = get_first_url(BeautifulSoup(main_page, 'lxml'))

    # 保存一下第一篇URL，下一次就以这个URL作为截止
    # save_url('first_url', url)

    # 循环读取每篇文章，再保存
    count = 0
    while url != '':
        count += 1
        page_soup = BeautifulSoup(requests.get(url).text, 'lxml')
        save_article(page_soup)
        url = get_next_url(page_soup)

    end = datetime.datetime.now() - start
    print('全部完成，共计备份{}篇文章，谢谢使用！耗时：{}'.format(count, end.total_seconds()))


if __name__ == '__main__':
    main()

