#!/usr/bin/env python3
"""
NORMALIZADOR FINAL DE MOVIMENTO DE CAIXA
=======================================

Este script normaliza os dados consolidados para estrutura final do banco:
1. Mapear lojas pelo ID_emp (42 = ??, 48 = ??)
2. Normalizar categorias de movimento
3. Criar estrutura para importação no Supabase
4. Gerar arquivos finais organizados
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

class NormalizadorMovimentoCaixa:
    def __init__(self):
        self.pasta_dados = Path("d:/projetos/carne_facil/carne_facil/data/processados/movimento_caixa")
        self.pasta_final = Path("d:/projetos/carne_facil/carne_facil/data/processados/movimento_caixa/normalizado")
        self.pasta_final.mkdir(exist_ok=True)
        self.df = None
        
        # Mapeamento de funcionários/lojas (baseado na análise)
        self.mapeamento_lojas = {
            42: 'LOJA_PRINCIPAL',  # 4,334 movimentos
            48: 'LOJA_SECUNDARIA'  # 2,334 movimentos
        }
        
        # Mapeamento de categorias para estrutura do banco
        self.categorias_normalizadas = {
            'PARCELA_CARNE': 'pagamento_parcela',
            'ABERTURA_CAIXA': 'operacao_caixa',
            'SANGRIA': 'sangria',
            'CARTAO': 'pagamento_cartao',
            'DINHEIRO': 'pagamento_dinheiro',
            'FREELANCE': 'servico_freelance',
            'OPERACAO_CAIXA': 'operacao_caixa',
            'OUTROS': 'outros'
        }
    
    def carregar_dados_consolidados(self):
        """Carrega o arquivo consolidado mais recente"""
        arquivos = list(self.pasta_dados.glob("movimento_caixa_consolidado_*.csv"))
        if not arquivos:
            logging.error("Nenhum arquivo consolidado encontrado!")
            return False
        
        arquivo_mais_recente = max(arquivos, key=lambda x: x.stat().st_mtime)
        logging.info(f"Carregando: {arquivo_mais_recente.name}")
        
        self.df = pd.read_csv(arquivo_mais_recente)
        self.df['Dh_movimento'] = pd.to_datetime(self.df['Dh_movimento'])
        
        logging.info(f"Dados carregados: {len(self.df)} registros")
        return True
    
    def normalizar_estrutura(self):
        """Normaliza a estrutura dos dados para o banco final"""
        logging.info("Normalizando estrutura dos dados...")
        
        # Aplicar categorização (do script anterior)
        def categorizar_movimento(historico):
            historico = str(historico).upper()
            
            if 'CARNE LANCASTER' in historico:
                return 'PARCELA_CARNE'
            elif 'ABERTURA' in historico:
                return 'ABERTURA_CAIXA'
            elif 'SANGRIA' in historico or 'RETIRADA' in historico:
                return 'SANGRIA'
            elif 'DÉBITO' in historico or 'CRÉDITO' in historico:
                return 'CARTAO'
            elif 'DINHEIRO' in historico:
                return 'DINHEIRO'
            elif 'RESERVA' in historico or 'TROCO' in historico:
                return 'OPERACAO_CAIXA'
            elif 'FREELANCE' in historico:
                return 'FREELANCE'
            else:
                return 'OUTROS'
        
        self.df['categoria_movimento'] = self.df['Histórico'].apply(categorizar_movimento)
        
        # Criar estrutura normalizada
        df_normalizado = pd.DataFrame()
        
        # IDs e identificadores
        df_normalizado['id'] = [str(uuid.uuid4()) for _ in range(len(self.df))]
        df_normalizado['id_movimento_original'] = self.df['ID_fin_']
        df_normalizado['numero_documento'] = self.df['Nro_doc_']
        
        # Informações temporais
        df_normalizado['data_movimento'] = self.df['Dh_movimento'].dt.date
        df_normalizado['hora_movimento'] = self.df['Dh_movimento'].dt.time
        df_normalizado['timestamp_movimento'] = self.df['Dh_movimento']
        
        # Identificação de loja/funcionário
        df_normalizado['codigo_funcionario'] = self.df['ID_emp_']
        df_normalizado['loja_identificada'] = self.df['ID_emp_'].map(self.mapeamento_lojas)
        df_normalizado['codigo_caixa'] = self.df['ID_caixa']
        
        # Categoria e descrição
        df_normalizado['categoria_original'] = self.df['categoria_movimento']
        df_normalizado['categoria_normalizada'] = self.df['categoria_movimento'].map(self.categorias_normalizadas)
        df_normalizado['historico_completo'] = self.df['Histórico']
        df_normalizado['segmento'] = self.df['Segmento']
        
        # Valores financeiros
        df_normalizado['valor_liquido'] = self.df['Vl_líquido']
        df_normalizado['tipo_documento'] = self.df['ID_doc_']
        
        # Cliente/Fornecedor
        df_normalizado['cliente_fornecedor'] = self.df['Fornecedor/cliente']
        df_normalizado['id_cliente_original'] = self.df['ID']
        
        # Metadados de origem
        df_normalizado['arquivo_origem'] = self.df['arquivo_origem']
        df_normalizado['periodo_origem'] = self.df['periodo_origem']
        df_normalizado['ano_movimento'] = self.df['Dh_movimento'].dt.year
        df_normalizado['mes_movimento'] = self.df['Dh_movimento'].dt.month
        df_normalizado['dia_semana'] = self.df['Dh_movimento'].dt.day_name()
        
        # Flags e indicadores
        df_normalizado['is_parcela_carne'] = (self.df['categoria_movimento'] == 'PARCELA_CARNE')
        df_normalizado['is_operacao_caixa'] = (self.df['categoria_movimento'].isin(['ABERTURA_CAIXA', 'SANGRIA', 'OPERACAO_CAIXA']))
        df_normalizado['is_pagamento'] = (self.df['categoria_movimento'].isin(['CARTAO', 'DINHEIRO', 'PARCELA_CARNE']))
        
        # Timestamps de processamento
        df_normalizado['created_at'] = datetime.now()
        df_normalizado['updated_at'] = datetime.now()
        
        self.df_normalizado = df_normalizado
        logging.info(f"Estrutura normalizada criada: {len(df_normalizado)} registros")
    
    def gerar_estatisticas_normalizacao(self):
        """Gera estatísticas da normalização"""
        logging.info("Gerando estatísticas da normalização...")
        
        print(f"\n📊 ESTATÍSTICAS DA NORMALIZAÇÃO:")
        print(f"   • Total de registros: {len(self.df_normalizado):,}")
        
        print(f"\n🏪 DISTRIBUIÇÃO POR LOJA:")
        dist_loja = self.df_normalizado['loja_identificada'].value_counts()
        for loja, quantidade in dist_loja.items():
            percentual = (quantidade / len(self.df_normalizado)) * 100
            print(f"   • {loja}: {quantidade:,} ({percentual:.1f}%)")
        
        print(f"\n🏷️ CATEGORIAS NORMALIZADAS:")
        dist_categoria = self.df_normalizado['categoria_normalizada'].value_counts()
        for categoria, quantidade in dist_categoria.items():
            percentual = (quantidade / len(self.df_normalizado)) * 100
            print(f"   • {categoria}: {quantidade:,} ({percentual:.1f}%)")
        
        print(f"\n💰 VALORES POR CATEGORIA:")
        valores_categoria = self.df_normalizado.groupby('categoria_normalizada')['valor_liquido'].agg([
            'count', 'sum', 'mean'
        ]).round(2)
        print(valores_categoria)
        
        print(f"\n📅 DISTRIBUIÇÃO TEMPORAL:")
        print(f"   • Período: {self.df_normalizado['data_movimento'].min()} até {self.df_normalizado['data_movimento'].max()}")
        print(f"   • Anos únicos: {sorted(self.df_normalizado['ano_movimento'].unique())}")
        print(f"   • Total de dias: {self.df_normalizado['data_movimento'].nunique()}")
    
    def exportar_dados_finais(self):
        """Exporta os dados normalizados em diferentes formatos"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. Arquivo principal completo
        arquivo_principal = self.pasta_final / f"movimento_caixa_normalizado_{timestamp}.csv"
        self.df_normalizado.to_csv(arquivo_principal, index=False, encoding='utf-8')
        logging.info(f"Arquivo principal salvo: {arquivo_principal}")
        
        # 2. Apenas parcelas de carnê (para análise específica)
        df_parcelas = self.df_normalizado[self.df_normalizado['is_parcela_carne']]
        arquivo_parcelas = self.pasta_final / f"parcelas_carne_normalizado_{timestamp}.csv"
        df_parcelas.to_csv(arquivo_parcelas, index=False, encoding='utf-8')
        logging.info(f"Arquivo de parcelas salvo: {arquivo_parcelas} ({len(df_parcelas)} registros)")
        
        # 3. Operações de caixa (para análise operacional)
        df_operacoes = self.df_normalizado[self.df_normalizado['is_operacao_caixa']]
        arquivo_operacoes = self.pasta_final / f"operacoes_caixa_normalizado_{timestamp}.csv"
        df_operacoes.to_csv(arquivo_operacoes, index=False, encoding='utf-8')
        logging.info(f"Arquivo de operações salvo: {arquivo_operacoes} ({len(df_operacoes)} registros)")
        
        # 4. Resumo por período (para dashboards)
        resumo_mensal = self.df_normalizado.groupby(['ano_movimento', 'mes_movimento', 'categoria_normalizada']).agg({
            'valor_liquido': ['count', 'sum', 'mean'],
            'id': 'count'
        }).round(2)
        
        arquivo_resumo = self.pasta_final / f"resumo_mensal_{timestamp}.csv"
        resumo_mensal.to_csv(arquivo_resumo, encoding='utf-8')
        logging.info(f"Resumo mensal salvo: {arquivo_resumo}")
        
        return {
            'principal': arquivo_principal,
            'parcelas': arquivo_parcelas,
            'operacoes': arquivo_operacoes,
            'resumo': arquivo_resumo
        }
    
    def gerar_scripts_importacao(self, arquivos_gerados):
        """Gera scripts SQL para importação no Supabase"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Script de criação de tabela
        sql_create = f"""
-- CRIAÇÃO DA TABELA MOVIMENTO_CAIXA
-- Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}

CREATE TABLE IF NOT EXISTS movimento_caixa (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_movimento_original BIGINT NOT NULL,
    numero_documento BIGINT,
    data_movimento DATE NOT NULL,
    hora_movimento TIME,
    timestamp_movimento TIMESTAMP WITH TIME ZONE,
    
    -- Identificação
    codigo_funcionario INTEGER,
    loja_identificada TEXT,
    codigo_caixa BIGINT,
    
    -- Categoria e descrição
    categoria_original TEXT,
    categoria_normalizada TEXT,
    historico_completo TEXT,
    segmento TEXT,
    
    -- Valores
    valor_liquido DECIMAL(10,2),
    tipo_documento TEXT,
    
    -- Cliente/Fornecedor
    cliente_fornecedor TEXT,
    id_cliente_original BIGINT,
    
    -- Metadados
    arquivo_origem TEXT,
    periodo_origem TEXT,
    ano_movimento INTEGER,
    mes_movimento INTEGER,
    dia_semana TEXT,
    
    -- Flags
    is_parcela_carne BOOLEAN DEFAULT FALSE,
    is_operacao_caixa BOOLEAN DEFAULT FALSE,
    is_pagamento BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_movimento_caixa_data ON movimento_caixa(data_movimento);
CREATE INDEX IF NOT EXISTS idx_movimento_caixa_categoria ON movimento_caixa(categoria_normalizada);
CREATE INDEX IF NOT EXISTS idx_movimento_caixa_loja ON movimento_caixa(loja_identificada);
CREATE INDEX IF NOT EXISTS idx_movimento_caixa_valor ON movimento_caixa(valor_liquido);
CREATE INDEX IF NOT EXISTS idx_movimento_caixa_parcela ON movimento_caixa(is_parcela_carne) WHERE is_parcela_carne = TRUE;

-- Comentários
COMMENT ON TABLE movimento_caixa IS 'Movimentos de caixa consolidados de todas as lojas';
COMMENT ON COLUMN movimento_caixa.id_movimento_original IS 'ID original do sistema legado';
COMMENT ON COLUMN movimento_caixa.categoria_normalizada IS 'Categoria padronizada do movimento';
COMMENT ON COLUMN movimento_caixa.is_parcela_carne IS 'Flag para identificar pagamentos de carnê Lancaster';
"""
        
        arquivo_create = self.pasta_final / f"01_create_table_movimento_caixa_{timestamp}.sql"
        with open(arquivo_create, 'w', encoding='utf-8') as f:
            f.write(sql_create)
        
        # Script de importação via COPY
        sql_import = f"""
-- IMPORTAÇÃO DE DADOS - MOVIMENTO CAIXA
-- Arquivo: {arquivos_gerados['principal'].name}
-- Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}

-- Limpar dados existentes (se necessário)
-- TRUNCATE TABLE movimento_caixa;

-- Importar dados via COPY (executar no psql ou ferramenta que suporte COPY)
\\COPY movimento_caixa FROM '{arquivos_gerados['principal']}' WITH (FORMAT CSV, HEADER TRUE, DELIMITER ',');

-- Verificações pós-importação
SELECT 
    'IMPORTAÇÃO CONCLUÍDA' as status,
    COUNT(*) as total_registros,
    MIN(data_movimento) as data_inicio,
    MAX(data_movimento) as data_fim,
    COUNT(DISTINCT loja_identificada) as lojas_unicas,
    COUNT(DISTINCT categoria_normalizada) as categorias_unicas
FROM movimento_caixa;

-- Estatísticas por categoria
SELECT 
    categoria_normalizada,
    COUNT(*) as quantidade,
    SUM(valor_liquido) as valor_total,
    AVG(valor_liquido) as valor_medio
FROM movimento_caixa 
GROUP BY categoria_normalizada 
ORDER BY quantidade DESC;
"""
        
        arquivo_import = self.pasta_final / f"02_import_movimento_caixa_{timestamp}.sql"
        with open(arquivo_import, 'w', encoding='utf-8') as f:
            f.write(sql_import)
        
        logging.info(f"Scripts SQL gerados:")
        logging.info(f"  - CREATE: {arquivo_create}")
        logging.info(f"  - IMPORT: {arquivo_import}")
        
        return {
            'create': arquivo_create,
            'import': arquivo_import
        }
    
    def executar_normalizacao_completa(self):
        """Executa todo o processo de normalização"""
        logging.info("=== INICIANDO NORMALIZAÇÃO FINAL ===")
        
        if not self.carregar_dados_consolidados():
            return False
        
        self.normalizar_estrutura()
        self.gerar_estatisticas_normalizacao()
        arquivos = self.exportar_dados_finais()
        scripts = self.gerar_scripts_importacao(arquivos)
        
        # Relatório final
        print(f"\n✅ NORMALIZAÇÃO CONCLUÍDA COM SUCESSO!")
        print(f"📁 Arquivos gerados em: {self.pasta_final}")
        print(f"")
        print(f"📊 ARQUIVOS PRINCIPAIS:")
        print(f"   • Dados completos: {arquivos['principal'].name}")
        print(f"   • Parcelas carnê: {arquivos['parcelas'].name}")
        print(f"   • Operações caixa: {arquivos['operacoes'].name}")
        print(f"   • Resumo mensal: {arquivos['resumo'].name}")
        print(f"")
        print(f"🗃️ SCRIPTS SQL:")
        print(f"   • Criação tabela: {scripts['create'].name}")
        print(f"   • Importação: {scripts['import'].name}")
        
        logging.info("=== NORMALIZAÇÃO FINAL CONCLUÍDA ===")
        return True

def main():
    """Função principal"""
    normalizador = NormalizadorMovimentoCaixa()
    sucesso = normalizador.executar_normalizacao_completa()
    
    if not sucesso:
        print("\n❌ Erro na normalização!")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())