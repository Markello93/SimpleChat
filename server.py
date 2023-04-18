import socket
import threading
import logging

HOST = "127.0.0.1"
PORT = 12345

clients = set()
nicknames = set()


def broadcast(message):
    """Функция отправки сообщений клиента в общий чат"""
    for client in clients:
        client.sendall(message)


def handle_client(conn, addr):
    """Функция обработки подключения нового участника чата"""
    logging.info(f"Новое подключение от {addr}")
    nickname = None

    while not nickname:
        try:
            conn.send("Enter nickname: ".encode("utf-8"))
            nickname = conn.recv(1024).decode("utf-8")
            if nickname in nicknames:
                conn.send(" Этот никнейм занят, пожалуйста используйте другой: ".encode("utf-8"))
                nickname = None
            else:
                nicknames.add(nickname)
        except ConnectionResetError:
            logging.info(f"Соединение с {addr} прервано до ввода никнейма")
            conn.close()
            return

    clients.add(conn)
    broadcast(f"{nickname} присоединился к чату".encode("utf-8"))

    while True:
        try:
            message = conn.recv(1024).decode("utf-8")
            if message == "exit":
                clients.remove(conn)
                conn.close()
                logging.info(f"{nickname} покинул чат.")
                nicknames.remove(nickname)
                broadcast(f"{nickname} покинул чат.".encode("utf-8"))
                break
            else:
                logging.info(f"{nickname}: {message}")
                broadcast(f"{nickname}: {message}".encode("utf-8"))
        except Exception as e:
            if conn in clients:
                clients.remove(conn)
                conn.close()
                logging.error(f"Error: {e}")
                nicknames.remove(nickname)
                broadcast(f"{nickname} покинул чат.".encode("utf-8"))
                break


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        logging.info(f"Server is listening on {HOST}:{PORT}")
        try:
            while True:
                conn, addr = s.accept()
                logging.info(f"{addr} присоединился к серверу.")
                client_thread = threading.Thread(target=handle_client, args=(conn, addr))
                client_thread.start()
        finally:
            s.close()


if __name__ == "__main__":
    main()
