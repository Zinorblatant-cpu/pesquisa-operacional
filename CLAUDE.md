# Pesquisa Operacional — Consultoria

Projeto pessoal para resolver problemas de **pesquisa operacional** que surgem em
consultorias, usando o método de **Leonid Kantorovich e Tjalling Koopmans**
(programação linear / análise de atividades — base teórica pela qual dividiram o
Prêmio Nobel de Economia de 1975).

## Objetivo

O único objetivo do código aqui é **obter a resposta numérica de problemas de
otimização** (alocação de recursos, transporte, mix de produção, etc.). Não é um
produto, não tem interface, não precisa de testes automatizados nem de
abstrações genéricas — cada problema é resolvido, a resposta é extraída, fim.

## Metodologia (Kantorovich–Koopmans)

Os problemas são modelados como **programação linear**:

- Definir variáveis de decisão (níveis de atividade / quantidades alocadas).
- Definir a função objetivo (minimizar custo ou maximizar lucro/eficiência).
- Definir restrições lineares (recursos limitados, demanda, capacidade).
- Resolver com um solver de PL e extrair: valor ótimo, variáveis de decisão e,
  quando fizer sentido, os preços-sombra (variáveis duais) — a leitura
  econômica de Kantorovich sobre o "valor" implícito dos recursos escassos.

## Stack

- **Python puro**, sem outras linguagens no projeto.
- Bibliotecas: `pulp` (modelagem de PL, principal), `scipy.optimize.linprog`
  (alternativa/checagem), `numpy` e `pandas` quando os dados justificarem.
- Scripts simples (`.py`), sem notebooks.

## Estrutura

Cada problema/cliente de consultoria vive em sua própria pasta na raiz do
projeto, nomeada de forma descritiva (ex.: `PoParaConsultaAtos`). Dentro da
pasta:

- Um script Python que modela e resolve o problema.
- Os dados de entrada (se vierem de planilha/CSV) ficam na mesma pasta.
- O script deve imprimir claramente a resposta: valor ótimo da função
  objetivo e os valores das variáveis de decisão.

Não criar uma camada de abstração/framework compartilhado entre pastas a
menos que isso seja pedido explicitamente — cada problema é resolvido de
forma direta e independente.

## Convenções de código

- Sem comentários explicando o óbvio; só quando uma restrição ou escolha de
  modelagem não for óbvia a partir do código.
- Sem tratamento de erros para cenários que não podem ocorrer (dados de
  entrada são controlados pelo próprio usuário).
- Nomes de variáveis podem refletir o vocabulário do problema real (em
  português, se for mais natural para o domínio da consultoria).
