#!/usr/bin/env python3
"""
Script para normalizar entregas de carnes com divisão de parcelas
1. Primeiro normaliza e mapeia todos os UUIDs
2. Depois divide as linhas conforme número de parcelas
"""

import pandas as pd
import json
import uuid
from pathlib import Path
from datetime import datetime, date
import numpy as np
from dateutil.relativedelta import relativedelta

def mapear_loja_uuid(nome_arquivo):
    """Mapear nome do arquivo para UUID da loja - CORRIGIDO COM IDS REAIS SUPABASE"""
    mapping = {
        'maua': ('9a22ccf1-36fe-4b9f-9391-ca31433dc31e', 'MAUÁ'),
        'perus': ('da3978c9-bba2-431a-91b7-970a406d3acf', 'PERUS'), 
        'rio_pequeno': ('4e94f51f-3b0f-4e0f-ba73-64982b870f2c', 'RIO PEQUENO'),
        'sao_mateus': ('1c35e0ad-3066-441e-85cc-44c0eb9b3ab4', 'SÃO MATEUS'),
        'suzano2': ('aa7a5646-f7d6-4239-831c-6602fbabb10a', 'SUZANO2'),
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

def buscar_venda_id_por_os(os_numero, vendas_df):
    """Busca venda_id baseado no número da OS"""
    if vendas_df.empty:
        return None
    
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

def dividir_parcelas(row):
    """Divide uma linha em múltiplas parcelas"""
    parcelas = []
    
    try:
        num_parcelas = int(row['parcela'])
        if num_parcelas <= 0:
            num_parcelas = 1
    except (ValueError, TypeError):
        num_parcelas = 1
    
    valor_total = float(row['valor_total'])
    valor_por_parcela = valor_total / num_parcelas
    data_base = pd.to_datetime(row['data_entrega']).date()
    
    for i in range(num_parcelas):
        parcela = row.copy()
        
        # Gerar novo UUID para cada parcela
        parcela['id'] = str(uuid.uuid4())
        
        # Número da parcela atual
        parcela['parcela'] = str(i + 1)
        
        # Valor da parcela
        if i == num_parcelas - 1:  # Última parcela recebe o resto
            valor_parcela = valor_total - (valor_por_parcela * i)
        else:
            valor_parcela = valor_por_parcela
        
        parcela['valor_total'] = round(valor_parcela, 2)
        
        # Data da parcela (mensal)
        if i == 0:
            parcela['data_entrega'] = data_base
        else:
            try:
                nova_data = data_base + relativedelta(months=i)
                parcela['data_entrega'] = nova_data
            except:
                # Se der erro, usar data base + dias
                nova_data = data_base + relativedelta(days=30*i)
                parcela['data_entrega'] = nova_data
        
        # Observações sobre a parcela
        obs_original = row.get('observacoes', '') or ''
        parcela['observacoes'] = f"{obs_original} - Parcela {i+1}/{num_parcelas}".strip(' -')
        
        parcelas.append(parcela)
    
    return parcelas

def processar_arquivo_entrega(arquivo_path):
    """Processa um arquivo individual de entrega de carnes"""
    print(f"Processando: {arquivo_path.name}")
    
    try:
        df = pd.read_csv(arquivo_path, dtype=str, low_memory=False)
        print(f"  - {len(df)} registros carregados")
        
        # Mapear loja
        loja_uuid, loja_nome = mapear_loja_uuid(arquivo_path.name)
        if not loja_uuid:
            print(f"  - ❌ Não foi possível identificar loja de {arquivo_path.name}")
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
        campos_obrigatorios = ['os_numero', 'valor_total', 'data_entrega']
        for campo in campos_obrigatorios:
            if campo not in df.columns:
                print(f"  - ❌ Campo obrigatório ausente: {campo}")
                return pd.DataFrame()
        
        # Limpar dados
        df_limpo = df.dropna(subset=['os_numero', 'valor_total', 'data_entrega']).copy()
        
        # Converter tipos
        df_limpo['valor_total'] = pd.to_numeric(df_limpo['valor_total'], errors='coerce')
        df_limpo = df_limpo[df_limpo['valor_total'] > 0]
        
        # Converter data
        df_limpo['data_entrega'] = pd.to_datetime(df_limpo['data_entrega']).dt.date
        
        # Padronizar campos
        df_limpo['os_numero'] = df_limpo['os_numero'].astype(str)
        df_limpo['parcela'] = df_limpo['parcela'].fillna('1').astype(str)
        
        print(f"  - ✅ {len(df_limpo)} registros válidos")
        return df_limpo
        
    except Exception as e:
        print(f"  - ❌ Erro: {e}")
        return pd.DataFrame()

def main():
    print("=== NORMALIZAÇÃO ENTREGAS CARNES COM PARCELAS ===")
    print(f"Início: {datetime.now()}")
    
    # Diretórios
    originais_dir = Path("data/originais/cxs/entrega_carnes/originais")
    processados_dir = Path("data/originais/cxs/entrega_carnes/processados")
    final_dir = Path("data/originais/cxs/entrega_carnes/final")
    
    # Criar diretórios se não existirem
    processados_dir.mkdir(parents=True, exist_ok=True)
    final_dir.mkdir(parents=True, exist_ok=True)
    
    # Buscar arquivos
    arquivos_entrega = list(originais_dir.glob("entrega_carne_*_final.csv"))
    
    if not arquivos_entrega:
        print("❌ Nenhum arquivo de entrega encontrado!")
        return
    
    print(f"\n1. FASE 1 - NORMALIZAÇÃO E MAPEAMENTO")
    print(f"Encontrados {len(arquivos_entrega)} arquivos:")
    for arquivo in arquivos_entrega:
        print(f"   - {arquivo.name}")
    
    # Carregar vendas para mapeamento
    print(f"\n2. Carregando vendas para mapeamento venda_id...")
    vendas_file = "data/vendas_para_importar/vendas_totais_com_uuid.csv"
    
    if Path(vendas_file).exists():
        vendas_df = pd.read_csv(vendas_file, dtype=str, low_memory=False)
        print(f"   - {len(vendas_df)} vendas carregadas")
    else:
        print(f"   - ⚠️  Arquivo de vendas não encontrado")
        vendas_df = pd.DataFrame()
    
    # FASE 1: Processar e normalizar cada arquivo
    print(f"\n3. Processando e normalizando arquivos...")
    todos_registros = []
    estatisticas_por_loja = {}
    
    for arquivo in arquivos_entrega:
        df_entrega = processar_arquivo_entrega(arquivo)
        
        if not df_entrega.empty:
            loja_nome = df_entrega.iloc[0]['loja_nome']
            
            # Mapear venda_id
            print(f"   - Mapeando venda_id para {loja_nome}...")
            df_entrega['venda_id'] = df_entrega['os_numero'].apply(
                lambda os_num: buscar_venda_id_por_os(os_num, vendas_df)
            )
            
            venda_ids_encontrados = df_entrega['venda_id'].notna().sum()
            print(f"     {venda_ids_encontrados}/{len(df_entrega)} venda_id encontrados")
            
            # Salvar arquivo normalizado
            arquivo_normalizado = processados_dir / f"{arquivo.stem}_normalizado.csv"
            df_entrega.to_csv(arquivo_normalizado, index=False, encoding='utf-8')
            
            todos_registros.append(df_entrega)
            estatisticas_por_loja[loja_nome] = {
                'arquivo': arquivo.name,
                'registros_originais': len(df_entrega),
                'valor_total': df_entrega['valor_total'].sum(),
                'venda_ids_encontrados': venda_ids_encontrados,
                'periodo': f"{df_entrega['data_entrega'].min()} a {df_entrega['data_entrega'].max()}"
            }
    
    if not todos_registros:
        print("❌ Nenhum registro válido encontrado!")
        return
    
    # Consolidar registros normalizados
    print(f"\n4. FASE 2 - DIVISÃO DE PARCELAS")
    df_consolidado = pd.concat(todos_registros, ignore_index=True)
    print(f"   - {len(df_consolidado)} registros consolidados")
    
    # Análise de parcelas
    parcelas_stats = df_consolidado['parcela'].value_counts().sort_index()
    print(f"   - Distribuição de parcelas:")
    for parcela, count in parcelas_stats.head(10).items():
        print(f"     {parcela} parcela(s): {count} registros")
    
    # FASE 2: Dividir parcelas
    print(f"\n5. Dividindo registros em parcelas...")
    
    todas_parcelas = []
    total_parcelas_geradas = 0
    
    for idx, row in df_consolidado.iterrows():
        if idx % 100 == 0:
            print(f"   - Processando registro {idx}/{len(df_consolidado)}...")
        
        parcelas_row = dividir_parcelas(row)
        todas_parcelas.extend(parcelas_row)
        total_parcelas_geradas += len(parcelas_row)
    
    print(f"   - ✅ {total_parcelas_geradas} parcelas geradas de {len(df_consolidado)} registros")
    
    # Criar DataFrame final
    print(f"\n6. Preparando estrutura final...")
    df_parcelas = pd.DataFrame(todas_parcelas)
    
    # Preparar estrutura para tabela
    df_final = pd.DataFrame()
    df_final['id'] = df_parcelas['id']
    df_final['venda_id'] = df_parcelas['venda_id']
    df_final['loja_id'] = df_parcelas['loja_id']
    df_final['os_numero'] = df_parcelas['os_numero']
    df_final['parcela'] = df_parcelas['parcela']
    df_final['data_entrega'] = df_parcelas['data_entrega']
    df_final['valor_total'] = df_parcelas['valor_total']
    df_final['observacoes'] = df_parcelas['observacoes']
    
    # Timestamps
    timestamp_now = datetime.now().isoformat()
    df_final['created_at'] = timestamp_now
    df_final['updated_at'] = timestamp_now
    df_final['deleted_at'] = None
    
    # Estatísticas finais
    print(f"\n=== ESTATÍSTICAS FINAIS ===")
    print(f"Registros originais: {len(df_consolidado)}")
    print(f"Parcelas geradas: {len(df_final)}")
    print(f"Expansão: {len(df_final)/len(df_consolidado):.1f}x")
    print(f"Valor total: R$ {df_final['valor_total'].sum():,.2f}")
    print(f"Período: {df_final['data_entrega'].min()} a {df_final['data_entrega'].max()}")
    print(f"Parcelas com venda_id: {df_final['venda_id'].notna().sum()}")
    
    print(f"\nPor loja (registros originais):")
    for loja, stats in estatisticas_por_loja.items():
        print(f"  {loja}: {stats['registros_originais']} registros → ~{stats['registros_originais']*2} parcelas estimadas")
        print(f"    Valor: R$ {stats['valor_total']:,.2f} | venda_id: {stats['venda_ids_encontrados']}")
    
    # Validação final
    print(f"\n7. Validação final...")
    erros = []
    
    # Campos obrigatórios
    if df_final['id'].isna().any():
        erros.append("IDs nulos encontrados")
    if df_final['loja_id'].isna().any():
        erros.append("loja_id nulos encontrados")
    if df_final['data_entrega'].isna().any():
        erros.append("data_entrega nulos encontrados")
    if (df_final['valor_total'] <= 0).any():
        erros.append("Valores <= 0 encontrados")
    
    if erros:
        print(f"   ❌ Erros encontrados:")
        for erro in erros:
            print(f"      - {erro}")
        return
    
    print(f"   ✅ Validação aprovada!")
    
    # Salvar arquivo final
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    arquivo_final = final_dir / f"ENTREGAS_CARNE_PARCELAS_FINAL_{timestamp}.csv"
    
    df_final.to_csv(arquivo_final, index=False, encoding='utf-8')
    print(f"\n✅ ARQUIVO FINAL SALVO: {arquivo_final}")
    
    # Relatório detalhado
    relatorio = {
        'timestamp': timestamp,
        'registros_originais': len(df_consolidado),
        'parcelas_geradas': len(df_final),
        'fator_expansao': round(len(df_final)/len(df_consolidado), 2),
        'valor_total': float(df_final['valor_total'].sum()),
        'periodo_inicio': str(df_final['data_entrega'].min()),
        'periodo_fim': str(df_final['data_entrega'].max()),
        'parcelas_com_venda_id': int(df_final['venda_id'].notna().sum()),
        'estatisticas_por_loja': estatisticas_por_loja,
        'distribuicao_parcelas': parcelas_stats.to_dict(),
        'arquivos_processados': [f.name for f in arquivos_entrega]
    }
    
    arquivo_relatorio = final_dir / f"RELATORIO_ENTREGAS_PARCELAS_{timestamp}.json"
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
    
    print(f"\n🎉 ENTREGAS COM PARCELAS PROCESSADAS COM SUCESSO!")
    print(f"Fim: {datetime.now()}")
    
    return arquivo_final

if __name__ == "__main__":
    main()