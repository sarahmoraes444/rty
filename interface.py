import pygame
from configuracoes import *

class Interface:
    def __init__(self, tela):
        self.tela=tela
        self.fontes={n:pygame.font.SysFont('Arial',n,bold=b) for n,b in [(13,False),(15,False),(18,True),(24,True),(34,True)]}
    def texto(self,s,x,y,n=15,cor=(230,237,245)):
        self.tela.blit(self.fontes[n].render(str(s),True,cor),(x,y))
    def caixa(self,r,cor=(25,36,50),borda=None):
        pygame.draw.rect(self.tela,cor,r,border_radius=10)
        if borda: pygame.draw.rect(self.tela,borda,r,1,border_radius=10)
    def fundo(self,modo,detalhe=''):
        self.tela.fill((15,23,34))
        self.texto('REBUILD',30,12,34)
        self.texto('RECONSTRUINDO EMPRESAS  /  '+modo,32,53,13,(145,165,185))
        self.texto(detalhe,390,22,15)
        pygame.draw.line(self.tela,(54,73,92),(30,78),(1070,78))
    def painel(self,jogo,botao,ativo,status,detalhe=''):
        self.caixa((710,90,360,610),borda=(54,73,92))
        self.texto('CENTRAL DE OPERACOES',730,105,18)
        self.texto(detalhe,730,133,13,(150,170,190))
        for i,j in enumerate(jogo.jogadores):
            y=158+i*47
            self.caixa((730,y,320,42),(34,47,63),j.cor if i==jogo.turno else None)
            pygame.draw.rect(self.tela,j.cor,(739,y+8,5,26),border_radius=2)
            self.texto(j.nome,753,y+3,15)
            self.texto(f'{j.peoes_finalizados()}/4 concluidos',753,y+22,13,(150,170,190))
            img=self.fontes[18].render(str(j.pontos)+' pts',True,(230,237,245)); self.tela.blit(img,img.get_rect(midright=(1040,y+21)))
        self.texto(status,730,445,15,jogo.jogadores[jogo.turno].cor)
        linha=''; y=470
        for palavra in jogo.mensagem.split():
            teste=(linha+' '+palavra).strip()
            if self.fontes[15].size(teste)[0]>315 and linha:
                self.texto(linha,730,y); y+=18; linha=palavra
            else: linha=teste
        self.texto(linha,730,y)
        self.texto('DADO',735,550,13,(150,170,190))
        r=pygame.Rect(735,575,70,70); self.caixa(r,(235,240,245))
        faces={1:[(0,0)],2:[(-1,-1),(1,1)],3:[(-1,-1),(0,0),(1,1)],4:[(-1,-1),(1,-1),(-1,1),(1,1)],5:[(-1,-1),(1,-1),(0,0),(-1,1),(1,1)],6:[(-1,-1),(1,-1),(-1,0),(1,0),(-1,1),(1,1)]}
        for x,y in faces.get(jogo.dado,[]): pygame.draw.circle(self.tela,(25,36,50),(r.centerx+x*18,r.centery+y*18),5)
        self.caixa(botao,(48,111,165) if ativo else (48,59,72))
        s='ESCOLHA O PEAO' if jogo.aguardando_movimento else 'JOGAR DADO'
        img=self.fontes[15].render(s,True,(230,237,245)); self.tela.blit(img,img.get_rect(center=botao.center))
        self.texto('ESC: menu  |  ESPACO: dado  |  1-4: peoes',730,675,13,(150,170,190))
    def carta(self,carta):
        cor=(75,205,145) if carta['pontos']>0 else (245,110,110)
        self.caixa((85,90,590,115),(23,34,47),cor)
        pygame.draw.rect(self.tela,cor,(85,100,5,95),border_radius=2)
        self.texto('EVENTO EMPRESARIAL / '+carta['empresa'],105,102,15,cor)
        self.texto(carta['nome'],105,132,24)
        self.texto(f"{carta['pontos']:+d} pontos",105,166,18,cor)
    def classificacao(self,jogo):
        self.caixa((100,170,540,365),(22,33,46),(95,125,150))
        self.texto('CLASSIFICACAO FINAL',125,190,24)
        ordem=sorted(jogo.jogadores,key=lambda j:(j.pontos,j.peoes_finalizados()),reverse=True)
        for i,j in enumerate(ordem):
            self.texto(f'{i+1}. {j.nome}',125,240+i*40,18,j.cor)
            self.texto(f'{j.pontos} pts',490,240+i*40,18)
        self.texto('ESC para retornar ao menu',125,500,15)
