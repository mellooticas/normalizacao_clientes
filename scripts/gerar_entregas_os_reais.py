#!/usr/bin/env python3
"""
Gerador de Entregas OS - Dados Reais
===================================

Consolida APENAS dados reais de entregas dos arquivos:
- os_entregues_dia_*_final.csv

Estratégia:
1. Carrega todos os arquivos de entregas reais
2. Normaliza estrutura para tabela entregas_os
3. Cruza com vendas existentes para obter venda_id
4. Gera CSV apenas com dados reais (sem mock)
5. Deixa normalização futura completar conforme necessário

Resultado: CSV com entregas reais verificadas
"""

import pandas as pd
import glob
import uuid
from datetime import datetime
from pathlib import Path

def carregar_entregas_reais():
    """Carrega e consolida todas as entregas reais"""
    
    print("📂 Carregando arquivos de entregas reais...")
    
    # Localiza todos os arquivos
    pattern = 'data/originais/cxs/finais_postgresql_prontos/os_entregues_dia_*_final.csv'
    arquivos = glob.glob(pattern)
    
    if not arquivos:
        print("❌ Nenhum arquivo encontrado!")
        return None
    
    print(f"✅ Encontrados {len(arquivos)} arquivos")
    
    # Lista para consolidar
    todas_entregas = []
    
    for arquivo in sorted(arquivos):
        loja_nome = arquivo.split('_')[-2]
        print(f"   📄 Processando: {loja_nome.upper()}")
        
        try:
            df = pd.read_csv(arquivo)
            
            # Adiciona identificação da loja
            df['loja_origem'] = loja_nome.upper()
            df['arquivo_origem'] = arquivo.split('/')[-1]
            
            todas_entregas.append(df)
            print(f"      ✅ {len(df):,} registros carregados")
            
        except Exception as e:
            print(f"      ❌ Erro: {e}")
    
    # Consolida tudo
    if todas_entregas:
        df_consolidado = pd.concat(todas_entregas, ignore_index=True)
        print(f"\n✅ Total consolidado: {len(df_consolidado):,} registros")
        return df_consolidado
    
    return None

def normalizar_entregas(df_entregas):
    """Normaliza dados de entregas para estrutura da tabela"""
    
    print("🔄 Normalizando estrutura de dados...")
    
    # Normaliza datas
    df_entregas['data_movimento'] = pd.to_datetime(df_entregas['data_movimento'], errors='coerce')
    
    # Remove registros sem data válida
    antes = len(df_entregas)
    df_entregas = df_entregas.dropna(subset=['data_movimento'])
    depois = len(df_entregas)
    
    if antes != depois:
        print(f"   ⚠️ Removidos {antes - depois} registros sem data válida")
    
    # Remove registros sem OS
    antes = len(df_entregas)
    df_entregas = df_entregas.dropna(subset=['os_numero'])
    depois = len(df_entregas)
    
    if antes != depois:
        print(f"   ⚠️ Removidos {antes - depois} registros sem OS")
    
    # Converte OS para string
    df_entregas['os_numero'] = df_entregas['os_numero'].astype(str)
    
    # Gera estrutura final
    entregas_normalizadas = []
    
    for idx, entrega in df_entregas.iterrows():
        if idx % 1000 == 0 and idx > 0:
            print(f"   Processando {idx:,}/{len(df_entregas):,}...")
        
        # Determina status baseado em tipo
        status = 'entregue'  # Todos os registros são entregas realizadas
        
        # Observações baseadas no tipo
        observacao = None
        if entrega.get('carne') == 'Sim':
            observacao = 'Entrega de carnê realizada'
        elif entrega.get('carne') == 'Não':
            observacao = 'Entrega de produtos realizada'
        
        # Cria registro normalizado
        registro = {
            'id': str(uuid.uuid4()),
            'os_numero': entrega['os_numero'],
            'data_prevista': entrega['data_movimento'].strftime('%Y-%m-%d'),
            'data_entrega': entrega['data_movimento'].strftime('%Y-%m-%d'),
            'status': status,
            'observacoes': observacao,
            'loja_id': entrega.get('loja_id'),
            'vendedor_uuid': entrega.get('vendedor_uuid'),
            'carne': entrega.get('carne'),
            'loja_origem': entrega.get('loja_origem'),
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        entregas_normalizadas.append(registro)
    
    df_final = pd.DataFrame(entregas_normalizadas)
    print(f"✅ Normalizadas {len(df_final):,} entregas")
    
    return df_final

def cruzar_com_vendas(df_entregas):
    """Cruza entregas com vendas para obter venda_id"""
    
    print("🔗 Cruzando com vendas existentes...")
    
    try:
        # Carrega vendas
        vendas_df = pd.read_csv('data/vendas_para_importar/vendas_totais_com_uuid.csv')
        print(f"✅ Vendas carregadas: {len(vendas_df):,}")
        
        # Prepara dados para cruzamento
        vendas_df['numero_venda'] = vendas_df['numero_venda'].astype(str)
        df_entregas['os_numero'] = df_entregas['os_numero'].astype(str)
        
        # Faz o merge
        antes = len(df_entregas)
        df_entregas = df_entregas.merge(
            vendas_df[['numero_venda', 'id']],
            left_on='os_numero',
            right_on='numero_venda',
            how='left'
        )
        
        # Renomeia e limpa
        df_entregas['venda_id'] = df_entregas['id_y']
        df_entregas = df_entregas.drop(['id_y', 'numero_venda'], axis=1)
        df_entregas = df_entregas.rename(columns={'id_x': 'id'})
        
        # Estatísticas do cruzamento
        com_venda = df_entregas['venda_id'].notna().sum()
        sem_venda = df_entregas['venda_id'].isna().sum()
        
        print(f"✅ Cruzamento concluído:")
        print(f"   🎯 Com venda_id: {com_venda:,} ({com_venda/len(df_entregas)*100:.1f}%)")
        print(f"   ❓ Sem venda_id: {sem_venda:,} ({sem_venda/len(df_entregas)*100:.1f}%)")
        
        return df_entregas
        
    except Exception as e:
        print(f"❌ Erro no cruzamento: {e}")
        print("⚠️ Continuando sem venda_id...")
        df_entregas['venda_id'] = None
        return df_entregas

def main():
    """Processa entregas reais completas"""
    
    print("🚚 === GERADOR DE ENTREGAS OS - DADOS REAIS === 🚚")
    print("📊 Consolidando dados reais de entregas...")
    
    # 1. Carrega todas as entregas reais
    df_entregas = carregar_entregas_reais()
    if df_entregas is None:
        return
    
    # 2. Normaliza estrutura
    df_final = normalizar_entregas(df_entregas)
    
    # 3. Cruza com vendas
    df_final = cruzar_com_vendas(df_final)
    
    # 4. Estatísticas finais
    print(f"\n📊 === ESTATÍSTICAS FINAIS === 📊")
    print(f"📋 Total de entregas: {len(df_final):,}")
    print(f"🎯 OS únicas: {df_final['os_numero'].nunique():,}")
    
    # Por loja
    print(f"\n🏪 Distribuição por loja:")
    loja_stats = df_final['loja_origem'].value_counts()
    for loja, count in loja_stats.items():
        pct = (count / len(df_final)) * 100
        print(f"   {loja}: {count:,} ({pct:.1f}%)")
    
    # Por tipo
    if 'carne' in df_final.columns:
        print(f"\n🚚 Tipo de entrega:")
        tipo_stats = df_final['carne'].value_counts()
        for tipo, count in tipo_stats.items():
            pct = (count / len(df_final)) * 100
            print(f"   {tipo}: {count:,} ({pct:.1f}%)")
    
    # Período
    if 'data_entrega' in df_final.columns:
        print(f"\n📅 Período das entregas:")
        print(f"   Primeira: {df_final['data_entrega'].min()}")
        print(f"   Última: {df_final['data_entrega'].max()}")
    
    # Com/sem venda_id
    if 'venda_id' in df_final.columns:
        com_venda = df_final['venda_id'].notna().sum()
        sem_venda = df_final['venda_id'].isna().sum()
        print(f"\n🔗 Cruzamento com vendas:")
        print(f"   ✅ Com venda_id: {com_venda:,} ({com_venda/len(df_final)*100:.1f}%)")
        print(f"   ❓ Sem venda_id: {sem_venda:,} ({sem_venda/len(df_final)*100:.1f}%)")
    
    # 5. Salva arquivo final
    output_path = 'data/vendas_para_importar/entregas_os_reais.csv'
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Seleciona colunas finais para o CSV
    colunas_finais = [
        'id', 'venda_id', 'os_numero', 'data_prevista', 'data_entrega', 
        'status', 'observacoes', 'created_at', 'updated_at'
    ]
    
    # Adiciona colunas auxiliares para referência
    colunas_auxiliares = ['loja_id', 'vendedor_uuid', 'carne', 'loja_origem']
    for col in colunas_auxiliares:
        if col in df_final.columns:
            colunas_finais.append(col)
    
    df_export = df_final[colunas_finais].copy()
    
    df_export.to_csv(output_path, index=False)
    print(f"\n💾 Arquivo salvo: {output_path}")
    print(f"📁 Tamanho: {len(df_export):,} registros")
    print(f"📊 Colunas: {', '.join(colunas_finais)}")
    
    # 6. Validações
    print(f"\n🔍 === VALIDAÇÕES === 🔍")
    print(f"✅ IDs únicos: {df_export['id'].nunique() == len(df_export)}")
    print(f"✅ OS válidas: {df_export['os_numero'].notna().all()}")
    print(f"✅ Datas válidas: {df_export['data_entrega'].notna().all()}")
    print(f"✅ Status válidos: {df_export['status'].notna().all()}")
    
    print(f"\n🎯 === SUCESSO === 🎯")
    print("✅ Dados reais de entregas processados!")
    print("✅ Estrutura compatível com Supabase!")
    print("✅ Pronto para importação!")
    print(f"🚀 Arquivo: {output_path}")
    
    # 7. Próximos passos
    print(f"\n🔧 === PRÓXIMOS PASSOS === 🔧")
    print("1. Importar entregas_os_reais.csv no Supabase")
    print("2. Conforme normalização avança, adicionar mais dados")
    print("3. Manter apenas dados verificados e reais")
    print("4. Expandir organicamente conforme necessário")

if __name__ == "__main__":
    main()