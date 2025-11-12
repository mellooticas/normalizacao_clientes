#!/usr/bin/env python3
"""
Script para corrigir venda_id e criar versão final limpa para Supabase
"""

import pandas as pd
import uuid
from pathlib import Path
from datetime import datetime

def main():
    print("=== CORREÇÃO FINAL VENDA_ID OSS ===")
    print(f"Início: {datetime.now()}")
    
    # Carregar dados
    matches_files = list(Path("data/processados").glob("OSS_ITENS_MATCHES_PARA_SUPABASE_*.csv"))
    matches_file = sorted(matches_files)[-1]
    
    print(f"\n1. Carregando: {matches_file}")
    df_matches = pd.read_csv(matches_file, dtype=str, low_memory=False)
    print(f"   - {len(df_matches)} itens carregados")
    
    # Carregar vendas para mapeamento correto
    vendas_file = "data/vendas_para_importar/vendas_TODAS_RENUMERADAS_SEM_DUPLICATAS.csv"
    df_vendas = pd.read_csv(vendas_file, dtype=str, low_memory=False)
    print(f"   - {len(df_vendas)} vendas carregadas")
    
    # Criar mapeamento numero_venda -> UUID
    print(f"\n2. Criando mapeamento de vendas...")
    venda_uuid_map = {}
    for _, venda in df_vendas.iterrows():
        numero = str(venda['numero_venda'])
        # Usar numero_venda como base para venda_id consistente
        venda_uuid_map[numero] = f"venda_{numero}"
    
    print(f"   - {len(venda_uuid_map)} vendas mapeadas")
    
    # Corrigir venda_id nos itens
    print(f"\n3. Corrigindo venda_id...")
    df_corrigido = df_matches.copy()
    
    vendas_corrigidas = 0
    vendas_novas = 0
    
    for idx, item in df_corrigido.iterrows():
        venda_id_original = str(item['venda_id'])
        
        if venda_id_original in venda_uuid_map:
            # Usar ID consistente baseado no número
            df_corrigido.at[idx, 'venda_id'] = venda_uuid_map[venda_id_original]
            vendas_corrigidas += 1
        else:
            # Criar nova venda para itens órfãos
            df_corrigido.at[idx, 'venda_id'] = f"nova_venda_{str(uuid.uuid4())[:8]}"
            vendas_novas += 1
    
    print(f"   - {vendas_corrigidas} vendas mapeadas")
    print(f"   - {vendas_novas} novas vendas criadas")
    
    # Garantir campos obrigatórios
    print(f"\n4. Finalizando estrutura...")
    
    # Garantir que quantidade é número
    df_corrigido['quantidade'] = df_corrigido['quantidade'].fillna('1').astype(str)
    
    # Garantir que valores são numéricos válidos
    for col in ['valor_unitario', 'valor_total', 'desconto']:
        df_corrigido[col] = pd.to_numeric(df_corrigido[col], errors='coerce').fillna(0)
    
    # Garantir timestamps
    timestamp_now = datetime.now().isoformat()
    df_corrigido['created_at'] = df_corrigido['created_at'].fillna(timestamp_now)
    df_corrigido['updated_at'] = df_corrigido['updated_at'].fillna(timestamp_now)
    
    # Limpar campos vazios
    df_corrigido['observacoes'] = df_corrigido['observacoes'].fillna('')
    df_corrigido['produto_descricao'] = df_corrigido['produto_descricao'].fillna('')
    
    print(f"   - Estrutura finalizada: {len(df_corrigido)} itens")
    
    # Validação final
    print(f"\n5. Validação final...")
    
    # Verificar campos obrigatórios
    campos_obrigatorios = ['item_venda_uuid', 'venda_id', 'produto_codigo']
    erro_validacao = False
    
    for campo in campos_obrigatorios:
        nulos = df_corrigido[campo].isna().sum()
        if nulos == 0:
            print(f"   ✅ {campo}: OK")
        else:
            print(f"   ❌ {campo}: {nulos} valores nulos!")
            erro_validacao = True
    
    # Verificar UUIDs únicos
    uuids = df_corrigido['item_venda_uuid'].dropna()
    if uuids.nunique() == len(uuids):
        print(f"   ✅ UUIDs únicos: OK")
    else:
        print(f"   ❌ UUIDs duplicados!")
        erro_validacao = True
    
    # Estatísticas finais
    valor_total = df_corrigido['valor_total'].sum()
    produtos_unicos = df_corrigido['produto_codigo'].nunique()
    
    print(f"\n=== ESTATÍSTICAS FINAIS ===")
    print(f"Total de itens: {len(df_corrigido)}")
    print(f"Produtos únicos: {produtos_unicos}")
    print(f"Valor total: R$ {valor_total:,.2f}")
    print(f"Vendas mapeadas: {vendas_corrigidas}")
    print(f"Novas vendas: {vendas_novas}")
    
    if erro_validacao:
        print(f"❌ ERRO NA VALIDAÇÃO!")
        return
    
    # Salvar versão final
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Arquivo final para Supabase
    arquivo_final = Path("data/processados") / f"OSS_ITENS_FINAL_SUPABASE_{timestamp}.csv"
    
    # Ordenar colunas para Supabase
    colunas_finais = [
        'item_venda_uuid', 'venda_id', 'produto_codigo', 'produto_descricao',
        'quantidade', 'valor_unitario', 'valor_total', 'desconto', 'observacoes',
        'created_at', 'updated_at'
    ]
    
    df_final = df_corrigido[colunas_finais]
    df_final.to_csv(arquivo_final, index=False, encoding='utf-8')
    
    print(f"\n✅ ARQUIVO FINAL SALVO: {arquivo_final}")
    print(f"🎉 PRONTO PARA IMPORTAÇÃO NO SUPABASE!")
    
    print(f"\nComando SQL para importação:")
    print(f"```sql")
    print(f"COPY itens_venda (")
    print(f"    item_venda_uuid, venda_id, produto_codigo, produto_descricao,")
    print(f"    quantidade, valor_unitario, valor_total, desconto, observacoes,")
    print(f"    created_at, updated_at")
    print(f") FROM '{arquivo_final.name}'")
    print(f"WITH (FORMAT CSV, HEADER);")
    print(f"```")
    
    print(f"\nFim: {datetime.now()}")
    return arquivo_final

if __name__ == "__main__":
    main()