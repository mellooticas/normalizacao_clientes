#!/usr/bin/env python3
"""
Script para processar dados de Carne Lancaster do arquivo ordem_servico_pdv_carne_lancaster.csv
Converte para o formato da tabela vendas.entregas_carne
"""

import pandas as pd
import uuid
from pathlib import Path
from datetime import datetime
import numpy as np

def mapear_empresa_para_loja(id_emp):
    """Mapear ID da empresa para UUID da loja no Supabase"""
    # Mapeamento baseado nos IDs reais das lojas no Supabase
    mapping = {
        42: ('52f92716-d2ba-441a-ac3c-94bdfabd9722', 'SUZANO'),      # ID 42 = Suzano
        48: ('9a22ccf1-36fe-4b9f-9391-ca31433dc31e', 'MAUÁ')        # ID 48 = Mauá
    }
    
    return mapping.get(int(id_emp), (None, None))

def buscar_venda_id_por_os(os_numero, vendas_df):
    """Busca venda_id baseado no número da OS - melhorado para Lancaster"""
    if vendas_df.empty:
        return None
    
    os_str = str(os_numero)
    
    # Match direto por numero_venda
    match_direto = vendas_df[vendas_df['numero_venda'].astype(str) == os_str]
    if not match_direto.empty:
        return match_direto.iloc[0]['id']
    
    # Match sem pontos/vírgulas
    os_limpo = os_str.replace('.', '').replace(',', '')
    match_limpo = vendas_df[vendas_df['numero_venda'].astype(str).str.replace('.', '').str.replace(',', '') == os_limpo]
    if not match_limpo.empty:
        return match_limpo.iloc[0]['id']
    
    # Match considerando zeros à esquerda removidos
    try:
        os_int = int(os_str)
        match_int = vendas_df[vendas_df['numero_venda'].astype(str).astype(int) == os_int]
        if not match_int.empty:
            return match_int.iloc[0]['id']
    except:
        pass
    
    return None

def extrair_numero_parcela(referencia):
    """Extrai número da parcela a partir do campo Referência (ex: PARC.1/8)"""
    if pd.isna(referencia) or not isinstance(referencia, str):
        return 1
    
    # Buscar padrão PARC.X/Y
    import re
    match = re.search(r'PARC\.(\d+)/(\d+)', referencia)
    if match:
        return int(match.group(1))
    
    return 1

def processar_lancaster():
    """Processa dados do Lancaster"""
    
    print("=== PROCESSAMENTO CARNE LANCASTER ===")
    print(f"Início: {datetime.now()}")
    
    # Caminhos
    arquivo_lancaster = Path("data/originais/controles_gerais/trans_financ/separados_por_pagamento/ordem_servico_pdv_carne_lancaster.csv")
    arquivo_vendas = Path("data/vendas_para_importar/vendas_totais_com_uuid.csv")  # CAMINHO CORRIGIDO
    pasta_destino = Path("data/originais/cxs/entrega_carnes/final")
    
    print(f"\n1. Carregando arquivo Lancaster: {arquivo_lancaster}")
    
    if not arquivo_lancaster.exists():
        print(f"❌ Arquivo não encontrado: {arquivo_lancaster}")
        return
    
    # Carregar dados Lancaster
    try:
        df_lancaster = pd.read_csv(arquivo_lancaster, encoding='utf-8')
        print(f"   ✅ {len(df_lancaster)} registros carregados")
    except Exception as e:
        try:
            df_lancaster = pd.read_csv(arquivo_lancaster, encoding='latin1')
            print(f"   ✅ {len(df_lancaster)} registros carregados (latin1)")
        except Exception as e2:
            print(f"   ❌ Erro ao carregar: {e2}")
            return
    
    print(f"   📊 Colunas: {len(df_lancaster.columns)}\"")
    print(f"   📊 Empresas: {df_lancaster['ID emp.'].value_counts().to_dict()}\"")
    
    # Carregar vendas para mapeamento
    print(f"\n2. Carregando vendas para mapeamento venda_id...")
    vendas_df = pd.DataFrame()
    if arquivo_vendas.exists():
        try:
            vendas_df = pd.read_csv(arquivo_vendas)
            print(f"   ✅ {len(vendas_df)} vendas carregadas")
        except Exception as e:
            print(f"   ⚠️  Erro ao carregar vendas: {e}")
    else:
        print(f"   ⚠️  Arquivo de vendas não encontrado: {arquivo_vendas}")
    
    # Filtrar apenas registros de CARNE LANCASTER
    df_filtered = df_lancaster[
        (df_lancaster['Pagamento'] == 'CARNE LANCASTER') & 
        (df_lancaster['Tipo'] == 'PRESTAÇÃO')
    ].copy()
    
    print(f"\n3. Filtrados {len(df_filtered)} registros de Carne Lancaster")
    
    if len(df_filtered) == 0:
        print("❌ Nenhum registro de Carne Lancaster encontrado!")
        return
    
    # Processar registros
    dados_processados = []
    debug_os = []  # Para debug
    
    for idx, row in df_filtered.iterrows():
        try:
            # Mapear loja
            loja_id, nome_loja = mapear_empresa_para_loja(row['ID emp.'])
            if not loja_id:
                print(f"   ⚠️  Empresa desconhecida: {row['ID emp.']}")
                continue
            
            # Extrair número da OS (remover prefixo da loja 42 ou 48)
            nro_operacao = str(row['Nro.operação']).replace('.0', '')
            id_emp = int(row['ID emp.'])
            
            # Remover prefixo da loja para obter o número real da OS
            if nro_operacao.startswith(str(id_emp)):
                os_numero = nro_operacao[len(str(id_emp)):]
            else:
                os_numero = nro_operacao
            
            # Remover zeros à esquerda para compatibilidade com banco
            os_numero_original = os_numero
            os_numero = str(int(os_numero)) if os_numero.isdigit() else os_numero
            
            # Debug primeiros 5 registros
            if len(debug_os) < 5:
                debug_os.append({
                    'nro_operacao': nro_operacao,
                    'os_original': os_numero_original,
                    'os_final': os_numero,
                    'empresa': id_emp
                })
            
            venda_id = buscar_venda_id_por_os(os_numero, vendas_df)
            
            # Extrair número da parcela
            parcela = extrair_numero_parcela(row['Referência'])
            
            # Data de vencimento
            data_entrega = row['Dt.venc.']
            if pd.isna(data_entrega):
                continue
                
            # Converter data
            try:
                if isinstance(data_entrega, str):
                    data_entrega = datetime.strptime(data_entrega.split()[0], '%Y-%m-%d').date()
                else:
                    data_entrega = pd.to_datetime(data_entrega).date()
            except:
                continue
            
            # Valor
            valor = float(row['Vl.movimento']) if not pd.isna(row['Vl.movimento']) else 0.0
            if valor <= 0:
                continue
            
            # Criar registro
            registro = {
                'id': str(uuid.uuid4()),
                'venda_id': venda_id,
                'loja_id': loja_id,
                'os_numero': os_numero,
                'parcela': parcela,
                'data_entrega': data_entrega.strftime('%Y-%m-%d'),
                'valor_total': valor,
                'observacoes': f"Lancaster - {row['Referência']} - Cliente: {row['Cliente']}",
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'deleted_at': ''
            }
            
            dados_processados.append(registro)
            
        except Exception as e:
            print(f"   ⚠️  Erro ao processar linha {idx}: {e}")
            continue
    
    print(f"\n4. Processamento concluído: {len(dados_processados)} registros válidos")
    
    # Exibir debug dos primeiros registros
    if debug_os:
        print(f"\n🔍 DEBUG - Exemplos de conversão de OS:")
        for d in debug_os:
            print(f"   Empresa {d['empresa']}: {d['nro_operacao']} → {d['os_original']} → {d['os_final']}")
    
    if len(dados_processados) == 0:
        print("❌ Nenhum registro válido processado!")
        return
    
    # Converter para DataFrame
    df_final = pd.DataFrame(dados_processados)
    
    # Estatísticas
    print(f"\n=== ESTATÍSTICAS LANCASTER ===")
    print(f"Total de parcelas: {len(df_final)}")
    print(f"Valor total: R$ {df_final['valor_total'].sum():,.2f}")
    print(f"Período: {df_final['data_entrega'].min()} a {df_final['data_entrega'].max()}")
    print(f"Parcelas com venda_id: {df_final['venda_id'].notna().sum()}")
    
    # Por loja
    print(f"\nPor loja:")
    for loja_id, grupo in df_final.groupby('loja_id'):
        nome_loja = mapear_empresa_para_loja(42)[1] if loja_id == mapear_empresa_para_loja(42)[0] else mapear_empresa_para_loja(48)[1]
        valor_loja = grupo['valor_total'].sum()
        with_venda = grupo['venda_id'].notna().sum()
        print(f"  {nome_loja}: {len(grupo)} parcelas - R$ {valor_loja:,.2f} - venda_id: {with_venda}")
    
    # Salvar arquivo final
    pasta_destino.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    arquivo_final = pasta_destino / f"LANCASTER_ENTREGAS_FINAL_{timestamp}.csv"
    
    df_final.to_csv(arquivo_final, index=False)
    print(f"\n✅ ARQUIVO FINAL SALVO: {arquivo_final}")
    
    # Comando SQL
    print(f"\n📋 COMANDO SQL PARA IMPORTAÇÃO:")
    print(f"```sql")
    print(f"\\copy vendas.entregas_carne (")
    print(f"    id, venda_id, loja_id, os_numero, parcela,")
    print(f"    data_entrega, valor_total, observacoes,")
    print(f"    created_at, updated_at, deleted_at")
    print(f") FROM '{arquivo_final.name}'")
    print(f"WITH (FORMAT CSV, HEADER);")
    print(f"```")
    
    print(f"\n🎉 LANCASTER PROCESSADO COM SUCESSO!")
    print(f"Fim: {datetime.now()}")

if __name__ == "__main__":
    processar_lancaster()