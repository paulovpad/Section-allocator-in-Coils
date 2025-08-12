import math

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
        # ---- controle de volume ----
        self.volume_usado_m3 = 0.0

    def adicionar_camada(self, camada):
        """Adiciona uma nova camada à bobina e atualiza peso/volume pelos itens já presentes na camada."""
        self.camadas.append(camada)
        # peso da(s) linha(s) já na camada
        self.peso_atual_ton += sum(linha['objeto'].peso_ton for linha in camada.linhas)
        # volume da(s) linha(s) já na camada
        self.volume_usado_m3 += sum(self._volume_linha_m3(linha['objeto']) for linha in camada.linhas)

    @property
    def capacidade_disponivel(self):
        """Retorna o peso ainda disponível na bobina (ton)."""
        return self.peso_maximo_ton - self.peso_atual_ton

    @property
    def volume_total_m3(self):
        """Volume geométrico do anel da bobina (m³)."""
        return (math.pi/4.0) * (self.diametro_externo**2 - self.diametro_interno**2) * self.largura

    @property
    def volume_cap_m3(self):
        """Capacidade efetiva de volume (m³), aplicando fator de empacotamento."""
        return self.volume_total_m3 * self.fator_empacotamento

    @staticmethod
    def _volume_linha_m3(linha):
        """Volume da linha como cilindro (m³) usando diâmetro físico (mm -> m)."""
        d_m = linha.diametro / 1000.0
        return math.pi * (d_m/2.0)**2 * linha.comprimento

    def adicionar_volume_linha(self, linha):
        """Acumula volume usado ao adicionar uma linha numa camada já existente."""
        v = self._volume_linha_m3(linha)
        self.volume_usado_m3 += v
        return v
