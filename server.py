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
        try:
            client.sendall(message)
        except ConnectionResetError:
            logging.error(f"Соединение с клиентом {client.getpeername()} было разорвано")
            break
        except Exception as e:
            logging.exception(f"Произошла ошибка при отправке сообщения клиенту {client.getpeername()}: {e}")
            break


def handle_client(conn, addr):
    """Функция обработки подключения нового участника чата"""
    logging.info(f"Новое подключение от {addr}")
    nickname = None

    while not nickname:
        try:
            conn.send("Enter nickname: ".encode())
            nickname = conn.recv(1024).decode()
            if nickname in nicknames:
                conn.send(" Этот никнейм занят, пожалуйста используйте другой: ".encode())
                nickname = None
            else:
                nicknames.add(nickname)
        except ConnectionResetError:
            logging.error(f"Соединение с {addr} прервано до ввода никнейма")
            conn.close()
            return

    clients.add(conn)
    broadcast(f"{nickname} присоединился к чату".encode())

    while True:
        try:
            message = conn.recv(1024).decode()
            if message == "exit":
                clients.remove(conn)
                conn.close()
                logging.info(f"{nickname} покинул чат.")
                nicknames.remove(nickname)
                broadcast(f"{nickname} покинул чат.".encode())
                break
            else:
                logging.info(f"{nickname}: {message}")
                broadcast(f"{nickname}: {message}".encode())
        except Exception as e:
            if conn in clients:
                clients.remove(conn)
                conn.close()
                logging.exception(f"Произошла ошибка: {e}")
                nicknames.remove(nickname)
                broadcast(f"{nickname} покинул чат.".encode())
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
        except KeyboardInterrupt:
            logging.exception("Сервер остановлен по требованию пользователя.")
            s.close()
        except Exception as e:
            logging.exception(f"Произошла ошибка: {e}")
            s.close()


if __name__ == "__main__":
    main()
