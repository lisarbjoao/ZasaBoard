"""Preferências por cartão e controle de mídia HTML/Web Audio da sua página."""

import json

SCRIPT = r"""(() => {
const config = __CONFIG__;
if (window.__idleboardGameAudio) { window.__idleboardGameAudio.set(config); return; }
let atual = config;
const ganhos = new Map();
const medias = new Set();
const nivel = () => atual.silenciado ? 0 : atual.volume / 100;
function ajustar(m) {
  if (m.muted !== atual.silenciado) m.muted = atual.silenciado;
  if (m.volume !== atual.volume / 100) m.volume = atual.volume / 100;
}
function visitar(no) {
  if (no !== document && no.nodeType !== 1) return;
  const itens = [...no.querySelectorAll('audio,video')];
  if (no.matches?.('audio,video')) itens.push(no);
  for (const m of itens) {
    if (!medias.has(m)) { medias.add(m); m.addEventListener('volumechange', () => ajustar(m)); }
    ajustar(m);
  }
  for (const m of medias) if (!m.isConnected) medias.delete(m);
}
if (window.AudioNode) {
  const conectar = AudioNode.prototype.connect;
  const desconectar = AudioNode.prototype.disconnect;
  function destino(node, alvo) {
    const ctx = node.context;
    if (!ctx || alvo !== ctx.destination ||
        (window.OfflineAudioContext && ctx instanceof OfflineAudioContext)) return alvo;
    if (!ganhos.has(ctx)) {
      const ganho = ctx.createGain();
      ganho.gain.value = nivel();
      conectar.call(ganho, ctx.destination);
      ganhos.set(ctx, ganho);
      ctx.addEventListener('statechange', () => {
        if (ctx.state === 'closed') ganhos.delete(ctx);
      });
    }
    return ganhos.get(ctx);
  }
  AudioNode.prototype.connect = function(...args) {
    const alvo = args[0];
    args[0] = destino(this, alvo);
    const resultado = conectar.apply(this, args);
    return args[0] !== alvo ? alvo : resultado;
  };
  AudioNode.prototype.disconnect = function(...args) {
    if (args[0] === this.context.destination && ganhos.has(this.context))
      args[0] = ganhos.get(this.context);
    return desconectar.apply(this, args);
  };
}
const observador = new MutationObserver(registros => {
  for (const registro of registros) for (const no of registro.addedNodes) visitar(no);
});
observador.observe(document, {childList:true, subtree:true});
window.__idleboardGameAudio = { set(c) {
  atual = c;
  for (const [ctx, ganho] of ganhos) {
    if (ctx.state === 'closed') ganhos.delete(ctx);
    else ganho.gain.value = nivel();
  }
  for (const m of medias) if (m.isConnected) ajustar(m); else medias.delete(m);
}};
visitar(document);
})();"""


def validar(config):
    if config is None:
        return {'volume': 100, 'silenciado': False}
    if not isinstance(config, dict):
        raise ValueError('Preferência de som inválida.')
    volume, silenciado = config.get('volume', 100), config.get('silenciado', False)
    if type(volume) is not int or not 0 <= volume <= 100 or type(silenciado) is not bool:
        raise ValueError('Use volume de 0 a 100 e uma opção válida de silêncio.')
    return {'volume': volume, 'silenciado': silenciado}


def script(config):
    return SCRIPT.replace('__CONFIG__', json.dumps(validar(config)))


def script_inicial(config):
    return script(dict(validar(config), silenciado=True))


def aplicar(estado, config):
    config = validar(config)
    estado['_script_inicial'] = script_inicial(config)
    if estado.get('_audio_atualizado'):
        estado['_audio_atualizado'](config)
    web = estado.get('web')
    if web is not None and web.ready:
        def falhou(_erro):
            estado['status'] = 'Não foi possível aplicar o som nesta página'
            if estado.get('notificar'):
                estado['notificar'](estado['status'])
        web.eval_js(script(config), on_error=falhou)


def salvar(perfil, estado, config):
    config = validar(config)
    anterior = perfil.get('audio')
    perfil['audio'] = config
    if not perfil['_salvar']():
        if anterior is None:
            perfil.pop('audio', None)
        else:
            perfil['audio'] = anterior
        return False
    aplicar(estado, config)
    return True
