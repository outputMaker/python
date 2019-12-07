import argparse, socket, os, select, time
from threading import Thread

def create_srv_socket(address):
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(address)
    listener.listen(64)
    print('Listening at {}'.format(address))
    return listener

def all_events_forever(poll_object):
    while True:
        for fd, event in poll_object.poll():
            yield fd, event

def async_server(listener):
    #fileno()返回文件描述符
    sockets = {listener.fileno(): listener}
    addresses = {}
    bytes_received = {}#在等待某个请求完成时，会将受到的数据存储在bytes_received字典中。
    bytes_to_send = {}#在等待操作系统安排发送数据时，会将要发送的字节存储在bytes_to_send字典中。

    poll_object = select.poll()
    poll_object.register(listener, select.POLLIN)
    #fd数字代表连接的不同客户端
    #event代表不同的事件
    for fd, event in all_events_forever(poll_object):
        sock = sockets[fd]

        if event & (select.POLLHUP | select.POLLERR | select.POLLNVAL):
            print("挂起|出错|无法读取\n")
            address = addresses.pop(sock)#移除地址
            rb = bytes_received.pop(sock, b'')#
            sb = bytes_to_send.pop(sock, b'')
            if rb:
                print('Client {} sent {} but then closed'.format(address, rb))
            elif sb:
                print('Client {} closed before we sent {}'.format(address, sb))
            else:
                print('Client {} closed socket normally'.format(address))
            print('-*' * 25 ," END ",'*-' * 25)
            poll_object.unregister(fd)
            del sockets[fd]

        # New socket: add it to our data structures.
        elif sock is listener:
            print('-*' * 25 ,"START",'*-' * 25)
            print("新套接字注册进poll\n")
            time.sleep(15)
            sock, address = sock.accept()
            print('Accepted connection from {}'.format(address))
            sock.setblocking(False)     # force socket.timeout if we blunder
            sockets[sock.fileno()] = sock
            addresses[sock] = address
            poll_object.register(sock, select.POLLIN)

        # Incoming data: keep receiving until we see the suffix.

        elif event & select.POLLIN:
            print("读取数据\n")
            time.sleep(15)
            more_data = sock.recv(4096)
            if not more_data:  # end-of-file
                sock.close()  # next poll() will POLLNVAL, and thus clean up
                continue
            file = bytes_received.pop(sock, b'') + more_data
            #此时data为文件名
            if os.path.isfile(file):
                fileSize = (os.stat(file)).st_size#文件大小
                packageNum = int(fileSize / 4096) + 1#包个数
                sock.sendall(str(packageNum).encode('utf8'))#先发送包的个数
                #读取文件,放入字典bytes_to_send[sock]
                GetRunS = open(file, "rb")
                RunS = GetRunS.read()
                bytes_to_send[sock] = RunS
                GetRunS.close()
                poll_object.modify(sock, select.POLLOUT)
            else:
                bytes_to_send[sock] = b'0'
                poll_object.modify(sock, select.POLLOUT)

        # Socket ready to send: keep sending until all bytes are delivered.

        elif event & select.POLLOUT:
            print("发送数据\n")
            time.sleep(15)
            data = bytes_to_send.pop(sock)
            n = sock.send(data)
            if n < len(data):
                bytes_to_send[sock] = data[n:]
            else:
                poll_object.modify(sock, select.POLLIN)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="a description")
    parser.add_argument('host', help='IP or hostname')
    parser.add_argument('-p', metavar='port', type=int, default=1060,
                        help='TCP port (default 1060)')
    args = parser.parse_args()
    address = (args.host, args.p)

    listener = create_srv_socket(address)
    async_server(listener)
