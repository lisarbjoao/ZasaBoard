"""Entrada pública da edição de uso; nenhuma personalização ou sessão incluída."""
import os
from pathlib import Path
import sys

raiz=Path(__file__).resolve().parent
os.environ['IDLEBOARD_EDICAO']='uso'
if 'IDLEBOARD_DADOS' not in os.environ:
    os.environ['IDLEBOARD_DADOS']=str(Path(os.environ['LOCALAPPDATA'])/'IdleboardBeta/profiles')
sys.path.insert(0,str(raiz/'app'))
import main

if '--smoke-test' in sys.argv:
    original=main.criar_janela
    def criar():
        janela=original()
        janela.attributes('-alpha',0)
        def fechar():
            comando=janela.protocol('WM_DELETE_WINDOW')
            if comando:janela.tk.call(comando)
            else:janela.destroy()
        janela.after(1200,fechar)
        return janela
    main.criar_janela=criar

main.main()
