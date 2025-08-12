# models/camada.py
class Camada:
    """Representa uma camada (radial) de bobinagem."""
    
    def __init__(self, diametro_base, tipo='bobinagem'):
        self.diametro_base = diametro_base
        self.linhas = []
        self.altura_camada = 0
        self.largura_ocupada = 0
        self.tipo = tipo
    
    def adicionar_linha(self, linha, pos_x, pos_y, ordem=None,
                        comprimento_alocado=None, voltas_usadas=None,
                        voltas_capacidade=None, passo=None, lado=None):
        """
        Adiciona uma 'alocação' de linha nesta camada.
        - comprimento_alocado: comprimento (m) alocado desta linha nesta camada
        - voltas_usadas: número de voltas usadas nesta camada (float)
        - voltas_capacidade: capacidade de voltas da camada (int)
        - passo: passo horizontal entre voltas (m)
        - lado: 'esquerda' ou 'direita' (ponto de partida informativo)
        """
        self.linhas.append({
            'objeto': linha,
            'posicao': (pos_x, pos_y),
            'ordem': ordem,
            'comprimento_alocado': comprimento_alocado,
            'voltas_usadas': voltas_usadas,
            'voltas_capacidade': voltas_capacidade,
            'passo': passo,
            'lado': lado
        })
        self._atualizar_dimensoes(linha, pos_x, pos_y)
    
    def _atualizar_dimensoes(self, linha, pos_x, pos_y):
        """Mantém compatibilidade: atualiza métricas geométricas básicas."""
        diametro_m = linha.diametro / 1000.0  # usa diâmetro real
        self.altura_camada = max(self.altura_camada, pos_y + diametro_m/2.0)
        self.largura_ocupada = max(self.largura_ocupada, abs(pos_x) + diametro_m/2.0)
