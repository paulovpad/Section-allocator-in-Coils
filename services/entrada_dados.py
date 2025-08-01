from models.bobina import Bobina
from models.linha import Linha

class EntradaDados:
    """Responsável por obter dados de entrada do usuário."""
    
    def obter_bobinas(self):
        """Obtém dados das bobinas interativamente."""
        bobinas = []
        print("\n=== CADASTRO DE BOBINAS ===")
        while True:
            bobinas.append(self._solicitar_dados_bobina())
            if input("Adicionar outra bobina? (s/n): ").lower() != 's':
                break
        return bobinas
    
    def obter_linhas(self):
        """Obtém dados das linhas interativamente."""
        linhas = []
        print("\n=== CADASTRO DE LINHAS ===")
        while True:
            linhas.append(self._solicitar_dados_linha())
            if input("Adicionar outra linha? (s/n): ").lower() != 's':
                break
        return linhas
    
    def _solicitar_dados_bobina(self):
        """Solicita dados de uma única bobina."""
        print("\n--- Dados da Bobina ---")
        while True:
            try:
                de = float(input("Diâmetro externo (m): "))
                di = float(input("Diâmetro interno (m): "))
                largura = float(input("Largura (m): "))
                peso_max_ton = float(input("Peso máximo (ton): "))
                
                fator_input = input("Fator de empacotamento (0.0 a 1.0) [Padrão=0.85]: ").strip()
                fator_emp = float(fator_input) if fator_input else 0.85
                
                if de <= di:
                    print("Erro: Diâmetro externo deve ser maior que o interno!")
                    continue
                if not 0.0 <= fator_emp <= 1.0:
                    print("Erro: Fator deve estar entre 0.0 e 1.0!")
                    continue
                
                return Bobina(de, di, largura, peso_max_ton, fator_emp)
            except ValueError:
                print("Erro: Insira um número válido!")
    
    def _solicitar_dados_linha(self):
        """Solicita dados de uma única linha."""
        while True:
            try:
                print("\n--- Dados do Flexível ---")
                codigo = input("Código de identificação: ").strip()
                diametro = float(input("Diâmetro (mm): "))
                comprimento = float(input("Comprimento (m): "))
                peso_metro_kg = float(input("Peso por metro (kg/m): "))
                raio_min = float(input("Raio mínimo de curvatura (m): "))
                
                if diametro <= 0 or comprimento <= 0 or peso_metro_kg <= 0 or raio_min <= 0:
                    print("Erro: Valores devem ser positivos!")
                    continue
                
                return Linha(codigo, diametro, comprimento, peso_metro_kg, raio_min)
            except ValueError:
                print("Erro: Insira um número válido!")