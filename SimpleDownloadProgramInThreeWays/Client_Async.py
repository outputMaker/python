import argparse, socket, sys, time

def client(address, remote_file, local_file):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(address)
    #发送文件名
    sock.sendall(remote_file.encode("utf8"))
    #接收数据
    message = sock.recv(4096)
    if message == b'0':
        print("文件不存在!")
        sock.close()
        sys.exit()
    else:      
        filep = open(local_file, "ab+")
        view_bar_head = 1
        while True:
            data = sock.recv(1024)
            dataS = filep.write(data)
            if len(data) < 1024:
                print("文件接收完毕!")
                break
        filep.close()
        sock.close()
        sys.exit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Example client')
    parser.add_argument('host', help='IP or hostname')
    parser.add_argument('remote_file', help='remote file')
    parser.add_argument('local_file', help='local file')
    parser.add_argument('-p', metavar='port', type=int, default=1060,
                        help='TCP port (default 1060)')
    args = parser.parse_args()
    address = (args.host, args.p)
    client(address, args.remote_file, args.local_file)
