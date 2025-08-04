import pandas as pd
from pathlib import Path

class LeitorExcel:
    @staticmethod
    def ler_bobinas(caminho_arquivo):
        """Versão com tratamento robusto para coluna de peso"""
        try:
            df = pd.read_excel(caminho_arquivo, sheet_name='Bobinas')
            
            # Mapeamento de colunas esperadas
            mapeamento = {
                'ID': ['ID', 'Código'],
                'Diâmetro Externo (m)': ['Diâmetro Externo (m)', 'DE'],
                'Diâmetro Interno (m)': ['Diâmetro Interno (m)', 'DI'],
                'Comprimento (m)': ['Comprimento (m)', 'Comp'],
                'Peso Máximo (kg)': ['Peso Máximo (kg)', 'Peso Max']
            }
            
            # Renomear colunas
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
        """Lê dados da aba 'Linhas' com tratamento flexível"""
        try:
            df = pd.read_excel(caminho_arquivo, sheet_name='Linhas')
            
            mapeamento = {
                'ID': ['ID', 'Código'],
                'Diâmetro (m)': ['Diâmetro (m)', 'Diametro'],
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
            return df.to_dict('records')
            
        except Exception as e:
            raise Exception(f"Erro ao ler linhas: {str(e)}")

    @staticmethod
    def calcular_camadas(bobina, linhas_alocadas):
        """Calcula a disposição física das linhas na bobina"""
        linhas_ordenadas = sorted(linhas_alocadas, 
                                key=lambda x: x['Diâmetro (m)'], 
                                reverse=True)
        
        camadas = []
        raio_atual = bobina['Diâmetro Interno (m)'] / 2
        
        for i, linha in enumerate(linhas_ordenadas, 1):
            camada = {
                'Camada': i,
                'Linha ID': linha['ID'],
                'Diâmetro': linha['Diâmetro (m)'],
                'Raio Interno': raio_atual,
                'Raio Externo': raio_atual + linha['Diâmetro (m)'],
                'Comprimento': linha['Comprimento Necessário (m)']
            }
            camadas.append(camada)
            raio_atual += linha['Diâmetro (m)']
        
        return camadas