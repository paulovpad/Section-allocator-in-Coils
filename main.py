# main.py
import sys
from services.leitor_excel import LeitorExcel
from services import Relatorio
from models import Bobina, Linha
from core.alocador_bobinagem import AlocadorBobinagemReal  # novo

CAMINHO_EXCEL_PADRAO = r"C:\Users\paulo.andrade\Desktop\dados.xlsx"

def carregar_dados_excel(caminho: str):
    bobinas_raw = LeitorExcel.ler_bobinas(caminho)
    linhas_raw  = LeitorExcel.ler_linhas(caminho)

    # Bobinas: ID, Diâmetro Externo (m), Diâmetro Interno (m), Comprimento (m) -> largura, Peso Máximo (kg)
    bobinas = []
    for b in bobinas_raw:
        de = float(b['Diâmetro Externo (m)'])
        di = float(b['Diâmetro Interno (m)'])
        largura = float(b['Comprimento (m)'])  # usamos como largura da bobina
        peso_max_ton = float(b['Peso Máximo (kg)']) / 1000.0  # kg -> ton
        bobinas.append(Bobina(de, di, largura, peso_max_ton, 0.85))

    # Linhas: ID, Diâmetro (m), Comprimento Necessário (m), Peso por Metro (kg/m), Raio Mínimo (m)
    linhas = []
    for l in linhas_raw:
        codigo = str(l['ID']).strip()
        diametro_mm = float(l['Diâmetro (m)']) * 1000.0
        comp_m = float(l['Comprimento Necessário (m)'])
        peso_um = float(l['Peso por Metro (kg/m)'])
        raio_min = float(l['Raio Mínimo (m)'])
        linhas.append(Linha(codigo, diametro_mm, comp_m, peso_um, raio_min))

    return bobinas, linhas

def main():
    print("=== SISTEMA DE BOBINAGEM REAL (voltas por camada radial) ===")
    try:
        bobinas, linhas = carregar_dados_excel(CAMINHO_EXCEL_PADRAO)
        if not bobinas or not linhas:
            print(f"Nenhuma bobina ou linha encontrada em: {CAMINHO_EXCEL_PADRAO}")
            sys.exit(1)

        print(f"\n✅ {len(bobinas)} bobina(s) carregada(s)")
        print(f"✅ {len(linhas)} linha(s) carregada(s)")

        alocador = AlocadorBobinagemReal()
        bobinas_utilizadas = []
        linhas_nao = []

        for bobina in bobinas:
            bobina, nao = alocador.alocar_em_bobina(bobina, linhas)
            bobinas_utilizadas.append(bobina)
            linhas_nao.extend(nao)

        resultado = {
            "bobinas_utilizadas": bobinas_utilizadas,
            "linhas_nao_alocadas": linhas_nao
        }

        Relatorio().gerar(resultado)

    except Exception as e:
        print(f"\n⛔ ERRO ao processar '{CAMINHO_EXCEL_PADRAO}': {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
