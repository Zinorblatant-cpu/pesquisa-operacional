"""
Quantidade minima de professores para cobrir todas as aulas do Fundamental 1
(1o ao 5o ano) e Fundamental 2 (6o ao 9o ano).

Modelo: dimensionamento agregado de quadro (nao eh grade horaria detalhada
slot a slot). Cada turma precisa de 30 aulas/semana. Cada professor tem uma
capacidade maxima de aulas em sala por semana, definida pela jornada de
trabalho menos a hora-atividade garantida por lei.

Fundamental 1: modelo polivalente -> um unico professor cobre a turma inteira
(nao ha fragmentacao entre turmas).

Fundamental 2: modelo agregado -> as aulas de uma turma podem ser cobertas
por mais de um professor, e um professor pode dar aulas em mais de uma
turma, respeitando sua capacidade maxima semanal. Resolvido como um
problema de cobertura minima (Kantorovich-Koopmans / programacao linear
inteira) com PuLP.
"""

import math
import pulp

AULA_MINUTOS = 45
JORNADA_SEMANAL_HORAS = 40
FRACAO_HORA_ATIVIDADE = 1 / 3

TURMAS_F1 = [f"{ano}o_ano" for ano in range(1, 6)]   # 1o ao 5o ano
TURMAS_F2 = [f"{ano}o_ano" for ano in range(6, 10)]  # 6o ao 9o ano
AULAS_POR_TURMA = 30


def capacidade_maxima_aulas_por_professor(
    jornada_horas: float = JORNADA_SEMANAL_HORAS,
    fracao_hora_atividade: float = FRACAO_HORA_ATIVIDADE,
) -> int:
    minutos_jornada = jornada_horas * 60
    minutos_em_sala = minutos_jornada * (1 - fracao_hora_atividade)
    return math.floor(minutos_em_sala / AULA_MINUTOS)


def resolver_fundamental_1(capacidade_max: int) -> int:
    for turma in TURMAS_F1:
        assert AULAS_POR_TURMA <= capacidade_max, (
            f"Turma {turma} precisa de {AULAS_POR_TURMA} aulas/semana, "
            f"acima da capacidade maxima de {capacidade_max} aulas/semana "
            "de um professor -- modelo polivalente inviavel."
        )
    return len(TURMAS_F1)


def resolver_cobertura_minima(turmas: list, capacidade_max: int) -> tuple[int, dict]:
    """Cobertura minima generica: quantos professores (capacidade <= capacidade_max
    cada) sao necessarios para cobrir AULAS_POR_TURMA aulas em cada turma da lista."""
    demanda_total = len(turmas) * AULAS_POR_TURMA
    limite_superior_profs = max(len(turmas), math.ceil(demanda_total / capacidade_max) + 1)
    professores = list(range(limite_superior_profs))

    problema = pulp.LpProblem("minimo_professores", pulp.LpMinimize)

    usado = pulp.LpVariable.dicts("usado", professores, cat="Binary")
    aulas = pulp.LpVariable.dicts(
        "aulas", (professores, turmas), lowBound=0, cat="Integer"
    )

    problema += pulp.lpSum(usado[p] for p in professores)

    for turma in turmas:
        problema += pulp.lpSum(aulas[p][turma] for p in professores) == AULAS_POR_TURMA

    for p in professores:
        problema += (
            pulp.lpSum(aulas[p][turma] for turma in turmas)
            <= capacidade_max * usado[p]
        )

    problema.solve(pulp.PULP_CBC_CMD(msg=False))

    assert problema.status == pulp.LpStatusOptimal, (
        f"Problema nao ficou otimo (status={pulp.LpStatus[problema.status]}) "
        f"para {len(turmas)} turmas com capacidade {capacidade_max}"
    )

    professores_usados = [p for p in professores if usado[p].value() == 1]
    alocacao = {
        p: {turma: aulas[p][turma].value() for turma in turmas}
        for p in professores_usados
    }
    return len(professores_usados), alocacao


def resolver_fundamental_2(capacidade_max: int) -> tuple[int, dict]:
    return resolver_cobertura_minima(TURMAS_F2, capacidade_max)


def main():
    capacidade_max = capacidade_maxima_aulas_por_professor()

    print("== Parametros ==")
    print(f"Jornada semanal: {JORNADA_SEMANAL_HORAS}h")
    print(f"Hora-atividade minima: 1/3 da jornada")
    print(f"Capacidade maxima de aulas em sala por professor: {capacidade_max} aulas/semana")
    print(f"Aulas por turma: {AULAS_POR_TURMA} aulas/semana")
    print()

    num_f1 = resolver_fundamental_1(capacidade_max)
    print("== Fundamental 1 (1o ao 5o ano, polivalente) ==")
    print(f"Turmas: {len(TURMAS_F1)}")
    print(f"Professores necessarios: {num_f1} (1 por turma)")
    print()

    num_f2, alocacao_f2 = resolver_fundamental_2(capacidade_max)
    print("== Fundamental 2 (6o ao 9o ano, agregado) ==")
    print(f"Turmas: {len(TURMAS_F2)}")
    print(f"Professores necessarios (minimo): {num_f2}")
    for p, turmas in alocacao_f2.items():
        detalhes = ", ".join(
            f"{turma}: {qtd:.0f} aulas" for turma, qtd in turmas.items() if qtd > 0
        )
        print(f"  Professor {p + 1}: {detalhes}")
    print()

    total = num_f1 + num_f2
    print("== Resultado final ==")
    print(f"Quantidade minima de professores (Fundamental 1 + Fundamental 2): {total}")


CENARIOS_CARGA_HORARIA = [
    (20, 0, "20h sem desconto"),
    (20, 1 / 3, "20h com 1/3"),
    (25, 0, "25h sem desconto"),
    (25, 1 / 3, "25h com 1/3 (= Jornada Completa SEDUC-SP)"),
    (30, 0, "30h sem desconto"),
    (30, 1 / 3, "30h com 1/3"),
    (40, 0, "40h sem desconto"),
    (40, 1 / 3, "40h com 1/3 (= Jornada Ampliada SEDUC-SP)"),
    (44, 0, "44h sem desconto"),
    (44, 1 / 3, "44h com 1/3"),
]


def conferir_todas_as_cargas_horarias():
    print()
    print("== Conferindo todos os cenarios de carga horaria (README secao 3.1) ==")
    print(f"{'Cenario':45} {'C (aulas/sem)':>14} {'N* (solver)':>12}")

    for jornada_horas, fracao, rotulo in CENARIOS_CARGA_HORARIA:
        capacidade = capacidade_maxima_aulas_por_professor(jornada_horas, fracao)

        if capacidade >= AULAS_POR_TURMA:
            num_f1 = resolver_fundamental_1(capacidade)
            num_f2, _ = resolver_cobertura_minima(TURMAS_F2, capacidade)
            total = num_f1 + num_f2
            marcador = ""
        else:
            total, _ = resolver_cobertura_minima(TURMAS_F1 + TURMAS_F2, capacidade)
            marcador = " (flexivel, sem exigir 1 regente/turma no F1)"

        print(f"{rotulo:45} {capacidade:>14} {total:>9}{marcador}")


if __name__ == "__main__":
    main()
    conferir_todas_as_cargas_horarias()
