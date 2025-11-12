#!/usr/bin/env python3
"""
UNIFICADOR DE ARQUIVOS DE MOVIMENTO DE CAIXA
============================================

Este script consolida todos os arquivos CSV de movimento de caixa em um único arquivo normalizado.

Estrutura dos dados:
- Período: DEZ/2020 a NOV/2023
- Colunas: ID fin., ID caixa, Dh.movimento, ID emp., Histórico, etc.
- Arquivos duplicados: alguns têm versão "_Planilha1" (ignorar duplicatas)

Objetivo:
1. Unir todos os CSVs em um único arquivo
2. Adicionar coluna de origem (ano/mês)
3. Normalizar formatos de data
4. Identificar e remover duplicatas
5. Gerar estatísticas de consolidação
"""

import pandas as pd
import os
from pathlib import Path
import logging
from datetime import datetime
import re

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('movimento_caixa_consolidacao.log'),
        logging.StreamHandler()
    ]
)

class ConsolidadorMovimentoCaixa:
    def __init__(self):
        self.pasta_origem = Path("d:/projetos/carne_facil/carne_facil/data/originais/controles_gerais/mov_cx")
        self.pasta_destino = Path("d:/projetos/carne_facil/carne_facil/data/processados/movimento_caixa")
        self.arquivos_processados = []
        self.dados_consolidados = []
        self.estatisticas = {
            'total_arquivos': 0,
            'arquivos_processados': 0,
            'arquivos_ignorados': 0,
            'total_registros': 0,
            'duplicatas_removidas': 0,
            'periodo_inicio': None,
            'periodo_fim': None
        }
    
    def listar_arquivos(self):
        """Lista todos os arquivos CSV e identifica duplicatas"""
        arquivos = list(self.pasta_origem.glob("*.csv"))
        
        # Separar arquivos principais dos "_Planilha1" (duplicatas)
        arquivos_principais = []
        arquivos_duplicados = []
        
        for arquivo in arquivos:
            if "_Planilha1" in arquivo.name:
                arquivos_duplicados.append(arquivo)
            else:
                arquivos_principais.append(arquivo)
        
        logging.info(f"Encontrados {len(arquivos)} arquivos CSV:")
        logging.info(f"  - {len(arquivos_principais)} arquivos principais")
        logging.info(f"  - {len(arquivos_duplicados)} arquivos duplicados (_Planilha1)")
        
        self.estatisticas['total_arquivos'] = len(arquivos_principais)
        return sorted(arquivos_principais)
    
    def extrair_periodo_arquivo(self, nome_arquivo):
        """Extrai ano e mês do nome do arquivo"""
        # Padrões: ABR_21.csv, NOV23.csv, DEZ_20.csv
        nome = nome_arquivo.stem
        
        # Padrão 1: MES_ANO (ex: ABR_21, DEZ_20)
        match1 = re.match(r'([A-Z]{3})_(\d{2})', nome)
        if match1:
            mes_str, ano_str = match1.groups()
            ano = 2000 + int(ano_str)
            return ano, mes_str
        
        # Padrão 2: MESANO (ex: NOV23)
        match2 = re.match(r'([A-Z]{3})(\d{2})', nome)
        if match2:
            mes_str, ano_str = match2.groups()
            ano = 2000 + int(ano_str)
            return ano, mes_str
        
        logging.warning(f"Não foi possível extrair período de: {nome}")
        return None, None
    
    def mes_para_numero(self, mes_str):
        """Converte nome do mês para número"""
        meses = {
            'JAN': 1, 'FEV': 2, 'MAR': 3, 'ABR': 4,
            'MAI': 5, 'JUN': 6, 'JUL': 7, 'AGO': 8,
            'SET': 9, 'OUT': 10, 'NOV': 11, 'DEZ': 12
        }
        return meses.get(mes_str, 0)
    
    def processar_arquivo(self, arquivo):
        """Processa um arquivo CSV individual"""
        try:
            logging.info(f"Processando: {arquivo.name}")
            
            # Ler CSV
            df = pd.read_csv(arquivo, encoding='utf-8')
            
            # Verificar se tem dados
            if df.empty:
                logging.warning(f"Arquivo vazio: {arquivo.name}")
                return None
            
            # Extrair período
            ano, mes_str = self.extrair_periodo_arquivo(arquivo)
            if not ano or not mes_str:
                logging.error(f"Não foi possível extrair período de: {arquivo.name}")
                return None
            
            # Adicionar colunas de origem
            df['arquivo_origem'] = arquivo.name
            df['ano_origem'] = ano
            df['mes_origem'] = mes_str
            df['mes_numero'] = self.mes_para_numero(mes_str)
            df['periodo_origem'] = f"{ano}-{self.mes_para_numero(mes_str):02d}"
            
            # Normalizar nomes das colunas (remover espaços e caracteres especiais)
            df.columns = df.columns.str.strip().str.replace('.', '_').str.replace(' ', '_')
            
            # Log estatísticas do arquivo
            logging.info(f"  - {len(df)} registros em {mes_str}/{ano}")
            
            return df
            
        except Exception as e:
            logging.error(f"Erro ao processar {arquivo.name}: {e}")
            self.estatisticas['arquivos_ignorados'] += 1
            return None
    
    def consolidar_dados(self):
        """Consolida todos os arquivos em um único DataFrame"""
        arquivos = self.listar_arquivos()
        
        logging.info("Iniciando consolidação dos dados...")
        
        for arquivo in arquivos:
            df = self.processar_arquivo(arquivo)
            if df is not None:
                self.dados_consolidados.append(df)
                self.estatisticas['arquivos_processados'] += 1
        
        if not self.dados_consolidados:
            logging.error("Nenhum arquivo foi processado com sucesso!")
            return None
        
        # Concatenar todos os DataFrames
        df_final = pd.concat(self.dados_consolidados, ignore_index=True)
        self.estatisticas['total_registros'] = len(df_final)
        
        # Ordenar por data de movimento
        df_final['Dh_movimento'] = pd.to_datetime(df_final['Dh_movimento'])
        df_final = df_final.sort_values('Dh_movimento')
        
        # Calcular período de cobertura
        self.estatisticas['periodo_inicio'] = df_final['Dh_movimento'].min()
        self.estatisticas['periodo_fim'] = df_final['Dh_movimento'].max()
        
        logging.info(f"Consolidação concluída: {len(df_final)} registros")
        return df_final
    
    def remover_duplicatas(self, df):
        """Remove registros duplicados baseado em ID fin."""
        logging.info("Removendo duplicatas...")
        
        registros_antes = len(df)
        
        # Remover duplicatas baseado no ID fin. (identificador único)
        df_limpo = df.drop_duplicates(subset=['ID_fin_'], keep='first')
        
        registros_depois = len(df_limpo)
        self.estatisticas['duplicatas_removidas'] = registros_antes - registros_depois
        
        logging.info(f"Duplicatas removidas: {self.estatisticas['duplicatas_removidas']}")
        return df_limpo
    
    def gerar_arquivo_consolidado(self, df):
        """Gera o arquivo CSV consolidado final"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"movimento_caixa_consolidado_{timestamp}.csv"
        caminho_arquivo = self.pasta_destino / nome_arquivo
        
        # Salvar CSV
        df.to_csv(caminho_arquivo, index=False, encoding='utf-8')
        
        logging.info(f"Arquivo consolidado salvo: {caminho_arquivo}")
        return caminho_arquivo
    
    def gerar_relatorio_estatisticas(self):
        """Gera relatório detalhado das estatísticas"""
        relatorio = f"""
=== RELATÓRIO DE CONSOLIDAÇÃO - MOVIMENTO DE CAIXA ===
Data/Hora: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}

ARQUIVOS PROCESSADOS:
- Total de arquivos encontrados: {self.estatisticas['total_arquivos']}
- Arquivos processados com sucesso: {self.estatisticas['arquivos_processados']}
- Arquivos ignorados (erro): {self.estatisticas['arquivos_ignorados']}

DADOS CONSOLIDADOS:
- Total de registros: {self.estatisticas['total_registros']:,}
- Duplicatas removidas: {self.estatisticas['duplicatas_removidas']:,}
- Registros únicos finais: {self.estatisticas['total_registros'] - self.estatisticas['duplicatas_removidas']:,}

PERÍODO DE COBERTURA:
- Data inicial: {self.estatisticas['periodo_inicio']}
- Data final: {self.estatisticas['periodo_fim']}
- Duração: {(self.estatisticas['periodo_fim'] - self.estatisticas['periodo_inicio']).days} dias

QUALIDADE DOS DADOS:
- Taxa de sucesso: {(self.estatisticas['arquivos_processados'] / self.estatisticas['total_arquivos'] * 100):.1f}%
- Taxa de duplicação: {(self.estatisticas['duplicatas_removidas'] / self.estatisticas['total_registros'] * 100):.2f}%

=== FIM DO RELATÓRIO ===
        """
        
        # Salvar relatório
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        caminho_relatorio = self.pasta_destino / f"relatorio_consolidacao_{timestamp}.txt"
        
        with open(caminho_relatorio, 'w', encoding='utf-8') as f:
            f.write(relatorio)
        
        print(relatorio)
        logging.info(f"Relatório salvo: {caminho_relatorio}")
    
    def executar_consolidacao(self):
        """Executa todo o processo de consolidação"""
        logging.info("=== INICIANDO CONSOLIDAÇÃO DE MOVIMENTO DE CAIXA ===")
        
        # 1. Consolidar dados
        df_consolidado = self.consolidar_dados()
        if df_consolidado is None:
            return False
        
        # 2. Remover duplicatas
        df_limpo = self.remover_duplicatas(df_consolidado)
        
        # 3. Gerar arquivo final
        arquivo_final = self.gerar_arquivo_consolidado(df_limpo)
        
        # 4. Gerar relatório
        self.gerar_relatorio_estatisticas()
        
        logging.info("=== CONSOLIDAÇÃO CONCLUÍDA COM SUCESSO ===")
        return True

def main():
    """Função principal"""
    consolidador = ConsolidadorMovimentoCaixa()
    sucesso = consolidador.executar_consolidacao()
    
    if sucesso:
        print("\n✅ Consolidação de movimento de caixa concluída com sucesso!")
        print(f"📁 Arquivos salvos em: {consolidador.pasta_destino}")
    else:
        print("\n❌ Erro na consolidação de movimento de caixa!")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())