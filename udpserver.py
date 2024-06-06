import socket
import time
import random
import threading

# 定义服务器端口
serverPort = 50007
drop_rate = 0.6  # 丢包率，20%

# 创建UDP socket
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSocket.bind(('', serverPort))  # 监听所有IP地址

print("Server is ready to receive")

# 模拟TCP连接建立过程
# 接收客户端的SYN包
syn_message, clientAddress = serverSocket.recvfrom(2048)
if syn_message.decode() == "SYN":
    # 发送SYN-ACK包
    serverSocket.sendto("SYN-ACK".encode(), clientAddress)

    # 接收客户端的ACK包
    ack_message, _ = serverSocket.recvfrom(2048)
    if ack_message.decode() == "ACK":
        print("TCP-like connection established")

# 定义一个全局变量来控制服务器的运行状态
running = True

# 定义一个函数来监听键盘输入
def listen_for_exit():
    global running
    while True:
        cmd = input()
        if cmd.strip().lower() == 'exit':
            running = False
            break

# 启动一个线程来监听键盘输入
listener_thread = threading.Thread(target=listen_for_exit)
listener_thread.start()

# 开始数据传输阶段
first_response_time = None
last_response_time = None

while running:
    try:
        serverSocket.settimeout(1.0)  # 设置1秒超时
        message, clientAddress = serverSocket.recvfrom(2048)
        recv_time = time.time()

        # 检查是否是FIN包
        if message.decode() == "FIN":
            # 发送ACK包
            serverSocket.sendto("ACK".encode(), clientAddress)
            # 发送FIN包
            serverSocket.sendto("FIN".encode(), clientAddress)
            print("Server is shutting down...")
            # 接收客户端的ACK包
            ack_message, _ = serverSocket.recvfrom(2048)
            if ack_message.decode() == "ACK":
                break

        # 模拟丢包
        if random.random() < drop_rate:
            print(f"Packet with Seq={message[:2].decode()} dropped")
            continue

        # 解析客户端数据
        seq_num = int(message[:2].decode())
        ver = int(message[2:3].decode())
        content = message[3:203].decode()

        # 构造响应数据包
        response_time = time.strftime('%H:%M:%S', time.localtime(recv_time))
        response = f'{seq_num:02d}{ver:01d}{response_time}' + ' ' * (200 - len(response_time))  # 填充数据到200字节
        serverSocket.sendto(response.encode(), clientAddress)

        # 记录第一次和最后一次响应的时间
        if first_response_time is None:
            first_response_time = recv_time
        last_response_time = recv_time

        # 打印接收时间和系统时间
        print(f"Received message from client: Seq={seq_num}, Ver={ver}, Time={time.strftime('%H:%M:%S', time.localtime(recv_time))}")
    except socket.timeout:
        # 超时继续循环，检查running状态
        continue

serverSocket.close()
print("Server has been shut down.")
