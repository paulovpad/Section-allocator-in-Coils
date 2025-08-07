from models import Bobina, Camada
from core.calculadora import CalculadoraHexagonal
from core.validador import ValidadorAlocacao
import math

class AlocadorBobinas:
    """Gerencia a alocação de linhas em bobinas com empacotamento hexagonal."""

    def __init__(self):
        self.calculadora = CalculadoraHexagonal()
        self.validador = ValidadorAlocacao()

    def _tentar_adicionar_linha_na_camada(self, linha, camada, bobina):
        """Tenta adicionar uma linha em uma camada existente usando padrão hexagonal"""
        diametro_linha_m = linha.diametro_efetivo / 1000
        num_camada = len(bobina.camadas)  # Índice da camada atual
        
        # Tenta até 100 posições na camada
        for tentativa in range(100):
            # Calcula posição hexagonal
            pos_x, pos_y = self.calculadora.calcular_posicao_hexagonal(
                tentativa, 
                diametro_linha_m,
                num_camada
            )
            
            # Centraliza na largura da bobina
            pos_x -= (tentativa * diametro_linha_m) / 2
            
            # Validações físicas
            if not self.validador.validar_largura(pos_x, diametro_linha_m, bobina):
                continue
                
            if self.calculadora.verificar_colisao((pos_x, pos_y), diametro_linha_m, bobina, camada):
                continue
                
            raio_atual = self.calculadora.calcular_raio_efetivo(pos_x, pos_y)
            if not self.validador.validar_raio_minimo(raio_atual, linha):
                continue
                
            # Adiciona se passar em todas as validações
            camada.adicionar_linha(linha, pos_x, pos_y)
            return True
            
        return False

    def _tentar_criar_nova_camada(self, linha, bobina):
        """Cria uma nova camada com posicionamento hexagonal"""
        diametro_linha_m = linha.diametro_efetivo / 1000
        altura_acumulada = sum(c.altura_camada for c in bobina.camadas)
        
        # Altura da nova camada (padrão hexagonal)
        altura_camada = (math.sqrt(3) / 2) * diametro_linha_m
        pos_y = altura_acumulada + altura_camada
        
        # Verificação de espaço vertical
        diametro_final = bobina.diametro_interno + 2 * (altura_acumulada + diametro_linha_m)
        if diametro_final > bobina.diametro_externo:
            return False

        # Posição inicial (centralizada)
        pos_x = 0
        
        # Cria e adiciona camada
        nova_camada = Camada(
            diametro_base = bobina.diametro_interno + 2 * altura_acumulada,
            tipo = 'hexagonal'
        )
        nova_camada.adicionar_linha(linha, pos_x, pos_y)
        bobina.adicionar_camada(nova_camada)
        return True

    # ... (restante do código permanece igual)