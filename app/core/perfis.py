"""Cadastro local: somente metadados; nunca serializa sessões ou credenciais."""

import json
import os
from pathlib import Path
import re
import tempfile
from uuid import uuid4
from urllib.parse import urlsplit
from core.enderecos import normalizar_url
from core import lives as cadastro_lives
from core import audio, multitwitch
from core.ambiente import PASTA_PERFIS

PASTA = PASTA_PERFIS
CATALOGO = PASTA / 'catalogo.json'


def nome_valido(nome):
    if not isinstance(nome, str) or len(nome.strip()) > 80:
        raise ValueError('Use um nome com até 80 caracteres.')
    return nome.strip()


def novo(nome=''):
    return {'id': uuid4().hex, 'personagem': nome_valido(nome), 'visivel': True, 'vinculos': [], 'lives': []}


def validar_id(identificador):
    if not isinstance(identificador, str) or not re.fullmatch(r'[a-zA-Z0-9-]{1,64}', identificador):
        raise ValueError('Identificação inválida.')
    return identificador


def validar_vinculo(vinculo):
    if vinculo.get('servico') not in ('twitch', 'kick', 'web'):
        raise ValueError('Serviço de conta vinculada desconhecido.')
    confirmado = vinculo.get('confirmado', False)
    if not isinstance(confirmado, bool):
        raise ValueError('Confirmação de conta inválida.')
    resultado = {'id': validar_id(vinculo.get('id')), 'servico': vinculo['servico'],
                 'nome': nome_valido(vinculo.get('nome')), 'confirmado': confirmado}
    if 'url' in vinculo:
        resultado['url'] = normalizar_url(vinculo['url'])
    elif vinculo['servico'] == 'web':
        raise ValueError('Informe a URL da plataforma.')
    if 'multitwitch' in vinculo:
        resultado['multitwitch'] = multitwitch.validar(vinculo['multitwitch'])
    return resultado


def novo_vinculo_url(url):
    url = normalizar_url(url)
    host = urlsplit(url).hostname.lower().removeprefix('www.')
    servico = 'twitch' if host == 'twitch.tv' else 'kick' if host == 'kick.com' else 'web'
    return validar_vinculo({'id': uuid4().hex, 'servico': servico, 'nome': host[:80],
                            'url': url, 'confirmado': False})


def novo_vinculo(servico, nome=''):
    return validar_vinculo({'id': uuid4().hex, 'servico': servico, 'nome': nome})


def pasta_vinculo(jogo, perfil, vinculo):
    return PASTA / validar_id(jogo) / validar_id(perfil['id']) / 'vinculos' / validar_id(vinculo['id'])


def validar(perfil):
    identificador = validar_id(perfil.get('id'))
    if not isinstance(perfil.get('visivel'), bool):
        raise ValueError('Visibilidade de perfil inválida.')
    vinculos = perfil.get('vinculos', [])
    if not isinstance(vinculos, list):
        raise ValueError('Lista de contas vinculadas inválida.')
    vinculos = [validar_vinculo(vinculo) for vinculo in vinculos]
    if len({v['id'] for v in vinculos}) != len(vinculos):
        raise ValueError('Contas vinculadas duplicadas.')
    lives = perfil.get('lives', [])
    if not isinstance(lives, list):
        raise ValueError('Lista de lives inválida.')
    lives = [cadastro_lives.validar(live, vinculos) for live in lives]
    if len({live['id'] for live in lives}) != len(lives):
        raise ValueError('Lives duplicadas no cadastro.')
    visualizacao = perfil.get('visualizacao', 'encaixar')
    if visualizacao not in ('encaixar', 'responsiva'):
        raise ValueError('Modo de visualização inválido.')
    return {'id': identificador, 'personagem': nome_valido(perfil.get('personagem')),
            'visivel': perfil['visivel'], 'vinculos': vinculos, 'lives': lives,
            'visualizacao': visualizacao, 'audio': audio.validar(perfil.get('audio'))}


def carregar(caminho=CATALOGO, jogos=('pokeidle',)):
    caminho = Path(caminho)
    if not caminho.exists():
        resultado = {jogo: [novo() for _ in range(4)] for jogo in jogos}
        if 'pokeidle' in resultado:
            resultado['pokeidle'][0]['id'] = 'prova-01'
        return resultado
    try:
        dados = json.loads(caminho.read_text(encoding='utf-8'))
        if dados['versao'] != 1 or not isinstance(dados['jogos'], dict):
            raise ValueError('Formato do cadastro desconhecido.')
        # Preservar cadastros de jogos fora da configuração atual.
        resultado = {}
        for jogo, registros in dados['jogos'].items():
            if not re.fullmatch(r'[a-zA-Z0-9-]{1,64}', jogo) or not isinstance(registros, list):
                raise ValueError('Cadastro de jogo inválido.')
            resultado[jogo] = [validar(registro) for registro in registros]
            if len({p['id'] for p in resultado[jogo]}) != len(registros):
                raise ValueError('Perfis duplicados no cadastro.')
        for jogo in jogos:
            resultado.setdefault(jogo, [])
        return resultado
    except (KeyError, TypeError, AttributeError, json.JSONDecodeError) as erro:
        raise ValueError('Não foi possível ler o cadastro de perfis; o arquivo foi preservado.') from erro


def salvar(jogos, caminho=CATALOGO):
    caminho = Path(caminho)
    dados = {'versao': 1, 'jogos': {jogo: [validar(p) for p in registros]
                                  for jogo, registros in jogos.items()}}
    caminho.parent.mkdir(parents=True, exist_ok=True)
    temporario = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=caminho.parent,
                                         prefix='.catalogo-', suffix='.tmp', delete=False) as arquivo:
            temporario = Path(arquivo.name)
            json.dump(dados, arquivo, ensure_ascii=False, indent=2)
            arquivo.flush()
            os.fsync(arquivo.fileno())
        os.replace(temporario, caminho)
    finally:
        if temporario is not None:
            temporario.unlink(missing_ok=True)
