"""Carga opt-in da extensão local; seus arquivos não fazem parte do projeto."""

from functools import lru_cache
import hashlib
import json
from pathlib import Path
from core.ambiente import PASTA_PERFIS


@lru_cache(maxsize=4)
def _carregar(pasta, alteracao_script, alteracao_manifesto):
    manifesto = json.loads((pasta / 'instalacao.json').read_text(encoding='utf-8'))
    conteudo = (pasta / 'inicializacao.js').read_bytes()
    if not isinstance(manifesto, dict) or hashlib.sha256(conteudo).hexdigest() != manifesto.get('sha256'):
        raise ValueError('A instalação local do /hunt foi alterada; reinstale a cópia local.')
    return conteudo.decode('utf-8')


def script_para(pasta_perfil, dados=PASTA_PERFIS):
    dados = Path(dados).resolve()
    perfil = Path(pasta_perfil).resolve()
    if not perfil.is_relative_to(dados):
        return None
    partes = perfil.relative_to(dados).parts
    if len(partes) != 2 or partes[0] != 'pokeidle':
        return None
    pasta = dados / '.extensoes' / 'hunt'
    if not (pasta / 'instalacao.json').exists():
        return None
    return _carregar(pasta, (pasta / 'inicializacao.js').stat().st_mtime_ns,
                     (pasta / 'instalacao.json').stat().st_mtime_ns)
