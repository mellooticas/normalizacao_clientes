#!/usr/bin/env python3
"""
Script para corrigir venda_id usando UUIDs reais das vendas
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

def main():
    print("=== CORREÇÃO FINAL VENDA_ID COM UUIDS REAIS ===")
    print(f"Início: {datetime.now()}")
    
    # Carregar arquivo atual
    arquivo_atual = "data/processados/OSS_ITENS_TABELA_REAL_20251105_143427.csv"
    print(f"\n1. Carregando: {arquivo_atual}")
    df_itens = pd.read_csv(arquivo_atual, dtype=str, low_memory=False)
    print(f"   - {len(df_itens)} itens carregados")
    
    # Carregar vendas com UUID
    vendas_uuid_file = "data/vendas_para_importar/vendas_totais_com_uuid.csv"
    print(f"2. Carregando vendas com UUID: {vendas_uuid_file}")
    df_vendas_uuid = pd.read_csv(vendas_uuid_file, dtype=str, low_memory=False)
    print(f"   - {len(df_vendas_uuid)} vendas carregadas")
    
    # Criar mapeamento numero_venda -> UUID
    print(f"3. Criando mapeamento número -> UUID...")
    venda_mapping = {}
    
    for _, venda in df_vendas_uuid.iterrows():
        numero = str(venda['numero_venda']).replace('.0', '')
        uuid_venda = venda['id']
        venda_mapping[numero] = uuid_venda
    
    print(f"   - {len(venda_mapping)} vendas mapeadas")
    
    # Corrigir venda_id nos itens
    print(f"4. Corrigindo venda_id...")
    
    itens_corrigidos = 0
    itens_sem_venda = 0
    
    for idx, item in df_itens.iterrows():
        numero_venda = str(item['venda_id'])
        
        if numero_venda in venda_mapping:
            df_itens.at[idx, 'venda_id'] = venda_mapping[numero_venda]
            itens_corrigidos += 1
        else:
            # Item sem venda correspondente - vamos manter para análise
            itens_sem_venda += 1
            print(f"   ⚠️  Venda não encontrada: {numero_venda}")
    
    print(f"   - {itens_corrigidos} itens com venda_id corrigido")
    print(f"   - {itens_sem_venda} itens sem venda correspondente")
    
    # Remover itens sem venda válida para garantir integridade referencial
    if itens_sem_venda > 0:
        print(f"5. Removendo itens sem venda válida...")
        df_itens_validos = df_itens[df_itens['venda_id'].isin(venda_mapping.values())].copy()
        print(f"   - {len(df_itens_validos)} itens mantidos")
    else:
        df_itens_validos = df_itens.copy()
    
    # Validação final
    print(f"\n6. Validação final...")
    
    # Verificar se todos os venda_id são UUIDs válidos
    uuids_vendas = set(df_vendas_uuid['id'].dropna())
    venda_ids_itens = set(df_itens_validos['venda_id'].dropna())
    
    vendas_validas = venda_ids_itens.intersection(uuids_vendas)
    vendas_invalidas = venda_ids_itens - uuids_vendas
    
    print(f"   - Vendas válidas: {len(vendas_validas)}")
    print(f"   - Vendas inválidas: {len(vendas_invalidas)}")
    
    if vendas_invalidas:
        print(f"   ❌ Ainda há venda_id inválidos!")
        for venda_id in list(vendas_invalidas)[:5]:
            print(f"      - {venda_id}")
        return
    
    print(f"   ✅ Todos os venda_id são válidos!")
    
    # Estatísticas finais
    print(f"\n=== ESTATÍSTICAS FINAIS ===")
    print(f"Total de itens válidos: {len(df_itens_validos)}")
    print(f"Vendas únicas referenciadas: {df_itens_validos['venda_id'].nunique()}")
    
    valor_total = pd.to_numeric(df_itens_validos['valor_unitario'], errors='coerce').sum()
    print(f"Valor total: R$ {valor_total:,.2f}")
    
    # Distribuição por tipo
    tipo_counts = df_itens_validos['tipo_produto'].value_counts()
    print(f"Distribuição por tipo:")
    for tipo, count in tipo_counts.items():
        print(f"  - {tipo}: {count}")
    
    # Salvar arquivo final
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    arquivo_final = Path("data/processados") / f"OSS_ITENS_FINAL_CORRIGIDO_{timestamp}.csv"
    
    df_itens_validos.to_csv(arquivo_final, index=False, encoding='utf-8')
    
    print(f"\n✅ ARQUIVO FINAL SALVO: {arquivo_final}")
    
    print(f"\n📋 COMANDO SQL PARA IMPORTAÇÃO:")
    print(f"```sql")
    print(f"-- Verificar se todas as vendas existem")
    print(f"SELECT COUNT(*) as vendas_existentes FROM vendas.vendas ")
    print(f"WHERE id IN (SELECT DISTINCT venda_id FROM temp_itens);")
    print(f"")
    print(f"-- Importar itens")
    print(f"COPY vendas.itens_venda (")
    print(f"    id, venda_id, tipo_produto, descricao, marca, modelo,")
    print(f"    codigo_produto, codigo_barras, cor, tamanho, material,")
    print(f"    fornecedor, codigo_fornecedor, quantidade, valor_unitario,")
    print(f"    valor_desconto, possui_estoque, requer_encomenda,")
    print(f"    data_encomenda, data_prevista_chegada, observacoes,")
    print(f"    created_at, updated_at, deleted_at, updated_by")
    print(f") FROM '{arquivo_final.name}'")
    print(f"WITH (FORMAT CSV, HEADER);")
    print(f"```")
    
    print(f"\n🎉 PRONTO PARA IMPORTAÇÃO COM INTEGRIDADE REFERENCIAL!")
    print(f"Fim: {datetime.now()}")
    
    return arquivo_final

if __name__ == "__main__":
    main()