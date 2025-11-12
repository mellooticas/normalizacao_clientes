#!/usr/bin/env python3
"""
Script para validar dados OSS antes da importação no Supabase
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime

def validar_dados_oss():
    print("=== VALIDAÇÃO FINAL DADOS OSS ===")
    print(f"Início: {datetime.now()}")
    
    # Carregar arquivo de matches
    matches_files = list(Path("data/processados").glob("OSS_ITENS_MATCHES_PARA_SUPABASE_*.csv"))
    if not matches_files:
        print("❌ Arquivo de matches não encontrado!")
        return
    
    matches_file = sorted(matches_files)[-1]
    print(f"\n1. Carregando: {matches_file}")
    df_matches = pd.read_csv(matches_file, dtype=str, low_memory=False)
    print(f"   ✅ {len(df_matches)} itens carregados")
    
    # Carregar vendas para validação
    vendas_file = "data/vendas_para_importar/vendas_TODAS_RENUMERADAS_SEM_DUPLICATAS.csv"
    print(f"\n2. Carregando vendas: {vendas_file}")
    df_vendas = pd.read_csv(vendas_file, dtype=str, low_memory=False)
    print(f"   ✅ {len(df_vendas)} vendas carregadas")
    
    # Validações
    validacoes = {
        'total_itens': len(df_matches),
        'itens_com_uuid': 0,
        'itens_com_venda_id': 0,
        'vendas_validas': 0,
        'vendas_invalidas': 0,
        'produtos_unicos': 0,
        'valor_total': 0.0,
        'itens_zerados': 0,
        'erros': []
    }
    
    print(f"\n3. Executando validações...")
    
    # Validação 1: UUIDs únicos
    uuids = df_matches['item_venda_uuid'].dropna()
    uuids_unicos = uuids.nunique()
    validacoes['itens_com_uuid'] = len(uuids)
    
    if uuids_unicos == len(uuids):
        print("   ✅ Todos os UUIDs são únicos")
    else:
        print(f"   ❌ {len(uuids) - uuids_unicos} UUIDs duplicados!")
        validacoes['erros'].append(f"UUIDs duplicados: {len(uuids) - uuids_unicos}")
    
    # Validação 2: venda_id válidos
    venda_ids = df_matches['venda_id'].dropna()
    validacoes['itens_com_venda_id'] = len(venda_ids)
    
    # Converter números de venda para comparação
    vendas_numeros = set()
    for num in df_vendas['numero_venda'].dropna():
        try:
            vendas_numeros.add(str(float(num)))
        except:
            pass
    
    vendas_validas = 0
    vendas_invalidas = 0
    
    for venda_id in venda_ids:
        if str(venda_id) in vendas_numeros:
            vendas_validas += 1
        else:
            vendas_invalidas += 1
    
    validacoes['vendas_validas'] = vendas_validas
    validacoes['vendas_invalidas'] = vendas_invalidas
    
    if vendas_invalidas == 0:
        print("   ✅ Todos os venda_id são válidos")
    else:
        print(f"   ⚠️  {vendas_invalidas} venda_id inválidos")
        validacoes['erros'].append(f"venda_id inválidos: {vendas_invalidas}")
    
    # Validação 3: Produtos únicos
    produtos = df_matches['produto_codigo'].dropna()
    validacoes['produtos_unicos'] = produtos.nunique()
    print(f"   ✅ {validacoes['produtos_unicos']} produtos únicos")
    
    # Validação 4: Valores
    valores_validos = 0
    valores_zerados = 0
    valor_total = 0.0
    
    for valor in df_matches['valor_total'].dropna():
        try:
            v = float(valor)
            if v == 0:
                valores_zerados += 1
            else:
                valores_validos += 1
                valor_total += v
        except:
            pass
    
    validacoes['valor_total'] = valor_total
    validacoes['itens_zerados'] = valores_zerados
    
    print(f"   ✅ Valor total: R$ {valor_total:,.2f}")
    print(f"   ℹ️  Itens zerados: {valores_zerados}")
    
    # Validação 5: Campos obrigatórios
    campos_obrigatorios = ['item_venda_uuid', 'venda_id', 'produto_codigo']
    for campo in campos_obrigatorios:
        nulos = df_matches[campo].isna().sum()
        if nulos == 0:
            print(f"   ✅ {campo}: sem valores nulos")
        else:
            print(f"   ❌ {campo}: {nulos} valores nulos!")
            validacoes['erros'].append(f"{campo} nulos: {nulos}")
    
    # Análise por loja (se disponível no arquivo completo)
    arquivo_completo = str(matches_file).replace('_MATCHES_PARA_SUPABASE_', '_CRUZADOS_POR_NUMERO_')
    if Path(arquivo_completo).exists():
        print(f"\n4. Análise por loja...")
        df_completo = pd.read_csv(arquivo_completo, dtype=str, low_memory=False)
        
        if 'loja_nome' in df_completo.columns:
            por_loja = df_completo.groupby('loja_nome').agg({
                'item_venda_uuid': 'count',
                'valor_total': lambda x: pd.to_numeric(x, errors='coerce').sum()
            }).round(2)
            
            print("   Distribuição por loja:")
            for loja, row in por_loja.iterrows():
                print(f"     {loja}: {row['item_venda_uuid']} itens, R$ {row['valor_total']:,.2f}")
    
    # Validação final
    print(f"\n=== RESULTADO DA VALIDAÇÃO ===")
    
    if not validacoes['erros']:
        print("🎉 VALIDAÇÃO PASSOU - DADOS PRONTOS PARA IMPORTAÇÃO!")
        status = "APROVADO"
    else:
        print("⚠️  VALIDAÇÃO COM RESSALVAS:")
        for erro in validacoes['erros']:
            print(f"   - {erro}")
        status = "APROVADO_COM_RESSALVAS"
    
    print(f"\nResumo:")
    print(f"  - Total de itens: {validacoes['total_itens']}")
    print(f"  - Vendas válidas: {validacoes['vendas_validas']}")
    print(f"  - Produtos únicos: {validacoes['produtos_unicos']}")
    print(f"  - Valor total: R$ {validacoes['valor_total']:,.2f}")
    print(f"  - Status: {status}")
    
    # Salvar relatório de validação
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    relatorio_validacao = {
        'timestamp': timestamp,
        'arquivo_validado': str(matches_file),
        'status_validacao': status,
        'estatisticas': validacoes,
        'recomendacao': "IMPORTAR" if status == "APROVADO" else "REVISAR_ERROS"
    }
    
    arquivo_relatorio = Path("data/processados") / f"VALIDACAO_OSS_FINAL_{timestamp}.json"
    with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
        json.dump(relatorio_validacao, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\nRelatório salvo: {arquivo_relatorio}")
    print(f"Fim: {datetime.now()}")
    
    return status == "APROVADO"

if __name__ == "__main__":
    validar_dados_oss()