import threading
import socket
import logging

HOST = "127.0.0.1"
PORT = 12345
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
print("Для выхода из чата используйте команду exit")


def receive_messages():
    """Функция получения сообщений от клиента на сервера."""
    while True:
        try:
            data = s.recv(1024)
            if not data:
                break
            message = data.decode()
            print(message)
        except ConnectionAbortedError as e:
            print("Сервер прервал соединение")
            logging.error(f"{e},Сервер прервал соединение")
            s.close()
            break
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            logging.exception(e)
            s.close()
            break


def send_messages():
    """Функция отправки сообщений от клиента на сервер."""
    while True:
        try:
            message = input()
            s.send(message.encode())
            if message == "exit":
                print("Вы вышли из чата")
                s.shutdown(socket.SHUT_RDWR)
                s.close()
                break
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            logging.exception(e)
            break


receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()

send_thread = threading.Thread(target=send_messages)
send_thread.start()
