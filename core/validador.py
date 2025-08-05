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
        return abs(pos_x) + diametro_linha_m/2 <= bobina.largura/2

    @staticmethod
    def validar_espaco_vertical(bobina, camada, diametro_linha_m):
        altura_total = sum(c.altura_camada for c in bobina.camadas) + diametro_linha_m
        return (bobina.diametro_externo - bobina.diametro_interno)/2 >= altura_total