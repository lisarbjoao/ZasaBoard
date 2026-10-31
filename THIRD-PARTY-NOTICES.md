# Dependências distribuídas

O código do Idleboard e seu empacotamento são próprios. Os arquivos binários da distribuição incluem dependências de terceiros, com seus arquivos de licença preservados:

- Python 3.12: `runtime/LICENSE.txt` e avisos da biblioteca padrão.
- Tcl/Tk: arquivos de licença sob `runtime/tcl`.
- CustomTkinter 6.0.0: licença do pacote em `runtime/Lib/site-packages/customtkinter-6.0.0.dist-info/licenses/LICENSE`.
- darkdetect 0.8.0: metadados/licenças no respectivo diretório `.dist-info`.
- packaging 26.3: metadados/licenças no respectivo diretório `.dist-info`.
- tkwry 0.1.9: metadados/licenças no respectivo diretório `.dist-info`.

As versões e hashes de instalação estão em `requirements-runtime.lock`. O navegador usa Microsoft Edge WebView2 Runtime instalado no Windows; ele não é copiado de um perfil de usuário nem incorporado ao instalador. O iniciador e o instalador utilizam o .NET Framework do Windows.

Não são incluídos arquivos da extensão /hunt, código coletado do jogo, cookies ou bancos de navegador.
