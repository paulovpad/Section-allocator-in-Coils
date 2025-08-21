# core/alocador_bobinagem.py
import math
from core.validador import ValidadorAlocacao
from models import Camada

class AlocadorBobinagemReal:
    """
    Bobinagem real por camadas radiais com alocação eficiente:
    em cada camada, escolhe-se a combinação de faixas (tracks) que
    maximiza a largura ocupada (mochila inteira), respeitando:
      • Peso e Volume máximos da bobina
      • Limites geométricos DI/DE
      • Raio mínimo de cada linha
    A espessura da camada é o MAIOR diâmetro real usado nela.
    """

    # parâmetros do algoritmo
    MARGEM_FRAC = 0.05   # folga lateral entre faixas (fração do diâmetro)
    EPS = 1e-9

    # ---------- helpers de unidade e geometria ----------
    @staticmethod
    def _d_real_m(linha) -> float:
        """Diâmetro real da linha em metros (no Excel costuma vir em mm)."""
        try:
            return float(getattr(linha, "diametro", 0.0) or 0.0) / 1000.0
        except Exception:
            return 0.0

    def _passo(self, d_m: float) -> float:
        """Passo efetivo na largura p/ uma faixa dessa linha."""
        return d_m * (1.0 + 2.0 * self.MARGEM_FRAC)

    @staticmethod
    def _circ(r_m: float) -> float:
        return 2.0 * math.pi * r_m

    @staticmethod
    def _peso_m(L) -> float:
        return float(getattr(L, "peso_por_metro_kg", 0.0) or 0.0)

    @staticmethod
    def _comprimento(L) -> float:
        return float(getattr(L, "comprimento", 0.0) or 0.0)

    # ---------- algoritmo principal ----------
    def alocar_em_bobina(self, bobina, linhas):
        """
        Aloca 'linhas' em 'bobina' camada a camada resolvendo, em cada camada,
        um problema de mochila inteira (bounded knapsack) que maximiza a
        largura ocupada por faixas, respeitando DE, raio mínimo, peso e volume.
        """
        EPS = self.EPS

        # Ordene por criticidade: maior diâmetro, menor raio_min, maior peso total
        def _peso_total(L):
            return self._peso_m(L) * self._comprimento(L)

        linhas_ord = sorted(
            list(linhas),
            key=lambda L: (
                -self._d_real_m(L),
                float(getattr(L, "raio_minimo_m", 0.0) or 0.0),
                -_peso_total(L)
            )
        )

        # Estado radial e dimensões da bobina
        r_atual = float(getattr(bobina, "diametro_interno", 0.0) or 0.0) / 2.0
        de_total = float(getattr(bobina, "diametro_externo", 0.0) or 0.0)
        largura_m = float(getattr(bobina, "largura", 0.0) or 0.0)

        # Remanescente por linha (m)
        rem = {id(L): self._comprimento(L) for L in linhas_ord}

        val = ValidadorAlocacao()
        lado_inicio = "esquerda"
        linhas_nao = []

        # Loop de camadas
        while True:
            # parar se acabou ou atingiu DE
            if all(rem[id(L)] <= EPS for L in linhas_ord):
                break
            if (2.0 * r_atual) >= (de_total - EPS):
                break

            # Monta "catálogo" de tipos elegíveis nesta camada
            tipos = []
            for idx, L in enumerate(linhas_ord):
                if rem[id(L)] <= EPS:
                    continue
                d = self._d_real_m(L)
                if d <= EPS:
                    continue
                # DE com esta linha nesta camada
                if 2.0 * (r_atual + d) > de_total + EPS:
                    continue
                r_mid = r_atual + d / 2.0
                # raio mínimo
                if r_mid + EPS < float(getattr(L, "raio_minimo_m", 0.0) or 0.0):
                    continue

                p = self._passo(d)     # consumo de largura por faixa (m)
                C = self._circ(r_mid)  # consumo de comprimento por faixa (m)
                if p <= EPS or C <= EPS:
                    continue

                # Limites de faixas por: remanescente, peso e volume.
                max_by_rem = int(math.floor(rem[id(L)] / C))
                max_len_peso = val.max_comprimento_por_peso(bobina, L)   # m
                max_by_peso = int(math.floor(max_len_peso / C))
                max_len_vol = val.max_comprimento_por_volume(bobina, L)  # m
                max_by_vol  = int(math.floor(max_len_vol / C))

                qtd_max = max(0, min(max_by_rem, max_by_peso, max_by_vol))
                if qtd_max <= 0:
                    continue

                tipos.append({
                    "idx": idx,
                    "L": L,
                    "d_m": d,
                    "r_mid": r_mid,
                    "passo": p,
                    "compr_por_faixa": C,
                    "qtd_max": qtd_max
                })

            if not tipos:
                # ninguém cabe nesta camada com o raio atual
                break

            # Capacidade da mochila (mm)
            W = int(round(largura_m * 1000.0))
            if W <= 0:
                break

            # Expansão em itens unitários (bounded -> vários unários)
            items = []
            for t in tipos:
                w_mm = int(round(t["passo"] * 1000.0))
                v_mm = w_mm  # maximizar largura ocupada
                for _ in range(t["qtd_max"]):
                    items.append((w_mm, v_mm, t))

            # DP 1D: dp[w] = valor; keep[w] = (w_prev, k_item)
            dp = [-1] * (W + 1)
            keep = [None] * (W + 1)
            dp[0] = 0
            for k, (w_mm, v_mm, t) in enumerate(items):
                for w in range(W, w_mm - 1, -1):
                    if dp[w - w_mm] != -1:
                        cand = dp[w - w_mm] + v_mm
                        if cand > dp[w]:
                            dp[w] = cand
                            keep[w] = (w - w_mm, k)

            w_best = max(range(W + 1), key=lambda w: dp[w])
            if dp[w_best] <= 0:
                break  # nada melhorou

            # Reconstrói escolha ótima
            usados_por_tipo = {}
            w = w_best
            while w > 0 and keep[w] is not None:
                w_prev, k = keep[w]
                _, _, t = items[k]
                usados_por_tipo[t["idx"]] = usados_por_tipo.get(t["idx"], 0) + 1
                w = w_prev

            if not usados_por_tipo:
                break

            # Constrói a camada com as escolhas
            camada = Camada(diametro_base=2.0 * r_atual)
            lado = lado_inicio
            maior_d = 0.0

            for idx, qtd in usados_por_tipo.items():
                t = next(tt for tt in tipos if tt["idx"] == idx)
                L = t["L"]
                d = t["d_m"]
                C = t["compr_por_faixa"]
                p = t["passo"]
                r_mid = t["r_mid"]

                comprimento_total = qtd * C
                # segurança extra (já respeitado pela DP)
                comprimento_total = min(
                    comprimento_total,
                    rem[id(L)],
                    val.max_comprimento_por_peso(bobina, L),
                    val.max_comprimento_por_volume(bobina, L),
                )
                faixas_ok = int(math.floor(comprimento_total / C))
                if faixas_ok <= 0:
                    continue

                camada.adicionar_linha(
                    linha=L,
                    pos_x=0.0,
                    pos_y=r_mid,
                    ordem=None,
                    comprimento_alocado=faixas_ok * C,
                    voltas_usadas=faixas_ok,                           # nº de faixas
                    voltas_capacidade=int(largura_m / max(EPS, p)),    # teórica p/ essa linha
                    passo=p,
                    lado=lado
                )
                rem[id(L)] -= faixas_ok * C
                maior_d = max(maior_d, d)
                lado = "direita" if lado == "esquerda" else "esquerda"

            # nada escolhido de fato? encerra
            if maior_d <= EPS or not camada.linhas:
                break

            bobina.adicionar_camada(camada)
            r_atual += maior_d  # espessura = maior diâmetro usado

            if 2.0 * r_atual > de_total + EPS:
                break

            lado_inicio = "direita" if lado_inicio == "esquerda" else "esquerda"

        # Linhas com sobra
        for L in linhas_ord:
            if rem[id(L)] > EPS:
                linhas_nao.append(L)

        return bobina, linhas_nao


__all__ = ["AlocadorBobinagemReal"]
