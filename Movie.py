#-*- coding: utf-8 -*-
import re
import os
import json
import requests

from multiprocessing import Pool
from requests.exceptions import RequestException

def get_one_page(url):
    '''
    获取网页html内容并返回
    '''
    try:
        # 获取网页html内容
        response = requests.get(url)
        # 通过状态码判断是否获取成功
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None

def parse_one_page(html):
    '''
    解析HTML代码，提取有用信息并返回
    '''
    # 正则表达式进行解析
    pattern = re.compile('<dd>.*?board-index.*?>(\d+)</i>.*?data-src="(.*?)".*?name">'
        + '<a.*?>(.*?)</a>.*?"star">(.*?)</p>.*?releasetime">(.*?)</p>'
        + '.*?integer">(.*?)</i>.*?fraction">(.*?)</i>.*?</dd>', re.S)
    # 匹配所有符合条件的内容
    items = re.findall(pattern, html)

    for item in items:
        yield {
            'index': item[0],
            'image': item[1],
            'title': item[2],
            'actor': item[3].strip()[3:],
            'time': item[4].strip()[5:],
            'score': item[5] + item[6]
        }

def write_to_file(content):
    '''
    将文本信息写入文件
    '''
    with open('result.txt', 'a') as f:
        f.write(json.dumps(content) + '\n')
        f.close()

def save_image_file(url, path):
    '''
    保存电影封面
    '''
    ir = requests.get(url)
    if ir.status_code == 200:
        with open(path, 'wb') as f:
            f.write(ir.content)
            f.close()

def main(offset):
    url = 'http://maoyan.com/board/4?offset=' + str(offset)
    html = get_one_page(url)
    # 封面文件夹不存在则创建
    if not os.path.exists('covers'):
        os.mkdir('covers')

    for item in parse_one_page(html):
        print(item)
        write_to_file(item)
        save_image_file(item['image'], 'covers/' + '%03d'%int(item['index']) + item['title'] + '.jpg')

if __name__ == '__main__':
    for i in range(10):
        main(i * 10)

