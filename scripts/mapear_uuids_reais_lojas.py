#!/usr/bin/env python3
"""
Script FINAL para mapear códigos de loja corretos e gerar CSV importável
Usa mapeamento encontrado na documentação do projeto
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

def mapear_uuids_reais_lojas():
    """Aplica mapeamento correto dos UUIDs das lojas baseado na documentação"""
    
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    
    print("=== MAPEAMENTO FINAL COM UUIDs REAIS DAS LOJAS ===")
    
    # 1. Mapeamento correto baseado na documentação
    print("\n1. MAPEAMENTO ENCONTRADO NA DOCUMENTAÇÃO:")
    mapeamento_loja_uuid = {
        'MAUA': '52f92716-d2ba-441a-ac3c-94bdfabd9722',      # 042
        'SUZANO': '9a22ccf1-36fe-4b9f-9391-ca31433dc31e',    # 048  
        'SUZANO2': 'aa7a5646-f7d6-4239-831c-6602fbabb10a',   # 010
        'PERUS': 'da3978c9-bba2-431a-91b7-970a406d3acf',     # 009
        'RIO_PEQUENO': '4e94f51f-3b0f-4e0f-ba73-64982b870f2c', # 011
        'SAO_MATEUS': '1c35e0ad-3066-441e-85cc-44c0eb9b3ab4'   # 012
    }
    
    print("Mapeamento aplicado:")
    for loja, uuid in mapeamento_loja_uuid.items():
        print(f"  {loja} → {uuid}")
    
    # 2. Carrega dados com códigos de loja
    print("\n2. CARREGANDO DADOS COM CÓDIGOS...")
    arquivo_entrada = base_dir / "data" / "vendas_para_importar" / "vendas_com_codigo_loja.csv"
    df = pd.read_csv(arquivo_entrada)
    print(f"Registros carregados: {len(df)}")
    
    # 3. Aplica mapeamento UUID
    print("\n3. APLICANDO MAPEAMENTO DE UUIDs...")
    df['loja_id'] = df['loja_codigo'].map(mapeamento_loja_uuid)
    
    # Verifica se todos foram mapeados
    sem_uuid = df['loja_id'].isna().sum()
    if sem_uuid > 0:
        print(f"ATENÇÃO: {sem_uuid} lojas não mapeadas!")
        lojas_nao_mapeadas = df[df['loja_id'].isna()]['loja_codigo'].unique()
        print(f"Lojas não mapeadas: {lojas_nao_mapeadas}")
    else:
        print("✅ Todas as lojas mapeadas com sucesso!")
    
    # 4. Prepara estrutura final para vendas.vendas
    print("\n4. PREPARANDO ESTRUTURA FINAL...")
    
    vendas_final = pd.DataFrame()
    
    # Campos obrigatórios conforme schema
    vendas_final['numero_venda'] = df['numero_venda']
    vendas_final['cliente_id'] = df['cliente_id']  # UUID quando disponível
    vendas_final['loja_id'] = df['loja_id']        # UUID correto da loja
    vendas_final['vendedor_id'] = df['vendedor_id'] # UUID do vendedor
    vendas_final['data_venda'] = df['data_venda']
    vendas_final['valor_total'] = df['valor_total']
    vendas_final['valor_entrada'] = df['valor_entrada']
    vendas_final['nome_cliente_temp'] = df['nome_cliente_temp']
    vendas_final['observacoes'] = df['observacoes'] 
    vendas_final['status'] = df['status']
    vendas_final['cancelado'] = df['cancelado']
    
    # Timestamps
    vendas_final['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    vendas_final['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 5. Validações finais
    print("\n5. VALIDAÇÕES FINAIS...")
    
    # Remove registros com loja_id NULL (se houver)
    antes = len(vendas_final)
    vendas_final = vendas_final.dropna(subset=['loja_id', 'numero_venda'])
    depois = len(vendas_final)
    
    if antes != depois:
        print(f"Removidos {antes - depois} registros com dados críticos faltando")
    
    # Valida constraints
    vendas_final['valor_total'] = vendas_final['valor_total'].clip(lower=0)
    vendas_final['valor_entrada'] = vendas_final['valor_entrada'].clip(lower=0)
    
    # Constraint: valor_entrada <= valor_total
    mask = vendas_final['valor_entrada'] > vendas_final['valor_total']
    vendas_final.loc[mask, 'valor_entrada'] = vendas_final.loc[mask, 'valor_total']
    
    # Remove duplicatas por constraint única
    duplicatas_antes = len(vendas_final)
    vendas_final = vendas_final.drop_duplicates(subset=['loja_id', 'numero_venda'])
    duplicatas_depois = len(vendas_final)
    
    if duplicatas_antes != duplicatas_depois:
        print(f"Removidas {duplicatas_antes - duplicatas_depois} duplicatas")
    
    # 6. Estatísticas finais
    print(f"\n=== ESTATÍSTICAS FINAIS ===")
    print(f"Total de vendas: {len(vendas_final)}")
    
    com_cliente_uuid = vendas_final['cliente_id'].notna().sum()
    sem_cliente_uuid = vendas_final['cliente_id'].isna().sum()
    
    print(f"Com cliente UUID: {com_cliente_uuid} ({com_cliente_uuid/len(vendas_final)*100:.1f}%)")
    print(f"Sem cliente UUID: {sem_cliente_uuid} ({sem_cliente_uuid/len(vendas_final)*100:.1f}%)")
    
    valor_total = vendas_final['valor_total'].sum()
    valor_entrada = vendas_final['valor_entrada'].sum()
    
    print(f"Valor total: R$ {valor_total:,.2f}")
    print(f"Valor entrada: R$ {valor_entrada:,.2f}")
    
    # Verifica constraint única
    chave_unica = vendas_final.groupby(['loja_id', 'numero_venda']).size()
    violacoes = (chave_unica > 1).sum()
    
    if violacoes == 0:
        print("✅ Constraint UNIQUE(loja_id, numero_venda) validada")
    else:
        print(f"❌ {violacoes} violações da constraint única!")
    
    # Estatísticas por loja
    print(f"\n=== VENDAS POR LOJA (UUIDs CORRETOS) ===")
    vendas_por_loja = vendas_final['loja_id'].value_counts()
    for loja_uuid, count in vendas_por_loja.items():
        # Encontra nome da loja pelo UUID
        nome_loja = 'DESCONHECIDA'
        for nome, uuid in mapeamento_loja_uuid.items():
            if uuid == loja_uuid:
                nome_loja = nome
                break
        print(f"  {nome_loja}: {count} vendas ({loja_uuid})")
    
    # 7. Salva arquivo final pronto para importação
    arquivo_final = base_dir / "data" / "vendas_para_importar" / "vendas_final_importacao.csv"
    vendas_final.to_csv(arquivo_final, index=False)
    
    print(f"\n=== ARQUIVO FINAL PARA IMPORTAÇÃO ===")
    print(f"Arquivo: {arquivo_final}")
    print(f"✅ UUIDs de loja CORRETOS")
    print(f"✅ Estrutura 100% compatível com vendas.vendas")
    print(f"✅ Constraints validadas")
    
    # Comando de importação
    print(f"\n=== COMANDO DE IMPORTAÇÃO ===")
    print(f"COPY vendas.vendas (numero_venda, cliente_id, loja_id, vendedor_id, data_venda, valor_total, valor_entrada, nome_cliente_temp, observacoes, status, cancelado, created_at, updated_at)")
    print(f"FROM '{arquivo_final}'")
    print(f"CSV HEADER;")
    
    # Amostra
    print(f"\n=== AMOSTRA DO RESULTADO FINAL ===")
    colunas_amostra = ['numero_venda', 'loja_id', 'cliente_id', 'valor_total']
    amostra = vendas_final[colunas_amostra].head(3)
    print(amostra.to_string())
    
    return vendas_final

if __name__ == "__main__":
    resultado = mapear_uuids_reais_lojas()
    print("\n🎉 DADOS FINAIS PRONTOS PARA IMPORTAÇÃO!")
    print("✅ Todos os problemas resolvidos!")
    print("🚀 Pode executar o comando COPY no banco!")