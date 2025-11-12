#!/usr/bin/env python3
"""
Corrige estrutura do arquivo de vendas para compatibilidade com tabela Supabase
"""

import pandas as pd
from pathlib import Path

def corrigir_estrutura_vendas():
    """Corrige estrutura do arquivo vendas para compatibilidade com tabela"""
    
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    
    print("🔧 === CORRIGINDO ESTRUTURA VENDAS === 🔧")
    
    # 1. Carrega arquivo gerado
    arquivo_vendas = base_dir / "data" / "vendas_para_importar" / "vendas_COMPLETAS_PRONTO_PARA_IMPORTAR.csv"
    vendas_df = pd.read_csv(arquivo_vendas)
    
    print(f"📊 Carregadas: {len(vendas_df)} vendas")
    print(f"📋 Colunas atuais: {list(vendas_df.columns)}")
    
    # 2. Estrutura correta da tabela vendas.vendas no Supabase
    """
    Campos obrigatórios:
    - numero_venda VARCHAR(50) NOT NULL
    - loja_id UUID NOT NULL REFERENCES core.lojas(id)
    - data_venda DATE NOT NULL
    - valor_total DECIMAL(12,2) NOT NULL
    
    Campos opcionais com defaults:
    - cliente_id UUID REFERENCES core.clientes(id) [pode ser NULL]
    - vendedor_id UUID REFERENCES core.vendedores(id) [pode ser NULL]
    - valor_entrada DECIMAL(12,2) DEFAULT 0
    - nome_cliente_temp VARCHAR(200)
    - observacoes TEXT
    - status status_type DEFAULT 'ATIVO'
    - cancelado BOOLEAN DEFAULT false
    - data_cancelamento TIMESTAMP [NULL]
    - motivo_cancelamento TEXT [NULL]
    
    Campos de auditoria com defaults automáticos:
    - id UUID PRIMARY KEY DEFAULT uuid_generate_v4()
    - created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    - updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    - created_by VARCHAR(100) [NULL]
    - updated_by VARCHAR(100) [NULL]
    - deleted_at TIMESTAMP NULL
    - version INT DEFAULT 1
    """
    
    # 3. Ajustes necessários
    print(f"\n🔧 Aplicando correções...")
    
    # Remove campos que não existem na tabela
    if 'nome_cliente' in vendas_df.columns:
        vendas_df.rename(columns={'nome_cliente': 'nome_cliente_temp'}, inplace=True)
        print(f"✅ Renomeado 'nome_cliente' → 'nome_cliente_temp'")
    
    # Remove campos de auditoria que serão gerados automaticamente pelo banco
    campos_remover = ['created_at', 'updated_at']
    for campo in campos_remover:
        if campo in vendas_df.columns:
            vendas_df.drop(columns=[campo], inplace=True)
            print(f"🗑️  Removido campo '{campo}' (será gerado automaticamente)")
    
    # 4. Validação de tipos
    print(f"\n📋 Validando tipos...")
    
    # UUID fields - verificar formato
    uuid_fields = ['cliente_id', 'vendedor_id', 'loja_id']
    for field in uuid_fields:
        if field in vendas_df.columns:
            # Conta valores nulos
            nulls = vendas_df[field].isna().sum()
            validos = len(vendas_df) - nulls
            print(f"   {field}: {validos} válidos, {nulls} nulos")
    
    # Numeric fields
    vendas_df['valor_total'] = pd.to_numeric(vendas_df['valor_total'], errors='coerce')
    vendas_df['valor_entrada'] = pd.to_numeric(vendas_df['valor_entrada'], errors='coerce').fillna(0)
    
    # String fields - limitar tamanho
    if 'numero_venda' in vendas_df.columns:
        vendas_df['numero_venda'] = vendas_df['numero_venda'].astype(str).str[:50]
    
    if 'nome_cliente_temp' in vendas_df.columns:
        vendas_df['nome_cliente_temp'] = vendas_df['nome_cliente_temp'].astype(str).str[:200]
    
    # Boolean fields
    if 'cancelado' in vendas_df.columns:
        vendas_df['cancelado'] = vendas_df['cancelado'].astype(bool)
    
    # 5. Ordem correta dos campos para importação
    campos_finais = [
        'numero_venda',      # VARCHAR(50) NOT NULL
        'cliente_id',        # UUID (pode ser NULL)
        'loja_id',          # UUID NOT NULL
        'vendedor_id',      # UUID (pode ser NULL)
        'data_venda',       # DATE NOT NULL
        'valor_total',      # DECIMAL(12,2) NOT NULL
        'valor_entrada',    # DECIMAL(12,2) DEFAULT 0
        'nome_cliente_temp', # VARCHAR(200)
        'observacoes',      # TEXT
        'status',           # status_type DEFAULT 'ATIVO'
        'cancelado'         # BOOLEAN DEFAULT false
    ]
    
    # Seleciona apenas campos que existem
    campos_existentes = [campo for campo in campos_finais if campo in vendas_df.columns]
    vendas_final = vendas_df[campos_existentes].copy()
    
    print(f"\n📋 Campos finais: {list(vendas_final.columns)}")
    
    # 6. Validação final
    print(f"\n🔍 Validação final...")
    
    # Campos obrigatórios
    obrigatorios = ['numero_venda', 'loja_id', 'data_venda', 'valor_total']
    for campo in obrigatorios:
        if campo in vendas_final.columns:
            nulos = vendas_final[campo].isna().sum()
            if nulos > 0:
                print(f"⚠️  ATENÇÃO: {campo} tem {nulos} valores nulos!")
            else:
                print(f"✅ {campo}: OK (sem nulos)")
        else:
            print(f"❌ ERRO: Campo obrigatório '{campo}' não encontrado!")
    
    # 7. Salva arquivo corrigido
    output_dir = base_dir / "data" / "vendas_para_importar"
    arquivo_corrigido = output_dir / "vendas_COMPLETAS_ESTRUTURA_CORRIGIDA.csv"
    
    vendas_final.to_csv(arquivo_corrigido, index=False)
    
    print(f"\n💾 Arquivo corrigido salvo: {arquivo_corrigido}")
    print(f"📊 {len(vendas_final)} vendas prontas para importar")
    print(f"💰 Valor total: R$ {vendas_final['valor_total'].sum():,.2f}")
    
    # 8. Amostra dos dados
    print(f"\n📋 Amostra dos dados corrigidos:")
    print(vendas_final.head())
    
    return vendas_final, arquivo_corrigido

if __name__ == "__main__":
    vendas_corrigidas, arquivo_final = corrigir_estrutura_vendas()
    print(f"\n🎉 ESTRUTURA CORRIGIDA!")
    print(f"📂 Arquivo: {arquivo_final}")
    print(f"✅ Pronto para importar no Supabase")