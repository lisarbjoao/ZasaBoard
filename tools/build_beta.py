"""Gera distribuição pública por seleção explícita, sem copiar cadastros ou sessões."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import zipfile

RAIZ=Path(__file__).resolve().parents[1]
VERSAO='0.1.0-beta.1'
PACOTES=('customtkinter','darkdetect','packaging','tkwry')


def permitido(caminho):
    partes=Path(caminho).parts
    if not partes or any(p in ('__pycache__','site-packages','test','tests') or p.endswith('.WebView2')
                         or p.lower().startswith('codex-') for p in partes):return False
    if Path(caminho).suffix.lower() in ('.pem','.key','.pfx','.p12'):return False
    if len(partes)==1:
        return partes[0] in ('python.exe','pythonw.exe','python3.dll','python312.dll','vcruntime140.dll','vcruntime140_1.dll','LICENSE.txt')
    return partes[0] in ('DLLs','Lib')


def copiar(origem,destino):
    destino.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(origem,destino)


def compilar(csc,fonte,saida,*extras):
    subprocess.run([str(csc),'/nologo','/target:winexe','/platform:x64','/optimize+',
                    '/r:System.Windows.Forms.dll','/r:System.Drawing.dll','/r:System.IO.Compression.dll',
                    '/r:System.IO.Compression.FileSystem.dll','/out:'+str(saida),*extras,str(fonte)],check=True)


def construir(python,dependencias,tcl,saida,csc):
    saida=Path(saida).resolve()
    if saida.exists():raise ValueError('A saída já existe; use uma pasta nova.')
    python,dependencias,tcl,csc=map(lambda p:Path(p).resolve(),(python,dependencias,tcl,csc))
    if not (python/'python312.dll').is_file():raise ValueError('Use o runtime Windows Python 3.12 x64 validado.')
    pacote=saida/'IdleboardBeta'
    pacote.mkdir(parents=True)
    base=json.loads((RAIZ/'BASE.json').read_text(encoding='utf-8'))
    for nome,sha in base['fontes_sha256'].items():
        arquivo=RAIZ/'app'/nome
        if hashlib.sha256(arquivo.read_bytes()).hexdigest()!=sha:raise ValueError('Fonte do checkpoint modificada: '+nome)
        copiar(arquivo,pacote/'app'/nome)
    for arquivo in python.iterdir():
        if arquivo.is_file() and permitido(arquivo.name):copiar(arquivo,pacote/'runtime'/arquivo.name)
    for nome in ('DLLs','Lib'):
        for pasta,dirs,arquivos in os.walk(python/nome):
            dirs[:]=[d for d in dirs if d not in ('__pycache__','site-packages','test','tests') and not d.endswith('.WebView2')]
            for nome_arquivo in arquivos:
                arquivo=Path(pasta)/nome_arquivo
                rel=arquivo.relative_to(python)
                if permitido(rel):copiar(arquivo,pacote/'runtime'/rel)
    for nome in PACOTES:
        if not (dependencias/nome).is_dir():raise ValueError('Dependência ausente: '+nome)
        for arquivo in dependencias.iterdir():
            if arquivo.is_dir() and (arquivo.name==nome or arquivo.name.startswith(nome+'-') and arquivo.name.endswith('.dist-info')):
                shutil.copytree(arquivo,pacote/'runtime/Lib/site-packages'/arquivo.name,
                                ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    shutil.copytree(tcl,pacote/'runtime/tcl',ignore=shutil.ignore_patterns('__pycache__'))
    for nome in ('README.md','THIRD-PARTY-NOTICES.md','BASE.json'):
        copiar(RAIZ/nome,pacote/nome)
    copiar(RAIZ/'packaging/bootstrap.py',pacote/'bootstrap.py')
    compilar(csc,RAIZ/'packaging/Launcher.cs',pacote/'IdleboardBeta.exe')
    compilar(csc,RAIZ/'packaging/Uninstall.cs',pacote/'UninstallBeta.exe')
    hashes={p.relative_to(pacote).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in pacote.rglob('*') if p.is_file()}
    (pacote/'manifesto.json').write_text(json.dumps({'versao':VERSAO,'checkpoint':base['checkpoint'],
        'dados_pessoais_incluidos':False,'arquivos_sha256':hashes},ensure_ascii=False,indent=2),encoding='utf-8')
    portatil=saida/('IdleboardBeta-'+VERSAO+'-Windows-x64.zip')
    with zipfile.ZipFile(portatil,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as z:
        for nome in list(hashes)+['manifesto.json']:z.write(pacote/nome,nome)
    sha=hashlib.sha256(portatil.read_bytes()).hexdigest()
    fonte=(RAIZ/'packaging/Setup.cs').read_text(encoding='utf-8').replace('__PAYLOAD_SHA__',sha)
    gerado=saida/'Setup.generated.cs';gerado.write_text(fonte,encoding='utf-8-sig')
    instalador=saida/('IdleboardBeta-'+VERSAO+'-Setup.exe')
    compilar(csc,gerado,instalador,'/resource:'+str(portatil)+',IdleboardPayload.zip')
    checksums=saida/'SHA256SUMS.txt'
    checksums.write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in (instalador,portatil)),encoding='ascii')
    print(json.dumps({'instalador':str(instalador),'portatil':str(portatil),'arquivos':len(hashes)+1,'checksums':str(checksums)},ensure_ascii=False))


if __name__=='__main__':
    p=argparse.ArgumentParser()
    for argumento in ('python','dependencias','tcl','saida','csc'):p.add_argument('--'+argumento,required=True)
    a=p.parse_args();construir(a.python,a.dependencias,a.tcl,a.saida,a.csc)
