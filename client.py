from socket import socket
import sys

class FTPClient:
    def __init__(self, server_host='192.168.5.200', server_port=8888):
        self.ADDR = (server_host, server_port)
        self.sockfd = socket()

    def connect(self):
        try:
            self.sockfd.connect(self.ADDR)
        except Exception as e:
            print("连接服务器失败:", e)
            sys.exit()

    def send_cmd(self, command):
        self.sockfd.send(command.encode())
        return self.sockfd.recv(128).decode()

    def list_files(self):
        response = self.send_cmd('L')
        if response == 'OK':
            data = self.sockfd.recv(4096).decode()
            files = data.split(',')
            for file in files:
                print(file)
        else:
            print(response)

    def quit(self):
        self.send_cmd('Q')
        self.sockfd.close()
        sys.exit("谢谢使用")

    def get_file(self, filename):
        response = self.send_cmd(f'G {filename}')
        if response == 'OK':
            with open(filename, 'wb') as fd:
                while True:
                    data = self.sockfd.recv(1024)
                    if data == b"##":
                        break
                    fd.write(data)
        else:
            print(response)

    def put_file(self, filename):
        try:
            with open(filename, 'rb') as f:
                filename = filename.split('/')[-1]
                response = self.send_cmd(f'P {filename}')
                if response == 'OK':
                    while True:
                        data = f.read(1024)
                        if not data:
                            self.sockfd.send(b'##')
                            break
                        self.sockfd.send(data)
                else:
                    print(response)
        except FileNotFoundError:
            print("没有该文件")

    def close_connection(self):
        self.sockfd.close()

def main():
    ftp_client = FTPClient()  # 创建FTP客户端实例
    ftp_client.connect()

    while True:
        print("\n=======命令选项=========")
        print("1. 列出文件 (list)")
        print("2. 下载文件 (get filename)")
        print("3. 上传文件 (put filename)")
        print("4. 退出 (quit)")
        print("========================")

        cmd = input("输入命令>>")
        if cmd == 'list':
            ftp_client.list_files()
        elif cmd == 'quit':
            ftp_client.quit()
        elif cmd.startswith('get '):
            filename = cmd.split(' ')[1]
            ftp_client.get_file(filename)
        elif cmd.startswith('put '):
            filename = cmd.split(' ')[1]
            ftp_client.put_file(filename)
        else:
            print("请输入正确命令")

    ftp_client.close_connection()

if __name__ == "__main__":
    main()
