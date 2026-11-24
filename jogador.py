
from configuracoes import *


class Peao:

    def __init__(self, jogador, numero):
        self.jogador = jogador
        self.numero = numero

        # -1 significa que esta na base
        self.posicao = -1
        self.finalizado = False


class Jogador:

    def __init__(self, numero, nome):

        self.numero = numero
        self.nome = nome
        self.cor = CORES[numero]
        self.pontos = PONTOS_INICIAIS

        self.peoes = [
            Peao(numero, i)
            for i in range(PEOES_POR_JOGADOR)
        ]

    def adicionar_pontos(self, valor):
        self.pontos += valor

    def peoes_finalizados(self):
        return sum(
            peao.finalizado
            for peao in self.peoes
        )
