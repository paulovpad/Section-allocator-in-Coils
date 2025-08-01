class Bobina:
    """Representa uma bobina para armazenamento de linhas."""
    
    def __init__(self, diametro_externo, diametro_interno, largura, peso_maximo_ton, fator_empacotamento=0.85):
        self.diametro_externo = diametro_externo
        self.diametro_interno = diametro_interno
        self.largura = largura
        self.peso_maximo_ton = peso_maximo_ton
        self.fator_empacotamento = fator_empacotamento
        self.camadas = []
        self.peso_atual_ton = 0.0
    
    def adicionar_camada(self, camada):
        """Adiciona uma nova camada à bobina."""
        self.camadas.append(camada)
        self.peso_atual_ton += sum(linha['objeto'].peso_ton for linha in camada.linhas)  # Acesse o objeto Linha
 
    @property
    def capacidade_disponivel(self):
        """Retorna o peso ainda disponível na bobina."""
        return self.peso_maximo_ton - self.peso_atual_ton