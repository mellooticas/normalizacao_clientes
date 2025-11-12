#!/usr/bin/env python3
"""
MIGRAÇÃO PARA SCHEMA PAGAMENTOS
==============================

Este script migra os dados existentes de movimento de caixa para a nova estrutura
do schema pagamentos, aproveitando os UUIDs de core.clientes
"""

import pandas as pd
from pathlib import Path
import logging
from datetime import datetime
import uuid

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class MigradorSchemaPagamentos:
    def __init__(self):
        self.pasta_dados = Path("d:/projetos/carne_facil/carne_facil/data/processados/movimento_caixa")
        self.pasta_output = Path("d:/projetos/carne_facil/carne_facil/data/processados/schema_pagamentos")
        self.pasta_output.mkdir(exist_ok=True)
        
        # DataFrames
        self.df_movimentos = None
        self.df_pagamentos_carne = None
        
        # Mapeamentos (simulados - na prática viriam do banco)
        self.mapeamento_clientes = {}
        self.mapeamento_lojas = {
            42: str(uuid.uuid4()),  # LOJA_PRINCIPAL 
            48: str(uuid.uuid4())   # LOJA_SECUNDARIA
        }
    
    def carregar_dados_normalizados(self):
        """Carrega os dados já normalizados"""
        # Movimento de caixa normalizado
        arquivos_mov = list(self.pasta_dados.glob("normalizado/movimento_caixa_normalizado_*.csv"))
        if arquivos_mov:
            arquivo_mov = max(arquivos_mov, key=lambda x: x.stat().st_mtime)
            self.df_movimentos = pd.read_csv(arquivo_mov)
            logging.info(f"Movimentos carregados: {len(self.df_movimentos)} registros")
        
        # Pagamentos de carnê específicos
        arquivos_carne = list(self.pasta_dados.glob("pagamentos_carne/pagamentos_carne_extraidos_*.csv"))
        if arquivos_carne:
            arquivo_carne = max(arquivos_carne, key=lambda x: x.stat().st_mtime)
            self.df_pagamentos_carne = pd.read_csv(arquivo_carne)
            logging.info(f"Pagamentos carnê carregados: {len(self.df_pagamentos_carne)} registros")
        
        return True
    
    def criar_mapeamento_clientes(self):
        """Cria mapeamento de IDs para UUIDs de clientes"""
        logging.info("Criando mapeamento de clientes...")
        
        # Na prática, isso viria de uma consulta ao banco core.clientes
        # Aqui vou simular baseado nos dados de pagamentos
        
        if self.df_pagamentos_carne is not None:
            clientes_unicos = self.df_pagamentos_carne[
                self.df_pagamentos_carne['cliente_id'].notna()
            ]['cliente_id'].unique()
            
            for cliente_id in clientes_unicos:
                if cliente_id not in self.mapeamento_clientes:
                    self.mapeamento_clientes[cliente_id] = str(uuid.uuid4())
        
        logging.info(f"Mapeamento criado para {len(self.mapeamento_clientes)} clientes")
        
        # Salvar mapeamento para referência
        df_mapeamento = pd.DataFrame([
            {'cliente_id_original': k, 'cliente_uuid': v} 
            for k, v in self.mapeamento_clientes.items()
        ])
        
        arquivo_mapeamento = self.pasta_output / f"mapeamento_clientes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df_mapeamento.to_csv(arquivo_mapeamento, index=False)
        logging.info(f"Mapeamento salvo: {arquivo_mapeamento}")
    
    def migrar_movimentos_caixa(self):
        """Migra dados para pagamentos.movimentos_caixa"""
        logging.info("=== MIGRANDO MOVIMENTOS DE CAIXA ===")
        
        if self.df_movimentos is None:
            logging.error("Dados de movimentos não carregados!")
            return None
        
        # Estrutura para pagamentos.movimentos_caixa
        df_migrado = pd.DataFrame()
        
        # IDs e identificação
        df_migrado['id'] = [str(uuid.uuid4()) for _ in range(len(self.df_movimentos))]
        df_migrado['id_movimento_original'] = self.df_movimentos['id_movimento_original']
        df_migrado['numero_documento'] = self.df_movimentos['numero_documento']
        
        # Temporal
        df_migrado['data_movimento'] = pd.to_datetime(self.df_movimentos['data_movimento'])
        df_migrado['hora_movimento'] = self.df_movimentos['hora_movimento']
        df_migrado['timestamp_movimento'] = pd.to_datetime(self.df_movimentos['timestamp_movimento'])
        
        # Relacionamentos via UUID
        def mapear_cliente_uuid(row):
            # Na prática, isso seria uma consulta ao banco
            # Aqui vou simular baseado nos dados disponíveis
            return None  # Será preenchido posteriormente com dados reais
        
        def mapear_loja_uuid(codigo_funcionario):
            return self.mapeamento_lojas.get(codigo_funcionario)
        
        df_migrado['cliente_uuid'] = None  # Será preenchido com dados reais
        df_migrado['loja_uuid'] = self.df_movimentos['codigo_funcionario'].map(mapear_loja_uuid)
        df_migrado['venda_uuid'] = None  # Será preenchido quando houver cruzamento
        
        # Categoria e tipo
        df_migrado['categoria_movimento'] = self.df_movimentos['categoria_normalizada']
        
        def definir_tipo_pagamento(categoria):
            if categoria == 'pagamento_parcela':
                return 'CARNE_LANCASTER'
            elif categoria == 'pagamento_cartao':
                return 'CARTAO'
            elif categoria == 'pagamento_dinheiro':
                return 'DINHEIRO'
            elif categoria == 'operacao_caixa':
                return 'OPERACAO_CAIXA'
            else:
                return 'OUTROS'
        
        df_migrado['tipo_pagamento'] = self.df_movimentos['categoria_normalizada'].apply(definir_tipo_pagamento)
        
        def definir_subtipo(categoria, historico):
            if 'PARCELA' in str(historico).upper():
                return 'PARCELA'
            elif 'ENTRADA' in str(historico).upper():
                return 'ENTRADA'
            elif 'SANGRIA' in str(historico).upper():
                return 'SANGRIA'
            elif 'ABERTURA' in str(historico).upper():
                return 'ABERTURA'
            else:
                return 'OUTROS'
        
        df_migrado['subtipo'] = self.df_movimentos.apply(
            lambda row: definir_subtipo(row['categoria_normalizada'], row['historico_completo']), 
            axis=1
        )
        
        # Informações financeiras
        df_migrado['valor_movimento'] = self.df_movimentos['valor_liquido']
        df_migrado['valor_original'] = self.df_movimentos['valor_liquido']  # Para auditoria
        
        # Detalhes
        df_migrado['historico_completo'] = self.df_movimentos['historico_completo']
        df_migrado['segmento'] = self.df_movimentos['segmento']
        df_migrado['forma_pagamento'] = None  # A ser preenchido
        
        # Informações operacionais
        df_migrado['codigo_funcionario'] = self.df_movimentos['codigo_funcionario']
        df_migrado['codigo_caixa'] = self.df_movimentos['codigo_caixa']
        df_migrado['codigo_pdv'] = None
        
        # Metadados
        df_migrado['arquivo_origem'] = self.df_movimentos['arquivo_origem']
        df_migrado['periodo_origem'] = self.df_movimentos['periodo_origem']
        df_migrado['sistema_origem'] = 'MOVIMENTO_CAIXA'
        
        # Flags
        df_migrado['is_pagamento_carne'] = self.df_movimentos['is_parcela_carne']
        df_migrado['is_operacao_caixa'] = self.df_movimentos['is_operacao_caixa']
        df_migrado['is_entrada_venda'] = False  # A ser determinado
        df_migrado['is_processado'] = True
        
        # Auditoria
        df_migrado['created_at'] = datetime.now()
        df_migrado['updated_at'] = datetime.now()
        df_migrado['created_by'] = None
        
        # Salvar
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo_movimentos = self.pasta_output / f"movimentos_caixa_migrado_{timestamp}.csv"
        df_migrado.to_csv(arquivo_movimentos, index=False, encoding='utf-8')
        
        logging.info(f"Movimentos migrados salvos: {arquivo_movimentos} ({len(df_migrado)} registros)")
        return df_migrado, arquivo_movimentos
    
    def migrar_parcelas_carne(self):
        """Migra dados específicos para pagamentos.parcelas_carne"""
        logging.info("=== MIGRANDO PARCELAS DE CARNÊ ===")
        
        if self.df_pagamentos_carne is None:
            logging.error("Dados de pagamentos carnê não carregados!")
            return None
        
        # Filtrar apenas registros com informações de parcela
        df_com_parcela = self.df_pagamentos_carne[
            self.df_pagamentos_carne['tem_parcela_info'] == True
        ].copy()
        
        # Estrutura para pagamentos.parcelas_carne
        df_migrado = pd.DataFrame()
        
        # IDs
        df_migrado['id'] = [str(uuid.uuid4()) for _ in range(len(df_com_parcela))]
        df_migrado['movimento_caixa_id'] = None  # Será relacionado posteriormente
        
        # Relacionamentos
        df_migrado['cliente_uuid'] = df_com_parcela['cliente_id'].map(
            lambda x: self.mapeamento_clientes.get(x) if pd.notna(x) else None
        )
        df_migrado['venda_uuid'] = None  # A ser preenchido
        
        # Informações da parcela
        df_migrado['numero_parcela'] = df_com_parcela['parcela_numero']
        df_migrado['total_parcelas'] = df_com_parcela['total_parcelas']
        df_migrado['valor_parcela'] = df_com_parcela['valor_pago']
        
        # Informações do carnê
        df_migrado['numero_carne'] = None  # A ser extraído se disponível
        df_migrado['plano_pagamento'] = df_com_parcela['total_parcelas'].apply(
            lambda x: f"{int(x)}x" if pd.notna(x) else None
        )
        df_migrado['valor_total_carne'] = None  # Será calculado
        
        # Status
        df_migrado['status_parcela'] = 'PAGA'  # Todos os registros são pagamentos efetivados
        df_migrado['data_vencimento'] = None  # Não disponível nos dados atuais
        df_migrado['data_pagamento'] = pd.to_datetime(df_com_parcela['data_pagamento'])
        
        # Informações do cliente (denormalizado)
        df_migrado['cliente_nome'] = df_com_parcela['cliente_nome']
        df_migrado['cliente_documento'] = None  # A ser preenchido com dados do core.clientes
        
        # Auditoria
        df_migrado['created_at'] = datetime.now()
        df_migrado['updated_at'] = datetime.now()
        
        # Salvar
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo_parcelas = self.pasta_output / f"parcelas_carne_migrado_{timestamp}.csv"
        df_migrado.to_csv(arquivo_parcelas, index=False, encoding='utf-8')
        
        logging.info(f"Parcelas migradas salvas: {arquivo_parcelas} ({len(df_migrado)} registros)")
        return df_migrado, arquivo_parcelas
    
    def gerar_scripts_importacao(self, arquivos_gerados):
        """Gera scripts SQL para importação no schema pagamentos"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Script de importação
        sql_import = f"""
-- IMPORTAÇÃO PARA SCHEMA PAGAMENTOS
-- Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}

-- 1. CRIAR SCHEMA E ESTRUTURA (executar SCHEMA_PAGAMENTOS_COMPLETO.sql primeiro)

-- 2. IMPORTAR MOVIMENTOS DE CAIXA
\\COPY pagamentos.movimentos_caixa FROM '{arquivos_gerados['movimentos']}' WITH (FORMAT CSV, HEADER TRUE, DELIMITER ',');

-- 3. IMPORTAR PARCELAS DE CARNÊ  
\\COPY pagamentos.parcelas_carne FROM '{arquivos_gerados['parcelas']}' WITH (FORMAT CSV, HEADER TRUE, DELIMITER ',');

-- 4. VERIFICAÇÕES PÓS-IMPORTAÇÃO
SELECT 
    'MOVIMENTOS CAIXA' as tabela,
    COUNT(*) as registros_importados,
    COUNT(DISTINCT cliente_uuid) as clientes_unicos,
    SUM(valor_movimento) as valor_total
FROM pagamentos.movimentos_caixa

UNION ALL

SELECT 
    'PARCELAS CARNÊ' as tabela,
    COUNT(*) as registros_importados,
    COUNT(DISTINCT cliente_uuid) as clientes_unicos,
    SUM(valor_parcela) as valor_total
FROM pagamentos.parcelas_carne;

-- 5. POPULAR RESUMO DE CLIENTES (automático via triggers)
INSERT INTO pagamentos.resumo_clientes (cliente_uuid)
SELECT DISTINCT cliente_uuid 
FROM pagamentos.movimentos_caixa 
WHERE cliente_uuid IS NOT NULL
ON CONFLICT (cliente_uuid) DO NOTHING;

-- 6. RECALCULAR SCORES (opcional)
UPDATE pagamentos.resumo_clientes 
SET score_pagamento = pagamentos.calcular_score_cliente(cliente_uuid);

SELECT 'IMPORTAÇÃO CONCLUÍDA' as status;
"""
        
        arquivo_import = self.pasta_output / f"importar_schema_pagamentos_{timestamp}.sql"
        with open(arquivo_import, 'w', encoding='utf-8') as f:
            f.write(sql_import)
        
        logging.info(f"Script de importação gerado: {arquivo_import}")
        return arquivo_import
    
    def executar_migracao_completa(self):
        """Executa toda a migração"""
        logging.info("=== INICIANDO MIGRAÇÃO PARA SCHEMA PAGAMENTOS ===")
        
        # Carregar dados
        if not self.carregar_dados_normalizados():
            return False
        
        # Criar mapeamentos
        self.criar_mapeamento_clientes()
        
        # Migrar dados
        movimentos_result = self.migrar_movimentos_caixa()
        parcelas_result = self.migrar_parcelas_carne()
        
        if not movimentos_result or not parcelas_result:
            logging.error("Erro na migração!")
            return False
        
        # Gerar scripts
        arquivos_gerados = {
            'movimentos': movimentos_result[1],
            'parcelas': parcelas_result[1]
        }
        
        script_import = self.gerar_scripts_importacao(arquivos_gerados)
        
        print(f"\n✅ MIGRAÇÃO PARA SCHEMA PAGAMENTOS CONCLUÍDA!")
        print(f"📁 Arquivos gerados em: {self.pasta_output}")
        print(f"")
        print(f"📊 ESTRUTURA MIGRADA:")
        print(f"   • Movimentos de caixa: {len(movimentos_result[0]):,} registros")
        print(f"   • Parcelas de carnê: {len(parcelas_result[0]):,} registros")
        print(f"   • Clientes mapeados: {len(self.mapeamento_clientes):,}")
        print(f"")
        print(f"🗃️ PRÓXIMOS PASSOS:")
        print(f"   1. Executar: SCHEMA_PAGAMENTOS_COMPLETO.sql")
        print(f"   2. Executar: {script_import.name}")
        print(f"   3. Integrar com core.clientes para UUIDs reais")
        
        logging.info("=== MIGRAÇÃO CONCLUÍDA ===")
        return True

def main():
    """Função principal"""
    migrador = MigradorSchemaPagamentos()
    sucesso = migrador.executar_migracao_completa()
    
    if not sucesso:
        print("\n❌ Erro na migração!")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())