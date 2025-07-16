import sys
import os

# Configura o caminho para importações
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.entrada_dados import EntradaDados
from core.alocador import AlocadorBobinas
from services.relatorio import Relatorio

def main():
    """Função principal do programa."""
    print("\n=== SISTEMA DE ALOCAÇÃO DE LINHAS EM BOBINAS ===")
    
    # Obter dados
    dados = EntradaDados()
    bobinas = dados.obter_bobinas()
    linhas = dados.obter_linhas()
    
    # Alocar
    alocador = AlocadorBobinas()
    resultado = alocador.alocar(linhas, bobinas)
    
    # Gerar relatório
    relatorio = Relatorio()
    relatorio.gerar(resultado)
    
    input("\nPressione Enter para sair...")

if __name__ == "__main__":
    main()