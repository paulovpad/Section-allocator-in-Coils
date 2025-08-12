# core/validador.py
import math

class ValidadorAlocacao:
    """Valida restrições físicas da alocação (modelo bobinagem real)."""

    # -------- Peso --------
    @staticmethod
    def validar_peso_parcial(bobina, linha, comprimento_m):
        """Checa se dá pra adicionar 'comprimento_m' dessa linha no peso."""
        delta_ton = (linha.peso_por_metro_kg * comprimento_m) * 0.001
        return (bobina.peso_atual_ton + delta_ton) <= (bobina.peso_maximo_ton + 1e-12)

    def max_comprimento_por_peso(self, bobina, linha):
        """Comprimento máximo (m) que ainda cabe pelo limite de peso."""
        cap_ton = bobina.peso_maximo_ton - bobina.peso_atual_ton
        if cap_ton <= 0: return 0.0
        kg_por_m = linha.peso_por_metro_kg
        return (cap_ton * 1000.0) / max(1e-12, kg_por_m)

    # -------- Raio mínimo --------
    @staticmethod
    def validar_raio_minimo(raio_atual, linha):
        return raio_atual >= linha.raio_minimo_m

    # -------- Volume --------
    @staticmethod
    def validar_volume_parcial(bobina, linha, comprimento_m):
        """Checa se 'comprimento_m' da linha cabe no volume efetivo."""
        d_m = linha.diametro / 1000.0
        v = math.pi * (d_m/2.0)**2 * comprimento_m
        return (bobina.volume_usado_m3 + v) <= (bobina.volume_cap_m3 + 1e-12)

    def max_comprimento_por_volume(self, bobina, linha):
        """Comprimento máximo (m) que ainda cabe por volume."""
        cap = bobina.volume_cap_m3 - bobina.volume_usado_m3
        if cap <= 0: return 0.0
        d_m = linha.diametro / 1000.0
        area = math.pi * (d_m/2.0)**2
        return cap / max(1e-12, area)
