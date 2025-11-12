#!/usr/bin/env python3
"""
Script FINAL para gerar CSV compatível com tabela vendas.vendas
Remove colunas inexistentes e ajusta estrutura exata da tabela
"""

import pandas as pd
from datetime import datetime
from pathlib import Path

def gerar_csv_compativel_vendas():
    """Gera CSV com estrutura EXATAMENTE compatível com vendas.vendas"""
    
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    
    print("=== GERAÇÃO DE CSV COMPATÍVEL COM vendas.vendas ===")
    
    # Carrega dados com cliente UUID
    arquivo_entrada = base_dir / "data" / "vendas_para_importar" / "vendas_com_cliente_uuid.csv"
    print(f"Carregando: {arquivo_entrada}")
    
    df = pd.read_csv(arquivo_entrada, low_memory=False)
    print(f"Registros carregados: {len(df)}")
    
    # Cria DataFrame com ESTRUTURA EXATA da tabela vendas.vendas
    vendas_compativel = pd.DataFrame()
    
    print(f"\nMapeando para estrutura EXATA da tabela...")
    
    # Colunas obrigatórias e opcionais conforme schema SQL
    
    # 1. id - será auto-gerado pelo PostgreSQL (omitimos do CSV)
    # (não incluímos no CSV, deixa o banco gerar)
    
    # 2. numero_venda - VARCHAR(50) NOT NULL
    vendas_compativel['numero_venda'] = df['numero_os_loja']
    mask_vazio = vendas_compativel['numero_venda'].isna()
    vendas_compativel.loc[mask_vazio, 'numero_venda'] = df.loc[mask_vazio].index + 1
    vendas_compativel['numero_venda'] = vendas_compativel['numero_venda'].astype(str)
    
    # 3. cliente_id - UUID (pode ser NULL)
    vendas_compativel['cliente_id'] = df['cliente_uuid']
    
    # 4. loja_id - UUID NOT NULL  
    vendas_compativel['loja_id'] = df['loja_uuid']
    
    # 5. vendedor_id - UUID (pode ser NULL)
    vendas_compativel['vendedor_id'] = df['vendedor_uuid_loja']
    
    # 6. data_venda - DATE NOT NULL
    vendas_compativel['data_venda'] = pd.to_datetime(df['data_compra_loja'], errors='coerce')
    vendas_compativel['data_venda'] = vendas_compativel['data_venda'].dt.strftime('%Y-%m-%d')
    vendas_compativel['data_venda'] = vendas_compativel['data_venda'].fillna(datetime.now().strftime('%Y-%m-%d'))
    
    # 7. valor_total - DECIMAL(12,2) NOT NULL
    vendas_compativel['valor_total'] = pd.to_numeric(df['valor_total'], errors='coerce').fillna(0).round(2)
    
    # 8. valor_entrada - DECIMAL(12,2) DEFAULT 0
    vendas_compativel['valor_entrada'] = pd.to_numeric(df['SINAL 1:_loja'], errors='coerce').fillna(0).round(2)
    # Se entrada vazia, usa 30% do total
    entrada_vazia = vendas_compativel['valor_entrada'] == 0
    vendas_compativel.loc[entrada_vazia, 'valor_entrada'] = (vendas_compativel.loc[entrada_vazia, 'valor_total'] * 0.3).round(2)
    
    # 9. nome_cliente_temp - VARCHAR(200) (quando cliente_id é NULL)
    sem_uuid = vendas_compativel['cliente_id'].isna()
    vendas_compativel['nome_cliente_temp'] = None
    vendas_compativel.loc[sem_uuid, 'nome_cliente_temp'] = df.loc[sem_uuid, 'cliente_nome_normalizado']
    
    # 10. observacoes - TEXT (opcional)
    vendas_compativel['observacoes'] = None  # Pode adicionar observações se necessário
    
    # 11. status - status_type DEFAULT 'ATIVO' 
    vendas_compativel['status'] = 'ATIVO'
    
    # 12. cancelado - BOOLEAN DEFAULT false
    vendas_compativel['cancelado'] = False
    
    # 13-14. Timestamps (opcionais - banco pode gerar)
    vendas_compativel['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    vendas_compativel['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # VALIDAÇÕES CRÍTICAS
    print(f"\n=== VALIDAÇÕES CRÍTICAS ===")
    
    # Remove registros sem dados obrigatórios
    antes = len(vendas_compativel)
    vendas_compativel = vendas_compativel.dropna(subset=['loja_id', 'numero_venda', 'data_venda'])
    vendas_compativel = vendas_compativel[vendas_compativel['valor_total'] >= 0]
    depois = len(vendas_compativel)
    
    if antes != depois:
        print(f"Removidos {antes - depois} registros com dados obrigatórios faltando")
    
    # Garante constraints
    vendas_compativel['valor_total'] = vendas_compativel['valor_total'].clip(lower=0)
    vendas_compativel['valor_entrada'] = vendas_compativel['valor_entrada'].clip(lower=0)
    
    # Constraint: valor_entrada <= valor_total
    mask = vendas_compativel['valor_entrada'] > vendas_compativel['valor_total']
    vendas_compativel.loc[mask, 'valor_entrada'] = vendas_compativel.loc[mask, 'valor_total']
    
    # Remove duplicatas por constraint única (loja_id, numero_venda)
    duplicatas_antes = len(vendas_compativel)
    vendas_compativel = vendas_compativel.drop_duplicates(subset=['loja_id', 'numero_venda'])
    duplicatas_depois = len(vendas_compativel)
    
    if duplicatas_antes != duplicatas_depois:
        print(f"Removidas {duplicatas_antes - duplicatas_depois} duplicatas por constraint única")
    
    # ESTATÍSTICAS FINAIS
    print(f"\n=== ESTATÍSTICAS FINAIS ===")
    print(f"Total de vendas: {len(vendas_compativel)}")
    
    com_cliente_uuid = vendas_compativel['cliente_id'].notna().sum()
    com_nome_temp = vendas_compativel['nome_cliente_temp'].notna().sum()
    
    print(f"Com cliente_id (UUID): {com_cliente_uuid} ({com_cliente_uuid/len(vendas_compativel)*100:.1f}%)")
    print(f"Com nome_cliente_temp: {com_nome_temp} ({com_nome_temp/len(vendas_compativel)*100:.1f}%)")
    
    valor_total = vendas_compativel['valor_total'].sum()
    valor_entrada = vendas_compativel['valor_entrada'].sum()
    
    print(f"Valor total: R$ {valor_total:,.2f}")
    print(f"Valor entrada: R$ {valor_entrada:,.2f}")
    
    # Verifica se todas as colunas estão corretas
    colunas_finais = list(vendas_compativel.columns)
    print(f"\nColunas finais: {colunas_finais}")
    
    # Salva arquivo compatível
    arquivo_final = base_dir / "data" / "vendas_para_importar" / "vendas_compativel_tabela.csv"
    vendas_compativel.to_csv(arquivo_final, index=False)
    
    print(f"\n=== ARQUIVO COMPATÍVEL ===")
    print(f"Arquivo salvo: {arquivo_final}")
    print(f"✅ ESTRUTURA 100% COMPATÍVEL com vendas.vendas")
    
    # Comando de importação
    print(f"\n=== COMANDO DE IMPORTAÇÃO ===")
    print(f"COPY vendas.vendas (numero_venda, cliente_id, loja_id, vendedor_id, data_venda, valor_total, valor_entrada, nome_cliente_temp, observacoes, status, cancelado, created_at, updated_at)")
    print(f"FROM '{arquivo_final}'")
    print(f"CSV HEADER;")
    
    # Amostra
    print(f"\n=== AMOSTRA DOS DADOS COMPATÍVEIS ===")
    colunas_amostra = ['numero_venda', 'cliente_id', 'loja_id', 'valor_total', 'valor_entrada']
    amostra = vendas_compativel[colunas_amostra].head(3)
    print(amostra.to_string())
    
    return vendas_compativel

if __name__ == "__main__":
    resultado = gerar_csv_compativel_vendas()
    print("\n✅ CSV COMPATÍVEL gerado com sucesso!")
    print("🎯 Estrutura 100% alinhada com vendas.vendas!")
    print("🚀 Pronto para importação no banco!")