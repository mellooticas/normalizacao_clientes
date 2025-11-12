#!/usr/bin/env python3
"""
Script para normalização final dos dados de caixa
Sistema Carne Fácil - Normalização baseada nos padrões identificados
"""

import pandas as pd
import json
from datetime import datetime
import os
import re
import uuid

def gerar_uuid():
    """Gera UUID único"""
    return str(uuid.uuid4())

def normalizar_valor_monetario(valor):
    """Normaliza valores monetários"""
    if pd.isna(valor) or valor == '' or str(valor).lower() == 'nan':
        return 0.0
    
    try:
        # Converter para string e limpar
        valor_str = str(valor).strip()
        # Remover caracteres não numéricos exceto . e ,
        valor_limpo = re.sub(r'[^\d.,]', '', valor_str)
        # Substituir vírgula por ponto
        valor_limpo = valor_limpo.replace(',', '.')
        return float(valor_limpo) if valor_limpo else 0.0
    except:
        return 0.0

def normalizar_data(data_str):
    """Normaliza datas para formato padrão"""
    if pd.isna(data_str) or not data_str:
        return None
    
    try:
        data_str = str(data_str).strip()
        if 'T' in data_str:
            return data_str.split('T')[0]  # Remover parte do tempo
        return data_str
    except:
        return None

def normalizar_loja(loja):
    """Normaliza nome da loja"""
    if pd.isna(loja) or not loja or str(loja).lower() == 'nan':
        return 'INDEFINIDA'
    
    loja_str = str(loja).upper().strip()
    
    # Mapeamento para códigos de loja conhecidos
    mapeamento = {
        'MAUÁ': 'MAUA',
        'MAUA': 'MAUA',
        'PERUS': 'PERUS',
        'RIO PEQUENO': 'RIO_PEQUENO',
        'SAO MATEUS': 'SAO_MATEUS',
        'SUZANO 1': 'SUZANO',
        'SUZANO': 'SUZANO',
        'SUZANO 2': 'SUZANO2',
        'SUZANO2': 'SUZANO2'
    }
    
    for original, normalizado in mapeamento.items():
        if original in loja_str:
            return normalizado
    
    return loja_str

def is_valor_valido(valor):
    """Verifica se um valor é válido (não nulo, não vazio)"""
    return not pd.isna(valor) and valor != '' and str(valor).lower() != 'nan' and str(valor).strip() != ''

def normalizar_dados_caixa():
    """
    Normaliza todos os dados de caixa em tabelas padronizadas
    """
    print("🔄 NORMALIZAÇÃO DOS DADOS DE CAIXA")
    print("=" * 60)
    
    # Carregar dados de todas as lojas
    lojas = ['maua', 'perus', 'sao_mateus', 'suzano', 'suzano2']
    todos_registros = []
    
    print("📊 Carregando dados das lojas...")
    for loja in lojas:
        caminho_csv = f'data/originais/cxs/dados_loja_{loja}.csv'
        
        if os.path.exists(caminho_csv):
            try:
                df = pd.read_csv(caminho_csv)
                registros_loja = df.to_dict('records')
                todos_registros.extend(registros_loja)
                print(f"   ✅ {loja.upper()}: {len(registros_loja)} registros")
            except Exception as e:
                print(f"   ❌ Erro ao carregar {loja}: {str(e)}")
    
    print(f"\n📋 Total de registros carregados: {len(todos_registros)}")
    
    # Tabelas normalizadas
    tabelas_normalizadas = {
        'movimentacoes_financeiras': [],
        'recebimentos_parcelas': [],
        'entregas_os': [],
        'controle_carnes': []
    }
    
    # Processar cada registro
    for registro in todos_registros:
        tipo_estrutura = registro.get('tipo_estrutura', '')
        
        # Campos comuns para todos os registros
        campos_comuns = {
            'id': gerar_uuid(),
            'data_movimento': normalizar_data(registro.get('data_movimento')),
            'loja': normalizar_loja(registro.get('loja')),
            'arquivo_origem': registro.get('arquivo_origem', ''),
            'aba': registro.get('aba', ''),
            'linha_arquivo': registro.get('linha_arquivo', 0)
        }
        
        # 1. MOVIMENTAÇÕES FINANCEIRAS (VENDAS + RESTANTE_ENTRADA)
        if tipo_estrutura in ['VENDAS', 'RESTANTE_ENTRADA']:
            if is_valor_valido(registro.get('nn_venda')) or is_valor_valido(registro.get('cliente')):
                registro_financeiro = {
                    **campos_comuns,
                    'tipo_movimentacao': tipo_estrutura,
                    'numero_venda': registro.get('nn_venda', ''),
                    'cliente': registro.get('cliente', ''),
                    'forma_pagamento': registro.get('forma_de_pgto', ''),
                    'valor_venda': normalizar_valor_monetario(registro.get('valor_venda')),
                    'valor_entrada': normalizar_valor_monetario(registro.get('entrada')),
                    'observacoes': registro.get('entrada', '') if tipo_estrutura == 'RESTANTE_ENTRADA' else ''
                }
                tabelas_normalizadas['movimentacoes_financeiras'].append(registro_financeiro)
        
        # 2. RECEBIMENTOS DE PARCELAS (RECEBIMENTO_CARNE)
        elif tipo_estrutura == 'RECEBIMENTO_CARNE':
            if is_valor_valido(registro.get('os')) or is_valor_valido(registro.get('valor_parcela')):
                registro_recebimento = {
                    **campos_comuns,
                    'numero_os': registro.get('os', ''),
                    'cliente': registro.get('cliente', ''),
                    'forma_pagamento': registro.get('forma_de_pgto', ''),
                    'valor_parcela': normalizar_valor_monetario(registro.get('valor_parcela')),
                    'numero_parcela': registro.get('nn_parcela', ''),
                    'observacoes': ''
                }
                tabelas_normalizadas['recebimentos_parcelas'].append(registro_recebimento)
        
        # 3. ENTREGAS DE OS (OS_ENTREGUES_DIA)
        elif tipo_estrutura == 'OS_ENTREGUES_DIA':
            if is_valor_valido(registro.get('os')):
                registro_entrega = {
                    **campos_comuns,
                    'numero_os': registro.get('os', ''),
                    'vendedor': registro.get('vendedor', ''),
                    'tem_carne': registro.get('carn', ''),
                    'observacoes': ''
                }
                tabelas_normalizadas['entregas_os'].append(registro_entrega)
        
        # 4. CONTROLE DE CARNÊS (ENTREGA_CARNE)
        elif tipo_estrutura == 'ENTREGA_CARNE':
            if is_valor_valido(registro.get('os')):
                registro_controle = {
                    **campos_comuns,
                    'numero_os': registro.get('os', ''),
                    'total_parcelas': registro.get('parcelas', ''),
                    'valor_total': normalizar_valor_monetario(registro.get('valor_total')),
                    'observacoes': ''
                }
                tabelas_normalizadas['controle_carnes'].append(registro_controle)
    
    # Salvar tabelas normalizadas
    os.makedirs('data/originais/cxs/normalizados', exist_ok=True)
    
    resumo_normalizacao = {
        'data_normalizacao': datetime.now().isoformat(),
        'total_registros_origem': len(todos_registros),
        'tabelas_geradas': {}
    }
    
    for nome_tabela, registros in tabelas_normalizadas.items():
        if registros:
            # Salvar CSV
            df_tabela = pd.DataFrame(registros)
            caminho_csv = f'data/originais/cxs/normalizados/{nome_tabela}.csv'
            df_tabela.to_csv(caminho_csv, index=False, encoding='utf-8')
            
            # Salvar JSON para análise
            caminho_json = f'data/originais/cxs/normalizados/{nome_tabela}.json'
            with open(caminho_json, 'w', encoding='utf-8') as f:
                json.dump(registros, f, indent=2, ensure_ascii=False)
            
            resumo_normalizacao['tabelas_geradas'][nome_tabela] = {
                'total_registros': len(registros),
                'arquivo_csv': caminho_csv,
                'arquivo_json': caminho_json
            }
            
            print(f"💾 {nome_tabela}: {len(registros)} registros salvos")
    
    # Salvar resumo da normalização
    caminho_resumo = 'data/originais/cxs/normalizados/resumo_normalizacao.json'
    with open(caminho_resumo, 'w', encoding='utf-8') as f:
        json.dump(resumo_normalizacao, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resumo da normalização salvo em: {caminho_resumo}")
    
    return resumo_normalizacao

def gerar_relatorio_normalizacao(resumo):
    """
    Gera relatório detalhado da normalização
    """
    print(f"\n📊 RELATÓRIO DE NORMALIZAÇÃO:")
    print(f"   📅 Data: {resumo['data_normalizacao']}")
    print(f"   📋 Registros de origem: {resumo['total_registros_origem']}")
    print(f"   🗂️  Tabelas geradas: {len(resumo['tabelas_geradas'])}")
    
    total_normalizados = 0
    for nome_tabela, dados in resumo['tabelas_geradas'].items():
        print(f"\n   📄 {nome_tabela.upper()}:")
        print(f"      📈 Registros: {dados['total_registros']}")
        print(f"      💾 CSV: {dados['arquivo_csv']}")
        total_normalizados += dados['total_registros']
    
    print(f"\n🎯 RESUMO FINAL:")
    print(f"   ✅ Total normalizado: {total_normalizados} registros")
    print(f"   📊 Taxa de normalização: {(total_normalizados/resumo['total_registros_origem']*100):.1f}%")
    
    print(f"\n📋 ESTRUTURA PARA POSTGRESQL:")
    print(f"   1. 💰 movimentacoes_financeiras → financeiro.movimentacoes_caixa")
    print(f"   2. 📦 recebimentos_parcelas → financeiro.recebimentos_parcelas")
    print(f"   3. 🚚 entregas_os → operacional.entregas_os")
    print(f"   4. 📋 controle_carnes → operacional.controle_carnes")

def gerar_scripts_sql():
    """
    Gera scripts SQL para criação das tabelas normalizadas
    """
    print(f"\n🔄 Gerando scripts SQL...")
    
    sql_script = """-- =========================================
-- ESTRUTURA PARA DADOS DE CAIXA NORMALIZADOS
-- Sistema Carne Fácil
-- =========================================

-- Schema para dados financeiros
CREATE SCHEMA IF NOT EXISTS financeiro;
CREATE SCHEMA IF NOT EXISTS operacional;

-- 1. MOVIMENTAÇÕES FINANCEIRAS (Vendas + Entradas)
CREATE TABLE financeiro.movimentacoes_caixa (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    data_movimento DATE NOT NULL,
    loja VARCHAR(20) NOT NULL,
    tipo_movimentacao VARCHAR(20) CHECK (tipo_movimentacao IN ('VENDAS', 'RESTANTE_ENTRADA')),
    numero_venda VARCHAR(50),
    cliente VARCHAR(200),
    forma_pagamento VARCHAR(50),
    valor_venda DECIMAL(12,2) DEFAULT 0,
    valor_entrada DECIMAL(12,2) DEFAULT 0,
    observacoes TEXT,
    arquivo_origem VARCHAR(100),
    aba VARCHAR(10),
    linha_arquivo INTEGER,
    criado_em TIMESTAMP DEFAULT NOW()
);

-- 2. RECEBIMENTOS DE PARCELAS
CREATE TABLE financeiro.recebimentos_parcelas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    data_movimento DATE NOT NULL,
    loja VARCHAR(20) NOT NULL,
    numero_os VARCHAR(50),
    cliente VARCHAR(200),
    forma_pagamento VARCHAR(50),
    valor_parcela DECIMAL(12,2) DEFAULT 0,
    numero_parcela VARCHAR(20),
    observacoes TEXT,
    arquivo_origem VARCHAR(100),
    aba VARCHAR(10),
    linha_arquivo INTEGER,
    criado_em TIMESTAMP DEFAULT NOW()
);

-- 3. ENTREGAS DE OS
CREATE TABLE operacional.entregas_os (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    data_movimento DATE NOT NULL,
    loja VARCHAR(20) NOT NULL,
    numero_os VARCHAR(50),
    vendedor VARCHAR(100),
    tem_carne VARCHAR(10),
    observacoes TEXT,
    arquivo_origem VARCHAR(100),
    aba VARCHAR(10),
    linha_arquivo INTEGER,
    criado_em TIMESTAMP DEFAULT NOW()
);

-- 4. CONTROLE DE CARNÊS
CREATE TABLE operacional.controle_carnes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    data_movimento DATE NOT NULL,
    loja VARCHAR(20) NOT NULL,
    numero_os VARCHAR(50),
    total_parcelas VARCHAR(20),
    valor_total DECIMAL(12,2) DEFAULT 0,
    observacoes TEXT,
    arquivo_origem VARCHAR(100),
    aba VARCHAR(10),
    linha_arquivo INTEGER,
    criado_em TIMESTAMP DEFAULT NOW()
);

-- ÍNDICES PARA PERFORMANCE
CREATE INDEX idx_movimentacoes_data_loja ON financeiro.movimentacoes_caixa(data_movimento, loja);
CREATE INDEX idx_movimentacoes_numero_venda ON financeiro.movimentacoes_caixa(numero_venda);
CREATE INDEX idx_recebimentos_data_loja ON financeiro.recebimentos_parcelas(data_movimento, loja);
CREATE INDEX idx_recebimentos_os ON financeiro.recebimentos_parcelas(numero_os);
CREATE INDEX idx_entregas_data_loja ON operacional.entregas_os(data_movimento, loja);
CREATE INDEX idx_entregas_os ON operacional.entregas_os(numero_os);
CREATE INDEX idx_controle_data_loja ON operacional.controle_carnes(data_movimento, loja);
CREATE INDEX idx_controle_os ON operacional.controle_carnes(numero_os);

-- COMENTÁRIOS
COMMENT ON TABLE financeiro.movimentacoes_caixa IS 'Movimentações financeiras do caixa (vendas e entradas)';
COMMENT ON TABLE financeiro.recebimentos_parcelas IS 'Recebimentos de parcelas de carnês';
COMMENT ON TABLE operacional.entregas_os IS 'Controle de entregas de ordens de serviço';
COMMENT ON TABLE operacional.controle_carnes IS 'Controle de carnês entregues';
"""
    
    caminho_sql = 'data/originais/cxs/normalizados/estrutura_caixa_normalizada.sql'
    with open(caminho_sql, 'w', encoding='utf-8') as f:
        f.write(sql_script)
    
    print(f"💾 Script SQL salvo em: {caminho_sql}")

def main():
    """Função principal"""
    resumo = normalizar_dados_caixa()
    gerar_relatorio_normalizacao(resumo)
    gerar_scripts_sql()
    
    print(f"\n✅ NORMALIZAÇÃO CONCLUÍDA!")
    print(f"📁 Arquivos disponíveis em: data/originais/cxs/normalizados/")
    print(f"🚀 Próximo passo: Importar dados normalizados no PostgreSQL")

if __name__ == "__main__":
    main()