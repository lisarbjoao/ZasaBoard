"""Catálogo local de jogos; identificadores permanecem estáveis ao editar."""

import json
import os
from pathlib import Path
import re
import tempfile
from uuid import uuid4
from core.enderecos import normalizar_url
from core.ambiente import PASTA_PERFIS
from core.extensoes import listar as listar_extensoes

CATALOGO = PASTA_PERFIS / 'jogos.json'
PADRAO = {'pokeidle': {'nome': 'PokeIdle', 'url': 'https://pokeidle.io/app'}}


def validar(jogos):
    if not isinstance(jogos, dict) or not jogos:
        raise ValueError('Mantenha pelo menos um jogo cadastrado.')
    resultado, nomes = {}, set()
    for identificador, jogo in jogos.items():
        if not isinstance(identificador, str) or not re.fullmatch(r'[a-zA-Z0-9-]{1,64}', identificador):
            raise ValueError('Identificação de jogo inválida.')
        if not isinstance(jogo, dict) or not isinstance(jogo.get('nome'), str):
            raise ValueError('Nome de jogo inválido.')
        nome = jogo['nome'].strip()
        if not nome or len(nome) > 80 or nome.casefold() in nomes:
            raise ValueError('Use um nome único, com até 80 caracteres.')
        nomes.add(nome.casefold())
        resultado[identificador] = {'nome': nome, 'url': normalizar_url(jogo.get('url')),
                                     'extensoes': tuple(modulo.nome for modulo in listar_extensoes(identificador))}
    return resultado


def novo(nome, url):
    identificador = uuid4().hex
    return identificador, validar({identificador: {'nome': nome, 'url': url}})[identificador]


def carregar(caminho=CATALOGO):
    caminho = Path(caminho)
    if not caminho.exists():
        return validar(PADRAO)
    try:
        dados = json.loads(caminho.read_text(encoding='utf-8'))
        if dados['versao'] != 1:
            raise ValueError('Versão de catálogo desconhecida.')
        return validar(dados['jogos'])
    except (KeyError, TypeError, json.JSONDecodeError) as erro:
        raise ValueError('Não foi possível ler o catálogo de jogos; o arquivo foi preservado.') from erro


def salvar(jogos, caminho=CATALOGO):
    jogos = validar(jogos)
    dados = {'versao': 1, 'jogos': {identificador: {'nome': jogo['nome'], 'url': jogo['url']}
                                  for identificador, jogo in jogos.items()}}
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    temporario = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=caminho.parent,
                                         prefix='.jogos-', suffix='.tmp', delete=False) as arquivo:
            temporario = Path(arquivo.name)
            json.dump(dados, arquivo, ensure_ascii=False, indent=2)
            arquivo.flush()
            os.fsync(arquivo.fileno())
        os.replace(temporario, caminho)
    finally:
        if temporario is not None:
            temporario.unlink(missing_ok=True)
    return jogos
