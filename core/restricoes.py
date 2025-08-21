# core/restricoes.py
"""
Checagens de elegibilidade geométrica e limites de faixas por linha.
Converte peso/volume remanescentes para número de FAIXAS (voltas) na camada.
"""

from __future__ import annotations
import math
from typing import Optional

EPS = 1e-9

def checar_elegibilidade(bobina, linha, r_base_m: float, d_m: float, de_total_m: float) -> Optional[float]:
    """
    Verifica se a linha pode participar da camada:
      - Não estoura DE (se usar espessura d_m nesta camada)
      - Respeita raio mínimo no raio médio
    Retorna r_mid_m se elegível; senão, None.
    """
    # Checagem DE (usando a espessura desta linha)
    if 2.0 * (r_base_m + d_m) > de_total_m + EPS:
        return None

    r_mid_m = r_base_m + d_m / 2.0
    raio_min = float(getattr(linha, "raio_minimo_m", 0.0) or 0.0)
    if r_mid_m + EPS < raio_min:
        return None
    return r_mid_m

def limites_por_linha(bobina, linha, comp_por_faixa_m: float, rem_linha_m: float, validador) -> int:
    """
    Calcula o número MÁXIMO de faixas (voltas) desta linha que cabem na camada,
    limitado por:
      - comprimento remanescente da linha (rem_linha_m),
      - peso restante da bobina (via validador),
      - volume restante da bobina (via validador).
    """
    if comp_por_faixa_m <= EPS:
        return 0

    # Limite por remanescente da linha
    max_by_rem = int(math.floor(rem_linha_m / comp_por_faixa_m))

    # Limites por peso e volume (validador retorna "comprimento máximo" restante, em metros)
    max_len_peso = float(validador.max_comprimento_por_peso(bobina, linha) or 0.0)
    max_len_vol  = float(validador.max_comprimento_por_volume(bobina, linha) or 0.0)

    max_by_peso = int(math.floor(max_len_peso / comp_por_faixa_m)) if comp_por_faixa_m > 0 else 0
    max_by_vol  = int(math.floor(max_len_vol  / comp_por_faixa_m)) if comp_por_faixa_m > 0 else 0

    qtd_max = max(0, min(max_by_rem, max_by_peso, max_by_vol))
    return qtd_max
