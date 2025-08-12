import math

class CalculadoraHexagonal:
    """Cálculos auxiliares para empacotamento hexagonal."""

    # Margem relativa de colisão: 5% do diâmetro
    MARGEM_FRAC = 0.05

    @staticmethod
    def calcular_posicao_hexagonal(indice_linha, diametro_linha_m, num_camada):
        """
        Mantido por compatibilidade (não é usado diretamente no novo fluxo).
        - num_camada começa em 1
        - camadas ímpares: alinhadas (offset = 0)
        - camadas pares: deslocadas (offset = d/2)
        """
        if num_camada % 2 == 0:  # par -> deslocada
            pos_x = (indice_linha + 0.5) * diametro_linha_m
        else:  # ímpar -> alinhada
            pos_x = indice_linha * diametro_linha_m

        pos_y = (num_camada - 1) * (diametro_linha_m * math.sqrt(3.0) / 2.0)
        return pos_x, pos_y

    @staticmethod
    def calcular_raio_efetivo(pos_x, pos_y):
        """Raio efetivo (distância do centro)."""
        return math.sqrt(pos_x * pos_x + pos_y * pos_y)

    @classmethod
    def verificar_colisao(cls, posicao, diametro_linha_m, bobina, camada_atual=None):
        """
        Verifica colisão da posição proposta com linhas já existentes:
        - margem de segurança = MARGEM_FRAC * diâmetro
        - podas por caixa (AABB)
        - comparação por distância ao quadrado (sem sqrt)
        - ignora camadas muito distantes radialmente
        """
        margem = diametro_linha_m * cls.MARGEM_FRAC
        r_novo = diametro_linha_m / 2.0 + margem
        rx, ry = posicao

        for camada in bobina.camadas:
            # Se informado, ignore camadas muito distantes da camada atual
            if camada_atual and abs(camada.diametro_base - camada_atual.diametro_base) > 3.0 * diametro_linha_m:
                continue

            for reg in camada.linhas:
                px, py = reg['posicao']
                d_exist = reg['objeto'].diametro_efetivo / 1000.0
                r_exist = d_exist / 2.0 + d_exist * cls.MARGEM_FRAC

                sum_r = r_novo + r_exist
                dx = rx - px
                if abs(dx) > sum_r:
                    continue
                dy = ry - py
                if abs(dy) > sum_r:
                    continue

                if dx * dx + dy * dy < sum_r * sum_r:
                    return True
        return False
