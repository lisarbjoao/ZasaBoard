# Verificação da Beta 2

Exportação de fontes próprias por seleção explícita e hash, sem perfis de navegador, dados pessoais, diagnóstico do computador ou scripts externos. A tag pública identifica as fontes desta distribuição. A suíte privada de 86 testes passou incluindo desktop e WebView2; o repositório público executa testes de distribuição, protocolo e JavaScript selecionados. Ensaios locais não certificam desempenho prolongado em outros computadores.

O instalador incorpora um ZIP verificado por SHA-256. `Setup.exe --verify` verifica o payload; `--silent` instala para o usuário atual. O lançador aceita `--smoke-test` com dados sintéticos separados. O desinstalador mantém os dados de perfil. Arquivos não são assinados digitalmente.

Artefatos públicos não incluem o apontamento de dados da instalação pessoal, nem o script externo de /hunt. Os sites acessados mantêm suas próprias conexões. Relatos não devem conter cookies, senhas ou dados pessoais.
