
import pygame
import math
from configuracoes import *
from animacoes import Animacoes

class Tabuleiro:

    def __init__(self):
        self.casas = []
        self.font = pygame.font.SysFont("Arial", 14, bold=True)
        self.tamanho = TAMANHO_CASA
        self.interno = self.tamanho * 1.5 * math.sqrt(3)
        self.externo = self.interno + self.tamanho * 6
        self.animacoes = Animacoes()
        self.posicoes_visuais = {}
        

        self.criar_casas()
        
    # Rotaciona um ponto ao redor do centro
    def rotacionar(self, x, y, angulo):
        rad = math.radians(angulo)

        novo_x = x * math.cos(rad) - y * math.sin(rad)
        novo_y = x * math.sin(rad) + y * math.cos(rad)

        return (
            round(CENTRO[0] + novo_x),
            round(CENTRO[1] + novo_y)
        )

    # Cria os dados de cada casa
    def criar_casas(self):

        for setor in range(6):
            for linha in range(6):
                for coluna in range(3):

                    x = (coluna - 1) * self.tamanho
                    y = (
                        -self.externo
                        + linha * self.tamanho
                        + self.tamanho / 2
                    )

                    tipo = "normal"
                    pontos = 0
                    cor = BRANCO

                    if coluna == 1 and linha > 0:
                        tipo = "reta_final"
                        cor = CORES[setor]

                    elif coluna == 2 and linha == 1:
                        tipo = "saida"
                        cor = CORES[setor]

                    elif coluna == 0 and linha == 2:
                        tipo = "segura"

                    elif coluna == 2 and linha == 3:
                        tipo = "bonus"
                        pontos = PONTOS_BONUS
                        cor = (190, 235, 205)

                    elif coluna == 0 and linha == 4:
                        tipo = "prejuizo"
                        pontos = PONTOS_PREJUIZO
                        cor = (245, 195, 195)

                    metade = self.tamanho / 2

                    vertices = [
                        (x - metade, y - metade),
                        (x + metade, y - metade),
                        (x + metade, y + metade),
                        (x - metade, y + metade)
                    ]

                    vertices = [
                        self.rotacionar(vx, vy, setor * 60)
                        for vx, vy in vertices
                    ]

                    casa = {
                        "id": len(self.casas),
                        "setor": setor,
                        "linha": linha,
                        "coluna": coluna,
                        "tipo": tipo,
                        "pontos": pontos,
                        "cor": cor,
                        "vertices": vertices,
                        "centro": self.rotacionar(
                            x, y, setor * 60
                        )
                    }

                    self.casas.append(casa)

    # Desenha os seis setores coloridos
    def desenhar_setores(self, tela):

        metade = self.tamanho * 1.5
        externo = self.externo

        for setor in range(6):

            angulo = setor * 60
            cor = CORES[setor]

            vertice_x = externo / math.sqrt(3)

            pontos = [
                self.rotacionar(
                    metade, -self.interno, angulo
                ),
                self.rotacionar(
                    metade, -externo, angulo
                ),
                self.rotacionar(
                    vertice_x, -externo, angulo
                ),
                self.rotacionar(
                    -metade, -externo, angulo + 60
                )
            ]

            pygame.draw.polygon(tela, cor, pontos)
            pygame.draw.polygon(tela, PRETO, pontos, 2)

    # Desenha as areas centrais de chegada
    def desenhar_centro(self, tela):

        metade = self.tamanho * 1.5

        for setor in range(6):

            pontos = [
                CENTRO,
                self.rotacionar(
                    -metade, -self.interno, setor * 60
                ),
                self.rotacionar(
                    metade, -self.interno, setor * 60
                )
            ]

            pygame.draw.polygon(
                tela, CORES[setor], pontos
            )

            pygame.draw.polygon(
                tela, PRETO, pontos, 2
            )

    # Desenha as casas do percurso
    def desenhar_casas(self, tela):

        for casa in self.casas:

            pygame.draw.polygon(
                tela,
                casa["cor"],
                casa["vertices"]
            )

            pygame.draw.polygon(
                tela,
                PRETO,
                casa["vertices"],
                1
            )

            simbolo = ""
            cor_texto = PRETO

            if casa["tipo"] == "bonus":
                simbolo = "+"
                cor_texto = (20, 140, 70)

            elif casa["tipo"] == "prejuizo":
                simbolo = "-"
                cor_texto = (190, 40, 40)

            elif casa["tipo"] == "segura":
                simbolo = "S"
                cor_texto = CINZA

            elif casa["tipo"] == "saida":
                simbolo = "V"

            if simbolo:
                texto = self.font.render(
                    simbolo, True, cor_texto
                )

                rect = texto.get_rect(
                    center=casa["centro"]
                )

                tela.blit(texto, rect)

    # Desenha as bases com quatro peoes
    
    def posicao_base(self, setor, numero):

        centro_base = self.rotacionar(
            0,
            -self.externo * 0.82,
            setor * 60 + 30
        )

        deslocamentos = [
            (-21, -21),
            (-21, 21),
            (21, -21),
            (21, 21)
        ]

        dx, dy = deslocamentos[numero]

        return (
            centro_base[0] + dx,
            centro_base[1] + dy
        )

    def desenhar_bases(self, tela):

        for setor in range(6):

            centro_base = self.rotacionar(
                0,
                -self.externo * 0.82,
                setor * 60 + 30
            )

            base = pygame.Rect(0, 0, 88, 88)
            base.center = centro_base

            pygame.draw.rect(
                tela, BRANCO, base, border_radius=8
            )

            pygame.draw.rect(
                tela, PRETO, base, 2, border_radius=8
            )

            for numero in range(4):

                posicao = self.posicao_base(
                    setor, numero
                )

                pygame.draw.circle(
                    tela, CINZA, posicao, 16, 1
                )

    
    def posicao_peao(self, jogo, peao):
        if peao.finalizado:
            return None

        if peao.posicao == -1:
            return self.posicao_base(peao.jogador, peao.numero)

        casa_id = jogo.obter_casa(peao)
        return self.casas[casa_id]["centro"]

    def desenhar_peoes(self, tela, jogo, dt):

        grupos = {}

        # Agrupa os peoes que ocupam a mesma casa
        for jogador in jogo.jogadores:

            for peao in jogador.peoes:

                posicao = self.posicao_peao(
                    jogo, peao
                )

                if posicao is None:
                    continue

                if posicao not in grupos:
                    grupos[posicao] = []

                grupos[posicao].append(
                    (jogador, peao)
                )

        self.posicoes_visuais.clear()

        # Desenha os grupos de peoes
        for posicao, grupo in grupos.items():

            quantidade = len(grupo)

            for indice, (jogador, peao) in enumerate(grupo):

                x, y = posicao

                if quantidade > 1:

                    angulo = (
                        2 * math.pi * indice
                        / quantidade
                    )

                    x += math.cos(angulo) * 9
                    y += math.sin(angulo) * 9

                destino = (x, y)

                identificador = (
                    jogador.numero,
                    peao.numero
                )

                posicao_animada = (
                    self.animacoes.atualizar(
                        identificador,
                        destino,
                        dt
                    )
                )

                posicao_animada = (
                    round(posicao_animada[0]),
                    round(posicao_animada[1])
                )

                self.posicoes_visuais[
                    identificador
                ] = posicao_animada

                raio = 13 if quantidade == 1 else 7

                selecionavel = (
                    jogador.numero == jogo.turno
                    and jogo.aguardando_movimento
                    and jogo.pode_mover(peao)
                    and not jogo.encerrado
                )

                # Destaque dos peoes disponiveis
                if selecionavel:

                    pygame.draw.circle(
                        tela,
                        BRANCO,
                        posicao_animada,
                        raio + 4,
                        2
                    )

                # Sombra
                pygame.draw.circle(
                    tela,
                    (20, 20, 20),
                    (
                        posicao_animada[0] + 2,
                        posicao_animada[1] + 3
                    ),
                    raio
                )

                # Corpo do peao
                pygame.draw.circle(
                    tela,
                    jogador.cor,
                    posicao_animada,
                    raio
                )

                # Contorno
                pygame.draw.circle(
                    tela,
                    PRETO,
                    posicao_animada,
                    raio,
                    2
                )

                # Reflexo
                pygame.draw.circle(
                    tela,
                    BRANCO,
                    (
                        posicao_animada[0] - 3,
                        posicao_animada[1] - 4
                    ),
                    2
                )

                # Numero do peao
                if quantidade == 1:

                    texto = self.font.render(
                        str(peao.numero + 1),
                        True,
                        PRETO
                    )

                    tela.blit(
                        texto,
                        texto.get_rect(
                            center=posicao_animada
                        )
                    )



    
    def detectar_peao(self, mouse, jogo):

        jogador = jogo.jogador_atual()

        candidatos = []

        for peao in jogador.peoes:

            if not jogo.pode_mover(peao):
                continue

            identificador = (
                jogador.numero,
                peao.numero
            )

            posicao = self.posicoes_visuais.get(
                identificador
            )

            if posicao is None:
                continue

            distancia = math.hypot(
                mouse[0] - posicao[0],
                mouse[1] - posicao[1]
            )

            if distancia <= 18:

                candidatos.append(
                    (distancia, peao.numero)
                )

        if candidatos:

            candidatos.sort()

            return candidatos[0][1]

        return None


    def desenhar(self, tela, jogo, dt):

        self.desenhar_setores(tela)
        self.desenhar_centro(tela)
        self.desenhar_casas(tela)
        self.desenhar_bases(tela)
        self.desenhar_peoes(tela, jogo, dt)
