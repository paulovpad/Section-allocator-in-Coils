# core/alocador_bobinagem.py
import math
from core.validador import ValidadorAlocacao
from models import Camada

class AlocadorBobinagemReal:
    """
    Bobinagem real por camadas radiais, permitindo múltiplas linhas
    na MESMA camada (desde que tenham o MESMO diâmetro real ± tolerância).
    Respeita peso, volume, DI/DE e raio mínimo de cada linha.
    """

    # parâmetros do algoritmo
    MARGEM_FRAC = 0.05   # folga lateral (fração do diâmetro real)
    TOL_DIAM = 1e-6      # tolerância para considerar diâmetros iguais (m)
    EPS = 1e-9

    # ----------------- helpers -----------------
    @staticmethod
    def _diametro_real_m(linha) -> float:
        """Diâmetro da linha em metros (no Excel costuma vir em mm)."""
        try:
            return float(getattr(linha, "diametro", 0.0)) / 1000.0
        except Exception:
            return 0.0

    def _passo_largura(self, d_real_m: float) -> float:
        """Passo efetivo na largura para esta linha (diâmetro + margens laterais)."""
        return d_real_m * (1.0 + 2.0 * self.MARGEM_FRAC)

    @staticmethod
    def _circunferencia(r_m: float) -> float:
        return 2.0 * math.pi * r_m

    @staticmethod
    def _peso_total_kg(linha) -> float:
        pm = float(getattr(linha, "peso_por_metro_kg", 0.0) or 0.0)
        comp = float(getattr(linha, "comprimento", 0.0) or 0.0)
        return pm * comp

    # ----------------- algoritmo principal -----------------
    def alocar_em_bobina(self, bobina, linhas):
        """
        Aloca 'linhas' em 'bobina', permitindo MÚLTIPLAS linhas na MESMA camada
        (desde que compartilhem o MESMO diâmetro real, dentro de uma tolerância).

        Estratégia:
          1) Ordena as linhas (mais restritivas primeiro).
          2) Abre uma camada com o diâmetro da 1ª linha elegível.
          3) Preenche os 'slots' de largura dessa camada com outras linhas do MESMO diâmetro,
             respeitando peso, volume, DE e raio mínimo.
          4) Quando os slots acabam (ou trava por limites), empilha a camada e sobe o raio.
        """
        MARGEM_FRAC = self.MARGEM_FRAC
        TOL_DIAM    = self.TOL_DIAM
        EPS         = self.EPS

        # ordenação: diâmetro desc, raio_min asc, peso_total desc
        linhas_ord = sorted(
            list(linhas),
            key=lambda L: (
                -self._diametro_real_m(L),
                float(getattr(L, "raio_minimo_m", 0.0) or 0.0),
                -self._peso_total_kg(L)
            )
        )

        # remanescente (m) por linha
        rem = {id(L): float(getattr(L, "comprimento", 0.0) or 0.0) for L in linhas_ord}

        # estado radial
        r_atual = float(getattr(bobina, "diametro_interno", 0.0) or 0.0) / 2.0
        lado_inicio = "esquerda"
        val = ValidadorAlocacao()
        linhas_nao_alocadas = []

        de_total = float(getattr(bobina, "diametro_externo", 0.0) or 0.0)
        largura_bobina = float(getattr(bobina, "largura", 0.0) or 0.0)

        # Loop de camadas
        while True:
            # acabou tudo?
            if all(rem[id(L)] <= EPS for L in linhas_ord):
                break
            # chegou no DE?
            if (2.0 * r_atual) >= (de_total - EPS):
                break

            # escolhe a linha base da camada (primeira que caiba)
            base = None
            for L in linhas_ord:
                if rem[id(L)] <= EPS:
                    continue
                d_real = self._diametro_real_m(L)
                if d_real <= EPS:
                    continue
                # checa DE para a próxima camada com este diâmetro
                if 2.0 * (r_atual + d_real) > de_total + EPS:
                    continue
                # checa raio mínimo da linha para o raio médio da camada
                r_mid = r_atual + d_real / 2.0
                raio_min = float(getattr(L, "raio_minimo_m", 0.0) or 0.0)
                if r_mid + EPS < raio_min:
                    continue
                base = L
                break

            if base is None:
                # nada mais cabe com o DE/raio_min atuais
                break

            d_base = self._diametro_real_m(base)
            passo = self._passo_largura(d_base)
            n_slots_total = int(math.floor(largura_bobina / max(EPS, passo)))
            if n_slots_total <= 0:
                # largura insuficiente para qualquer volta
                break

            r_mid_camada = r_atual + d_base / 2.0
            circ = self._circunferencia(r_mid_camada)
            camada = Camada(diametro_base=2.0 * r_atual)
            slots_restantes = n_slots_total
            lado_corrente = lado_inicio

            houve_insercao = False

            # percorre as linhas e tenta preencher a camada com MESMO diâmetro
            for L in linhas_ord:
                if slots_restantes <= 0:
                    break
                if rem[id(L)] <= EPS:
                    continue
                d_L = self._diametro_real_m(L)
                if abs(d_L - d_base) > TOL_DIAM:
                    continue
                # raio mínimo desta linha
                raio_min_L = float(getattr(L, "raio_minimo_m", 0.0) or 0.0)
                if r_mid_camada + EPS < raio_min_L:
                    continue

                # limites por peso e volume
                max_len_peso = val.max_comprimento_por_peso(bobina, L)
                max_len_vol  = val.max_comprimento_por_volume(bobina, L)

                # quantas voltas podemos dar por cada limite
                max_voltas_peso = int(math.floor(max_len_peso / max(EPS, circ)))
                max_voltas_vol  = int(math.floor(max_len_vol  / max(EPS, circ)))
                max_voltas_rem  = int(math.floor(rem[id(L)]   / max(EPS, circ)))

                voltas_possiveis = min(slots_restantes, max_voltas_peso, max_voltas_vol, max_voltas_rem)
                if voltas_possiveis <= 0:
                    continue

                len_alocado = voltas_possiveis * circ

                # registra na camada
                camada.adicionar_linha(
                    linha=L,
                    pos_x=0.0,
                    pos_y=r_mid_camada,
                    ordem=None,
                    comprimento_alocado=len_alocado,
                    voltas_usadas=voltas_possiveis,
                    voltas_capacidade=n_slots_total,
                    passo=passo,
                    lado=lado_corrente
                )

                rem[id(L)] -= len_alocado
                slots_restantes -= voltas_possiveis
                houve_insercao = True
                lado_corrente = "direita" if lado_corrente == "esquerda" else "esquerda"

            # Se nada entrou nesta camada, paramos (evita loop infinito)
            if not houve_insercao:
                break

            # empilha a camada pronta e sobe o raio pela espessura do diâmetro base
            bobina.adicionar_camada(camada)
            r_atual += d_base
            lado_inicio = "direita" if lado_inicio == "esquerda" else "esquerda"

            # segurança: não ultrapassar DE
            if 2.0 * r_atual > de_total + EPS:
                break

        # compõe lista de linhas não totalmente alocadas
        linhas_nao_alocadas = [L for L in linhas_ord if rem[id(L)] > EPS]
        return bobina, linhas_nao_alocadas


__all__ = ["AlocadorBobinagemReal"]
