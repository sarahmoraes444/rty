import random
from regras import Jogo

POSITIVOS = [('Planejamento estrategico eficiente',20), ('Investimento em tecnologia',15), ('Reducao de custos operacionais',10), ('Conquista de novos clientes',20), ('Treinamento de funcionarios',10)]
NEGATIVOS = [('Falha no controle de estoque',-15), ('Crise financeira',-25), ('Erro de planejamento financeiro',-20)]

class JogoEmpresarial(Jogo):
    def __init__(self, tabuleiro):
        super().__init__(tabuleiro)
        self.evento = None
        self.evento_id = 0

    def aplicar_evento(self, peao):
        casa = self.obter_casa(peao)
        if casa is None:
            return 0
        tipo = self.tabuleiro.casas[casa]['tipo']
        if tipo not in ('bonus', 'prejuizo'):
            return 0
        nome, pontos = random.choice(POSITIVOS if tipo == 'bonus' else NEGATIVOS)
        self.evento_id += 1
        self.evento = {'id': self.evento_id, 'nome': nome, 'pontos': pontos, 'empresa': self.jogadores[peao.jogador].nome}
        return pontos
