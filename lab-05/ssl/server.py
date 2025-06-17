import socket
import ssl
import threading

# Thông tin server
server_address = ('localhost', 12345)

# Danh sách các client đã kết nối
clients = []

def handle_client(client_socket):
    # Thêm client vào danh sách
    clients.append(client_socket)

    print("Đã kết nối với:", client_socket.getpeername())

    try:
        # Nhận và gửi dữ liệu
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            print("Nhận:", data.decode('utf-8'))

            # Gửi dữ liệu đến tất cả các client khác
            for client in clients:
                if client != client_socket:
                    try:
                        client.send(data)
                    except Exception as e: # Nên bắt các ngoại lệ cụ thể hơn
                        print(f"Lỗi khi gửi dữ liệu đến client {client.getpeername()}: {e}")
                        # Nếu gửi lỗi, có thể client đã ngắt kết nối, xóa nó khỏi danh sách
                        clients.remove(client) 
    except ConnectionResetError: # Bắt lỗi khi client đột ngột ngắt kết nối
        print(f"Client {client_socket.getpeername()} đã ngắt kết nối đột ngột.")
    except Exception as e: # Bắt các lỗi tổng quát khác trong quá trình xử lý client
        print(f"Lỗi trong quá trình xử lý client {client_socket.getpeername()}: {e}")
    finally:
        print("Đã ngắt kết nối:", client_socket.getpeername())
        if client_socket in clients: # Đảm bảo client_socket còn trong danh sách trước khi remove
            clients.remove(client_socket)
        client_socket.close()

# Tạo socket server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(server_address)
server_socket.listen(5)

print("Server đang chờ kết nối...")
# Lắng nghe các kết nối
while True:
    client_socket, client_address = server_socket.accept()

    # Tạo SSL context
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER) # Sử dụng PROTOCOL_TLS_SERVER cho server
    context.load_cert_chain(certfile="./certificates/server-cert.crt",
                            keyfile="./certificates/server-key.key")

    # Thiết lập kết nối SSL
    ssl_socket = context.wrap_socket(client_socket, server_side=True)

    # Bắt đầu một luồng xử lý cho mỗi client
    client_thread = threading.Thread(target=handle_client, args=(ssl_socket,))
    client_thread.start()