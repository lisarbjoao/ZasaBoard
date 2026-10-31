"""Controle solicitado de áudio HTML5, sem ler dados da página ou do login."""

SCRIPT_AUDIO = r"""(() => {
  const host = location.hostname.toLowerCase();
  if (!['twitch.tv', 'www.twitch.tv', 'm.twitch.tv', 'player.twitch.tv',
         'kick.com', 'www.kick.com'].includes(host)) return;
  const anterior = window.__idleboardAudio;
  if (anterior) {
    anterior.observador.disconnect();
    anterior.eventos.abort();
  }
  const eventos = new AbortController();
  const vistos = new WeakSet();
  const silenciado = __SILENCIADO__;
  function ajustar(elemento) {
    if (elemento.muted !== silenciado) elemento.muted = silenciado;
    if (!vistos.has(elemento)) {
      vistos.add(elemento);
      elemento.addEventListener('volumechange', () => ajustar(elemento),
                               {signal: eventos.signal});
    }
  }
  function visitar(no) {
    if (no.nodeType !== Node.ELEMENT_NODE && no !== document) return;
    if (no.matches?.('video, audio')) ajustar(no);
    no.querySelectorAll('video, audio').forEach(ajustar);
  }
  const observador = new MutationObserver(registros => {
    for (const registro of registros) {
      for (const no of registro.addedNodes) visitar(no);
    }
  });
  observador.observe(document, {childList: true, subtree: true});
  window.__idleboardAudio = {observador, eventos};
  visitar(document);
})();
"""


def script_audio(silenciado):
    if not isinstance(silenciado, bool):
        raise ValueError('Preferência de áudio inválida.')
    return SCRIPT_AUDIO.replace('__SILENCIADO__', 'true' if silenciado else 'false')


def aplicar_audio(estado, silenciado, falhou=None):
    web = estado.get('web')
    if web is not None and web.ready:
        web.eval_js(script_audio(silenciado), on_error=falhou)
