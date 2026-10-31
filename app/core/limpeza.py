"""Apagamento local limitado à pasta validada de um único perfil."""

import os
from pathlib import Path
import shutil
from core.perfis import PASTA, validar_id


def apagar_dados_perfil(jogo_id, perfil_id, raiz=PASTA):
    base = Path(raiz).absolute()
    jogo = base / validar_id(jogo_id)
    destino = jogo / validar_id(perfil_id)
    # Validar o destino absoluto antes de qualquer operação recursiva.
    if base.resolve() != base or destino.resolve().parent != jogo.resolve():
        raise ValueError('A pasta do perfil contém um redirecionamento.')
    if not destino.resolve().is_relative_to(base.resolve()):
        raise ValueError('A pasta do perfil está fora do diretório permitido.')
    for pasta in (base, jogo, destino):
        if pasta.is_symlink() or pasta.is_junction():
            raise ValueError('Não é permitido apagar perfis que contenham atalhos ou junções.')
    if not destino.exists():
        return
    for pasta, diretorios, arquivos in os.walk(destino, followlinks=False):
        for nome in (*diretorios, *arquivos):
            entrada = Path(pasta) / nome
            if entrada.is_symlink() or entrada.is_junction():
                raise ValueError('Não é permitido apagar perfis que contenham atalhos ou junções.')
    shutil.rmtree(destino)
