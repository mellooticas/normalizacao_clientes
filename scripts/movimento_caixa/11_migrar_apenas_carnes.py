#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migração CORRETA - APENAS CARNÊS para Schema Pagamentos
Foco exclusivo em pagamentos de clientes
"""

import pandas as pd
import uuid
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MigradorPagamentosClientes:
    def __init__(self):
        self.pasta_base = Path("d:/projetos/carne_facil/carne_facil/data/processados")
        self.pasta_output = self.pasta_base / "schema_pagamentos"
        self.pasta_output.mkdir(exist_ok=True)
        
        # Dados
        self.df_carnes = None
        self.mapeamento_clientes = {}
        self.mapeamento_lojas = {}
    
    def carregar_pagamentos_carne(self):
        """Carregar APENAS os pagamentos de carnê"""
        logging.info("📁 Carregando pagamentos de carnê...")
        
        # Buscar arquivo de carnês
        pasta_carne = self.pasta_base / "movimento_caixa" / "pagamentos_carne"
        arquivos_carne = list(pasta_carne.glob("pagamentos_carne_extraidos_*.csv"))
        
        if not arquivos_carne:
            logging.error("❌ Arquivo de pagamentos carnê não encontrado!")
            return False
        
        arquivo_carne = max(arquivos_carne, key=lambda x: x.stat().st_mtime)
        self.df_carnes = pd.read_csv(arquivo_carne)
        
        logging.info(f"✅ Carnês carregados: {len(self.df_carnes)} registros")
        logging.info(f"📂 Arquivo: {arquivo_carne.name}")
        
        return True
    
    def criar_mapeamento_clientes(self):
        """Criar mapeamento cliente_id → cliente_uuid"""
        logging.info("🔗 Criando mapeamento de clientes...")
        
        # Extrair clientes únicos dos carnês
        clientes_unicos = self.df_carnes.dropna(subset=['cliente_id', 'cliente_nome'])
        clientes_unicos = clientes_unicos.drop_duplicates(subset=['cliente_id'])
        
        # Criar UUID para cada cliente
        for _, row in clientes_unicos.iterrows():
            cliente_id = int(row['cliente_id'])
            self.mapeamento_clientes[cliente_id] = {
                'uuid': str(uuid.uuid4()),
                'nome': row['cliente_nome']
            }
        
        logging.info(f"✅ Mapeamento criado para {len(self.mapeamento_clientes)} clientes")
        
        # Salvar mapeamento
        df_mapeamento = pd.DataFrame([
            {
                'cliente_id_original': k,
                'cliente_uuid': v['uuid'],
                'cliente_nome': v['nome']
            }
            for k, v in self.mapeamento_clientes.items()
        ])
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        arquivo_map = self.pasta_output / f"mapeamento_clientes_carnes_{timestamp}.csv"
        df_mapeamento.to_csv(arquivo_map, index=False)
        logging.info(f"💾 Mapeamento salvo: {arquivo_map.name}")
        
        return True
    
    def criar_mapeamento_lojas(self):
        """Criar mapeamento loja_codigo → loja_uuid"""
        logging.info("🏪 Criando mapeamento de lojas...")
        
        # Extrair lojas únicas dos carnês
        lojas_unicas = self.df_carnes['loja_codigo'].dropna().unique()
        
        # Criar UUID para cada loja
        for loja_codigo in lojas_unicas:
            self.mapeamento_lojas[int(loja_codigo)] = str(uuid.uuid4())
        
        logging.info(f"✅ Mapeamento criado para {len(self.mapeamento_lojas)} lojas")
        return True
    
    def migrar_entradas_carne(self):
        """Migrar carnês para pagamentos.entradas_carne"""
        logging.info("🔄 Migrando para pagamentos.entradas_carne...")
        
        df_migrado = pd.DataFrame()
        
        # IDs
        df_migrado['id'] = [str(uuid.uuid4()) for _ in range(len(self.df_carnes))]
        df_migrado['id_movimento_original'] = self.df_carnes['id_movimento']
        df_migrado['numero_documento'] = self.df_carnes['numero_documento']
        
        # CLIENTE
        df_migrado['cliente_uuid'] = self.df_carnes['cliente_id'].map(
            lambda x: self.mapeamento_clientes.get(int(x))['uuid'] if pd.notna(x) and int(x) in self.mapeamento_clientes else None
        )
        df_migrado['cliente_nome'] = self.df_carnes['cliente_nome']
        df_migrado['cliente_id_original'] = self.df_carnes['cliente_id']
        
        # LOJA E OPERACIONAL
        df_migrado['loja_uuid'] = self.df_carnes['loja_codigo'].map(
            lambda x: self.mapeamento_lojas.get(int(x)) if pd.notna(x) else None
        )
        df_migrado['loja_codigo'] = self.df_carnes['loja_codigo']
        df_migrado['codigo_caixa'] = self.df_carnes['caixa_codigo']
        
        # INFORMAÇÕES DA PARCELA
        df_migrado['numero_parcela'] = self.df_carnes['parcela_numero']
        df_migrado['total_parcelas'] = self.df_carnes['total_parcelas']
        df_migrado['valor_parcela'] = self.df_carnes['valor_pago']
        
        # INFORMAÇÕES DO CARNÊ
        df_migrado['plano_pagamento'] = self.df_carnes['total_parcelas'].map(
            lambda x: f"{int(x)}x" if pd.notna(x) else None
        )
        
        # TEMPORAL
        df_migrado['data_pagamento'] = pd.to_datetime(self.df_carnes['data_pagamento'])
        df_migrado['hora_pagamento'] = self.df_carnes['hora_pagamento']
        df_migrado['timestamp_pagamento'] = pd.to_datetime(self.df_carnes['timestamp_pagamento'])
        
        # DETALHES
        df_migrado['historico_completo'] = self.df_carnes['historico_completo']
        df_migrado['segmento'] = self.df_carnes['segmento']
        
        # STATUS
        df_migrado['status_parcela'] = 'PAGA'  # Todos os registros são pagamentos já efetuados
        
        # METADADOS
        df_migrado['arquivo_origem'] = self.df_carnes['arquivo_origem']
        df_migrado['periodo_origem'] = self.df_carnes['periodo_origem']
        
        # FLAGS
        df_migrado['tem_parcela_info'] = self.df_carnes['tem_parcela_info']
        df_migrado['tem_cliente_id'] = self.df_carnes['tem_cliente_id']
        df_migrado['is_consumidor'] = self.df_carnes['is_consumidor']
        
        # AUDITORIA
        df_migrado['created_at'] = datetime.now()
        df_migrado['updated_at'] = datetime.now()
        
        logging.info(f"✅ Entradas carnê migradas: {len(df_migrado)} registros")
        return df_migrado
    
    def normalizar_para_postgresql(self, df):
        """Normalizar para PostgreSQL"""
        logging.info("🔧 Normalizando para PostgreSQL...")
        
        df_norm = df.copy()
        
        # CONVERSÕES DE TIPOS ESPECÍFICAS
        # Inteiros - converter float para int
        int_cols = ['id_movimento_original', 'numero_documento', 'cliente_id_original', 
                   'loja_codigo', 'codigo_caixa', 'numero_parcela', 'total_parcelas']
        for col in int_cols:
            if col in df_norm.columns:
                # Converter para numérico primeiro, depois para int
                df_norm[col] = pd.to_numeric(df_norm[col], errors='coerce')
                # Substituir NaN por None e converter para int onde possível
                df_norm[col] = df_norm[col].apply(lambda x: int(x) if pd.notna(x) else '')
        
        # Decimais - garantir formato correto
        decimal_cols = ['valor_parcela']
        for col in decimal_cols:
            if col in df_norm.columns:
                df_norm[col] = pd.to_numeric(df_norm[col], errors='coerce')
                df_norm[col] = df_norm[col].round(2)
                # Manter valores NaN para colunas decimais
                df_norm[col] = df_norm[col].fillna('')
        
        # Datas
        df_norm['data_pagamento'] = pd.to_datetime(df_norm['data_pagamento']).dt.strftime('%Y-%m-%d')
        df_norm['timestamp_pagamento'] = pd.to_datetime(df_norm['timestamp_pagamento']).dt.strftime('%Y-%m-%d %H:%M:%S')
        df_norm['created_at'] = pd.to_datetime(df_norm['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
        df_norm['updated_at'] = pd.to_datetime(df_norm['updated_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # Booleanos
        bool_cols = ['tem_parcela_info', 'tem_cliente_id', 'is_consumidor']
        for col in bool_cols:
            if col in df_norm.columns:
                df_norm[col] = df_norm[col].astype(str).str.lower()
                df_norm[col] = df_norm[col].replace('nan', '')
        
        # Campos vazios apenas para strings e UUIDs (não aplicar aos inteiros convertidos)
        string_cols = [col for col in df_norm.columns if col not in int_cols + decimal_cols + bool_cols + 
                      ['data_pagamento', 'timestamp_pagamento', 'created_at', 'updated_at']]
        for col in string_cols:
            df_norm[col] = df_norm[col].fillna('')
        
        logging.info("✅ Normalização concluída")
        return df_norm
    
    def executar_migracao(self):
        """Executar migração completa"""
        logging.info("=== MIGRAÇÃO PAGAMENTOS DE CLIENTES ===")
        
        # 1. Carregar dados
        if not self.carregar_pagamentos_carne():
            return
        
        # 2. Criar mapeamentos
        self.criar_mapeamento_clientes()
        self.criar_mapeamento_lojas()
        
        # 3. Migrar entradas de carnê
        df_entradas = self.migrar_entradas_carne()
        
        # 4. Normalizar
        df_norm = self.normalizar_para_postgresql(df_entradas)
        
        # 5. Salvar
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        arquivo_final = self.pasta_output / f"entradas_carne_postgresql_{timestamp}.csv"
        
        df_norm.to_csv(arquivo_final, index=False, quoting=1)
        logging.info(f"✅ Arquivo final salvo: {arquivo_final.name}")
        
        # 6. Relatório
        self.gerar_relatorio(df_norm, arquivo_final)
    
    def gerar_relatorio(self, df, arquivo):
        """Gerar relatório da migração"""
        print(f"""
✅ MIGRAÇÃO DE PAGAMENTOS CONCLUÍDA!

📊 ESTATÍSTICAS:
   • Entradas de carnê: {len(df):,} registros
   • Clientes únicos: {len(self.mapeamento_clientes):,}
   • Lojas: {len(self.mapeamento_lojas):,}
   • Período: {df['data_pagamento'].min()} a {df['data_pagamento'].max()}

💰 VALORES:
   • Total pago: R$ {df['valor_parcela'].sum():,.2f}
   • Valor médio parcela: R$ {df['valor_parcela'].mean():.2f}
   • Maior parcela: R$ {df['valor_parcela'].max():.2f}

📁 ARQUIVO PRONTO:
   • Nome: {arquivo.name}
   • Tabela: pagamentos.entradas_carne
   • Status: ✅ Pronto para upload no Supabase

🔧 PRÓXIMOS PASSOS:
   1. Execute: SCHEMA_PAGAMENTOS_CLIENTES_SUPABASE.sql
   2. Upload CSV: {arquivo.name}
   3. Verificar triggers automáticos
   4. Analisar resumos gerados

🎯 FOCO CORRETO: Apenas pagamentos reais de clientes!
""")

if __name__ == "__main__":
    migrador = MigradorPagamentosClientes()
    migrador.executar_migracao()