"""Validação compartilhada dos endereços de jogos e plataformas."""

from urllib.parse import urlsplit


def normalizar_url(url):
    if not isinstance(url, str):
        raise ValueError('Cole uma URL HTTPS.')
    url = url.strip()
    if not url or len(url) > 2048 or any(c.isspace() for c in url):
        raise ValueError('Cole uma URL HTTPS válida.')
    if '://' not in url and ':' not in url:
        url = 'https://' + url
    try:
        destino = urlsplit(url)
        destino.port
    except ValueError as erro:
        raise ValueError('Cole uma URL HTTPS válida.') from erro
    if (destino.scheme != 'https' or not destino.hostname or destino.username is not None
            or destino.password is not None):
        raise ValueError('Use HTTPS e não inclua usuário ou senha na URL.')
    return url
