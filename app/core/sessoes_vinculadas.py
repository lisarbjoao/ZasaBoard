"""Referências em memória às visualizações de uma conta; nada é serializado."""

from core import browserman


def ativa(vinculo):
    candidatas = [vinculo.get('_sessao'), *vinculo.get('_reprodutores', [])]
    return next((estado for estado in candidatas if estado and estado.get('_grupo')
                 and estado.get('sessao') is not None), None)


def registrar(vinculo, estado):
    estados = vinculo.setdefault('_reprodutores', [])
    if not any(item is estado for item in estados):
        estados.append(estado)


def remover(vinculo, estado):
    vinculo['_reprodutores'] = [item for item in vinculo.get('_reprodutores', []) if item is not estado]


def fechar_reprodutores(vinculo):
    for estado in list(vinculo.get('_reprodutores', [])):
        encerrar = estado.get('_fechar_card')
        if encerrar is not None:
            encerrar()
        else:
            browserman.fechar(estado, avisar=False)
            remover(vinculo, estado)
