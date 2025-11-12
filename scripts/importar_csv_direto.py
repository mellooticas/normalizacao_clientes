#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Importação Direta CSV → Supabase
Importa arquivos CSV normalizados diretamente nas tabelas do Supabase
"""

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values, RealDictCursor
import os
from pathlib import Path
from dotenv import load_dotenv
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

class ImportadorCSV:
    """Importador de CSVs para Supabase"""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL') or os.getenv('SUPABASE_DATABASE_URL')
        self.conn = None
        
        if not self.database_url or '[SENHA_DO_BANCO]' in self.database_url:
            raise ValueError(
                "DATABASE_URL não configurada corretamente no .env\n"
                "Configure a senha do banco primeiro!"
            )
    
    def conectar(self):
        """Conecta ao Supabase"""
        try:
            self.conn = psycopg2.connect(self.database_url, sslmode='require')
            logger.info("✅ Conectado ao Supabase")
            return True
        except Exception as e:
            logger.error(f"❌ Erro de conexão: {e}")
            return False
    
    def desconectar(self):
        """Fecha conexão"""
        if self.conn:
            self.conn.close()
            logger.info("🔌 Conexão fechada")
    
    def limpar_cpf(self, cpf):
        """Remove formatação do CPF"""
        if pd.isna(cpf):
            return None
        cpf_limpo = str(cpf).replace('.', '').replace('-', '').replace(' ', '')
        return cpf_limpo if len(cpf_limpo) == 11 else None
    
    def limpar_telefone(self, telefone):
        """Remove formatação do telefone"""
        if pd.isna(telefone):
            return None
        tel_limpo = str(telefone).replace('(', '').replace(')', '').replace('-', '').replace(' ', '')
        return tel_limpo if len(tel_limpo) >= 10 else None
    
    def importar_csv(self, csv_path, tabela, schema='public', 
                     mapeamento=None, transformacoes=None, 
                     batch_size=1000, on_conflict='NOTHING'):
        """
        Importa CSV para tabela do Supabase
        
        Args:
            csv_path: Caminho do arquivo CSV
            tabela: Nome da tabela destino
            schema: Schema da tabela (default: public)
            mapeamento: Dict com {coluna_csv: coluna_banco}
            transformacoes: Dict com {coluna: funcao_transform}
            batch_size: Tamanho do lote para inserção
            on_conflict: Ação em caso de conflito (NOTHING, UPDATE)
        """
        
        logger.info(f"\n{'='*70}")
        logger.info(f"📊 Importando: {Path(csv_path).name}")
        logger.info(f"🎯 Destino: {schema}.{tabela}")
        logger.info(f"{'='*70}")
        
        # Ler CSV
        try:
            logger.info(f"📖 Lendo CSV...")
            df = pd.read_csv(csv_path, low_memory=False)
            logger.info(f"✅ {len(df):,} linhas carregadas")
            logger.info(f"📋 Colunas: {list(df.columns)[:10]}...")
        except Exception as e:
            logger.error(f"❌ Erro ao ler CSV: {e}")
            return False
        
        # Aplicar mapeamento de colunas
        if mapeamento:
            logger.info(f"🔄 Aplicando mapeamento de colunas...")
            df = df.rename(columns=mapeamento)
        
        # Aplicar transformações
        if transformacoes:
            logger.info(f"🔧 Aplicando transformações...")
            for coluna, funcao in transformacoes.items():
                if coluna in df.columns:
                    df[coluna] = df[coluna].apply(funcao)
        
        # Remover linhas completamente vazias
        df = df.dropna(how='all')
        logger.info(f"📊 Registros válidos: {len(df):,}")
        
        # Preparar query de inserção
        colunas = list(df.columns)
        colunas_str = ', '.join(colunas)
        placeholders = ', '.join(['%s'] * len(colunas))
        
        conflict_clause = {
            'NOTHING': 'ON CONFLICT DO NOTHING',
            'UPDATE': f'ON CONFLICT (id) DO UPDATE SET {", ".join([f"{c}=EXCLUDED.{c}" for c in colunas if c != "id"])}'
        }.get(on_conflict, 'ON CONFLICT DO NOTHING')
        
        query = f"""
            INSERT INTO {schema}.{tabela} ({colunas_str})
            VALUES %s
            {conflict_clause}
        """
        
        # Converter para lista de tuplas
        dados = [tuple(x) for x in df.to_numpy()]
        
        # Inserir em lotes
        try:
            cursor = self.conn.cursor()
            
            total_lotes = (len(dados) + batch_size - 1) // batch_size
            logger.info(f"⬆️  Iniciando importação em {total_lotes} lote(s)...")
            
            for i in range(0, len(dados), batch_size):
                lote = dados[i:i + batch_size]
                lote_num = (i // batch_size) + 1
                
                logger.info(f"   Lote {lote_num}/{total_lotes} - {len(lote)} registros...")
                execute_values(cursor, query, lote, page_size=100)
                
                self.conn.commit()
            
            cursor.close()
            logger.info(f"✅ Importação concluída com sucesso!")
            return True
            
        except Exception as e:
            self.conn.rollback()
            logger.error(f"❌ Erro na importação: {e}")
            return False
    
    def verificar_tabela(self, tabela, schema='public'):
        """Verifica se tabela existe e retorna contagem"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {schema}.{tabela}")
            count = cursor.fetchone()[0]
            cursor.close()
            logger.info(f"📊 {schema}.{tabela}: {count:,} registros")
            return count
        except Exception as e:
            logger.warning(f"⚠️  {schema}.{tabela}: não existe ou erro - {e}")
            return None

def exemplo_importacao_vendas():
    """Exemplo de importação do CSV de vendas"""
    
    importador = ImportadorCSV()
    
    if not importador.conectar():
        return
    
    # Definir mapeamento de colunas
    mapeamento = {
        'os_n': 'numero_os',
        'data_de_compra': 'data_venda',
        'consultor': 'vendedor_nome',
        'nome': 'cliente_nome',
        'total': 'valor_total'
    }
    
    # Definir transformações
    transformacoes = {
        'cpf': importador.limpar_cpf,
        'telefone': importador.limpar_telefone,
        'celular': importador.limpar_telefone,
    }
    
    # Importar
    sucesso = importador.importar_csv(
        csv_path='data_backup/vendas_os_completo.csv',
        tabela='vendas_raw',
        schema='staging',
        mapeamento=mapeamento,
        transformacoes=transformacoes,
        batch_size=500
    )
    
    if sucesso:
        # Verificar resultado
        importador.verificar_tabela('vendas_raw', 'staging')
    
    importador.desconectar()

def importar_todos_csvs():
    """Importa todos os CSVs na ordem correta"""
    
    logger.info("\n" + "="*70)
    logger.info("🚀 IMPORTAÇÃO COMPLETA DE CSVS")
    logger.info("="*70)
    
    importador = ImportadorCSV()
    
    if not importador.conectar():
        logger.error("❌ Não foi possível conectar ao banco")
        return
    
    # Lista de importações na ordem correta
    importacoes = [
        {
            'nome': 'Vendas OS Completo',
            'csv': 'data_backup/vendas_os_completo.csv',
            'tabela': 'vendas_raw',
            'schema': 'staging',
            'ativo': True
        },
        {
            'nome': 'Marketing Origens Vixen',
            'csv': 'data_backup/marketing_origens_vixen_correto.csv',
            'tabela': 'marketing_origens',
            'schema': 'staging',
            'ativo': True
        },
        # Adicione mais importações aqui
    ]
    
    resultados = []
    
    for config in importacoes:
        if not config.get('ativo', True):
            logger.info(f"⏭️  Pulando: {config['nome']}")
            continue
        
        sucesso = importador.importar_csv(
            csv_path=config['csv'],
            tabela=config['tabela'],
            schema=config['schema']
        )
        
        resultados.append({
            'nome': config['nome'],
            'sucesso': sucesso
        })
    
    # Resumo final
    logger.info("\n" + "="*70)
    logger.info("📊 RESUMO DA IMPORTAÇÃO")
    logger.info("="*70)
    
    sucessos = sum(1 for r in resultados if r['sucesso'])
    falhas = len(resultados) - sucessos
    
    for resultado in resultados:
        status = "✅" if resultado['sucesso'] else "❌"
        logger.info(f"{status} {resultado['nome']}")
    
    logger.info(f"\n📈 Total: {sucessos} sucessos, {falhas} falhas")
    
    importador.desconectar()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        comando = sys.argv[1]
        
        if comando == 'exemplo':
            exemplo_importacao_vendas()
        elif comando == 'todos':
            importar_todos_csvs()
        else:
            print("Uso:")
            print("  python importar_csv_direto.py exemplo  # Exemplo simples")
            print("  python importar_csv_direto.py todos    # Importar todos")
    else:
        # Por padrão, mostra instruções
        print("\n" + "="*70)
        print("📊 IMPORTADOR CSV → SUPABASE")
        print("="*70)
        print("\nUso:")
        print("  python importar_csv_direto.py exemplo  # Exemplo com vendas")
        print("  python importar_csv_direto.py todos    # Importar todos os CSVs")
        print("\nOu importe o módulo em seus scripts:")
        print("  from importar_csv_direto import ImportadorCSV")
        print("="*70 + "\n")
