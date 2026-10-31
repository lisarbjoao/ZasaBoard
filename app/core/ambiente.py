"""Identidade da edição e diretório exclusivo dos seus dados locais."""

import os
from pathlib import Path
import msvcrt

EDICAO_USO = os.environ.get('IDLEBOARD_EDICAO') == 'uso'
EDICAO_CANDIDATA = os.environ.get('IDLEBOARD_ABRIR_CANDIDATO') == '1'
RAIZ = Path(__file__).resolve().parents[1]
PASTA_PERFIS = Path(os.environ.get('IDLEBOARD_DADOS') or
                    RAIZ / 'data' / 'desenvolvimento' / 'profiles').resolve()


def conferir_sessoes_anteriores(pasta=None):
    """Recusa usar dados ainda abertos por uma interface anterior à separação."""
    for padrao in ('*/*/.idleboard.lock', '*/*/vinculos/*/.idleboard.lock'):
        for caminho in (pasta or PASTA_PERFIS).glob(padrao):
            with caminho.open('r+b') as trava:
                msvcrt.locking(trava.fileno(), msvcrt.LK_NBLCK, 1)


def adquirir_instancia(pasta=None, verificar_legadas=None):
    """Uma instância por pasta de dados; o SO libera a trava ao terminar."""
    pasta = pasta or PASTA_PERFIS
    pasta.mkdir(parents=True, exist_ok=True)
    verificar_legadas = EDICAO_USO if verificar_legadas is None else verificar_legadas
    if verificar_legadas:
        conferir_sessoes_anteriores(pasta)
    trava = (pasta / '.idleboard-app.lock').open('a+b')
    try:
        if trava.tell() == 0:
            trava.write(b'0')
            trava.flush()
        trava.seek(0)
        msvcrt.locking(trava.fileno(), msvcrt.LK_NBLCK, 1)
    except OSError:
        trava.close()
        raise
    return trava
