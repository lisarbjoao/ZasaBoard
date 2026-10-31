"""Preferências do aplicativo, separadas entre edições e sem dados de login."""

import json
import os
from pathlib import Path
import tempfile
from core.ambiente import PASTA_PERFIS

CAMINHO = PASTA_PERFIS / 'preferencias.json'
PADRAO = {'layout_padrao': 'Confortável', 'visualizacao_padrao': 'encaixar',
          'maximizar_ao_abrir': False}


def validar(dados):
    if not isinstance(dados, dict):
        raise ValueError('Preferências inválidas.')
    resultado = {nome: dados.get(nome, valor) for nome, valor in PADRAO.items()}
    if resultado['layout_padrao'] not in ('Amplo', 'Confortável', 'Compacto'):
        raise ValueError('Modo da grade inválido.')
    if resultado['visualizacao_padrao'] not in ('encaixar', 'responsiva'):
        raise ValueError('Visualização inválida.')
    if type(resultado['maximizar_ao_abrir']) is not bool:
        raise ValueError('Preferência de janela inválida.')
    return resultado


def carregar(caminho=CAMINHO):
    caminho = Path(caminho)
    if not caminho.exists():
        return dict(PADRAO)
    try:
        return validar(json.loads(caminho.read_text(encoding='utf-8')))
    except json.JSONDecodeError as erro:
        raise ValueError('Não foi possível ler as preferências. O arquivo foi preservado.') from erro


def salvar(dados, caminho=CAMINHO):
    resultado = validar(dados)
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    temporario = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=caminho.parent,
                                         prefix='.preferencias-', suffix='.tmp', delete=False) as arquivo:
            temporario = Path(arquivo.name)
            json.dump(resultado, arquivo, ensure_ascii=False, indent=2)
            arquivo.flush()
            os.fsync(arquivo.fileno())
        os.replace(temporario, caminho)
    finally:
        if temporario is not None:
            temporario.unlink(missing_ok=True)
    return resultado
