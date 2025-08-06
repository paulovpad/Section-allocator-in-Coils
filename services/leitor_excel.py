import pandas as pd
from pathlib import Path

class LeitorExcel:
    """Classe para leitura e processamento de dados de bobinas e linhas a partir de arquivos Excel."""

    @staticmethod
    def ler_bobinas(caminho_arquivo):
        """Lê dados de bobinas com tratamento robusto para colunas."""
        try:
            df = pd.read_excel(caminho_arquivo, sheet_name='Bobinas')
            
            mapeamento = {
                'ID': ['ID', 'Código'],
                'Diâmetro Externo (m)': ['Diâmetro Externo (m)', 'DE'],
                'Diâmetro Interno (m)': ['Diâmetro Interno (m)', 'DI'],
                'Largura (m)': ['Largura (m)', 'Largura'],
                'Peso Máximo (kg)': ['Peso Máximo (kg)', 'Peso Max']
            }
            
            colunas_renomear = {}
            for padrao, alternativas in mapeamento.items():
                for alternativa in alternativas:
                    if alternativa in df.columns:
                        colunas_renomear[alternativa] = padrao
                        break
            
            df = df.rename(columns=colunas_renomear)
            return df.to_dict('records')
            
        except Exception as e:
            raise Exception(f"Erro ao ler bobinas: {str(e)}")

    @staticmethod
    def ler_linhas(caminho_arquivo):
        """Lê dados de linhas com tratamento flexível para colunas."""
        try:
            df = pd.read_excel(caminho_arquivo, sheet_name='Linhas')
            
            mapeamento = {
                'ID': ['ID', 'Código'],
                'Diâmetro (mm)': ['Diâmetro (mm)', 'Diametro'],
                'Comprimento Necessário (m)': ['Comprimento Necessário (m)', 'Comp Necessario'],
                'Peso por Metro (kg/m)': ['Peso por Metro (kg/m)', 'Peso Unitario'],
                'Raio Mínimo (m)': ['Raio Mínimo (m)', 'Raio Min']
            }
            
            colunas_renomear = {}
            for padrao, alternativas in mapeamento.items():
                for alternativa in alternativas:
                    if alternativa in df.columns:
                        colunas_renomear[alternativa] = padrao
                        break
            
            df = df.rename(columns=colunas_renomear)
            
            # Conversão de mm para m
            if 'Diâmetro (mm)' in df.columns:
                df['Diâmetro (m)'] = df['Diâmetro (mm)'] / 1000
                df = df.drop(columns=['Diâmetro (mm)'])
            
            return df.to_dict('records')
            
        except Exception as e:
            raise Exception(f"Erro ao ler linhas: {str(e)}")

    @staticmethod
    def calcular_camadas(bobina, linhas_alocadas):
        """Calcula a disposição física das linhas na bobina com validação de espaço."""
        linhas_ordenadas = sorted(
            linhas_alocadas, 
            key=lambda x: x['Diâmetro (m)'], 
            reverse=True
        )
        
        camadas = []
        altura_acumulada = 0
        diametro_interno = bobina['Diâmetro Interno (m)']
        diametro_externo = bobina['Diâmetro Externo (m)']
        
        for i, linha in enumerate(linhas_ordenadas, 1):
            diam_linha = linha['Diâmetro (m)']
            
            # Verificação de espaço disponível
            diametro_final = diametro_interno + 2 * (altura_acumulada + diam_linha)
            if diametro_final > diametro_externo:
                print(f"⚠️ Linha {linha['ID']} não cabe - Diâmetro final seria {diametro_final:.3f}m (limite: {diametro_externo}m)")
                continue
                
            raio_interno = diametro_interno/2 + altura_acumulada
            raio_externo = raio_interno + diam_linha
            
            camada = {
                'Camada': i,
                'Linha ID': linha['ID'],
                'Diâmetro': diam_linha,
                'Raio Interno': raio_interno,
                'Raio Externo': raio_externo,
                'Comprimento': linha['Comprimento Necessário (m)'],
                'Peso por Metro (kg/m)': linha['Peso por Metro (kg/m)']
            }
            
            camadas.append(camada)
            altura_acumulada += diam_linha
        
        return camadas

    @staticmethod
    def calcular_resumo(bobina, camadas):
        """Calcula métricas de utilização da bobina."""
        if not camadas:
            return {
                'peso_total': 0,
                'diametro_final': bobina['Diâmetro Interno (m)'],
                'espaco_utilizado': 0
            }
        
        peso_total = sum(
            camada['Comprimento'] * camada['Peso por Metro (kg/m)']
            for camada in camadas
        )
        
        diametro_final = camadas[-1]['Raio Externo'] * 2
        espaco_utilizado = diametro_final / bobina['Diâmetro Externo (m)']
        
        return {
            'peso_total': peso_total,
            'diametro_final': diametro_final,
            'espaco_utilizado': espaco_utilizado
        }