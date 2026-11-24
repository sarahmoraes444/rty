import pygame
from interface import Interface
from configuracoes import *
from tabuleiro import Tabuleiro
from eventos import JogoEmpresarial


def iniciar():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption('REBUILD - Local')
    ui = Interface(tela)
    relogio = pygame.time.Clock()
    fonte = pygame.font.SysFont('Arial', 18)
    pequena = pygame.font.SysFont('Arial', 15)
    titulo = pygame.font.SysFont('Arial', 32, bold=True)
    tabuleiro = Tabuleiro()
    jogo = JogoEmpresarial(tabuleiro)
    botao = pygame.Rect(825, 590, 225, 55)
    ultimo_evento = 0
    mostrar_ate = 0
    faces = {1:[(0,0)],2:[(-18,-18),(18,18)],3:[(-18,-18),(0,0),(18,18)],4:[(-18,-18),(18,-18),(-18,18),(18,18)],5:[(-18,-18),(18,-18),(0,0),(-18,18),(18,18)],6:[(-18,-18),(18,-18),(-18,0),(18,0),(-18,18),(18,18)]}
    def texto(s,x,y,cor=BRANCO,f=fonte):
        tela.blit(f.render(str(s),True,cor),(x,y))
    def mensagem(s,x,y):
        linha = ''
        for palavra in s.split():
            teste = (linha+' '+palavra).strip()
            if pequena.size(teste)[0]>315 and linha:
                texto(linha,x,y,f=pequena); y+=18; linha=palavra
            else: linha=teste
        texto(linha,x,y,f=pequena)
    rodando = True
    while rodando:
        dt = relogio.tick(FPS)/1000
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                rodando = False
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if botao.collidepoint(e.pos): jogo.rolar_dado()
                elif jogo.aguardando_movimento:
                    p = tabuleiro.detectar_peao(e.pos,jogo)
                    if p is not None: jogo.mover_peao(p)
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE: jogo.rolar_dado()
                elif pygame.K_1 <= e.key <= pygame.K_4: jogo.mover_peao(e.key-pygame.K_1)
        if jogo.evento_id != ultimo_evento:
            ultimo_evento = jogo.evento_id
            mostrar_ate = pygame.time.get_ticks()+4500
        ui.fundo('LOCAL')
        tabuleiro.desenhar(tela,jogo,dt)
        ui.painel(jogo,botao,not jogo.aguardando_movimento and not jogo.encerrado,'Vez: '+jogo.jogador_atual().nome,'6 empresas / modo local')
        if jogo.evento and pygame.time.get_ticks()<mostrar_ate: ui.carta(jogo.evento)
        if jogo.encerrado: ui.classificacao(jogo)
        pygame.display.flip()
    pygame.quit()

if __name__=='__main__': iniciar()
