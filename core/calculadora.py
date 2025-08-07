import math

class CalculadoraHexagonal:
    """Realiza cálculos para empacotamento hexagonal otimizado."""
    
    @staticmethod
    def calcular_posicao_hexagonal(indice_linha, diametro_linha_m, num_camada):
        """
        Calcula a posição (x,y) no padrão hexagonal verdadeiro
        - Camadas ímpares: linhas alinhadas
        - Camadas pares: linhas deslocadas para encaixe nos vãos
        """
        # Padrão de deslocamento horizontal
        if num_camada % 2 == 0:  # Camada par
            pos_x = indice_linha * diametro_linha_m
        else:  # Camada ímpar
            pos_x = (indice_linha + 0.5) * diametro_linha_m
        
        # Cálculo vertical (triângulo equilátero)
        pos_y = (num_camada - 1) * (diametro_linha_m * math.sqrt(3) / 2)
        
        return pos_x, pos_y

    @staticmethod
    def calcular_raio_efetivo(pos_x, pos_y):
        """Calcula o raio efetivo como distância do centro da bobina"""
        return math.sqrt(pos_x**2 + pos_y**2)

    @staticmethod
    def verificar_colisao(posicao, diametro_linha_m, bobina, camada_atual=None):
        """
        Verifica colisões com outras linhas considerando:
        - Margem de segurança de 5% do diâmetro
        - Todas as camadas próximas
        """
        margem_seguranca = diametro_linha_m * 0.05
        raio_linha = diametro_linha_m / 2 + margem_seguranca
        
        for camada in bobina.camadas:
            # Ignora camadas muito distantes
            if camada_atual and abs(camada.diametro_base - camada_atual.diametro_base) > 3 * diametro_linha_m:
                continue
                
            for linha in camada.linhas:
                # Distância euclidiana entre centros
                distancia = math.sqrt(
                    (posicao[0] - linha['posicao'][0])**2 +
                    (posicao[1] - linha['posicao'][1])**2
                )
                
                # Raio da linha existente + margem
                raio_existente = linha['objeto'].diametro_efetivo / 2000 + margem_seguranca
                
                # Verifica sobreposição
                if distancia < (raio_linha + raio_existente):
                    return True
        return False