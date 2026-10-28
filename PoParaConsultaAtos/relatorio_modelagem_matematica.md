# Relatório de Modelagem Matemática — Consultoria Atos

Dimensionamento de professores do Ensino Fundamental (1º ao 9º ano) via
programação linear (inteira), no espírito de Kantorovich–Koopmans.

---

## 1. Modelo 1 — Quantidade Mínima de Professores

### 1.1 Conjuntos e parâmetros

| Símbolo | Significado |
|---|---|
| $T_1$ | turmas do Fundamental 1 (1º–5º ano), $\lvert T_1 \rvert = 5$ |
| $T_2$ | turmas do Fundamental 2 (6º–9º ano), $\lvert T_2 \rvert = 4$ |
| $T$ | $T_1 \cup T_2$, $\lvert T \rvert = 9$ |
| $d_t$ | demanda semanal de aulas da turma $t$: $d_t = 30$, $\forall t \in T$ |
| $J$ | jornada semanal do professor (horas) |
| $f$ | fração da jornada reservada para hora-atividade |
| $m$ | duração de uma aula: $m = 45$ min |
| $C$ | capacidade máxima semanal de aulas em sala por professor |
| $P$ | conjunto de professores candidatos |
| $N^{*}$, $N_1^{*}$, $N_2^{*}$, $N^{*}_{\text{flex}}$ | **quantidade mínima de professores** — valor ótimo do problema de minimização, não uma estimativa |

### 1.2 Capacidade máxima por professor

$$
C(J,f) = \left\lfloor \frac{J \cdot 60 \cdot (1 - f)}{m} \right\rfloor
$$

### 1.3 Fundamental 1 — modelo polivalente

Um único professor cobre a turma inteira; não há fragmentação entre
turmas.

$$
N_1^{*} =
\begin{cases}
\lvert T_1 \rvert & \text{se } C \ge \max_{t \in T_1} d_t \\[4pt]
\text{inviável} & \text{caso contrário}
\end{cases}
$$

### 1.4 Fundamental 2 — cobertura mínima (programação linear inteira)

**Variáveis de decisão**

$$
x_{p,t} \in \mathbb{Z}_{\ge 0} \quad \text{(aulas que o professor } p \text{ dá na turma } t \in T_2) \qquad
y_p \in \{0,1\} \quad \text{(professor } p \text{ contratado)}
$$

**Função objetivo**

$$
\min \sum_{p \in P} y_p
$$

**Restrições**

$$
\sum_{p \in P} x_{p,t} = d_t \qquad \forall\, t \in T_2
$$

$$
\sum_{t \in T_2} x_{p,t} \le C \cdot y_p \qquad \forall\, p \in P
$$

**Limite inferior** (divisão do recurso total pela capacidade unitária)

$$
N_2^{*} \ge \left\lceil \frac{\sum_{t \in T_2} d_t}{C} \right\rceil
$$

### 1.5 Modelo flexível (quando $C < 30$)

Se $C < \max_{t \in T_1} d_t$, o modelo polivalente da seção 1.3 é
inviável — um professor não fecha mais uma turma do Fundamental 1
sozinho. Usa-se o mesmo modelo de cobertura mínima da seção 1.4,
generalizado para $T = T_1 \cup T_2$ — a restrição "1 professor por
turma" é removida (flexibilizada):

$$
\min \sum_{p \in P} y_p
\quad \text{sujeito a} \quad
\sum_{p \in P} x_{p,t} = d_t \;\; \forall\, t \in T, \qquad
\sum_{t \in T} x_{p,t} \le C \cdot y_p \;\; \forall\, p \in P
$$

$$
N^{*}_{\text{flex}} \ge \left\lceil \frac{\sum_{t \in T} d_t}{C} \right\rceil = \left\lceil \frac{270}{C} \right\rceil
$$

Esse número ignora a exigência de "1 professor fixo por turma" no
Fundamental 1 — é um piso otimista.

### 1.6 Exemplo numérico — $J = 20$h

**Capacidade**

$$
C(20, 0) = \left\lfloor \frac{20 \cdot 60 \cdot 1}{45} \right\rfloor = \left\lfloor 26{,}67 \right\rfloor = 26
$$

$$
C(20, \tfrac{1}{3}) = \left\lfloor \frac{20 \cdot 60 \cdot \frac{2}{3}}{45} \right\rfloor = \left\lfloor 17{,}78 \right\rfloor = 17
$$

**Checagem de viabilidade do modelo polivalente**

$$
C(20,0) = 26 < 30 \qquad C(20,\tfrac{1}{3}) = 17 < 30
$$

Em ambos os cenários $C < 30$: o modelo da seção 1.3 é inviável, e o
dimensionamento cai no modelo flexível da seção 1.5, aplicado às 9
turmas ($T = T_1 \cup T_2$, demanda total $\sum_t d_t = 270$).

**Sem desconto de hora-atividade** ($C = 26$)

$$
N^{*}_{\text{flex}} \ge \left\lceil \frac{270}{26} \right\rceil = \left\lceil 10{,}38 \right\rceil = 11
$$

Resolvido via PLI (PuLP/CBC): $N^{*}_{\text{flex}} = 11$ — o limite
inferior é atingido exatamente.

**Com 1/3 de hora-atividade** ($C = 17$)

$$
N^{*}_{\text{flex}} \ge \left\lceil \frac{270}{17} \right\rceil = \left\lceil 15{,}88 \right\rceil = 16
$$

Resolvido via PLI: $N^{*}_{\text{flex}} = 16$ — limite inferior
também atingido exatamente.

### 1.7 Resultados — todas as cargas horárias

$$
N^{*}(C) =
\begin{cases}
N_1^{*} + N_2^{*} = \lvert T_1 \rvert + \left\lceil \dfrac{\sum_{t \in T_2} d_t}{C} \right\rceil & \text{se } C \ge 30 \\[10pt]
N^{*}_{\text{flex}} = \left\lceil \dfrac{270}{C} \right\rceil & \text{se } C < 30
\end{cases}
$$

$N^{*}$ é sempre a **quantidade mínima de professores** para aquele
cenário — abaixo dela o problema não tem solução; acima dela sobra
folga desnecessária.

| $J$ | $f$ | $C(J,f)$ | $N^{*}$ — mín. de professores |
|---|---|---|---|
| 20h | $0$ | 26 | 11 ‡ |
| 20h | $1/3$ | 17 | 16 ‡ |
| 25h | $0$ | 33 | 9 |
| 25h | $1/3$ | 22 | 13 ‡ |
| 30h | $0$ | 40 | 8 |
| 30h | $1/3$ | 26 | 11 ‡ |
| 40h | $0$ | 53 | 8 |
| 40h | $1/3$ | 35 | 9 |
| 44h | $0$ | 58 | 8 |
| 44h | $1/3$ | 39 | 9 |

‡ modelo flexível ($C < 30$, seção 1.5). Todos os valores verificados
por PLI (PuLP/CBC).

---

## 2. Modelo 2 — Disponibilidade Mínima e Máximo de Recusas por Professor

### 2.1 Variável de decisão

$$
H_{a,b,c,d} \in \{0,1\}, \qquad a \in \text{matérias},\; b \in \text{turmas} \,(9),\; c \in \text{aulas} \,(6/\text{dia}),\; d \in \text{dias} \,(5)
$$

$$
H_{a,b,c,d} = 1 \iff \text{a matéria } a \text{ é ministrada na turma } b\text{, aula } c\text{, dia } d
$$

### 2.2 Função objetivo

$$
\max \sum_{a,b,c,d} H_{a,b,c,d}
$$

### 2.3 Restrições

$$
\text{R1: } \sum_{a} H_{a,b,c,d} \le 1 \qquad \forall\, b,c,d
$$

$$
\text{R2 (Anos Finais): } \sum_{b \,\in\, \text{Finais}} H_{a,b,c,d} \le 1 \qquad \forall\, a,c,d
$$

$$
\text{R3: } \sum_{c} H_{a,b,c,d} \le \text{máx}_{a,b} \qquad \forall\, a,b,d
$$

$$
\text{R4: } \sum_{c,d} H_{a,b,c,d} \ge \text{mín}_{a,b} \qquad \forall\, a,b
$$

$$
\text{R5: } H_{a,b,c,d} = 0 \quad \text{se a matéria } a \text{ está indisponível no dia } d\text{, aula } c \qquad \forall\, b
$$

### 2.4 Disponibilidade mínima ($N_{min}$)

$$
N_{min}(a) = \max\Big(\, \text{mín}_{a,\,\text{Iniciais}} \,,\; 4 \times \text{mín}_{a,\,\text{Finais}} \,\Big)
$$

$$
R_{max}(a) = 30 - N_{min}(a)
$$

### 2.5 Resultados por matéria

| Matéria | mín. Iniciais | mín. Finais | $N_{min}(a)$ | $R_{max}(a)$ |
|---|---|---|---|---|
| Arte | 2 | 1 | 4 | 26 |
| Ed. Física | 3 | 2 | 8 | 22 |
| Geografia | 3 | 3 | 12 | 18 |
| História | 3 | 3 | 12 | 18 |
| Inglês | 0 | 4 | 16 | 14 |
| Ciências | 5 | 5 | 20 | 10 |
| Língua Portuguesa | 8 | 6 | 24 | 6 |
| Matemática | 6 | 6 | 24 | 6 |
