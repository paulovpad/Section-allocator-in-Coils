import math

class CalculadoraHexagonal:
    """Realiza cálculos geométricos para empacotamento hexagonal."""
    
    @staticmethod
    def calcular_posicao_hexagonal(linha_atual, diametro_linha_m):
        """Calcula a próxima posição no padrão hexagonal."""
        offset_x = diametro_linha_m if linha_atual % 2 == 1 else diametro_linha_m/2
        offset_y = diametro_linha_m * math.sqrt(3)/2
        return offset_x, offset_y
    
    @staticmethod
    def calcular_raio_atual(bobina, camada, pos_y, diametro_linha_m):
        """Calcula o raio atual considerando a posição vertical."""
        return (camada.diametro_base + pos_y + diametro_linha_m/2) / 2
    
    @staticmethod
    def verificar_colisao(posicao, diametro_linha_m, camada):
        """Verifica se há colisão com outras linhas."""
        for linha in camada.linhas:
            distancia = math.sqrt(
                (posicao[0] - linha['posicao'][0])**2 +
                (posicao[1] - linha['posicao'][1])**2
            )
            if distancia < (diametro_linha_m + linha['objeto'].diametro_efetivo/1000)/2:
                return True
        return False