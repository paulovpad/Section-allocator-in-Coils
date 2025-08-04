import pandas as pd
from pathlib import Path

class LeitorExcel:
    @staticmethod
    def ler_bobinas(caminho_arquivo):
        """
        Lê dados da aba 'Bobinas' com tratamento flexível para nomes de colunas
        Retorna: Lista de dicionários com os dados
        """
        try:
            # Primeiro verifica se o arquivo existe
            if not Path(caminho_arquivo).is_file():
                raise FileNotFoundError(f"Arquivo não encontrado: {caminho_arquivo}")

            # Tentar ler sem especificar colunas para descobrir os nomes reais
            df = pd.read_excel(caminho_arquivo, sheet_name='Bobinas')
            
            # Mapeamento de colunas esperadas e possíveis variações
            mapeamento = {
                'ID': ['ID', 'Código', 'Numero'],
                'Diâmetro Externo (m)': ['Diâmetro Externo (m)', 'DE (m)', 'Diametro Externo'],
                'Diâmetro Interno (m)': ['Diâmetro Interno (m)', 'DI (m)', 'Diametro Interno'],
                'Comprimento (m)': ['Comprimento (m)', 'Comp (m)', 'Metragem'],
                'Peso Máximo (kg)': ['Peso Máximo (kg)', 'Peso Max (kg)', 'Capacidade (kg)']
            }
            
            # Encontrar correspondências
            colunas_renomear = {}
            for padrao, alternativas in mapeamento.items():
                for alternativa in alternativas:
                    if alternativa in df.columns:
                        colunas_renomear[alternativa] = padrao
                        break
            
            # Verificar colunas obrigatórias
            obrigatorias = ['ID', 'Diâmetro Externo (m)', 'Diâmetro Interno (m)']
            for col in obrigatorias:
                if col not in colunas_renomear.values():
                    raise ValueError(f"Coluna obrigatória não encontrada: {col}. Colunas disponíveis: {list(df.columns)}")
            
            # Renomear colunas e selecionar apenas as necessárias
            df = df.rename(columns=colunas_renomear)
            colunas_selecionadas = [c for c in mapeamento.keys() if c in colunas_renomear.values()]
            df = df[colunas_selecionadas]
            
            return df.to_dict('records')
            
        except Exception as e:
            raise Exception(f"Erro ao ler bobinas: {str(e)}")

    @staticmethod
    def ler_linhas(caminho_arquivo):
        """
        Lê dados da aba 'Linhas' com tratamento flexível
        Retorna: Lista de dicionários com os dados
        """
        try:
            df = pd.read_excel(caminho_arquivo, sheet_name='Linhas')
            
            mapeamento = {
                'ID': ['ID', 'Código'],
                'Diâmetro (m)': ['Diâmetro (m)', 'Diametro (m)', 'Espessura'],
                'Comprimento Necessário (m)': ['Comprimento Necessário (m)', 'Comp Necessario', 'Metragem Necessária'],
                'Peso por Metro (kg/m)': ['Peso por Metro (kg/m)', 'Peso Unitário', 'Peso/m'],
                'Raio Mínimo (m)': ['Raio Mínimo (m)', 'Raio Min', 'Curvatura Mínima']
            }
            
            colunas_renomear = {}
            for padrao, alternativas in mapeamento.items():
                for alternativa in alternativas:
                    if alternativa in df.columns:
                        colunas_renomear[alternativa] = padrao
                        break
            
            obrigatorias = ['ID', 'Diâmetro (m)', 'Comprimento Necessário (m)']
            for col in obrigatorias:
                if col not in colunas_renomear.values():
                    raise ValueError(f"Coluna obrigatória não encontrada: {col}. Colunas disponíveis: {list(df.columns)}")
            
            df = df.rename(columns=colunas_renomear)
            colunas_selecionadas = [c for c in mapeamento.keys() if c in colunas_renomear.values()]
            df = df[colunas_selecionadas]
            
            return df.to_dict('records')
            
        except Exception as e:
            raise Exception(f"Erro ao ler linhas: {str(e)}")