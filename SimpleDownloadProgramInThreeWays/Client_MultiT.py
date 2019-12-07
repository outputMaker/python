import argparse, socket, sys, time

def view_bar(num,total):
    rate = num / total
    rate_num = int(rate * 100)
    r = '\rloading[%d]%%%s>' % (rate_num,'='*num)
    time.sleep(1)
    sys.stdout.write(r)
    sys.stdout.flush()

def client(address, remote_file, local_file):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(address)
    #发送文件名
    sock.sendall(remote_file.encode("utf8"))
    #接收数据
    message = sock.recv(4096)
    print(message)
    if message == b'0':
        sock.close()
        sys.exit()
    else:      
        filep = open(local_file, "ab+")
        packageNum = int(message.decode('utf8'))
        total = packageNum
        num = 0
        while packageNum != 0:
            data = sock.recv(4096)
            dataS = filep.write(data)
            packageNum = packageNum - 1
            view_bar(total - packageNum,total)
        filep.close()
        sock.close()

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
