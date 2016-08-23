#!/usr/bin/env python3
# -*-coding: utf-8-*-
# Author : Christopher L
# Blog   : http://blog.chriscabin.com
# GitHub : https://www.github.com/chrisleegit
# File   : asort.py
# Date   : 2016/08/22 11:12
# Version: 0.1
# Description: A very simple python script that can sort items alphabetically.

import os
import shutil
import re
import pickle


README_FILE = 'cn.md'
TEMP_FILE = 'temp.md'

# only works for those items between BEGIN and END.
BEGIN = '## 应用程序'
END = '## 配置'


def main():
    global README_FILE

    # make sure the script can find file: README.md
    README_FILE = os.path.abspath(README_FILE)

    if not os.path.exists(README_FILE):
        print('Error: no such file or directory: {}'.format(README_FILE))
        exit(1)

    sort_enable = False
    items = list()

    app_pat = re.compile(r'^[-*+]\s*(?:.*?)\[(.*?)\].*')
    all_apps = set()

    print('Loading file: {}'.format(README_FILE))

    # read file: README.md
    with open(README_FILE) as infile, open(TEMP_FILE, 'w') as outfile:
        # process each line
        for line in infile:
            if not sort_enable and BEGIN in line:
                sort_enable = True

            # if sort_enable and END in line:
            #     sort_enable = False

            if sort_enable:
                line = line.strip()

                # each item starts with a character '-' (maybe '*' or '+')
                if line.startswith(('-', '*', '+')):
                    # get the app name
                    app_name = app_pat.findall(line.strip())
                    if len(app_name) == 1:
                        all_apps.add(app_name[0].strip())
                    items.append(line)
                elif line.startswith('#'):
                    sort_enable = False if END in line else True

                    # when we meet the next header, we should stop adding new item to the list.
                    for item in sorted(items, key=lambda x: x.upper()):
                        # write the ordered list to the temporary file.
                        print(item, file=outfile)
                    print('', file=outfile)
                    items.clear()

                    # remember to put the next header in the temporary file.
                    print(line, file=outfile)
                else:
                    print(line, end='', file=outfile)
            else:
                print(line, end='', file=outfile)

    print('Replace the original file: README.md')

    print(len(all_apps))
    with open('cn_apps.pk', 'wb') as f:
        pickle.dump(all_apps, f)
    # shutil.move(TEMP_FILE, README_FILE)


if __name__ == '__main__':
    main()

