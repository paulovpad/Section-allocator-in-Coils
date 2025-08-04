import sys
from pathlib import Path
from services.leitor_excel import LeitorExcel

def mostrar_erro(mensagem):
    """Exibe mensagens de erro formatadas"""
    print(f"\n⛔ ERRO: {mensagem}")
    print("Verifique:")
    print("1. Se o arquivo Excel existe no local especificado")
    print("2. Se as abas 'Bobinas' e 'Linhas' estão corretas")
    print("3. Se os nomes das colunas correspondem ao esperado\n")

def carregar_dados(caminho_planilha):
    """Carrega e valida todos os dados da planilha"""
    try:
        print(f"\n📊 Carregando dados de: {Path(caminho_planilha).name}")
        
        # Verificar se o arquivo existe
        if not Path(caminho_planilha).exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {caminho_planilha}")
        
        # Carregar dados
        bobinas = LeitorExcel.ler_bobinas(caminho_planilha)
        linhas = LeitorExcel.ler_linhas(caminho_planilha)
        
        # Validações básicas
        if not bobinas:
            raise ValueError("Nenhuma bobina encontrada na planilha")
        if not linhas:
            raise ValueError("Nenhuma linha encontrada na planilha")
        
        print(f"✅ {len(bobinas)} bobinas carregadas")
        print(f"✅ {len(linhas)} linhas carregadas")
        
        return bobinas, linhas
        
    except Exception as e:
        mostrar_erro(str(e))
        sys.exit(1)

def processar_alocacao(bobinas, linhas):
    """Simula o processamento da alocação"""
    print("\n⚙️ Processando alocação...")
    
    resultados = []
    for linha in linhas:
        for bobina in bobinas:
            # Verificação de diâmetro
            if linha['Diâmetro (m)'] > bobina['Diâmetro Interno (m)']:
                continue
                
            # Verificação de peso (simplificada)
            peso_total = linha['Comprimento Necessário (m)'] * linha['Peso por Metro (kg/m)']
            if 'Peso Máximo (kg)' in bobina and peso_total > bobina['Peso Máximo (kg)']:
                continue
                
            # Verificação de raio mínimo (se existir nos dados)
            if 'Raio Mínimo (m)' in linha and 'Diâmetro Externo (m)' in bobina:
                raio_bobina = bobina['Diâmetro Externo (m)'] / 2
                if linha['Raio Mínimo (m)'] > raio_bobina:
                    continue
            
            # Se passou em todas as verificações
            resultados.append({
                'Linha ID': linha['ID'],
                'Bobina ID': bobina['ID'],
                'Comprimento Alocado': linha['Comprimento Necessário (m)']
            })
            break
    
    return resultados

def main():
    print("\n=== SISTEMA DE ALOCAÇÃO DE LINHAS EM BOBINAS ===")
    
    # Configuração do caminho - ajuste conforme necessário
    caminho_planilha = r'C:\Users\paulo.andrade\Desktop\dados.xlsx'
    
    try:
        # Carregar dados
        bobinas, linhas = carregar_dados(caminho_planilha)
        
        # Processar alocação
        resultados = processar_alocacao(bobinas, linhas)
        
        # Exibir resultados
        print("\n📝 RESULTADOS DA ALOCAÇÃO:")
        if not resultados:
            print("Nenhuma alocação foi possível com os critérios atuais")
        else:
            for i, res in enumerate(resultados, 1):
                print(f"{i}. Linha {res['Linha ID']} → Bobina {res['Bobina ID']} "
                      f"(Alocado: {res['Comprimento Alocado']}m)")
    
    except KeyboardInterrupt:
        print("\nOperação cancelada pelo usuário")
    except Exception as e:
        mostrar_erro(f"Erro inesperado: {str(e)}")

if __name__ == "__main__":
    main()