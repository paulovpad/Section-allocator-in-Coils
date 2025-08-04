from services.leitor_excel import LeitorExcel
import sys

def mostrar_camadas(bobina, camadas):
    """Exibe a alocação por camadas de forma visual"""
    print("\n📊 DISPOSIÇÃO DAS CAMADAS NA BOBINA:")
    print(f"Diâmetro Interno: {bobina['Diâmetro Interno (m)']}m")
    print(f"Diâmetro Externo: {bobina['Diâmetro Externo (m)']}m\n")
    
    print(f"{'Camada':<7} | {'Linha':<6} | {'Diâmetro':<9} | {'Raio (m)':<12} | {'Comprimento':<12} | {'Peso (kg)':<10}")
    print("-"*80)
    
    for camada in camadas:
        peso = camada['Comprimento'] * next(
            linha['Peso por Metro (kg/m)'] 
            for linha in linhas_alocadas 
            if linha['ID'] == camada['Linha ID']
        )
        print(f"{camada['Camada']:<7} | {camada['Linha ID']:<6} | "
              f"{camada['Diâmetro']:>8.3f}m | "
              f"{camada['Raio Interno']:.3f}-{camada['Raio Externo']:.3f}m | "
              f"{camada['Comprimento']:>10}m | "
              f"{peso:>8.1f}")

def main():
    print("=== SISTEMA DE ALOCAÇÃO DE LINHAS EM BOBINAS ===")
    
    try:
        # Carregar dados
        caminho = r'C:\Users\paulo.andrade\Desktop\dados.xlsx'
        bobinas = LeitorExcel.ler_bobinas(caminho)
        linhas = LeitorExcel.ler_linhas(caminho)
        
        print(f"\n✅ {len(bobinas)} bobina(s) carregada(s)")
        print(f"✅ {len(linhas)} linha(s) carregada(s)")
        
        # Seleciona a primeira bobina
        bobina = bobinas[0]
        global linhas_alocadas  # Para acesso na função mostrar_camadas
        linhas_alocadas = []
        
        print("\n🔍 ALOCANDO LINHAS POR DIÂMETRO (maiores primeiro):")
        for linha in sorted(linhas, key=lambda x: x['Diâmetro (m)'], reverse=True):
            if linha['Diâmetro (m)'] <= bobina['Diâmetro Interno (m)']:
                linhas_alocadas.append(linha)
                print(f"Linha {linha['ID']} (Ø{linha['Diâmetro (m)']}m) alocada")
        
        # Calcular e mostrar camadas
        camadas = LeitorExcel.calcular_camadas(bobina, linhas_alocadas)
        mostrar_camadas(bobina, camadas)
        
        # RESUMO DE ALOCAÇÃO (NOVO)
        if camadas:
            peso_total = sum(
                linha['Comprimento Necessário (m)'] * linha['Peso por Metro (kg/m)']
                for linha in linhas_alocadas
            )
            diametro_final = camadas[-1]['Raio Externo'] * 2
            
            print(f"\n⚖️ RESUMO DE ALOCAÇÃO:")
            print(f"• Peso total: {peso_total:.1f} kg (de {bobina['Peso Máximo (kg)']} kg disponíveis)")
            print(f"• Diâmetro final: {diametro_final:.2f}m (de {bobina['Diâmetro Externo (m)']}m disponível)")
            print(f"• Espaço utilizado: {diametro_final/bobina['Diâmetro Externo (m)']:.1%}")
        
    except Exception as e:
        print(f"\n⛔ ERRO: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()