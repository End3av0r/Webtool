import sys
import socket
import threading

'''
Python黑帽子 黑客与渗透测试编程之道
基础网络编程工具
Proxy
四个模块
1. hexdump函数          将本地设备和远程设备之间的通信过程显示到屏幕上
2. receive_from函数     从本地设备或远程设备的入口socket接收数据
3. proxy_handler函数    控制远程设备和本地设备之间的流量方向
4. server_loop函数      创建一个监听的socket,并把他传给proxy_handler函数
'''

HEX_FILTER = ''.join(
   [(len(repr(chr(i)))==3) and chr(i) or '.' for i in range(0,256)]
)
'''
(len(repr(chr(i))) == 3) and chr(i) or '.'：
这是一个条件表达式(ternary conditional expression)。如果前面的条件为True，它返回字符本身(chr(i))，否则返回句点('.')。
'''
# try:
#     print(HEX_FILTER)
# except UnicodeEncodeError:
#     print(HEX_FILTER.encode('utf-8').decode(sys.stdout.encoding))

def hexdump(src,length=16,show=True):
    if(isinstance(src,bytes)): #isinstance() 判断src是否为byte类型
        src = src.decode()
    results = list()
    for i in range(0,len(src),length):
        word = str(src[i:i+length])
        printable = word.translate(HEX_FILTER)
        # translate() 方法，用于执行字符串的字符级别转换和删除操作。通常，这个方法用于执行字符替换或字符删除操作，其中需要一个字符映射表作为参数。
        # trans_table = str.maketrans({'a': 'x', 'b': 'y', 'c': None})
        # 使用转换表将字符串进行转换
        # text = "abcdefg"
        # new_text = text.translate(trans_table)
        # print(new_text)  # 输出 "xydefg"
        hexa = ' '.join([f'{ord(c):02X}' for c in word])
        hexwidth = length*3
        results.append((f'{i:04x} {hexa:<{hexwidth}} {printable}'))
        #{hexa:<{hexwidth}}：这部分是之前构建的 hexa 字符串，要求左对齐，并使用 hexwidth 的值来确定宽度。
    if show:
        for line in results:
            print(line)
    else:
        return results

# print(hexdump('python rocks\n and proxies roll\n'))
# 0000 70 79 74 68 6F 6E 20 72 6F 63 6B 73 0A 20 61 6E  python rocks. an
# 0010 64 20 70 72 6F 78 69 65 73 20 72 6F 6C 6C 0A     d proxies roll.
# None

# 接收数据的函数
def receive_from(connection:socket.socket):  # 函数形参预置类型
    buffer = b''
    connection.settimeout(5)  # 设置超时时间为5s
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except Exception as e:
        print(e)
    return buffer  # 编码形式

def request_handler(buffer:bytes):
    #perform packet modifications
    return buffer

def response_handler(buffer:bytes):
    #perform packet modifications
    return buffer

def proxy_handler(client_socket,remote_host,rempote_port,receive_first):
    remote_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    remote_socket.connect((remote_host,rempote_port))  # 连接远程的主机

    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)
    
    remote_buffer = response_handler(remote_buffer) # 用response_handler 处理服务器发来的数据
    # 将服务器发来的数据 通过代理转发给客户端
    if(len(remote_buffer)):
        print("[<==] Sending %d bytes to localhost."% len(remote_buffer))
        client_socket.send(remote_buffer)
    while(True):
        # 接收客户端数据
        local_buffer = receive_from(client_socket)
        if(len(local_buffer)):
            print("[<==] Received %d bytes from remote."% len(local_buffer))
            hexdump(local_buffer)
        local_buffer = request_handler(local_buffer)
        # 通过代理转发
        remote_socket.send(local_buffer)
        print("[==>] Sent to remote.")
        # 接收服务端数据
        remote_buffer = receive_from(remote_socket)
        if(len(remote_buffer)):
            print("[<==] Sending %d bytes to localhost."% len(remote_buffer))
            hexdump(remote_buffer)
        remote_buffer = request_handler(remote_buffer)
        # 通过代理转发
        remote_socket.send(remote_buffer)
        print("[<==] Sent to localhost.")

        if(len(remote_buffer) == 0 or len(local_buffer) == 0):
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing connections")
            break

def server_loop(local_host,local_port,remote_host,remote_port,receive_first):
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        server.bind((local_host,local_port))
    except Exception as e:
        print(f'problem on bind: {e}')
        print(f"[!!] Failed to listen on {local_host} : {local_port}")
        sys.exit(0)
    
    print(f"[*] Listening on {local_host} : {local_port}")
    server.listen(5)
    while True:
        client_socket,addr = server.accept()
        line = f'>Received incoming connection from {addr[0]:addr[1]}'
        print(line)
        proxy_thread = threading.Thread(
            target=proxy_handler,
            args=(client_socket,remote_host,remote_port,receive_first)
        )
        proxy_thread.start()

def main():
    if len(sys.argv[1:]) != 5:
        print("Usage: ./proxy.py [localhost] [localport]", end = '')
        print("[remotehost] [remoteport] [receive_first]")
        print("Example: ./proxy.py 127.0.0.1 9000 10.12.132.1 9000 True")
        sys.exit(0)
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])
    receive_first = sys.argv[5]
    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False
    
    server_loop(local_host, local_port, remote_host, remote_port, receive_first)

if __name__ == '__main__':
    main()


    

