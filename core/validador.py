import math

class ValidadorAlocacao:
    """Valida restrições físicas da alocação."""

    @staticmethod
    def validar_peso(bobina, linha):
        return bobina.capacidade_disponivel >= linha.peso_ton

    @staticmethod
    def validar_raio_minimo(raio_atual, linha):
        return raio_atual >= linha.raio_minimo_m

    @staticmethod
    def validar_largura(pos_x, diametro_linha_m, bobina):
        """
        Garante que o círculo caiba na largura útil da bobina.
        Usa uma pequena folga (5% do diâmetro) para não encostar na borda.
        """
        margem = diametro_linha_m * 0.05
        largura_util = max(0.0, bobina.largura - margem)
        return abs(pos_x) + diametro_linha_m / 2.0 <= largura_util / 2.0

    @staticmethod
    def validar_espaco_vertical(bobina, camada, diametro_linha_m):
        """
        Mantida por compatibilidade. O controle principal vertical está
        em _tentar_criar_nova_camada (via DI/DE).
        """
        altura_total = sum(c.altura_camada for c in bobina.camadas) + diametro_linha_m
        return (bobina.diametro_externo - bobina.diametro_interno) / 2.0 >= altura_total

    @staticmethod
    def validar_volume(bobina, linha):
        """
        Bloqueia se o volume acumulado da bobina + volume da nova linha exceder
        a capacidade efetiva (volume do anel × fator de empacotamento).
        Usa diâmetro físico (mm -> m), não o 'efetivo' de empacotamento.
        """
        d_m = linha.diametro / 1000.0
        v_linha = math.pi * (d_m/2.0)**2 * linha.comprimento
        v_cap = (math.pi/4.0) * (bobina.diametro_externo**2 - bobina.diametro_interno**2) * bobina.largura * getattr(bobina, "fator_empacotamento", 1.0)
        v_usado = getattr(bobina, "volume_usado_m3", 0.0)
        return (v_usado + v_linha) <= v_cap + 1e-12
