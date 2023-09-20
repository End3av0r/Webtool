import requests
from bs4 import BeautifulSoup as bs
import sys
import contextlib
import os
import queue
import threading
import time


# BeautifulSoup库使用
# url = "https://cn.bing.com/"
# req = requests.get(url=url)
# # print(req.content.decode())
# tree = bs(req.text,'html.parser')
# for link in tree.find_all('a'):
#     print(f"{link.get('href')} -> {link.text}")

FILTERED = ['.jpg','.gif','.png',".css"]  # 用于过滤不想用的文件
Target = "http://127.0.0.1/wordpress-6.0.5-zh_CN/wordpress"
THREADS = 10

answers = queue.Queue() # 存储最后扫描到的文件路径
web_paths = queue.Queue() # 路径字典

def gather_paths():
    for root,_,files in os.walk('.'):
        for fname in files:
            if(os.path.splitext(fname)[1] in FILTERED):
                continue
            path = os.path.join(root,fname)
            if(path[0]=='.'): #.\Webtool\python_web\TCP_proxy.py ==> \Webtool\python_web\TCP_proxy.py
                path = path[1:]   
            print(path)
            web_paths.put(path)

def chdir(path):
    this_dir = os.getcwd()
    os.chdir(path)
    try:
        # yield
        gather_paths()
    finally:
        os.chdir(this_dir)

def test_remote():
    temp_list = []
    while not web_paths.empty():
        item = web_paths.get()
        temp_list.append(item)

    # 对列表进行逆置
    temp_list.reverse()

    # 将逆置后的元素重新放回队列
    for item in temp_list:
        web_paths.put(item)
    while not web_paths.empty():
        path = web_paths.get()
        path = path.replace("\\","/")   # 注意windows系统需要将\ 替换为/
        url = f'{Target}{path}'
        url
        time.sleep(2)
        r = requests.get(url=url)
        # print(url)
        if r.status_code == 200:
            answers.put(url)
            sys.stdout.write('+')
        else:
            sys.stdout.write('x')
        sys.stdout.flush()
def run():
    mythreads = []
    for i in range(THREADS):
        print(f'Spawning thread {i}')
        thread = threading.Thread(target=test_remote)
        mythreads.append(thread)
        thread.start()
    
    for thread in mythreads:
        thread.join()

        


if __name__ == '__main__':
    # with chdir('E:\\样本\\白样本\\wordpress\\wordpress-2.8.5-zh_CN'):
    #       gather_paths()     运行失败
    chdir(r'D:\\phpstudy_pro\\WWW\\wordpress-6.0.5-zh_CN\\wordpress')
    run()
    # while not answers.empty():
    #     print(answers.get())
