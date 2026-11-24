import socket
import threading
import pygame
from protocolo import enviar, receber
from tabuleiro import Tabuleiro
from eventos import JogoEmpresarial

PORTA = 5555
clientes = {}
lock = threading.RLock()
jogo = None
iniciada = False


def estado():
    return {'tipo': 'estado', 'evento': jogo.evento, 'total': len(clientes), 'iniciada': iniciada,
            'turno': jogo.turno, 'dado': jogo.dado,
            'aguardando_movimento': jogo.aguardando_movimento,
            'encerrado': jogo.encerrado, 'mensagem': jogo.mensagem,
            'jogadores': [{'pontos': j.pontos, 'peoes': [
                {'posicao': p.posicao, 'finalizado': p.finalizado} for p in j.peoes
            ]} for j in jogo.jogadores]}


def publicar():
    mensagem = estado()
    for conexao in list(clientes.values()):
        try:
            enviar(conexao, mensagem)
        except OSError:
            pass


def atender(conexao):
    global iniciada
    numero = None
    try:
        with lock:
            numero = next((i for i in range(6) if i not in clientes), None)
            if numero is None or iniciada:
                enviar(conexao, {'tipo': 'erro', 'mensagem': 'Sala cheia ou partida iniciada.'})
                return
            enviar(conexao, {'tipo': 'entrada', 'jogador': numero})
            clientes[numero] = conexao
            iniciada = len(clientes) == 6
            publicar()
        with conexao.makefile('r', encoding='utf-8') as arquivo:
            while True:
                msg = receber(arquivo)
                if msg is None:
                    break
                if not isinstance(msg, dict):
                    continue
                with lock:
                    if not iniciada or len(clientes) != 6 or jogo.encerrado or jogo.turno != numero:
                        continue
                    if msg.get('tipo') == 'rolar':
                        jogo.rolar_dado()
                    elif msg.get('tipo') == 'mover' and type(msg.get('peao')) is int:
                        jogo.mover_peao(msg['peao'])
                    else:
                        continue
                    publicar()
    except (OSError, ValueError):
        pass
    finally:
        with lock:
            if clientes.get(numero) is conexao:
                del clientes[numero]
                publicar()
        conexao.close()


def iniciar():
    global jogo
    pygame.font.init()
    jogo = JogoEmpresarial(Tabuleiro())
    with socket.socket() as servidor:
        servidor.bind(('0.0.0.0', PORTA))
        servidor.listen()
        print('REBUILD_PRONTO', flush=True)
        while True:
            conexao, _ = servidor.accept()
            threading.Thread(target=atender, args=(conexao,), daemon=True).start()

if __name__ == '__main__':
    iniciar()
