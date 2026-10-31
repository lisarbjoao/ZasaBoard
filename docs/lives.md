# Lives por perfil

## Login, reprodução e bônus são estados diferentes

O cadastro de uma conta no Idleboard apenas conserva a sessão do navegador. Não substitui o vínculo OAuth feito dentro do jogo. O ✓ da janela de conta associada salva a confirmação e **fecha aquela página**: um vídeo ou chat aberto ali para de executar, embora o login permaneça salvo.

No cartão de live, **Conta** abre a janela da mesma conta vinculada usada pelo Multitwitch. **Chats** abre os chats reais dos canais em páginas próprias da Twitch, na mesma WebSession e pasta, evitando depender apenas do login no iframe de outra origem. Nenhum cookie é copiado entre vínculos. Cadastrar Twitch e Multitwitch como duas contas diferentes cria perfis distintos; o agrupamento correto é adicionar canais à mesma conta Twitch na aba Lives.

Minimizar a janela de chats mantém suas páginas existentes; fechá-la encerra os chats. Parar/remover o cartão encerra também os chats do conjunto. Trocar os canais fecha o conjunto antigo, que pode ser reaberto em Chats. O botão não envia mensagens automaticamente, não simula presença, não inicia vídeo sem ação do usuário e não comprova benefícios.

Na conferência pública desta etapa, o cliente do PokeIdle continuava declarado como 1.389.1. `livesTwitchQueFaltam` e o contexto de `linhaTwitch` usam a conta vinculada, detecção no chat, `assistindoEm` e canais com `bonus === true`. Isso sustenta verificar o vínculo dentro do jogo, o login nos chats reais e a elegibilidade do canal; não comprova que uma conta específica foi detectada pelo servidor. GETs públicos selecionados, hashes e contexto estão na execução externa `2026-10-31_pokeidle_12`, sem login ou dados de conta.

A aba Lives pertence ao jogo selecionado. Escolha um perfil, uma conta vinculada da Twitch ou Kick e cole a URL do canal. + Live salva o endereço. Canais Twitch da mesma conta são reunidos em uma única página Multitwitch; Kick mantém páginas individuais. A reprodução deve ser iniciada pelo usuário na própria página; não há garantia de bônus.

Cada cartão oferece abrir, parar, recarregar, foco e remover endereço. Parar preserva o login. Remover uma live preserva a conta vinculada. Remover o vínculo remove também seus endereços de lives e fecha suas janelas, preservando os dados locais do navegador. Excluir o perfil mantém a confirmação existente para apagar esses dados.

As páginas de uma mesma conta vinculada compartilham uma WebSession explícita. Um contador de referências mantém essa sessão e a trava do diretório até a última janela fechar. Contas diferentes continuam usando diretórios separados. A janela de login também pode reutilizar essa sessão; seu check permanece uma confirmação manual.

Endereços ficam em `lives` no cadastro privado do perfil, com id e referência ao vínculo. Cadastros antigos sem o campo recebem uma lista vazia. Objetos de navegador e referências em memória não são serializados. Ao reabrir o aplicativo, as lives salvas aguardam abertura manual.

A navegação entre abas conserva os componentes. Comportamento de mídia em segundo plano, áudio, autenticação real e elegibilidade de bônus dependem das plataformas e ainda precisam de conferência. A Twitch usa a página pública Multitwitch, com integração dos controles oficiais descrita abaixo; a Kick usa páginas completas.

## Multitwitch

Um cartão por perfil/conta vinculada Twitch, inclusive com somente um canal. Endereço gerado como `https://multitwitch.tv/canal1/canal2`, conforme [orientação do serviço](https://multitwitch.tv/). Os canais individuais permanecem no cadastro privado; o agrupamento é uma projeção em memória e preserva ids, dados e preferências anteriores. Contas vinculadas diferentes não são reunidas.

Adicionar canal atualiza a URL do mesmo navegador. Canais abre a lista para remoção individual; lixeira pede confirmação para remover o conjunto inteiro. Remover o último canal fecha o cartão. Repetições do mesmo canal na conta são recusadas em novas adições e deduplicadas na URL para registros anteriores. Alterar o conjunto recarrega os players.

Multitwitch é um serviço externo que recebe os nomes dos canais da URL. Reutilizar o diretório da conta não comprova que o login funcionará nos players incorporados: cookies de terceiros, autenticação, áudio e benefícios do jogo seguem pendentes de teste. Uma página conjunta não garante menor consumo de decodificação dos vídeos.

Atualização da candidata: há testes de agrupamento, validação e ciclo de vida, além de teste nativo de isolamento e compartilhamento de perfis persistentes. Reprodução e autenticação nos serviços reais ainda precisam de conferência. Ver `verificacao-pendente.md`.

## Controle de áudio

Nas páginas individuais da Kick, o ícone de som no rodapé alterna a preferência de cada live e salva `silenciado` no cadastro privado. Lives novas e registros sem essa preferência recebem `true`. O botão representa a preferência solicitada, não uma medição do áudio real. Falha ao salvar mantém o valor anterior. No Multitwitch o botão controla o conjunto por conta vinculada, cuja preferência fica em `vinculos[].multitwitch`. Preferências individuais antigas da Twitch são preservadas, mas não aplicadas ao conjunto.

O controle atua em elementos HTML5 `video` e `audio` do documento acessível, com observação de elementos adicionados pelo player, sem varredura periódica. É instalado na abertura e reaplicado ao terminar a navegação; alternar substitui a observação anterior. O script usa somente um booleano validado, não lê cookies, não envia informações e não aciona reprodução. A atuação é restrita aos domínios Twitch/Kick previstos no código.

Players em iframes de outra origem ou com mecanismos próprios podem não responder ao controle HTML5 da Kick. Silenciar não garante menor CPU, rede ou resolução. Conferência real permanece pendente.

## Qualidade e verificação do serviço

O [código publicado pelo Multitwitch](https://github.com/bhamrick/multitwitch/blob/master/multitwitch/static/js/multitwitch.js) constrói iframes não interativos. A candidata agora carrega o SDK oficial `https://player.twitch.tv/js/embed/v1.js` e substitui somente os iframes Twitch de canais válidos por players interativos. Conserva a classe usada pelo layout do site; não modifica chats, cookies ou autenticação. Se o SDK não carregar, conserva os iframes originais. Falha de construção conserva o iframe correspondente. A integração depende da estrutura externa do Multitwitch e pode precisar de manutenção quando ela mudar.

Os modos são Menor vídeo e Automática. Menor vídeo seleciona a menor resolução de vídeo identificável na lista retornada por `getQualities`; não solicita qualidade inventada nem modo somente áudio. Automática usa `auto` quando disponível. Se a lista ainda não estiver disponível, a seleção é reaplicada nos eventos READY e PLAYING. A [documentação oficial](https://dev.twitch.tv/docs/embed/video-and-clips/) exige mínimo de 400 × 300 pixels por player: o conteúdo das lives usa visualização responsiva e pode exigir rolagem ou foco. A grade aprovada dos jogos permanece igual.

Os novos players recebem `autoplay: false`; o usuário inicia a reprodução. O status indica instalação dos controles, não que a live está rodando ou concedendo bônus. Há até três consultas posteriores ao carregamento, sem polling contínuo. Qualidade e silêncio do conjunto são persistidos por conta vinculada, com reversão se a gravação falhar. Os testes executam o script real com DOM/SDK sintéticos, incluindo seleção da menor qualidade, reexecução sem duplicar players, falha do SDK, guarda de domínio e remoção de canais. Não substituem validação autenticada no serviço real.

Os testes desktop adicionais cobrem adição e remoção com persistência temporária, atualização do conjunto conservando o cartão, separação do mesmo canal em duas contas, rejeição de repetição na mesma conta, cancelamento e reversão quando a gravação falha. Os navegadores são substituídos nesses fluxos; isso não comprova reprodução ou benefícios reais.


## Beta 2 revisão 4 — conta compartilhada e duração ligada ao jogo

URLs Multitwitch adicionadas às contas vinculadas usam a pasta/WebSession da única conta Twitch do mesmo perfil. Nenhum cookie é copiado ou apagado. Sem conta Twitch, ou com várias possíveis, a abertura é recusada com instrução explícita em vez de escolher um login arbitrariamente. O vínculo Multitwitch antigo permanece no cadastro; seus dados anteriores são preservados, mas não selecionados para o novo fluxo.

Abrir o jogo abre também o Multitwitch cadastrado nesse perfil e os chats reais dos canais da URL, compartilhando a conta Twitch. Os chats podem pedir login na primeira utilização. Fechar a janela auxiliar do Multitwitch a oculta enquanto o jogo existe; fechar os chats os minimiza. Ocultar um cartão não chama o encerramento e conserva as páginas. Encerrar o navegador do jogo encerra as janelas Multitwitch e chats daquele perfil. Não existe início forçado de reprodução: inicie os players na plataforma. Persistência das páginas não comprova conexão IRC, autenticação ou bônus do servidor. A aba Lives continua disponível para controle manual dos conjuntos salvos nela; o acoplamento automático desta revisão se aplica às URLs Multitwitch das contas vinculadas, relatadas pelo usuário.
