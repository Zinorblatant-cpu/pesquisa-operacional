# Consultoria Atos — Dimensionamento de Professores (Fundamental 1 e 2)

Relatório técnico com os dois resultados obtidos para o cliente Atos
(Ensino Fundamental, 1º ao 9º ano): (1) quantidade mínima de professores
para cobrir a grade semanal e (2) quantidade máxima de restrições de
horário (recusas) que cada professor pode ter sem inviabilizar a grade.

Ambos os modelos usam **programação linear (inteira)**, no espírito de
Kantorovich–Koopmans: minimizar o número de "atividades" (professores)
necessárias para cobrir uma demanda fixa de recursos (aulas), sujeita a
restrições de capacidade.

---

## 1. Quantidade mínima de professores

Script: `minimo_professores.py`.

### 1.1 Parâmetros

| Símbolo | Significado | Valor |
|---|---|---|
| $T$ | conjunto de turmas | $\lvert T \rvert = 9$ |
| $T_1$ | turmas do Fundamental 1 (1º–5º ano) | $\lvert T_1 \rvert = 5$ |
| $T_2$ | turmas do Fundamental 2 (6º–9º ano) | $\lvert T_2 \rvert = 4$ |
| $d_t$ | demanda semanal de aulas da turma $t$ | $d_t = 30$ aulas/semana, $\forall t \in T$ |
| $J$ | jornada semanal do professor (tempo integral) | $40$ h |
| $f$ | fração mínima de hora-atividade (fora de sala) | $1/3$ |
| $m$ | duração de uma aula | $45$ min |
| $C$ | capacidade máxima semanal de aulas em sala por professor | ver 1.2 |
| $N^{*}$, $N_1^{*}$, $N_2^{*}$ | **quantidade mínima de professores** — valor ótimo do problema de minimização (a menor quantidade capaz de cobrir toda a demanda semanal, não uma estimativa) | ver 1.3–1.5 |

> **Nota (escola particular):** a fração $f=1/3$ vem da Lei do Piso
> (Lei 11.738/2008, art. 2º §4º), que o STF confirmou (ADI 4167) valer
> apenas para a rede **pública** de ensino ("magistério público"). Como a
> Atos é uma escola **privada**, essa fração não é uma obrigação legal —
> está sendo adotada aqui como **referência/política interna**, por ser o
> parâmetro mais usado como benchmark do setor. Ver seção 3 para a
> pesquisa completa sobre o que de fato se aplica à rede privada (CLT +
> convenção coletiva) e as demais opções de carga horária.

### 1.2 Capacidade máxima por professor

$$
C = \left\lfloor \frac{J \cdot 60 \cdot (1 - f)}{m} \right\rfloor
  = \left\lfloor \frac{40 \cdot 60 \cdot \frac{2}{3}}{45} \right\rfloor
  = \left\lfloor 35{,}56 \right\rfloor = 35 \text{ aulas/semana}
$$

### 1.3 Fundamental 1 — modelo polivalente

Um único professor cobre a turma inteira (não há fragmentação entre
turmas). O modelo é factível pois $d_t \le C$ para toda $t \in T_1$
($30 \le 35$), e como cada turma exige um professor dedicado:

$$
N_1^{*} = \lvert T_1 \rvert = 5
$$

### 1.4 Fundamental 2 — cobertura mínima (programação linear inteira)

**Variáveis de decisão**

- $x_{p,t} \ge 0$, inteiro — aulas que o professor $p$ dá na turma $t \in T_2$
- $y_p \in \{0,1\}$ — indica se o professor $p$ é contratado

**Função objetivo**

$$
\min \sum_{p \in P} y_p
$$

**Restrições**

$$
\sum_{p \in P} x_{p,t} = d_t \qquad \forall\, t \in T_2 \quad \text{(cobrir a demanda de cada turma)}
$$

$$
\sum_{t \in T_2} x_{p,t} \le C \cdot y_p \qquad \forall\, p \in P \quad \text{(capacidade do professor, só se contratado)}
$$

**Limite inferior teórico** (divisão do recurso total pela capacidade
unitária):

$$
N_2^{*} \ge \left\lceil \frac{\sum_{t \in T_2} d_t}{C} \right\rceil
         = \left\lceil \frac{120}{35} \right\rceil = \left\lceil 3{,}43 \right\rceil = 4
$$

O solver (PuLP/CBC) atinge esse limite: $N_2^{*} = 4$.

### 1.5 Resultado final

$$
N^{*} = N_1^{*} + N_2^{*} = 5 + 4 = \mathbf{9 \text{ professores}}
$$

> **$N^{*}$ é a quantidade mínima possível de professores** — o valor
> ótimo do problema de minimização ($\min \sum_p y_p$ na seção 1.4),
> não uma estimativa ou aproximação. Contratar menos que $N^{*}$ torna
> o problema **matematicamente inviável**: não existe alocação de
> aulas que cubra as 9 turmas respeitando a capacidade $C$ de cada
> professor. Contratar mais que $N^{*}$ é sempre possível, só não é
> necessário.

> Esse é um modelo de **dimensionamento agregado** (quantos professores
> contratar, por carga horária semanal), não uma grade horária slot a
> slot. Como as 9 turmas têm aula em todos os 30 horários possíveis da
> semana, o mínimo por concorrência de horários também é 9 — os dois
> raciocínios coincidem.

---

## 2. Máximo de restrições (recusas) por professor/matéria

Fonte: `D:\MyProgramings\horotimo` (projeto `horotimo`, variante Atos —
`backend/cronomaneger_atos.py` e `backend/tests/test_disponibilidade_minima_atos.py`).
Resultado já validado por teste automatizado (roda o solver de verdade em
$N_{min}$ e $N_{min}-1$ para cada matéria).

### 2.1 Modelo de grade horária (variável Horótima)

$$
H_{a,b,c,d} \in \{0,1\}
$$

onde $a \in$ matérias, $b \in$ turmas (9), $c \in$ aulas (6/dia),
$d \in$ dias (5). $H_{a,b,c,d}=1$ se a matéria $a$ é ministrada na turma
$b$, na aula $c$, no dia $d$.

**Função objetivo**

$$
\max \sum_{a,b,c,d} H_{a,b,c,d}
$$

**Restrições relevantes**

$$
\text{R1: } \sum_{a} H_{a,b,c,d} \le 1 \qquad \forall\, b,c,d
$$

$$
\text{R2 (só Anos Finais): } \sum_{b \,\in\, \text{Finais}} H_{a,b,c,d} \le 1 \qquad \forall\, a,c,d
$$

$$
\text{R3: } \sum_{c} H_{a,b,c,d} \le \text{máx}_{a,b} \qquad \forall\, a,b,d
$$

$$
\text{R4: } \sum_{c,d} H_{a,b,c,d} \ge \text{mín}_{a,b} \qquad \forall\, a,b
$$

$$
\text{R5: } H_{a,b,c,d} = 0 \quad \text{se a matéria } a \text{ está indisponível no dia } d,\ \text{aula } c \qquad \forall\, b
$$

R2 vale só entre turmas dos Anos Finais porque nos Anos Iniciais cada
turma tem seu próprio regente (sem concorrência de horário entre turmas
para a mesma matéria).

### 2.2 Disponibilidade mínima ($N_{min}$)

Para cada matéria $a$, $N_{min}(a)$ é o menor número de horários (dentre
os 30 possíveis/semana: 6 aulas × 5 dias) que precisam estar disponíveis
para que R4 ainda seja satisfazível em todas as turmas que lecionam $a$:

$$
N_{min}(a) = \max\Big(\, \text{mín}_{a,\,\text{Iniciais}} \,,\; 4 \times \text{mín}_{a,\,\text{Finais}} \,\Big)
$$

O fator $4\times$ existe porque R2 permite no máximo 1 turma por horário
para a mesma matéria nos Anos Finais (4 turmas competindo pelos mesmos
horários); nos Anos Iniciais não há esse conflito, então o mínimo próprio
($\text{mín}_{a,\text{Iniciais}}$) nunca é o gargalo.

### 2.3 Máximo de recusas toleráveis

$$
R_{max}(a) = 30 - N_{min}(a)
$$

| Matéria | mín. Iniciais | mín. Finais | $N_{min}(a)$ | $R_{max}(a)$ — recusas toleráveis |
|---|---|---|---|---|
| Arte | 2 | 1 | 4 | **26** |
| Ed. Física | 3 | 2 | 8 | **22** |
| Geografia | 3 | 3 | 12 | **18** |
| História | 3 | 3 | 12 | **18** |
| Inglês | 0 | 4 | 16 | **14** |
| Ciências | 5 | 5 | 20 | **10** |
| Língua Portuguesa | 8 | 6 | 24 | **6** |
| Matemática | 6 | 6 | 24 | **6** |

Matemática e Português são as matérias com menor folga (no máximo 6
recusas de horário por semana), pois têm a maior carga mínima nos Anos
Finais, multiplicada por 4 devido à R2.

### 2.4 Ressalva

$N_{min}(a)$ assume **1 único especialista** cobrindo a matéria $a$
inteira nos Anos Finais. Um professor de Matemática ou Português dando
24 aulas/semana sozinho é uma carga pesada e perto do teto de contratos
reais de regência no Brasil (geralmente ~20h/semana). Na prática, a
escola provavelmente vai querer 2 professores dividindo essas matérias
nos Anos Finais — o que folgaria a tolerância a recusas de cada um
individualmente, ainda que o modelo atual (por matéria, não por
professor nomeado) não calcule esse desdobramento automaticamente.

---

## 3. Pesquisa: carga horária semanal × capacidade de aulas (rede privada)

A Atos é uma escola **particular**, então a base legal usada em 1.2 (Lei
do Piso, 1/3 de hora-atividade) não se aplica automaticamente — ela é
uma norma para o **magistério público** (STF, ADI 4167: "constitucional
a norma geral federal reservar fração mínima de 1/3 da carga horária
dos docentes da educação básica **pública**"). Redes privadas seguem:

- **CLT**, com teto de **44 horas semanais** (Lei nº 13.415/2017, que
  passou a permitir a um professor somar turnos no mesmo estabelecimento
  até esse limite).
- A **convenção coletiva de trabalho (CCT)** do SINPRO (sindicato dos
  professores) com o sindicato patronal (SINEPE/SIEEESP) de cada estado,
  que define como a hora-atividade é tratada — e isso **varia bastante**:
  - SINPRO-SP: hora-atividade aparece como um **acréscimo salarial de
    ~5%** sobre a hora-aula, não como um desconto na carga horária
    contratada (ou seja, não reduz o número de aulas que o professor
    pode dar).
  - Outros estados (ex.: SINPRO-RJ, SINPRO-PA): a CCT costuma reservar
    algo entre **20% e 33% da hora-aula** como hora-atividade paga,
    percentual mais próximo do 1/3 do setor público, mas não idêntico
    nem padronizado nacionalmente.
- Conclusão prática: **não existe um único percentual nacional
  obrigatório de hora-atividade para escola privada.** O valor certo
  depende da CCT vigente no estado da Atos (ou do que estiver definido
  em contrato/regimento interno, se a escola quiser adotar uma política
  própria mais generosa que o mínimo da CCT).

### 3.1 Capacidade de aulas por carga horária semanal (menor → maior)

Mesma fórmula da seção 1.2, aplicada a cada carga horária comum no
mercado, em dois cenários: **sem desconto** de hora-atividade (todo o
contrato em sala, teto físico) e **com 1/3** (cenário do setor público,
usado aqui só como limite conservador de referência/benchmark):

$$
C(J, f) = \left\lfloor \frac{J \cdot 60 \cdot (1-f)}{45} \right\rfloor
$$

**Quantidade mínima de professores por linha**, reaplicando o modelo da
seção 1 com a capacidade $C$ de cada carga horária:

$$
N_1^{*}(C) = \begin{cases} 5 & \text{se } C \ge 30 \text{ (polivalente viável)} \\ \text{inviável} & \text{se } C < 30 \end{cases}
\qquad\qquad
N_2^{*}(C) = \left\lceil \frac{120}{C} \right\rceil
$$

Quando $C < 30$, um único professor não fecha mais uma turma inteira do
Fundamental 1 (30 aulas) sozinho — o modelo polivalente da seção 1.3
deixa de valer. Nesses casos a coluna mostra, em vez de $N_1^{*}+N_2^{*}$,
o **mínimo flexível da escola inteira** $\lceil 270/C \rceil$ (marcado
com ‡).

**O que é o "modelo flexível"?** É o mesmo problema de cobertura mínima
da seção 1.4 (Fundamental 2), só que aplicado às 9 turmas juntas em vez
de só as 4 do Fundamental 2. A diferença para o modelo original (seção
1.3) é o que ele **deixa de exigir**:

- **Modelo original (polivalente):** 1 turma do Fundamental 1 só pode
  ser coberta por **exatamente 1 professor** — restrição rígida de "essa
  turma é responsabilidade de um único regente".
- **Modelo flexível:** essa exigência é **removida**. Qualquer turma
  (Fundamental 1 ou 2) pode ser coberta por vários professores, cada um
  dando parte das 30 aulas, desde que a soma feche a demanda — mesma
  lógica já usada para o Fundamental 2.

**Por que flexibilizar:** se $C < 30$ (ex.: $C=17$ com jornada de 20h),
fisicamente nenhum professor sozinho dá as 30 aulas semanais de uma
turma — o modelo rígido não tem solução. Flexibilizando a regra "1
professor = 1 turma", ainda é possível responder uma pergunta mais
fraca: juntando todos os professores desse porte, qual o mínimo para
cobrir as 270 aulas da escola inteira, não importa como elas se dividem
entre turmas?

**O preço da flexibilização:** o número que sai é um **piso otimista**,
não uma resposta operacionalmente pronta. Ele soma só a carga horária
semanal de cada professor — não verifica se os horários das turmas
batem entre si. Como turmas diferentes têm aula no mesmo slot da
semana, um professor não pode literalmente dividir seu tempo entre duas
delas ao mesmo tempo; montar a grade de fato pra atingir esse número
pode não ser sempre possível. O modelo 2 (seção 2, variável Horótima)
é quem de fato respeita os horários, slot a slot — o modelo flexível
aqui é só um limite inferior de dimensionamento agregado.

Em cada coluna $N^{*}$, o número mostrado é a **quantidade mínima de
professores** para aquele cenário de carga horária — o valor ótimo do
modelo, não uma média nem um chute.

| Carga horária semanal $J$ | $C$ sem desconto | $N^{*}$ sem desconto — mín. de professores | $C$ com 1/3 hora-atividade | $N^{*}$ com 1/3 — mín. de professores |
|---|---|---|---|---|
| 20h (parcial) | 26 aulas | 11 ‡ | 17 aulas | 16 ‡ |
| 25h — *= Jornada Completa, SEDUC-SP (LC 1.374/2022)*[^completa] | 33 aulas | **9** | 22 aulas | 13 ‡ |
| 30h (básica) | 40 aulas | **8** | 26 aulas | 11 ‡ |
| 40h (integral) — *= Jornada Ampliada, SEDUC-SP (LC 1.374/2022)*[^ampliada] | 53 aulas | **8** | 35 aulas | **9** |
| 44h (teto CLT) | 58 aulas | **8** | 39 aulas | **9** |

> **Números conferidos pelo solver.** Os 10 valores de $N^{*}$ acima não
> são só a conta $\lceil \cdot \rceil$ manual — foram recalculados
> rodando o PuLP/CBC de verdade para cada cenário
> (`conferir_todas_as_cargas_horarias()` em `minimo_professores.py`) e
> bateram exatamente com a tabela. Nessa conferência, o script pegou um
> bug real: a cobertura mínima limitava o número de professores
> candidatos ao número de turmas (9), insuficiente para cargas com
> capacidade baixa (ex.: 26 aulas/semana exige 11 professores, não 9) —
> o solver ficava inviável em silêncio e devolvia números errados (8
> para todas as linhas ‡). Corrigido calculando o limite superior como
> $\lceil \text{demanda}/C \rceil + 1$ e adicionando checagem de status
> ótimo do solver.

[^completa]: Jornada Completa = 25h/semana, sendo 16h40 (2/3) com alunos
    e 8h20 (1/3) pedagógico — a lei já embute o desconto de 1/3, então
    só a coluna "com 1/3" (22 aulas, $N^{*}=13$ ‡) é o cenário real
    dessa jornada; a coluna "sem desconto" é hipotética.
[^ampliada]: Jornada Ampliada = 40h/semana, sendo 26h40 (2/3) com alunos
    e 13h20 (1/3) pedagógico — mesmo raciocínio: o cenário real é a
    coluna "com 1/3" (35 aulas, $N^{*}=9$).

### 3.2 Leitura para o relatório

- **Faixa do mínimo de professores, conforme a jornada adotada: de 8
  (30h+ sem hora-atividade) a 16 (20h com 1/3 de hora-atividade).**
- O número usado na seção 1 (**9 professores**, jornada de 40h com 1/3)
  **coincide exatamente** com a jornada oficial mais longa da rede
  pública estadual de SP (Jornada Ampliada, LC 1.374/2022) — não é um
  valor arbitrário, é o mesmo parâmetro que o próprio Estado de SP usa
  para seus professores efetivos, usado aqui como benchmark.
- Abaixo de 30h semanais (com o desconto de 1/3), o modelo de 1
  professor-regente por turma do Fundamental 1 deixa de fechar sozinho:
  a Atos precisaria ou de jornadas mais longas para os regentes, ou de
  2 regentes dividindo a turma (o que é um problema de modelagem
  diferente, não coberto pelo script atual).
- Jornadas curtas (20h) — mesmo sendo as mais comuns em contratações
  parciais — praticamente dobram o quadro necessário (16 professores)
  em relação ao cenário de 40h usado no restante do relatório.

### Sources

- [STF — Lei que reserva 1/3 da carga horária do magistério para atividades extraclasse é constitucional](https://noticias.stf.jus.br/postsnoticias/lei-que-reserva-1-3-da-carga-horaria-do-magisterio-para-atividades-extraclasse-e-constitucional/)
- [Lei nº 11.738/2008 — Planalto](https://www.planalto.gov.br/ccivil_03/_ato2007-2010/2008/lei/l11738.htm)
- [Piso Salarial Profissional Nacional (PSPN) — MEC](https://planodecarreira.mec.gov.br/piso-salarial-profissional-nacional-pspn)
- [Carga horária do professor pela CLT: quantas aulas pode dar por dia?](https://carvalhoadvogado.aliamkt.com/index.php/2026/05/05/carga-horaria-do-professor-clt/)
- [Jornada de trabalho do professor — Pontotel](https://www.pontotel.com.br/jornada-de-trabalho-de-professor/)
- [Convenção Coletiva de Trabalho dos Professores — SINPRO-SP](https://www.sinprosp.org.br/pdf/144)
- [Tabela de Carga Horária de Professor: Guia Completo — CIDESP](https://cidesp.com.br/conteudo/tabela-de-carga-horaria-de-professor-guia-completo)
- [SEDUC-SP publica Decreto sobre as Jornadas de Trabalho dos Professores (Decreto 66.793/2022, LC 1.374/2022) — PEBSP](https://www.pebsp.com/seduc-sp-publica-decreto-sobre-as-jornadas-de-trabalho-dos-professores/)
- [SEDUC-SP publica Resolução 105/2024 que muda a Carga Horária e Amplia as aulas para 50 minutos — PEBSP](https://www.pebsp.com/seduc-sp-publica-resolucao-105-2024-que-muda-a-carga-horaria-e-amplia-as-aulas-para-50-minutos/)
- [Jornada Docente — G.O.E. SP](https://egoesp.com/jornada_docente.php)
