import json


def enviar(conexao, mensagem):
    dados = json.dumps(mensagem, ensure_ascii=False) + '\n'
    conexao.sendall(dados.encode('utf-8'))


def receber(arquivo):
    linha = arquivo.readline()
    if not linha:
        return None
    return json.loads(linha)
