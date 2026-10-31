# Diário de desenvolvimento da beta pública

## 2026-10-31 — Separação e distribuição

O usuário autorizou distribuir a edição de uso a um amigo e publicar sua beta. A inspeção do processo aberto confirmou o checkpoint `85f5036`, com personalização privada de /hunt. Foram exportados somente os vinte arquivos próprios declarados no manifesto, após conferir seus hashes. Não foi copiada a personalização, seus scripts externos, cadastros ou sessões.

Criados iniciador executável, instalador e desinstalador para Windows x64. O empacotamento usa seleção explícita do runtime e das quatro dependências, conservando licenças. O instalador valida o hash do ZIP incorporado e extrai em pasta intermediária; caminhos fora dela são recusados. Instala por usuário e conserva os dados ao desinstalar. O núcleo de interface não foi alterado para esta distribuição.

Este diário começa na separação pública. O histórico privado permanece no projeto original, sem ser importado para este repositório.

Validação de distribuição: três testes Python aprovados; instalador verificou o payload e instalou por usuário; o executável instalado abriu e encerrou a interface no modo de teste; a desinstalação removeu a aplicação e seu registro, preservando um marcador de dados sintético. Todos os executáveis retornaram saída 0. Não houve teste de contas reais do destinatário. Os resultados estão em `verificacao.md`.

Publicada a versão `v0.1.0-beta.1` no GitHub, baseada no commit `e8ba8cc`, com instalador, ZIP portátil e SHA256SUMS. O CI público passou na execução 41203912037. O instalador final tem 20.208.640 bytes, e o ZIP, 20.196.199 bytes. Foi conferida a preservação dos vinte hashes também nos arquivos do commit, além da ausência de perfis, certificados avulsos e caminhos privados no pacote selecionado. A instalação em segundo plano usada pelo botão gráfico também foi executada com sucesso em teste separado.
