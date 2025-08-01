class Linha:
    """Representa uma linha/cabo a ser armazenado na bobina."""
    
    FLEXIBILIDADE_FATORES = {
        1: 1.0, 2: 0.9, 3: 0.75, 4: 0.6, 5: 0.45, 6: 0.3, 7: 0.15
    }
    
    def __init__(self, codigo, diametro, comprimento, peso_por_metro_kg, raio_minimo_m):  # Adicione codigo aqui
        self.codigo = codigo  # Código único de identificação
        self.diametro = diametro  # em mm
        self.comprimento = comprimento  # em m
        self.peso_por_metro_kg = peso_por_metro_kg
        self.raio_minimo_m = raio_minimo_m
        self.flexibilidade = self._calcular_flexibilidade()
    
    @property
    def peso_ton(self):
        """Peso total da linha em toneladas."""
        return (self.peso_por_metro_kg * self.comprimento) * 0.001
    
    @property
    def diametro_efetivo(self):
        """Diâmetro ajustado pela flexibilidade."""
        return self.diametro * self.FLEXIBILIDADE_FATORES.get(self.flexibilidade, 1.0)
    
    def _calcular_flexibilidade(self):
        """Calcula o nível de flexibilidade com base no raio mínimo."""
        razao = self.raio_minimo_m / (self.diametro / 1000)
        if razao <= 1.5: return 7
        elif razao <= 2.5: return 6
        elif razao <= 4: return 5
        elif razao <= 6: return 4
        elif razao <= 8: return 3
        elif razao <= 12: return 2
        else: return 1