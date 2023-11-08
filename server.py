from socket import *
import os
import sys
import signal
import time
import threading

class FTPserver:
    def __init__(self, host='0.0.0.0', port=8888, file_path='/home/brl/Desktop/FTP/server/'):
        self.HOST = host
        self.PORT = port
        self.ADDR = (self.HOST, self.PORT)
        self.FILE_PATH = file_path
        self.sock = socket()
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.sock.bind(self.ADDR)
        self.sock.listen(5)
        print(f"Listen the port {self.PORT}....")
        signal.signal(signal.SIGCHLD, signal.SIG_IGN)

    def do_list(self, connfd):
        # 获取文件列表
        file_list = os.listdir(self.FILE_PATH)
        if not file_list:
            connfd.send("文件库为空".encode())
            return
        else:
            connfd.send(b'OK')
            time.sleep(0.1)

        files = ""
        for file in file_list:
            if file[0] != '.' and os.path.isfile(self.FILE_PATH + file):
                files = files + file + ','
        # 将拼接好的字符串传给客户端
        connfd.send(files.encode())

    def do_get(self, connfd, filename):
        try:
            fd = open(self.FILE_PATH + filename, 'rb')
        except IOError:
            connfd.send('文件不存在'.encode())
            return
        else:
            connfd.send(b'OK')
            time.sleep(0.1)
        # 发送文件内容
        while True:
            data = fd.read(1024)
            if not data:
                time.sleep(0.1)
                connfd.send(b'##')
                break
            connfd.send(data)

    def do_put(self, connfd, filename):
        if os.path.exists(self.FILE_PATH + filename):
            connfd.send("该文件已存在".encode())
            return
        fd = open(self.FILE_PATH + filename, 'wb')
        connfd.send(b'OK')
        # 接收文件
        while True:
            data = connfd.recv(1024)
            if data == b'##':
                break
            fd.write(data)
        fd.close()

    def do_request(self, connfd):
        while True:
            data = connfd.recv(1024).decode()
            if not data or data[0] == 'Q':
                connfd.close()
                return
            elif data[0] == 'L':
                self.do_list(connfd)
            elif data[0] == 'G':
                filename = data.split(' ')[-1]
                self.do_get(connfd, filename)
            elif data[0] == 'P':
                filename = data.split(' ')[-1]
                self.do_put(connfd, filename)

    def run(self):
        while True:
            try:
                connfd, addr = self.sock.accept()
            except KeyboardInterrupt:
                self.sock.close()
                sys.exit("服务器退出")
            except Exception as e:
                print("服务器异常:", e)
                continue
            print("连接客户端：", addr)

            client_thread = threading.Thread(target=self.do_request, args=(connfd,))
            client_thread.start()

        self.sock.close()

if __name__ == "__main__":
    ftp_server = FTPserver()  # 创建FTP服务器实例
    ftp_server.run()  # 运行FTP服务器
