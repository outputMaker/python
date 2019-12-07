import argparse, socket, os

def create_srv_socket(address):
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(address)
    listener.listen(64)
    print('Listening at {}'.format(address))
    return listener

def accept_connections_forever(listener):
    while True:
        sock, address = listener.accept()
        print('用户 {} 正在请求资源...'.format(address))
        handle_conversation(sock, address)

def handle_conversation(sock, address):
    try:
        while True:
            send_file(sock)
    except EOFError:
        print('Client socket to {} has closed'.format(address))
    except Exception as e:
        print('Client {} error: {}'.format(address, e))
    finally:
        sock.close()

def send_file(sock):
    file = sock.recv(4096)
    if not file:
        print("传输通道关闭!")
        raise EOFError('socket closed')
    print("{}".format(file.decode("utf8")))
    if os.path.isfile(file):
        print("资源存在!正在传输!")
        fileSize = (os.stat(file)).st_size#文件大小
        packageNum = int(fileSize / 4096) + 1#包个数
        sock.sendall(str(packageNum).encode('utf8'))#先发送包的个数
        check = packageNum #倒数器
        GetRunS = open(file, "rb")
        while check != 0:
            RunS = GetRunS.read(4096)
            sock.sendall(RunS)
            check -= 1
        GetRunS.close()
    else:
        print("资源不存在!")
        sock.sendall(b'0')
#fileExsit("/Users/0yng/py课程/fopnp-m/py3/chapter07/client.py")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="a description")
    parser.add_argument('host', help='IP or hostname')
    parser.add_argument('-p', metavar='port', type=int, default=1060,
                        help='TCP port (default 1060)')
    args = parser.parse_args()
    address = (args.host, args.p)

    listener = create_srv_socket(address)
    accept_connections_forever(listener)
