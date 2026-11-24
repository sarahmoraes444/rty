
import math


class Animacoes:

    def __init__(self):

        self.posicoes = {}
        self.velocidade = 240

    def atualizar(self, identificador, destino, dt):

        if identificador not in self.posicoes:

            self.posicoes[identificador] = destino
            return destino

        x, y = self.posicoes[identificador]

        dx = destino[0] - x
        dy = destino[1] - y

        distancia = math.hypot(dx, dy)

        movimento = self.velocidade * dt

        if distancia <= movimento:

            self.posicoes[identificador] = destino

        else:

            x += dx / distancia * movimento
            y += dy / distancia * movimento

            self.posicoes[identificador] = (x, y)

        return self.posicoes[identificador]

    def em_movimento(self, identificador, destino):

        posicao = self.posicoes.get(
            identificador, destino
        )

        return math.dist(posicao, destino) > 1
