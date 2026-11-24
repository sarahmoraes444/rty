import socket
import threading
from queue import Queue
from protocolo import enviar, receber

class Cliente:
    def __init__(self, ip):
        self.conexao = socket.create_connection((ip, 5555), timeout=5)
        self.conexao.settimeout(None)
        self.fila = Queue()
        threading.Thread(target=self.ler, daemon=True).start()

    def ler(self):
        try:
            with self.conexao.makefile('r', encoding='utf-8') as arquivo:
                while True:
                    msg = receber(arquivo)
                    if msg is None:
                        break
                    self.fila.put(msg)
        except (OSError, ValueError):
            pass
        finally:
            self.fila.put({'tipo': 'desconectado'})

    def enviar(self, tipo, **dados):
        try:
            enviar(self.conexao, {'tipo': tipo, **dados})
        except OSError:
            self.fila.put({'tipo': 'desconectado'})

    def fechar(self):
        try:
            self.conexao.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        self.conexao.close()
