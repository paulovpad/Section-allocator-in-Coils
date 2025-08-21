# core/selecionador_faixas.py
"""
Knapsack (mochila inteira) por camada.
Recebe "itens" (faixas possíveis por linha) e devolve quantas faixas
de cada linha usar para maximizar a LARGURA ocupada (com desempate opcional).
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Callable, Tuple

@dataclass(frozen=True)
class ItemFaixa:
    linha: object
    passo_m: float              # largura consumida por faixa (m)
    comp_por_faixa_m: float     # 2π * r_mid (m)
    qtd_max: int                # máximo de faixas desta linha na camada
    r_mid_m: float              # raio médio da faixa nesta camada
    d_m: float                  # diâmetro real (m)
    sobra_linha_m: float        # comprimento remanescente (m), usado em empates (opcional)

def selecionar_faixas(
    itens: List[ItemFaixa],
    largura_m: float,
    valor_fn: Callable[[float, float, float | None], int],
) -> Dict[object, int]:
    """
    Resolve a mochila inteira com expansão em itens unitários (bounded -> 0/1).
    - Capacidade W = largura_m em mm
    - Para cada cópia de faixa: peso = passo_mm, valor = valor_fn(...)
    Retorna: {linha: faixas_escolhidas}
    """
    W = int(round(largura_m * 1000.0))
    if W <= 0 or not itens:
        return {}

    # Expansão de itens unitários
    unit_items: List[Tuple[int, int, ItemFaixa]] = []
    for t in itens:
        w_mm = int(round(t.passo_m * 1000.0))
        if w_mm <= 0 or t.qtd_max <= 0:
            continue
        v = valor_fn(t.passo_m, t.comp_por_faixa_m, t.sobra_linha_m)
        for _ in range(t.qtd_max):
            unit_items.append((w_mm, v, t))

    if not unit_items:
        return {}

    # DP 1D (0/1)
    dp = [-1] * (W + 1)
    keep: List[Tuple[int, int] | None] = [None] * (W + 1)
    dp[0] = 0

    for k, (w_mm, v, t) in enumerate(unit_items):
        for w in range(W, w_mm - 1, -1):
            if dp[w - w_mm] != -1:
                cand = dp[w - w_mm] + v
                if cand > dp[w]:
                    dp[w] = cand
                    keep[w] = (w - w_mm, k)

    # Melhor capacidade
    w_best = max(range(W + 1), key=lambda w: dp[w])
    if dp[w_best] <= 0 or keep[w_best] is None:
        return {}

    # Reconstrução
    usados_por_linha: Dict[object, int] = {}
    w = w_best
    while w > 0 and keep[w] is not None:
        w_prev, k = keep[w]
        _, _, t = unit_items[k]
        usados_por_linha[t.linha] = usados_por_linha.get(t.linha, 0) + 1
        w = w_prev

    return usados_por_linha
