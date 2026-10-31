# Verificação da distribuição 0.1.0-beta.1

Executado em 31/10/2026, com dados sintéticos e instalação beta separada da edição de uso ativa:

- Três testes Python: integridade dos vinte arquivos do checkpoint, seleção do runtime e ausência de perfis/extensões privadas nas fontes.
- Compilação x64 do iniciador, instalador e desinstalador com o compilador C# do Windows.
- `Setup.exe --verify`: hash do payload incorporado aprovado, saída 0.
- Instalação silenciosa: aplicativo, registro de desinstalação e atalhos criados; saída 0.
- Executável instalado com `--smoke-test`: interface aberta invisivelmente e encerrada pelo fluxo normal, saída 0.
- Desinstalação: pasta da aplicação e registro removidos, saída 0; marcador sintético de dados preservado.

O teste de abertura não reproduz quatro jogos reais nem valida o computador do destinatário. Login, serviços externos e estabilidade prolongada ficam para a avaliação beta. O checkpoint de uso e suas sessões não foram fechados ou modificados.

O ZIP inclui manifesto dos arquivos. Os dois downloads públicos têm SHA-256 publicado em `SHA256SUMS.txt`. Nenhum cadastro pessoal, cookie, banco de navegador ou código da extensão /hunt integra a distribuição pública.
