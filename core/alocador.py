from models import Bobina, Linha, Camada
from core.calculadora import CalculadoraHexagonal
from core.validador import ValidadorAlocacao

class AlocadorBobinas:
    """Classe principal que orquestra o processo de alocação."""
    
    def __init__(self, estrategia='hexagonal'):
        self.estrategia = estrategia
        self.calculadora = CalculadoraHexagonal()
        self.validador = ValidadorAlocacao()
    
    def alocar(self, linhas, bobinas):
        """Método principal para alocar linhas em bobinas."""
        linhas_ordenadas = self._ordenar_linhas(linhas)
        bobinas_ordenadas = self._ordenar_bobinas(bobinas)
        linhas_nao_alocadas = []
        
        for linha in linhas_ordenadas:
            if not self._alocar_linha(linha, bobinas_ordenadas):
                linhas_nao_alocadas.append(linha)
        
        return {
            'bobinas_utilizadas': [b for b in bobinas_ordenadas if b.camadas],
            'linhas_nao_alocadas': linhas_nao_alocadas
        }
    
    def _ordenar_linhas(self, linhas):
        """Ordena linhas por prioridade de alocação."""
        return sorted(linhas, key=lambda x: (
            x.flexibilidade, 
            -x.diametro,
            x.raio_minimo_m / (x.diametro / 1000)
        ))  # Corrigido o fechamento de parênteses
    
    def _ordenar_bobinas(self, bobinas):
        """Ordena bobinas por capacidade."""
        return sorted(bobinas, key=lambda b: (
            (b.diametro_externo - b.diametro_interno) * b.largura * b.peso_maximo_ton
        ), reverse=True)
    
    def _alocar_linha(self, linha, bobinas):
        """Tenta alocar uma linha em qualquer bobina disponível."""
        for bobina in bobinas:
            if self.validador.validar_peso(bobina, linha):
                # Tenta adicionar a uma camada existente
                for camada in bobina.camadas:
                    if self._tentar_adicionar_linha_na_camada(linha, camada, bobina):
                        return True
                
                # Tenta criar nova camada
                if self._tentar_criar_nova_camada(linha, bobina):
                    return True
        return False
    
    def _tentar_adicionar_linha_na_camada(self, linha, camada, bobina):
        """Tenta adicionar linha em uma camada existente."""
        diametro_linha_m = linha.diametro_efetivo / 1000
        pos_y = camada.altura_camada - diametro_linha_m/2
        
        # Tenta encontrar posição X disponível
        for linha_atual in range(100):  # Limite razoável de tentativas
            offset_x, offset_y = self.calculadora.calcular_posicao_hexagonal(linha_atual, diametro_linha_m)
            pos_x = offset_x - bobina.largura/2  # Centraliza na bobina
            
            # Verificação dividida em duas linhas para maior clareza
            valido_largura = self.validador.validar_largura(pos_x, diametro_linha_m, bobina)
            sem_colisao = not self.calculadora.verificar_colisao((pos_x, pos_y), diametro_linha_m, camada)
            
            if valido_largura and sem_colisao:
                raio_atual = self.calculadora.calcular_raio_atual(bobina, camada, pos_y, diametro_linha_m)
                if self.validador.validar_raio_minimo(raio_atual, linha):
                    camada.adicionar_linha(linha, pos_x, pos_y)
                    return True
        return False
    
    def _tentar_criar_nova_camada(self, linha, bobina):
        """Tenta criar nova camada para a linha."""
        diametro_linha_m = linha.diametro_efetivo / 1000
        
        # Calcula diâmetro base para nova camada
        if bobina.camadas:
            diametro_base = bobina.camadas[-1].diametro_base + 2*bobina.camadas[-1].altura_camada
        else:
            diametro_base = bobina.diametro_interno + diametro_linha_m
        
        # Verifica se cabe na bobina
        if diametro_base + 2*diametro_linha_m > bobina.diametro_externo:
            return False
        
        # Cria nova camada e tenta adicionar a linha
        nova_camada = Camada(diametro_base)
        pos_x = 0  # Posição central
        pos_y = diametro_linha_m/2
        
        raio_atual = self.calculadora.calcular_raio_atual(bobina, nova_camada, pos_y, diametro_linha_m)
        valido_largura = self.validador.validar_largura(pos_x, diametro_linha_m, bobina)
        valido_raio = self.validador.validar_raio_minimo(raio_atual, linha)
        
        if valido_largura and valido_raio:
            nova_camada.adicionar_linha(linha, pos_x, pos_y)
            bobina.adicionar_camada(nova_camada)
            return True
        
        return False