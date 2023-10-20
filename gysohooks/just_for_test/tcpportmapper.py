import socket
import threading


def forward(src_port, dest_ip, dest_port):
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('0.0.0.0', src_port))
        server.listen(5)
        print(f"等待连接在端口 {src_port} 上...")

        while True:
            client, addr = server.accept()
            print(f"接受来自 {addr[0]}:{addr[1]} 的连接")

            target = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target.connect((dest_ip, dest_port))

            def forward_data(source, target):
                while True:
                    data = source.recv(1024)
                    if len(data) == 0:
                        break
                    target.send(data)

            threading.Thread(target=forward_data, args=(client, target)).start()
            threading.Thread(target=forward_data, args=(target, client)).start()

    except Exception as e:
        print(f"发生错误: {str(e)}")


if __name__ == "__main__":
    src_port = 12345  # 源端口
    dest_ip = "127.0.0.1"  # 目标IP地址
    dest_port = 12312  # 目标端口

    forward(src_port, dest_ip, dest_port)
