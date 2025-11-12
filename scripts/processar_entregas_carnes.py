#!/usr/bin/env python3
"""
Script para processar e consolidar entregas de carnes para tabela vendas.entregas_carne
"""

import pandas as pd
import json
import uuid
from pathlib import Path
from datetime import datetime
import numpy as np

def mapear_loja_uuid(nome_arquivo):
    """Mapear nome do arquivo para UUID da loja"""
    mapping = {
        'maua': ('9a22ccf1-36fe-4b9f-9391-ca31433dc31e', 'MAUÁ'),
        'perus': ('aa7a5646-f7d6-4239-831c-6602fbabb10a', 'PERUS'), 
        'rio_pequeno': ('9cb2c5a8-5f0c-4d9e-8c5a-5f3d2e9f8c6b', 'RIO PEQUENO'),
        'sao_mateus': ('7e8f9a2b-3c4d-5e6f-7a8b-9c0d1e2f3a4b', 'SÃO MATEUS'),
        'suzano2': ('1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d', 'SUZANO2'),
        'suzano': ('52f92716-d2ba-441a-ac3c-94bdfabd9722', 'SUZANO')
    }
    
    # Verificar suzano2 primeiro para evitar que seja capturado por suzano
    if 'suzano2' in nome_arquivo.lower():
        return mapping['suzano2']
    elif 'suzano' in nome_arquivo.lower():
        return mapping['suzano']
    
    for loja, (uuid_loja, nome_loja) in mapping.items():
        if loja in nome_arquivo.lower() and loja not in ['suzano', 'suzano2']:
            return uuid_loja, nome_loja
    
    return None, None

def processar_arquivo_entrega(arquivo_path):
    """Processa um arquivo individual de entrega de carnes"""
    print(f"Processando: {arquivo_path.name}")
    
    try:
        df = pd.read_csv(arquivo_path, dtype=str, low_memory=False)
        print(f"  - {len(df)} registros carregados")
        
        # Verificar se loja_id já existe no arquivo
        if 'loja_id' not in df.columns:
            loja_uuid, loja_nome = mapear_loja_uuid(arquivo_path.name)
            if not loja_uuid:
                print(f"  - ⚠️  Não foi possível identificar loja de {arquivo_path.name}")
                return pd.DataFrame()
            
            df['loja_id'] = loja_uuid
            df['loja_nome'] = loja_nome
        
        # Padronizar nomes das colunas
        df = df.rename(columns={
            'os': 'os_numero',
            'parcelas': 'parcela', 
            'data_movimento': 'data_entrega'
        })
        
        # Validar campos obrigatórios
        campos_obrigatorios = ['os_numero', 'valor_total', 'data_entrega', 'loja_id']
        for campo in campos_obrigatorios:
            if campo not in df.columns:
                print(f"  - ❌ Campo obrigatório ausente: {campo}")
                return pd.DataFrame()
        
        # Limpar e validar dados
        df_limpo = df.copy()
        
        # Remover registros com campos essenciais nulos
        antes = len(df_limpo)
        df_limpo = df_limpo.dropna(subset=['os_numero', 'valor_total', 'data_entrega'])
        depois = len(df_limpo)
        
        if antes != depois:
            print(f"  - {antes - depois} registros removidos por dados nulos")
        
        # Converter valor_total para numérico
        df_limpo['valor_total'] = pd.to_numeric(df_limpo['valor_total'], errors='coerce')
        
        # Remover valores zero ou negativos
        antes = len(df_limpo)
        df_limpo = df_limpo[df_limpo['valor_total'] > 0]
        depois = len(df_limpo)
        
        if antes != depois:
            print(f"  - {antes - depois} registros removidos por valor <= 0")
        
        # Converter data_entrega
        try:
            df_limpo['data_entrega'] = pd.to_datetime(df_limpo['data_entrega']).dt.date
        except Exception as e:
            print(f"  - ⚠️  Erro na conversão de data: {e}")
            return pd.DataFrame()
        
        # Padronizar os_numero como string
        df_limpo['os_numero'] = df_limpo['os_numero'].astype(str)
        
        # Padronizar parcela
        if 'parcela' in df_limpo.columns:
            df_limpo['parcela'] = df_limpo['parcela'].astype(str)
        else:
            df_limpo['parcela'] = '1'  # Default
        
        print(f"  - ✅ {len(df_limpo)} registros válidos")
        return df_limpo
        
    except Exception as e:
        print(f"  - ❌ Erro: {e}")
        return pd.DataFrame()

def buscar_venda_id_por_os(os_numero, vendas_df):
    """Busca venda_id baseado no número da OS"""
    if vendas_df.empty:
        return None
    
    # Tentar diferentes formas de match
    os_str = str(os_numero)
    
    # Match direto por numero_venda
    match_direto = vendas_df[vendas_df['numero_venda'].astype(str) == os_str]
    if not match_direto.empty:
        return match_direto.iloc[0]['id']
    
    # Match por numero_venda com .0
    match_decimal = vendas_df[vendas_df['numero_venda'].astype(str) == f"{os_str}.0"]
    if not match_decimal.empty:
        return match_decimal.iloc[0]['id']
    
    return None

def main():
    print("=== PROCESSAMENTO ENTREGAS DE CARNES ===")
    print(f"Início: {datetime.now()}")
    
    # Diretórios
    originais_dir = Path("data/originais/cxs/entrega_carnes/originais")
    processados_dir = Path("data/originais/cxs/entrega_carnes/processados")
    final_dir = Path("data/originais/cxs/entrega_carnes/final")
    
    # Buscar arquivos
    arquivos_entrega = list(originais_dir.glob("entrega_carne_*_final.csv"))
    
    if not arquivos_entrega:
        print("❌ Nenhum arquivo de entrega encontrado!")
        return
    
    print(f"\n1. Encontrados {len(arquivos_entrega)} arquivos:")
    for arquivo in arquivos_entrega:
        print(f"   - {arquivo.name}")
    
    # Carregar vendas para mapeamento venda_id
    print(f"\n2. Carregando vendas para mapeamento...")
    vendas_file = "data/vendas_para_importar/vendas_totais_com_uuid.csv"
    
    if Path(vendas_file).exists():
        vendas_df = pd.read_csv(vendas_file, dtype=str, low_memory=False)
        print(f"   - {len(vendas_df)} vendas carregadas")
    else:
        print(f"   - ⚠️  Arquivo de vendas não encontrado, venda_id será NULL")
        vendas_df = pd.DataFrame()
    
    # Processar cada arquivo
    print(f"\n3. Processando arquivos...")
    todos_registros = []
    estatisticas_por_loja = {}
    
    for arquivo in arquivos_entrega:
        df_entrega = processar_arquivo_entrega(arquivo)
        
        if not df_entrega.empty:
            loja_nome = df_entrega.iloc[0]['loja_nome'] if 'loja_nome' in df_entrega.columns else 'DESCONHECIDA'
            
            # Salvar arquivo processado individual
            arquivo_processado = processados_dir / f"{arquivo.stem}_processado.csv"
            df_entrega.to_csv(arquivo_processado, index=False, encoding='utf-8')
            
            todos_registros.append(df_entrega)
            estatisticas_por_loja[loja_nome] = {
                'arquivo': arquivo.name,
                'registros': len(df_entrega),
                'valor_total': df_entrega['valor_total'].sum(),
                'periodo': f"{df_entrega['data_entrega'].min()} a {df_entrega['data_entrega'].max()}"
            }
    
    if not todos_registros:
        print("❌ Nenhum registro válido encontrado!")
        return
    
    # Consolidar todos os registros
    print(f"\n4. Consolidando registros...")
    df_consolidado = pd.concat(todos_registros, ignore_index=True)
    print(f"   - {len(df_consolidado)} registros consolidados")
    
    # Buscar venda_id para cada entrega
    print(f"\n5. Mapeando venda_id...")
    venda_ids_encontrados = 0
    
    df_consolidado['venda_id'] = df_consolidado['os_numero'].apply(
        lambda os_num: buscar_venda_id_por_os(os_num, vendas_df)
    )
    
    venda_ids_encontrados = df_consolidado['venda_id'].notna().sum()
    print(f"   - {venda_ids_encontrados} venda_id encontrados ({venda_ids_encontrados/len(df_consolidado)*100:.1f}%)")
    
    # Preparar estrutura final para tabela
    print(f"\n6. Preparando estrutura final...")
    
    df_final = pd.DataFrame()
    df_final['id'] = [str(uuid.uuid4()) for _ in range(len(df_consolidado))]
    df_final['venda_id'] = df_consolidado['venda_id']
    df_final['loja_id'] = df_consolidado['loja_id']
    df_final['os_numero'] = df_consolidado['os_numero']
    df_final['parcela'] = df_consolidado['parcela']
    df_final['data_entrega'] = df_consolidado['data_entrega']
    df_final['valor_total'] = df_consolidado['valor_total']
    df_final['observacoes'] = df_consolidado.get('observacoes')
    
    # Timestamps
    timestamp_now = datetime.now().isoformat()
    df_final['created_at'] = timestamp_now
    df_final['updated_at'] = timestamp_now
    df_final['deleted_at'] = None
    
    # Validação final
    print(f"\n7. Validação final...")
    
    # Verificar campos obrigatórios
    campos_obrigatorios = ['id', 'loja_id', 'data_entrega', 'valor_total']
    erros = []
    
    for campo in campos_obrigatorios:
        nulos = df_final[campo].isna().sum()
        if nulos > 0:
            erros.append(f"{campo}: {nulos} valores nulos")
        else:
            print(f"   ✅ {campo}: OK")
    
    # Verificar valores positivos
    if (df_final['valor_total'] <= 0).any():
        erros.append("Valores <= 0 encontrados")
    else:
        print(f"   ✅ valor_total > 0: OK")
    
    if erros:
        print(f"   ❌ Erros encontrados:")
        for erro in erros:
            print(f"      - {erro}")
        return
    
    # Estatísticas finais
    print(f"\n=== ESTATÍSTICAS FINAIS ===")
    print(f"Total de entregas: {len(df_final)}")
    print(f"Período: {df_final['data_entrega'].min()} a {df_final['data_entrega'].max()}")
    print(f"Valor total: R$ {df_final['valor_total'].sum():,.2f}")
    print(f"Entregas com venda_id: {df_final['venda_id'].notna().sum()}")
    
    print(f"\nPor loja:")
    for loja, stats in estatisticas_por_loja.items():
        print(f"  {loja}: {stats['registros']} entregas, R$ {stats['valor_total']:,.2f}")
        print(f"    Período: {stats['periodo']}")
    
    # Salvar arquivo final
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    arquivo_final = final_dir / f"ENTREGAS_CARNE_FINAL_{timestamp}.csv"
    
    df_final.to_csv(arquivo_final, index=False, encoding='utf-8')
    print(f"\n✅ ARQUIVO FINAL SALVO: {arquivo_final}")
    
    # Salvar relatório
    relatorio = {
        'timestamp': timestamp,
        'total_entregas': len(df_final),
        'valor_total': float(df_final['valor_total'].sum()),
        'periodo_inicio': str(df_final['data_entrega'].min()),
        'periodo_fim': str(df_final['data_entrega'].max()),
        'entregas_com_venda_id': int(df_final['venda_id'].notna().sum()),
        'taxa_mapeamento_vendas': f"{venda_ids_encontrados/len(df_consolidado)*100:.1f}%",
        'estatisticas_por_loja': estatisticas_por_loja,
        'arquivos_processados': [f.name for f in arquivos_entrega]
    }
    
    arquivo_relatorio = final_dir / f"RELATORIO_ENTREGAS_CARNE_{timestamp}.json"
    with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"Relatório: {arquivo_relatorio}")
    
    # Comando SQL
    print(f"\n📋 COMANDO SQL PARA IMPORTAÇÃO:")
    print(f"```sql")
    print(f"COPY vendas.entregas_carne (")
    print(f"    id, venda_id, loja_id, os_numero, parcela,")
    print(f"    data_entrega, valor_total, observacoes,")
    print(f"    created_at, updated_at, deleted_at")
    print(f") FROM '{arquivo_final.name}'")
    print(f"WITH (FORMAT CSV, HEADER);")
    print(f"```")
    
    print(f"\n🎉 ENTREGAS DE CARNES PROCESSADAS COM SUCESSO!")
    print(f"Fim: {datetime.now()}")
    
    return arquivo_final

if __name__ == "__main__":
    main()