import math

class CalculadoraHexagonal:
    """Realiza cálculos para empacotamento hexagonal otimizado."""

    @staticmethod
    def calcular_posicao_hexagonal(linha_atual, diametro_linha_m):
        """
        Calcula a posição (x,y) no padrão hexagonal, partindo da origem (0,0).
        Formato de colmeia: linhas ímpares são deslocadas por metade do diâmetro.
        """
        pos_x = (linha_atual // 2) * diametro_linha_m
        if linha_atual % 2 != 0:
            pos_x -= diametro_linha_m / 2
        pos_y = (linha_atual % 2) * (diametro_linha_m * math.sqrt(3)/2)
        return pos_x, pos_y

    @staticmethod
    def calcular_raio_atual(bobina, camada, pos_y, diametro_linha_m):
        """Calcula o raio efetivo da bobina na posição y atual."""
        return (camada.diametro_base + pos_y + diametro_linha_m/2) / 2

    @staticmethod
    def verificar_colisao(posicao, diametro_linha_m, camada):
        """Verifica colisões com outras linhas na camada."""
        for linha in camada.linhas:
            distancia = math.sqrt(
                (posicao[0] - linha['posicao'][0])**2 +
                (posicao[1] - linha['posicao'][1])**2
            )
            if distancia < (diametro_linha_m + linha['objeto'].diametro_efetivo/1000)/2:
                return True
        return False