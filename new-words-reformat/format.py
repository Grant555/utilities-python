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


def process_words(filename):
    with open(filename, 'r') as inf, open('tmp', 'w') as of:
        for line in inf:
            if line.startswith('1.'):
                # 提取单词或短语
                word = line.replace('1.', '').strip().capitalize()
                if word.startswith('**'):
                    word = '1. {}'.format(word)
                else:
                    word = '1. **{}**'.format(word)
                print(word, file=of)
            else:
                # 第一种情况是已经处理过的了，即含有缩进和 `-`
                if line.strip().startswith('-'):
                    # 原样写
                    print(line.rstrip(), file=of)
                elif line.strip() != '':
                    # 添加 `-` 再写回
                    print('    - {}'.format(line.strip()), file=of)
                else:
                    print('', file=of)

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

