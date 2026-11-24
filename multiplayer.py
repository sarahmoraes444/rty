import pygame
from interface import Interface
from queue import Empty
from configuracoes import *
from tabuleiro import Tabuleiro
from regras import Jogo
from cliente import Cliente


def iniciar(ip=None, ip_anfitriao=None):
    if ip is None:
        ip = input('IP do servidor (Enter para teste local): ').strip() or '127.0.0.1'
    try:
        cliente = Cliente(ip)
    except OSError as erro:
        raise ConnectionError(f'Falha na conexao: {erro}') from erro
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption('REBUILD - Multiplayer LAN')
    ui = Interface(tela)
    relogio = pygame.time.Clock()
    fonte = pygame.font.SysFont('Arial', 18)
    titulo = pygame.font.SysFont('Arial', 30, bold=True)
    tabuleiro = Tabuleiro()
    jogo = Jogo(tabuleiro)
    numero = None
    total = 0
    iniciada = False
    conectado = True
    aviso = ''
    evento_atual = None
    ultimo_evento = 0
    mostrar_ate = 0
    botao = pygame.Rect(825, 590, 225, 55)
    rodando = True

    def texto(s, x, y, cor=BRANCO, f=fonte):
        tela.blit(f.render(str(s), True, cor), (x, y))

    try:
        while rodando:
            dt = relogio.tick(FPS) / 1000
            while True:
                try:
                    msg = cliente.fila.get_nowait()
                except Empty:
                    break
                tipo = msg['tipo']
                if tipo == 'entrada':
                    numero = msg['jogador']
                elif tipo == 'estado':
                    carta = msg.get('evento')
                    if carta and carta['id'] > ultimo_evento:
                        ultimo_evento = carta['id']
                        evento_atual = carta
                        mostrar_ate = pygame.time.get_ticks() + 4500
                    total = msg['total']
                    iniciada = msg['iniciada']
                    for campo in ('turno', 'dado', 'aguardando_movimento', 'encerrado', 'mensagem'):
                        setattr(jogo, campo, msg[campo])
                    for j, dados in zip(jogo.jogadores, msg['jogadores']):
                        j.pontos = dados['pontos']
                        for p, d in zip(j.peoes, dados['peoes']):
                            p.posicao = d['posicao']
                            p.finalizado = d['finalizado']
                elif tipo == 'erro':
                    aviso = msg['mensagem']
                elif tipo == 'desconectado':
                    conectado = False
                    aviso = aviso or 'Servidor desconectado.'
            minha_vez = conectado and iniciada and total == 6 and numero == jogo.turno and not jogo.encerrado
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT or (evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE):
                    rodando = False
                elif minha_vez and evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    if botao.collidepoint(evento.pos) and not jogo.aguardando_movimento:
                        cliente.enviar('rolar')
                    elif jogo.aguardando_movimento:
                        p = tabuleiro.detectar_peao(evento.pos, jogo)
                        if p is not None:
                            cliente.enviar('mover', peao=p)
                elif minha_vez and evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_SPACE and not jogo.aguardando_movimento:
                        cliente.enviar('rolar')
                    elif pygame.K_1 <= evento.key <= pygame.K_4 and jogo.aguardando_movimento:
                        cliente.enviar('mover', peao=evento.key-pygame.K_1)
            ui.fundo('MULTIPLAYER LAN', 'IP: '+ip_anfitriao if ip_anfitriao else '')
            tabuleiro.desenhar(tela,jogo,dt)
            status = aviso or ('Aguardando jogadores...' if not iniciada else 'Partida pausada' if total != 6 else 'Partida encerrada' if jogo.encerrado else 'Sua vez!' if minha_vez else 'Aguarde sua vez')
            ui.painel(jogo,botao,minha_vez and not jogo.aguardando_movimento,status[:42],f'Conectados: {total}/6 | Empresa: '+(jogo.jogadores[numero].nome.replace('Empresa ','') if numero is not None else '...'))
            if evento_atual and pygame.time.get_ticks()<mostrar_ate: ui.carta(evento_atual)
            if jogo.encerrado: ui.classificacao(jogo)
            pygame.display.flip()
    finally:
        cliente.fechar()
        pygame.quit()

if __name__ == '__main__':
    iniciar()
