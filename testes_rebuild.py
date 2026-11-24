import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
import unittest
import pygame
from tabuleiro import Tabuleiro
from eventos import JogoEmpresarial, POSITIVOS, NEGATIVOS

class TestesRebuild(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.font.init()
    def setUp(self):
        self.t = Tabuleiro()
        self.j = JogoEmpresarial(self.t)
    def test_tabuleiro(self):
        self.assertEqual(len(self.t.casas),108)
        self.assertEqual(len(self.j.jogadores),6)
        self.assertTrue(all(len(j.peoes)==4 for j in self.j.jogadores))
    def test_percurso(self):
        for jogador in self.j.jogadores:
            p=jogador.peoes[0]
            casas=[]
            for pos in range(82):
                p.posicao=pos
                casa=self.j.obter_casa(p)
                self.assertIsNotNone(casa, (p.jogador,pos))
                casas.append(casa)
            self.assertEqual(len(set(casas)),82)
            self.assertEqual(self.t.casas[casas[0]]['tipo'],'saida')
            for casa in casas[-5:]:
                self.assertEqual(self.t.casas[casa]['tipo'],'reta_final')
                self.assertEqual(self.t.casas[casa]['setor'],p.jogador)
    def test_saida(self):
        p=self.j.jogadores[0].peoes[0]
        self.j.aguardando_movimento=True
        for dado in range(1,7):
            self.j.dado=dado
            self.assertEqual(self.j.pode_mover(p),dado==6)
    def test_eventos(self):
        p=self.j.jogadores[0].peoes[0]
        encontrados=set()
        for pos in range(82):
            p.posicao=pos
            tipo=self.t.casas[self.j.obter_casa(p)]['tipo']
            if tipo in ('bonus','prejuizo'):
                pontos=self.j.aplicar_evento(p)
                self.assertIn(pontos,[v for _,v in (POSITIVOS if tipo=='bonus' else NEGATIVOS)])
                self.assertEqual(self.j.evento['pontos'],pontos)
                encontrados.add(tipo)
        self.assertEqual(encontrados,{'bonus','prejuizo'})
    def test_classificacao(self):
        for i,j in enumerate(self.j.jogadores): j.pontos=100+i*10
        self.assertEqual([j.pontos for j in self.j.classificacao()], [150,140,130,120,110,100])
    def test_chegada(self):
        p=self.j.jogadores[0].peoes[0]
        p.posicao=81
        self.j.dado=1
        self.j.aguardando_movimento=True
        self.j.mover_peao(0)
        self.assertTrue(p.finalizado)
        self.assertEqual(self.j.jogadores[0].pontos,150)

if __name__=='__main__':
    unittest.main(verbosity=2)
