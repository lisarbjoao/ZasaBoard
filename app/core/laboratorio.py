"""Iniciador opt-in do projeto próprio; nunca recebe sessão ou credenciais."""
import json
from pathlib import Path
import subprocess
import sys
from core.ambiente import PASTA_PERFIS

CONFIGURACAO=PASTA_PERFIS/'.laboratorio.json'
_processos={}


def carregar(caminho=CONFIGURACAO):
    caminho=Path(caminho)
    if not caminho.exists():
        return None
    dados=json.loads(caminho.read_text(encoding='utf-8'))
    if not isinstance(dados,dict) or set(dados)!={'projeto','snapshot'} or not all(isinstance(v,str) for v in dados.values()):
        raise ValueError('Configuração local do laboratório inválida.')
    if not all(Path(v).is_absolute() for v in dados.values()):
        raise ValueError('Use caminhos absolutos na configuração local do laboratório.')
    projeto,snapshot=(Path(dados[k]).resolve() for k in ('projeto','snapshot'))
    if not (projeto/'pokeidle_lab/__main__.py').is_file() or not (snapshot/'snapshot.json').is_file():
        raise ValueError('Projeto ou snapshot do laboratório não encontrado.')
    return {'projeto':projeto,'snapshot':snapshot}


def abrir(caminho=CONFIGURACAO):
    config=carregar(caminho)
    if config is None:
        raise ValueError('O laboratório ainda não está configurado nesta edição.')
    dados=Path(caminho).resolve().parent/'.laboratorio-dados'
    chave=(str(config['projeto']),str(config['snapshot']),str(dados))
    anterior=_processos.get(chave)
    if anterior is not None and anterior.poll() is None:
        return anterior
    processo=subprocess.Popen([sys.executable,'-m','pokeidle_lab','--snapshot',str(config['snapshot']),
                               '--dados',str(dados),'--interface'],
        cwd=config['projeto'],creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    _processos[chave]=processo
    return processo
