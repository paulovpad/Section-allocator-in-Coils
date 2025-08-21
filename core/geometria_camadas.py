# core/geometria_camadas.py
"""
Registro geométrico das faixas escolhidas na camada e cálculo da espessura.
"""

from __future__ import annotations
from typing import Dict, Tuple
from models import Camada

EPS = 1e-9

def registrar_na_camada(
    camada: Camada,
    escolhas: Dict[object, int],                       # {linha: faixas}
    props: Dict[object, Tuple[float, float, float]],   # props[linha] = (r_mid_m, comp_por_faixa_m, passo_m)
    largura_m: float,
    lado_inicio: str = "esquerda",
) -> float:
    """
    Grava as faixas na camada e devolve a ESPESSURA radial (= maior diâmetro usado).
    """
    # Alternância de lado só para relatório/visualização
    lado = lado_inicio
    maior_d_m = 0.0

    for linha, faixas in escolhas.items():
        if faixas <= 0:
            continue
        r_mid_m, comp_por_faixa_m, passo_m = props[linha]
        comprimento_total = faixas * comp_por_faixa_m

        # capacidade teórica de faixas se a camada fosse só desta linha
        voltas_capacidade = int(largura_m / max(EPS, passo_m))

        camada.adicionar_linha(
            linha=linha,
            pos_x=0.0,
            pos_y=r_mid_m,
            ordem=None,
            comprimento_alocado=comprimento_total,
            voltas_usadas=faixas,
            voltas_capacidade=voltas_capacidade,
            passo=passo_m,
            lado=lado
        )

        # atualiza maior diâmetro usado
        d_m = float(getattr(linha, "diametro", 0.0) or 0.0) / 1000.0
        if d_m > maior_d_m:
            maior_d_m = d_m

        # alterna lado
        lado = "direita" if lado == "esquerda" else "esquerda"

    return maior_d_m
