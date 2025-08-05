from models import Bobina, Camada
from core.calculadora import CalculadoraHexagonal
from core.validador import ValidadorAlocacao

class AlocadorBobinas:
    """Gerencia a alocação de linhas em bobinas com empacotamento hexagonal."""

    def __init__(self):
        self.calculadora = CalculadoraHexagonal()
        self.validador = ValidadorAlocacao()

    def _tentar_adicionar_linha_na_camada(self, linha, camada, bobina):
        """Tenta adicionar uma linha em uma camada existente."""
        diametro_linha_m = linha.diametro_efetivo / 1000
        max_tentativas = int(bobina.largura / diametro_linha_m) * 2  # Limite baseado na largura

        for linha_atual in range(max_tentativas):
            # Calcula posição hexagonal pura
            pos_x, pos_y = self.calculadora.calcular_posicao_hexagonal(linha_atual, diametro_linha_m)
            
            # Ajusta para a borda da bobina (alterna esquerda/direita por camada)
            lado_inicial = -1 if len(bobina.camadas) % 2 == 0 else 1
            pos_x += lado_inicial * (bobina.largura/2 - diametro_linha_m/2)
            
            # Verifica validações
            if (self.validador.validar_largura(pos_x, diametro_linha_m, bobina) and
                not self.calculadora.verificar_colisao((pos_x, pos_y), diametro_linha_m, camada)):
                raio_atual = self.calculadora.calcular_raio_atual(bobina, camada, pos_y, diametro_linha_m)
                if self.validador.validar_raio_minimo(raio_atual, linha):
                    camada.adicionar_linha(linha, pos_x, pos_y)
                    return True
        return False

    def _tentar_criar_nova_camada(self, linha, bobina):
        """Cria uma nova camada começando na borda da bobina."""
        diametro_linha_m = linha.diametro_efetivo / 1000
        
        # Alterna o lado inicial (esquerda/direita) a cada camada
        lado_inicial = -1 if len(bobina.camadas) % 2 == 0 else 1
        pos_x = lado_inicial * (bobina.largura/2 - diametro_linha_m/2)
        pos_y = diametro_linha_m/2

        # Calcula diâmetro base da nova camada
        if bobina.camadas:
            diametro_base = bobina.camadas[-1].diametro_base + 2 * bobina.camadas[-1].altura_camada
        else:
            diametro_base = bobina.diametro_interno + diametro_linha_m

        # Verifica se cabe na bobina
        if (diametro_base + 2 * diametro_linha_m) > bobina.diametro_externo:
            return False

        # Cria e adiciona a camada
        nova_camada = Camada(diametro_base)
        nova_camada.adicionar_linha(linha, pos_x, pos_y)
        bobina.adicionar_camada(nova_camada)
        return True

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
                # 1. Tenta apenas na ÚLTIMA camada (se existir)
                if bobina.camadas:
                    if self._tentar_adicionar_linha_na_camada(linha, bobina.camadas[-1], bobina):
                        return True
                
                # 2. Se falhou ou não há camadas, tenta nova camada
                if self._tentar_criar_nova_camada(linha, bobina):
                    return True
        return False