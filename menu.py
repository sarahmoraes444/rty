import os
import sys
import socket
import subprocess
import time
import threading
from queue import Queue, Empty
import pygame
from configuracoes import *
from multiplayer import iniciar
from main import iniciar as iniciar_local
from servidor import iniciar as iniciar_rede
import traceback

COMPILADO = getattr(sys, 'frozen', False)
PASTA = os.path.dirname(os.path.abspath(sys.executable if COMPILADO else __file__))

def iniciar_servidor():
    flags = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
    processo = subprocess.Popen(([sys.executable, '--servidor'] if COMPILADO else [sys.executable, '-u', os.path.join(PASTA, 'menu.py'), '--servidor']), cwd=PASTA, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors='replace', creationflags=flags)
    fila = Queue()
    def ler():
        for linha in processo.stdout:
            fila.put(linha.strip())
        fila.put(None)
    threading.Thread(target=ler, daemon=True).start()
    limite = time.monotonic() + 45
    linhas = []
    try:
        while time.monotonic() < limite:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT or (evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE):
                    raise InterruptedError('Inicializacao cancelada.')
            try:
                linha = fila.get(timeout=0.2)
            except Empty:
                continue
            if linha == 'REBUILD_PRONTO':
                return processo
            if linha is None:
                break
            linhas.append(linha)
        if any('10048' in l or 'Address already in use' in l for l in linhas):
            raise OSError('Porta 5555 ocupada. Feche o servidor anterior.')
        raise OSError(linhas[-1] if linhas else 'Servidor nao respondeu em 45 segundos.')
    except BaseException:
        encerrar_servidor(processo)
        raise

def encerrar_servidor(processo):
    if processo is not None and processo.poll() is None:
        processo.terminate()
        try:
            processo.wait(timeout=3)
        except subprocess.TimeoutExpired:
            processo.kill()
            processo.wait()

def ip_local():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('192.0.2.1', 80))
            return s.getsockname()[0]
    except OSError:
        return 'Consulte ipconfig'

def menu():
    modo = 'menu'
    ip = ''
    aviso = ''
    while True:
        pygame.init()
        tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption('REBUILD - Menu principal')
        fonte = pygame.font.SysFont('Arial', 23)
        titulo = pygame.font.SysFont('Arial', 65, bold=True)
        relogio = pygame.time.Clock()
        cx = LARGURA // 2
        botoes = [pygame.Rect(cx-170, 280+i*65, 340, 50) for i in range(4)]
        campo = pygame.Rect(cx-170, 280, 340, 50)
        acao = None
        while acao is None:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit(); return
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        if modo == 'menu': pygame.quit(); return
                        modo = 'menu'; aviso = ''
                    elif modo == 'entrar':
                        if e.key == pygame.K_RETURN and ip.strip(): acao = 'entrar'
                        elif e.key == pygame.K_BACKSPACE: ip = ip[:-1]
                        elif e.unicode.isprintable() and len(ip) < 80: ip += e.unicode
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    if modo == 'menu':
                        for i,b in enumerate(botoes):
                            if b.collidepoint(e.pos):
                                if i == 1: modo = 'entrar'; aviso = ''
                                else: acao = ['criar','entrar','local','sair'][i]
                                break
                    elif botoes[1].collidepoint(e.pos) and ip.strip(): acao = 'entrar'
                    elif botoes[2].collidepoint(e.pos): modo = 'menu'; aviso = ''
            tela.fill(FUNDO)
            def texto(s,y,f=fonte,cor=BRANCO):
                img = f.render(s,True,cor); tela.blit(img,img.get_rect(center=(cx,y)))
            def botao(b,s):
                pygame.draw.rect(tela,(55,115,175) if b.collidepoint(pygame.mouse.get_pos()) else (37,51,69),b,border_radius=8)
                texto(s,b.centery)
            for i,cor in enumerate(CORES): pygame.draw.circle(tela,cor,(cx-75+i*30,90),10)
            texto('REBUILD',155,titulo)
            texto('RECONSTRUINDO EMPRESAS',215)
            if modo == 'menu':
                for b,s in zip(botoes,['CRIAR PARTIDA','ENTRAR EM PARTIDA','JOGAR LOCALMENTE','SAIR']): botao(b,s)
            else:
                texto('Digite o IPv4 do anfitriao',255)
                pygame.draw.rect(tela,(37,51,69),campo,border_radius=8)
                texto(ip or '192.168.x.x',campo.centery)
                botao(botoes[1],'CONECTAR'); botao(botoes[2],'VOLTAR')
            texto(aviso,590,cor=(245,150,120))
            texto('Versao 0.9 | LAN - 6 jogadores',ALTURA-30,cor=CINZA)
            pygame.display.flip(); relogio.tick(FPS)
        if acao == 'sair': pygame.quit(); return
        tela.fill(FUNDO)
        texto('Iniciando... ESC para cancelar o servidor', ALTURA//2)
        pygame.display.flip()
        servidor = None
        try:
            if acao == 'local': iniciar_local()
            elif acao == 'entrar': iniciar(ip.strip())
            elif acao == 'criar':
                servidor = iniciar_servidor()
                iniciar('127.0.0.1', ip_local())
            aviso = ''
        except Exception as erro:
            traceback.print_exc()
            aviso = str(erro)[:85]
        finally:
            encerrar_servidor(servidor)
        modo = 'menu'

if __name__ == '__main__':
    if '--servidor' in sys.argv:
        iniciar_rede()
    else:
        menu()
