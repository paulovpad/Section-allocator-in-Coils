# core/alocador_bobinagem.py
import math
from models import Camada
from core.validador import ValidadorAlocacao

class AlocadorBobinagemReal:
    """
    Enrola cabos por 'voltas' em camadas radiais:
      - Em cada camada, a linha faz N voltas ao longo da largura;
      - Comprimento por camada ≈ N * (2π * r_médio);
      - Quando acaba a capacidade da camada (ou o comprimento da linha), sobe o raio (+d_real) e repete;
      - Respeita peso, volume, DI/DE e raio mínimo.
    """

    MARGEM_FRAC = 0.05  # folga lateral (fração do diâmetro real)

    def __init__(self):
        self.validador = ValidadorAlocacao()
        self._seq = 0  # ordem global de alocação (para relatório)

    def _next_seq(self):
        self._seq += 1
        return self._seq

    @staticmethod
    def _circ(r):
        return 2.0 * math.pi * r

    def _passo_largura(self, d_real_m: float) -> float:
        """Passo entre voltas na largura (m) = d_real + 2*margem."""
        return d_real_m * (1.0 + 2.0 * self.MARGEM_FRAC)

    def alocar_em_bobina(self, bobina, linhas):
        """
        Consome as linhas uma a uma, enrolando por camadas radiais até esgotar comprimento
        ou atingir limites (peso, volume, DE).
        """
        linhas_nao_alocadas = []

        # política: maiores diâmetros primeiro, menor raio_min primeiro, mais pesadas primeiro
        linhas_ordenadas = sorted(
            linhas,
            key=lambda L: (-L.diametro, L.raio_minimo_m, -L.peso_ton)
        )

        r_inicial = bobina.diametro_interno / 2.0
        r_atual = r_inicial
        lado_inicio = 'esquerda'  # alterna por camada (vai-e-volta)

        for L in linhas_ordenadas:
            # validações globais (pelo comprimento total)
            if not self.validador.validar_peso_parcial(bobina, L, L.comprimento):
                linhas_nao_alocadas.append(L)
                continue
            if not self.validador.validar_volume_parcial(bobina, L, L.comprimento):
                linhas_nao_alocadas.append(L)
                continue

            d_real = L.diametro / 1000.0   # m
            passo  = self._passo_largura(d_real)
            if passo <= 0 or bobina.largura < (d_real * 0.5):
                linhas_nao_alocadas.append(L)
                continue

            # voltas possíveis na largura
            n_cap = int(bobina.largura // passo)
            if n_cap <= 0:
                linhas_nao_alocadas.append(L)
                continue

            rem = float(L.comprimento)

            while rem > 1e-9:
                # checa limite radial (DE) e raio mínimo p/ a próxima camada
                r_mid = r_atual + d_real / 2.0
                diametro_final = 2.0 * (r_atual + d_real)
                if diametro_final > bobina.diametro_externo:
                    break
                if r_mid < L.raio_minimo_m - 1e-12:
                    break

                C = self._circ(r_mid)          # circunferência desta camada
                cap_camada = n_cap * C         # comprimento máximo nesta camada
                if cap_camada <= 0:
                    break

                # limites por volume/peso (parciais)
                max_len_vol  = self.validador.max_comprimento_por_volume(bobina, L)
                max_len_peso = self.validador.max_comprimento_por_peso(bobina, L)

                len_possivel = min(rem, cap_camada, max_len_vol, max_len_peso)
                if len_possivel <= 1e-9:
                    break

                voltas_usadas = len_possivel / C
                largura_usada = min(voltas_usadas, n_cap) * passo

                # cria camada radial p/ este trecho
                diametro_base = 2.0 * r_atual
                camada = Camada(diametro_base=diametro_base, tipo='bobinagem')

                # posição "representativa" (informativa p/ relatório)
                x_repr = (-bobina.largura / 2.0 + passo / 2.0) if lado_inicio == 'esquerda' else (bobina.largura / 2.0 - passo / 2.0)
                y_repr = (r_atual - r_inicial)

                camada.adicionar_linha(
                    L,
                    pos_x=x_repr,
                    pos_y=y_repr,
                    ordem=self._next_seq(),
                    comprimento_alocado=len_possivel,
                    voltas_usadas=voltas_usadas,
                    voltas_capacidade=n_cap,
                    passo=passo,
                    lado=lado_inicio
                )

                # acumula peso/volume parciais desta camada
                bobina.adicionar_camada(camada)

                # atualiza
                rem -= len_possivel
                r_atual += d_real
                lado_inicio = 'direita' if lado_inicio == 'esquerda' else 'esquerda'

            if rem > 1e-6:
                # sobrou comprimento desta linha: sinaliza como não totalmente alocada
                linhas_nao_alocadas.append(L)

        return bobina, linhas_nao_alocadas
