import requests
import queue
import threading
import sys

'''
文件目录爆破
'''
AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
EXTENSIONS = ['.php','.bak','.inc']
TARGET  = "http://127.0.0.1"
THREADS = 50
WORDLIST = "E:\python_web\Webtool\python_web\dict.txt"

def get_words(resume=None):
    def extend_words(word):
        if("." in word):
            words.put(f'/{word}')
        else:
            words.put(f'/{word}/')
            for extension in EXTENSIONS:
                words.put(f'/{word}{extension}')
    with open(WORDLIST) as f:
        raw_words = f.read()
    raw_words = raw_words.split()
    found_resume = False
    words = queue.Queue()
    for word in raw_words:
        if resume is not None:
            if found_resume:
                extend_words(word=word)
            elif word == resume:
                found_resume = True
                print(f"Continue finding Web path from {resume}")
        else:
             extend_words(word=word)
    return words

def dir_bruter(words=queue.Queue()):
    headers = {'User-Agent':AGENT}
    while(not words.empty()):
        url = TARGET+words.get()
        try:
            req = requests.get(url=url,headers=headers)
        except Exception as e:
            print(e)
        if req.status_code == 200:
            print(f'[success] {url} {req.status_code}')

if __name__ == '__main__':
    words = get_words()
    print("Press return to continue")
    sys.stdin.readline()  # 开始
    for i in range(THREADS):
        thread = threading.Thread(target=dir_bruter(words=words))
        thread.start()





