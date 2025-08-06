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
    def calcular_raio_atual(camada, pos_y, diametro_linha_m):
        """
        Calcula CORRETAMENTE o raio efetivo no centro da linha.
        - camada.diametro_base: diâmetro da base da camada (em metros)
        - pos_y: altura vertical dentro da camada (em metros)
        - diametro_linha_m: diâmetro da linha (em metros)
        """
        # Converte diâmetro base para raio e soma as alturas
        raio_base = camada.diametro_base / 2
        return raio_base + pos_y + (diametro_linha_m / 2)

    @staticmethod
    def verificar_colisao(posicao, diametro_linha_m, bobina, camada_atual=None):
        """
        Verifica colisões com outras linhas em QUALQUER camada próxima.
        - camada_atual: a camada atual sendo preenchida (None para nova camada)
        - margem de segurança: 5% do diâmetro para evitar contato físico
        """
        margem_seguranca = diametro_linha_m * 0.05
        raio_linha = diametro_linha_m / 2 + margem_seguranca
        
        # Verifica todas as camadas próximas verticalmente
        for camada in bobina.camadas:
            # Verifica se é uma camada relevante (próxima)
            if camada_atual and abs(camada.diametro_base - camada_atual.diametro_base) > 3 * diametro_linha_m:
                continue
                
            for linha in camada.linhas:
                # Calcula distância entre centros
                distancia = math.sqrt(
                    (posicao[0] - linha['posicao'][0])**2 +
                    (posicao[1] - linha['posicao'][1])**2
                )
                
                # Raio da linha existente (com margem de segurança)
                raio_existente = linha['objeto'].diametro_efetivo / 2000 + margem_seguranca
                
                # Verifica se há sobreposição
                if distancia < (raio_linha + raio_existente):
                    return True
        return False