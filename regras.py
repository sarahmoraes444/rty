
import random

from jogador import Jogador
from configuracoes import *


class Jogo:

    def __init__(self, tabuleiro):

        self.tabuleiro = tabuleiro

        nomes = [
            "Empresa Vermelha",
            "Empresa Azul",
            "Empresa Amarela",
            "Empresa Roxa",
            "Empresa Verde",
            "Empresa Laranja"
        ]

        self.jogadores = [
            Jogador(i, nome)
            for i, nome in enumerate(nomes)
        ]

        self.turno = 0
        self.dado = 0
        self.aguardando_movimento = False
        self.mensagem = "Role o dado!"
        self.encerrado = False
        self.vencedor = None

        self.percurso = self.criar_percurso()

    # Cria o percurso compartilhado
    def criar_percurso(self):

        percurso = []

        for setor in range(JOGADORES):

            # Coluna direita: de fora para dentro
            for linha in range(6):

                percurso.append(
                    setor * 18 + linha * 3 + 2
                )

            proximo = (setor + 1) % JOGADORES

            # Coluna esquerda: de dentro para fora
            for linha in range(5, -1, -1):

                percurso.append(
                    proximo * 18 + linha * 3
                )

            # Casa central externa
            percurso.append(proximo * 18 + 1)

        return percurso

    def jogador_atual(self):

        return self.jogadores[self.turno]

    # Quantidade de passos ate a chegada
    def limite_percurso(self):

        return len(self.percurso) + 4

    # Sorteia o dado
    def rolar_dado(self):

        if self.encerrado:
            return

        if self.aguardando_movimento:
            return

        self.dado = random.randint(
            DADO_MINIMO, DADO_MAXIMO
        )

        self.aguardando_movimento = True

        self.mensagem = f"Dado: {self.dado}"

        movimentos = any(
            self.pode_mover(peao)
            for peao in self.jogador_atual().peoes
        )

        if not movimentos:

            self.proximo_turno()

            self.mensagem = (
                "Sem movimentos. Proximo jogador."
            )

    # Verifica se o movimento e permitido
    def pode_mover(self, peao):

        if self.encerrado:
            return False

        if not self.aguardando_movimento:
            return False

        if peao.jogador != self.turno:
            return False

        if peao.finalizado:
            return False

        if peao.posicao == -1:

            return self.dado == DADO_SAIDA

        return (
            peao.posicao + self.dado
            <= self.limite_percurso()
        )

    # Converte a posicao do peao em uma casa
    def obter_casa(self, peao):

        if peao.posicao == -1:
            return None

        if peao.finalizado:
            return None

        inicio = self.percurso.index(
            peao.jogador * 18 + 5
        )

        entrada_final = len(self.percurso) - 2

        if peao.posicao < entrada_final:

            indice = (
                inicio + peao.posicao
            ) % len(self.percurso)

            return self.percurso[indice]

        linha = peao.posicao - entrada_final

        return peao.jogador * 18 + linha * 3 + 1

    # Verifica se uma casa protege os peoes
    def casa_segura(self, casa_id):

        casa = self.tabuleiro.casas[casa_id]

        return casa["tipo"] in (
            "segura",
            "saida",
            "reta_final"
        )

    # Captura os adversarios na mesma casa
    def verificar_captura(self, peao):

        casa_id = self.obter_casa(peao)

        if casa_id is None:
            return 0

        if self.casa_segura(casa_id):
            return 0

        capturas = 0

        for adversario in self.jogadores:

            if adversario.numero == peao.jogador:
                continue

            for inimigo in adversario.peoes:

                if inimigo.posicao == -1:
                    continue

                if inimigo.finalizado:
                    continue

                casa_inimigo = self.obter_casa(
                    inimigo
                )

                if casa_inimigo == casa_id:

                    inimigo.posicao = -1

                    adversario.adicionar_pontos(
                        PONTOS_CAPTURADO
                    )

                    capturas += 1

        return capturas

    # Aplica os pontos das casas especiais
    def aplicar_evento(self, peao):

        casa_id = self.obter_casa(peao)

        if casa_id is None:
            return 0

        casa = self.tabuleiro.casas[casa_id]

        if casa["tipo"] == "bonus":
            return PONTOS_BONUS

        if casa["tipo"] == "prejuizo":
            return PONTOS_PREJUIZO

        return 0

    # Movimenta o peao escolhido
    def mover_peao(self, numero):

        if not self.aguardando_movimento:
            return

        if self.encerrado:
            return

        if not 0 <= numero < PEOES_POR_JOGADOR:
            return

        jogador = self.jogador_atual()

        peao = jogador.peoes[numero]

        if not self.pode_mover(peao):

            self.mensagem = "Movimento invalido."
            return

        # Retira o peao da base
        if peao.posicao == -1:

            peao.posicao = 0

        else:

            peao.posicao += self.dado

        # Verifica a chegada
        if peao.posicao == self.limite_percurso():

            peao.finalizado = True

            jogador.adicionar_pontos(
                PONTOS_CHEGADA
            )

            self.mensagem = (
                f"Chegada! +{PONTOS_CHEGADA} pts"
            )

        else:

            # Verifica capturas
            capturas = self.verificar_captura(peao)

            pontos_captura = (
                capturas * PONTOS_CAPTURA
            )

            # Verifica eventos
            pontos_evento = self.aplicar_evento(
                peao
            )

            jogador.adicionar_pontos(
                pontos_captura + pontos_evento
            )

            mensagens = []

            if capturas:

                mensagens.append(
                    f"Captura! +{pontos_captura} pts"
                )

            if pontos_evento:

                mensagens.append(
                    f"Evento: {pontos_evento:+d} pts"
                )

            if mensagens:

                self.mensagem = " | ".join(
                    mensagens
                )

            else:

                self.mensagem = "Peao movimentado."

        # Verifica o fim da partida
        if jogador.peoes_finalizados() == 4:

            self.encerrar_partida()
            return

        # Jogada adicional ao tirar seis
        if self.dado == DADO_SAIDA:

            self.aguardando_movimento = False

        else:

            self.proximo_turno()

    # Alterna os jogadores
    def proximo_turno(self):

        self.turno = (
            self.turno + 1
        ) % JOGADORES

        self.aguardando_movimento = False

    # Classifica as empresas
    def classificacao(self):

        return sorted(
            self.jogadores,
            key=lambda jogador: (
                jogador.pontos,
                jogador.peoes_finalizados()
            ),
            reverse=True
        )

    # Encerra a partida
    def encerrar_partida(self):

        self.encerrado = True

        self.aguardando_movimento = False

        self.vencedor = self.classificacao()[0]

        self.mensagem = (
            f"Vencedor: {self.vencedor.nome}"
        )
