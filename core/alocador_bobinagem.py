# core/alocador_bobinagem.py
"""
Orquestração da bobinagem por camadas:
- Monta itens elegíveis por camada (por linha)
- Resolve knapsack para escolher faixas
- Registra geometricamente a camada e avança o raio
"""

from __future__ import annotations
import math
from typing import Dict, List

from core.validador import ValidadorAlocacao
from models import Camada
from core.selecionador_faixas import ItemFaixa, selecionar_faixas
from core.geometria_camadas import registrar_na_camada
from core.restricoes import checar_elegibilidade, limites_por_linha
from core.objetivos import valor_largura_comprimento  # escolha padrão do objetivo

class AlocadorBobinagemReal:
    """
    Bobinagem por camadas radiais com seleção ótima (knapsack) e
    registro geométrico consistente.
    A espessura de cada camada é o MAIOR diâmetro usado nela.
    """

    MARGEM_FRAC = 0.05
    EPS = 1e-9

    # ---------- helpers de unidade e geometria ----------
    @staticmethod
    def _d_real_m(linha) -> float:
        """Diâmetro real da linha em metros (entrada geralmente em mm)."""
        try:
            return float(getattr(linha, "diametro", 0.0) or 0.0) / 1000.0
        except Exception:
            return 0.0

    def _passo(self, d_m: float) -> float:
        """Passo efetivo na largura para uma faixa dessa linha."""
        return d_m * (1.0 + 2.0 * self.MARGEM_FRAC)

    @staticmethod
    def _circ(r_m: float) -> float:
        return 2.0 * math.pi * r_m

    @staticmethod
    def _comprimento(L) -> float:
        return float(getattr(L, "comprimento", 0.0) or 0.0)

    # ---------- algoritmo principal ----------
    def alocar_em_bobina(self, bobina, linhas):
        """
        Aloca 'linhas' na 'bobina' camada a camada:
          1) cataloga faixas elegíveis,
          2) resolve knapsack para maximizar a largura ocupada,
          3) registra camada e avança o raio.
        Retorna: (bobina, linhas_nao_alocadas)
        """
        EPS = self.EPS

        # Ordena linhas por criticidade (ajuda levemente a estabilidade)
        def _peso_total(L):
            kgpm = float(getattr(L, "peso_por_metro_kg", 0.0) or 0.0)
            return kgpm * self._comprimento(L)

        linhas_ord = sorted(
            list(linhas),
            key=lambda L: (
                -self._d_real_m(L),
                float(getattr(L, "raio_minimo_m", 0.0) or 0.0),
                -_peso_total(L)
            )
        )

        # Estado radial e dimensões
        r_base_m = float(getattr(bobina, "diametro_interno", 0.0) or 0.0) / 2.0
        de_total_m = float(getattr(bobina, "diametro_externo", 0.0) or 0.0)
        largura_m = float(getattr(bobina, "largura", 0.0) or 0.0)

        # Remanescente por linha (m)
        rem: Dict[int, float] = {id(L): self._comprimento(L) for L in linhas_ord}

        val = ValidadorAlocacao()
        lado_inicio = "esquerda"
        linhas_nao: List[object] = []

        # Loop de camadas
        while True:
            # terminou ou sem espaço radial?
            if all(rem[id(L)] <= EPS for L in linhas_ord):
                break
            if (2.0 * r_base_m) >= (de_total_m - EPS):
                break
            if largura_m <= EPS:
                break

            # Monta catálogo de itens elegíveis
            itens: List[ItemFaixa] = []
            props: Dict[object, tuple] = {}  # props[linha] = (r_mid, comp_por_faixa, passo)

            for L in linhas_ord:
                rem_L = rem[id(L)]
                if rem_L <= EPS:
                    continue

                d_m = self._d_real_m(L)
                if d_m <= EPS:
                    continue

                r_mid_m = checar_elegibilidade(bobina, L, r_base_m, d_m, de_total_m)
                if r_mid_m is None:
                    continue

                passo_m = self._passo(d_m)
                comp_por_faixa_m = self._circ(r_mid_m)

                qtd_max = limites_por_linha(
                    bobina=bobina,
                    linha=L,
                    comp_por_faixa_m=comp_por_faixa_m,
                    rem_linha_m=rem_L,
                    validador=val
                )
                if qtd_max <= 0:
                    continue

                itens.append(
                    ItemFaixa(
                        linha=L,
                        passo_m=passo_m,
                        comp_por_faixa_m=comp_por_faixa_m,
                        qtd_max=qtd_max,
                        r_mid_m=r_mid_m,
                        d_m=d_m,
                        sobra_linha_m=rem_L
                    )
                )
                props[L] = (r_mid_m, comp_por_faixa_m, passo_m)

            if not itens:
                # nenhuma linha cabe nesta camada com o raio atual
                break

            # 1) Seleção ótima por knapsack (largura + comprimento como desempate)
            escolhas = selecionar_faixas(
                itens=itens,
                largura_m=largura_m,
                valor_fn=valor_largura_comprimento,  # troque aqui se quiser outro objetivo
            )

            if not escolhas:
                # por segurança (não deveria ocorrer se itens existirem)
                break

            # 2) Registro geométrico da camada
            camada = Camada(diametro_base=2.0 * r_base_m)
            maior_d_m = registrar_na_camada(
                camada=camada,
                escolhas=escolhas,
                props=props,
                largura_m=largura_m,
                lado_inicio=lado_inicio
            )

            if maior_d_m <= EPS or not getattr(camada, "linhas", None):
                # nada foi realmente alocado
                break

            # Debita remanescentes das linhas escolhidas
            for L, faixas in escolhas.items():
                if faixas <= 0:
                    continue
                r_mid_m, comp_por_faixa_m, _ = props[L]
                rem[id(L)] = max(0.0, rem[id(L)] - faixas * comp_por_faixa_m)

            # 3) Empilha a camada na bobina e avança raio
            bobina.adicionar_camada(camada)
            r_base_m += maior_d_m
            lado_inicio = "direita" if lado_inicio == "esquerda" else "esquerda"

            # segurança DE
            if 2.0 * r_base_m > de_total_m + EPS:
                break

        # Linhas que ficaram com remanescente são reportadas como "não totalmente alocadas"
        for L in linhas_ord:
            if rem[id(L)] > EPS:
                linhas_nao.append(L)

        return bobina, linhas_nao


__all__ = ["AlocadorBobinagemReal"]
