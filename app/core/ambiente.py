"""Identidade da edição e diretório exclusivo dos seus dados locais."""

import os
from pathlib import Path
import msvcrt

EDICAO_USO = os.environ.get('IDLEBOARD_EDICAO') == 'uso'
RAIZ = Path(__file__).resolve().parents[1]
PASTA_PERFIS = Path(os.environ.get('IDLEBOARD_DADOS') or
                    RAIZ / 'data' / 'desenvolvimento' / 'profiles').resolve()


def conferir_sessoes_anteriores():
    """Recusa usar dados ainda abertos por uma interface anterior à separação."""
    for padrao in ('*/*/.idleboard.lock', '*/*/vinculos/*/.idleboard.lock'):
        for caminho in PASTA_PERFIS.glob(padrao):
            with caminho.open('r+b') as trava:
                msvcrt.locking(trava.fileno(), msvcrt.LK_NBLCK, 1)


def adquirir_instancia():
    """Uma instância por pasta de dados; o SO libera a trava ao terminar."""
    PASTA_PERFIS.mkdir(parents=True, exist_ok=True)
    if EDICAO_USO:
        conferir_sessoes_anteriores()
    trava = (PASTA_PERFIS / '.idleboard-app.lock').open('a+b')
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
