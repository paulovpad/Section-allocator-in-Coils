# core/objetivos.py
"""
Funções de valor para o knapsack por camada.
O objetivo primário é sempre maximizar a LARGURA ocupada.
O segundo termo (opcional) desempata favorecendo mais COMPRIMENTO
ou redução de SOBRA, sem mudar o ótimo principal de largura.
"""

from __future__ import annotations

def valor_largura(passo_m: float, comp_por_faixa_m: float, sobra_linha_m: float | None = None) -> int:
    """Valor = largura ocupada (mm)."""
    largura_mm = int(round(passo_m * 1000.0))
    return largura_mm

def valor_largura_comprimento(passo_m: float, comp_por_faixa_m: float, sobra_linha_m: float | None = None) -> int:
    """
    Valor = largura_mm * 1e6 + comprimento_mm
    Mantém largura dominante e desempata por mais metros alocados.
    """
    largura_mm = int(round(passo_m * 1000.0))
    comp_mm = int(round(comp_por_faixa_m * 1000.0))
    return largura_mm * 1_000_000 + comp_mm

def valor_largura_balanceamento(passo_m: float, comp_por_faixa_m: float, sobra_linha_m: float | None = None) -> int:
    """
    Valor = largura_mm * 1e6 + min(comprimento_mm, sobra_mm)
    Desempata favorecendo reduzir a maior sobra.
    """
    largura_mm = int(round(passo_m * 1000.0))
    comp_mm = int(round(comp_por_faixa_m * 1000.0))
    bonus = 0
    if sobra_linha_m is not None:
        bonus = int(round(min(comp_por_faixa_m, sobra_linha_m) * 1000.0))
    return largura_mm * 1_000_000 + bonus
