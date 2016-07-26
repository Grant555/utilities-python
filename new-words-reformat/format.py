#!/usr/bin/env python3
# -*-coding: utf-8-*-
# Author : Christopher L
# Blog   : http://blog.chriscabin.com
# GitHub : https://www.github.com/chrisleegit
# File   : format.py
# Date   : 2016/07/26 19:29
# Version: 0.1
# Description: nothing here

import os
import sys
import shutil

"""
格式化生词本：
1. 排序所有单词及其释义；
2. 生成符合 Markdown 格式的文档。

# Fix
1. 破坏已经格式化好的文件。
"""


class Word(object):
    def __init__(self, word):
        self._word = word.capitalize()
        self._lines = list()

    @property
    def word(self):
        return self._word

    def append(self, line):
        self._lines.append(line)

    def __str__(self):
        lines = ''

        for line in self._lines:
            lines += '    - {}\n'.format(line)

        return '1. **{}**\n'.format(self._word) + lines


word = None


def process_words(filename):
    global word
    words = list()

    with open(filename, 'r') as inf, open('tmp', 'w') as of:
        for line in inf:
            line = line.strip()
            if line.startswith('1.'):
                line = line.replace('**', '')
                # 提取单词或短语
                word = Word(line.replace('1.', '').strip())
            elif line != '':
                line = line.replace('-', '')
                word.append(line.strip())
            else:
                words.append(word)

    # 排序
    words.sort(key=lambda x: x.word)

    # 写入文件
    with open('tmp', 'w') as of:
        for word in words:
            print(word, file=of)

    # 完成后替换原来的文件
    shutil.move('tmp', filename)
    print('处理完成！')


def main():
    # 当前工作目录
    current_dir = os.getcwd()
    words_path = os.path.join(current_dir, 'words.md')

    if not os.path.exists(words_path):
        print('错误：不存在文件：{}'.format(words_path))
        exit(1)

    process_words(words_path)


if __name__ == '__main__':
    main()

