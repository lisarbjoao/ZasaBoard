# Edição de uso e edição de desenvolvimento

## Abrir

- `iniciar-uso.cmd`: edição congelada, com os dados de navegador atuais em `data/profiles`. O checkpoint antigo oferece Início e Perfis; novos checkpoints oferecem a navegação completa.
- `iniciar.cmd`: edição completa em desenvolvimento, com dados separados em `data/desenvolvimento/profiles`.
- `iniciar-candidata.cmd`: cópia congelada completa para conferência, usando os dados de desenvolvimento e o ambiente próprio. Desenvolvimento e candidata compartilham essa pasta e não devem ser abertos simultaneamente; a trava do aplicativo impede a segunda instância.

Ambas podem permanecer abertas simultaneamente. Nomes, exclusões e logins de uma edição não se propagam à outra. Nenhum cookie ou perfil foi copiado: a edição de uso assume o diretório original, e o desenvolvimento usa um diretório novo. Abrir `main.py` diretamente também usa o diretório de desenvolvimento por padrão.

Se a interface anterior ainda estiver aberta, encerrá-la uma única vez antes de iniciar a edição de uso. Travas de navegador bloqueiam a abertura sobre dados ainda em uso; uma trava do aplicativo impede duas instâncias com o mesmo diretório. Essas travas são liberadas pelo sistema operacional ao encerrar o processo. Não remover arquivos de trava para tentar forçar abertura.

## Código congelado

`tools/preparar_uso.py` exporta somente fontes Python versionadas do commit atual para `local/edicao-uso/<commit>`. Não copia arquivos de trabalho, cadastro, logs ou dados de navegador. O manifesto local registra o commit e os hashes dos arquivos. O iniciador usa esse caminho congelado; alterações posteriores na fonte de desenvolvimento não substituem essa cópia.

A preparação recusa substituir uma edição existente. `atualizar-uso.cmd` promove a candidata congelada atual à edição de uso, somente quando os dados de uso estão livres. `local/` e ambos os diretórios de dados estão excluídos do Git.

## Atualização preservando os perfis

`tools/atualizar_uso.py` verifica os hashes das fontes da candidata antes da cópia. Adquire a mesma trava do aplicativo e confere sessões legadas; se a edição de uso estiver aberta, recusa a atualização sem encerrá-la. A cópia é preparada em uma pasta temporária e publicada somente quando completa. O ponteiro anterior fica em `local/edicao-uso/anterior.json`; a troca de `atual.json` é atômica. Se essa troca falhar, a edição anterior continua selecionada e a atualização pode ser repetida.

Somente fontes permitidas e o manifesto são copiados. O cadastro, cookies e cache continuam na pasta de uso existente; os dados da candidata não são importados. A atualização não abre jogos nem reinicia processos. O checkpoint anterior de código é conservado, mas isso não é um backup dos dados de navegador nem uma promessa de reversão de futuras migrações.

A promoção não é executada durante o desenvolvimento enquanto houver sessões de uso abertas. O encerramento para atualização ocorre na entrega final, depois de concluir a implementação. A conferência manual do usuário fica para essa entrega; os testes automatizados continuam a cada incremento.

`tools/preparar_uso.py --candidato` exporta uma cópia completa em `local/edicao-candidata/<commit>`, sem trocar o ponteiro da edição de uso. O pacote de código-fonte em dist também não inclui dados pessoais ou o ambiente Python.

O ponto de partida é o código atual, com navegação restrita às duas áreas pedidas. Ele preserva o formato atual do cadastro, inclusive informações de lives, sem expor as áreas experimentais. Não se afirma que todas as mudanças acumuladas foram testadas: testes funcionais e revisão visual continuam pendentes conforme solicitado.

Edição local preparada em 2026-10-29 a partir de `85f5036`. Abertura confirmada pelo título da janela `Idleboard · Uso` e processo respondendo, sem interação com contas ou execução da suíte de testes.

## Ambiente Python

O iniciador de uso prefere `local/runtime-uso`, ambiente próprio preparado com as versões e hashes de requirements-runtime.lock. Se ele não existir, mantém compatibilidade com `.venv`. O desenvolvimento usa `.venv`. Bibliotecas Tcl/Tk também ficam no ambiente de uso. A troca do iniciador afeta somente a próxima abertura: nenhum processo já aberto é reiniciado.

O ambiente próprio passou pela suíte desktop e nativa. Ele ainda depende da instalação base do Python 3.12; isto não é um executável portátil independente. Instalações novas podem recriá-lo com `python -m venv local/runtime-uso` e `local/runtime-uso/Scripts/python.exe -m pip install --require-hashes -r requirements-runtime.lock`, usando uma instalação de Python com Tk funcional.

## Conferência posterior

Verificar as duas edições simultâneas com perfis sintéticos; criação, renomeação e exclusão devem ficar restritas ao diretório correto. Confirmar bloqueio de segunda instância, bloqueio de sessões legadas, reabertura persistente, limpeza opcional na raiz correta e ausência de alterações na edição congelada ao editar o desenvolvimento. Rever fixtures para isolar também a trava do aplicativo e `core.ambiente.PASTA_PERFIS`.
