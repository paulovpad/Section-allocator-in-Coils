# models/bobina.py
import math

class Bobina:
    """Representa uma bobina para armazenamento de linhas (bobinagem real)."""
    
    def __init__(self, diametro_externo, diametro_interno, largura, peso_maximo_ton, fator_empacotamento=0.85):
        self.diametro_externo = diametro_externo
        self.diametro_interno = diametro_interno
        self.largura = largura
        self.peso_maximo_ton = peso_maximo_ton
        self.fator_empacotamento = fator_empacotamento
        self.camadas = []
        self.peso_atual_ton = 0.0
        self.volume_usado_m3 = 0.0

    def adicionar_camada(self, camada):
        """Adiciona a camada e acumula peso/volume PARCIAIS das alocações contidas nela."""
        self.camadas.append(camada)
        for reg in camada.linhas:
            L = reg['objeto']
            comp = reg.get('comprimento_alocado', None)
            if comp is None:
                comp = L.comprimento  # retrocompat
            # peso parcial (ton)
            self.peso_atual_ton += (L.peso_por_metro_kg * comp) * 0.001
            # volume parcial (m³)
            d_m = L.diametro / 1000.0
            self.volume_usado_m3 += math.pi * (d_m/2.0)**2 * comp
 
    @property
    def capacidade_disponivel(self):
        """Peso ainda disponível (ton)."""
        return self.peso_maximo_ton - self.peso_atual_ton

    @property
    def volume_total_m3(self):
        """Volume geométrico do anel da bobina (m³)."""
        return (math.pi/4.0) * (self.diametro_externo**2 - self.diametro_interno**2) * self.largura

    @property
    def volume_cap_m3(self):
        """Capacidade efetiva de volume (m³), com fator."""
        return self.volume_total_m3 * self.fator_empacotamento
