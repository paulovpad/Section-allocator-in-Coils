class Camada:
    """Representa uma camada de linhas na bobina."""
    
    def __init__(self, diametro_base):
        self.diametro_base = diametro_base
        self.linhas = []
        self.altura_camada = 0
        self.largura_ocupada = 0
    
    def adicionar_linha(self, linha, pos_x, pos_y):
        """Adiciona uma linha na posição especificada."""
        self.linhas.append({
            'objeto': linha,
            'posicao': (pos_x, pos_y)
        })
        self._atualizar_dimensoes(linha, pos_x, pos_y)
    
    def _atualizar_dimensoes(self, linha, pos_x, pos_y):
        """Atualiza altura e largura da camada."""
        diametro_m = linha.diametro_efetivo / 1000
        self.altura_camada = max(self.altura_camada, pos_y + diametro_m/2)
        self.largura_ocupada = max(self.largura_ocupada, abs(pos_x) + diametro_m/2)