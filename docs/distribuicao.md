# Decisão: distribuição beta independente

O pedido é testar a edição de uso aprovada enquanto o projeto completo continua evoluindo. Foi escolhido um repositório público independente, sem publicar o histórico ou os dados privados.

O pacote conserva as fontes do checkpoint aprovado, verificadas por SHA-256. Um iniciador .NET aciona o runtime Python incluído; o usuário não precisa preparar um ambiente de desenvolvimento. O instalador também usa .NET Framework, disponível nas versões de Windows suportadas, e instala sem elevação em `%LOCALAPPDATA%\Programs\IdleboardBeta\0.1.0-beta.1`.

Metadados e sessões ficam separados da instalação, em `%LOCALAPPDATA%\IdleboardBeta\profiles`. O ZIP portátil usa a mesma pasta privada por usuário; não deve abrir simultaneamente com a edição instalada. A trava da aplicação impede duas instâncias sobre esses dados.

O instalador recusa sobrescrever uma instalação da mesma versão. Para reinstalar, feche e desinstale primeiro; dados são preservados. O desinstalador fica fora da pasta removida, verifica a trava da beta e remove somente o destino de instalação conhecido, os atalhos e seu registro no Windows. Seu pequeno executável permanece na pasta privada para não tentar apagar o próprio processo.

O instalador não é assinado digitalmente. Não se solicita desabilitar o antivírus ou proteções do Windows. Publicar hashes ajuda a verificar integridade, mas não equivale a assinatura ou certificação de segurança.
