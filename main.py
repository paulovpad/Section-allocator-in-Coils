# main.py (raiz)
import sys

from core.alocador import AlocadorBobinas
from services.leitor_excel import LeitorExcel
from services import Relatorio
from models import Bobina, Linha

CAMINHO_EXCEL_PADRAO = r"C:\Users\paulo.andrade\Desktop\dados.xlsx"

def carregar_dados_excel(caminho: str):
    """Carrega bobinas e linhas usando os cabeçalhos das imagens enviadas."""
    bobinas_raw = LeitorExcel.ler_bobinas(caminho)
    linhas_raw  = LeitorExcel.ler_linhas(caminho)

    # ----- Bobinas (ID, Diâmetro Externo (m), Diâmetro Interno (m), Comprimento (m), Peso Máximo (kg))
    bobinas = []
    for b in bobinas_raw:
        try:
            de = float(b['Diâmetro Externo (m)'])
            di = float(b['Diâmetro Interno (m)'])
            largura = float(b['Comprimento (m)'])     # usamos "Comprimento" como largura da bobina
            peso_max_ton = float(b['Peso Máximo (kg)']) / 1000.0  # kg -> ton
        except KeyError as e:
            raise KeyError(f"Campo de bobina ausente no Excel: {e}")

        bobinas.append(Bobina(de, di, largura, peso_max_ton, 0.85))

    # ----- Linhas (ID, Diâmetro (m), Comprimento Necessário (m), Peso por Metro (kg/m), Raio Mínimo (m))
    linhas = []
    for l in linhas_raw:
        try:
            codigo = str(l['ID']).strip()
            diametro_mm = float(l['Diâmetro (m)']) * 1000.0          # m -> mm (models.Linha espera mm)
            comp_m = float(l['Comprimento Necessário (m)'])
            peso_um = float(l['Peso por Metro (kg/m)'])
            raio_min = float(l['Raio Mínimo (m)'])
        except KeyError as e:
            raise KeyError(f"Campo de linha ausente no Excel: {e}")

        linhas.append(Linha(codigo, diametro_mm, comp_m, peso_um, raio_min))

    return bobinas, linhas

def alocar_em_bobina(bobina, linhas, alocador: AlocadorBobinas):
    """Preenche camadas a partir da lateral, com padrão colmeia e validações."""
    linhas_nao_alocadas = []

    # Tenta primeiro as linhas mais críticas
    linhas_ordenadas = sorted(
        linhas,
        key=lambda L: (-L.diametro_efetivo, L.raio_minimo_m, -L.peso_ton)
    )

    for linha in linhas_ordenadas:
        if not alocador.validador.validar_peso(bobina, linha):
            linhas_nao_alocadas.append(linha)
            continue

        alocada = False
        for camada in bobina.camadas:
            if alocador._tentar_adicionar_linha_na_camada(linha, camada, bobina):
                alocada = True
                break

        if not alocada:
            if not alocador._tentar_criar_nova_camada(linha, bobina):
                linhas_nao_alocadas.append(linha)

    return bobina, linhas_nao_alocadas

def main():
    print("=== SISTEMA DE ALOCAÇÃO DE LINHAS EM BOBINAS (colmeia, lateral->centro) ===")
    try:
        bobinas, linhas = carregar_dados_excel(CAMINHO_EXCEL_PADRAO)
        if not bobinas or not linhas:
            print(f"Nenhuma bobina ou linha encontrada em: {CAMINHO_EXCEL_PADRAO}")
            sys.exit(1)

        print(f"\n✅ {len(bobinas)} bobina(s) carregada(s)")
        print(f"✅ {len(linhas)} linha(s) carregada(s)")

        alocador = AlocadorBobinas()
        bobinas_utilizadas = []
        linhas_restantes = linhas[:]
        linhas_nao_em_qualquer = []

        for bobina in bobinas:
            if not linhas_restantes:
                break
            bobina, nao = alocar_em_bobina(bobina, linhas_restantes, alocador)
            bobinas_utilizadas.append(bobina)

            ids_alocados = {item['objeto'].codigo for camada in bobina.camadas for item in camada.linhas}
            linhas_restantes = [L for L in linhas_restantes if L.codigo not in ids_alocados]
            linhas_nao_em_qualquer.extend(nao)

        linhas_nao_em_qualquer.extend(linhas_restantes)

        resultado = {
            "bobinas_utilizadas": bobinas_utilizadas,
            "linhas_nao_alocadas": linhas_nao_em_qualquer
        }

        Relatorio().gerar(resultado)

    except Exception as e:
        print(f"\n⛔ ERRO ao processar '{CAMINHO_EXCEL_PADRAO}': {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
