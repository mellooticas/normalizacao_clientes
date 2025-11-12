#!/usr/bin/env python3
"""
GERADOR DE ARQUIVOS FINAIS PARA BANCO
================================================================
Cria os arquivos finais limpos de cada loja com apenas os dados
essenciais que serão usados no banco de dados.
================================================================
"""

import pandas as pd
import os
import shutil
from datetime import datetime

def gerar_arquivos_finais():
    """Gera arquivos finais limpos para o banco"""
    
    base_dir = "data/originais/cxs/extraidos_corrigidos"
    output_dir = "data/finais_banco"
    
    # Criar diretório de saída
    os.makedirs(output_dir, exist_ok=True)
    
    print("🎯 GERANDO ARQUIVOS FINAIS PARA BANCO")
    print("=" * 60)
    
    lojas = ['maua', 'perus', 'rio_pequeno', 'sao_mateus', 'suzano', 'suzano2']
    
    # Colunas essenciais para o banco
    colunas_essenciais = [
        'os_numero',
        'vendedor',
        'vendedor_uuid', 
        'vendedor_nome_normalizado',
        'data_movimento',
        'loja_nome',
        'loja_id',
        'canal_captacao_uuid',
        'canal_captacao_nome',
        'carne',
        'arquivo_origem'
    ]
    
    total_registros = 0
    resumo_por_loja = {}
    
    for loja in lojas:
        print(f"\n🏪 PROCESSANDO LOJA: {loja.upper()}")
        print("-" * 50)
        
        # Arquivo origem (OS_ENTREGUES_DIA enriquecido)
        arquivo_origem = f"{base_dir}/os_entregues_dia/os_entregues_dia_{loja}_com_uuids_enriquecido_completo.csv"
        
        if os.path.exists(arquivo_origem):
            try:
                df = pd.read_csv(arquivo_origem)
                print(f"📊 Registros originais: {len(df):,}")
                
                # Filtrar apenas registros com dados válidos
                df_validos = df[
                    (df['os_numero'].notna()) & 
                    (df['os_numero'] != '') &
                    (df['vendedor'].notna()) & 
                    (df['vendedor'] != '')
                ].copy()
                
                print(f"✅ Registros válidos: {len(df_validos):,}")
                
                # Selecionar apenas colunas essenciais
                colunas_existentes = [col for col in colunas_essenciais if col in df_validos.columns]
                df_final = df_validos[colunas_existentes].copy()
                
                # Adicionar metadados
                df_final['data_processamento'] = datetime.now()
                df_final['versao_arquivo'] = 'FINAL_BANCO_v1.0'
                
                # Salvar arquivo final
                arquivo_final = f"{output_dir}/os_entregues_dia_{loja}_FINAL_BANCO.csv"
                df_final.to_csv(arquivo_final, index=False)
                
                # Estatísticas (tratando datas misturadas)
                total_registros += len(df_final)
                
                # Calcular período com segurança
                try:
                    datas_validas = pd.to_datetime(df_final['data_movimento'], errors='coerce').dropna()
                    if len(datas_validas) > 0:
                        periodo = f"{datas_validas.min().strftime('%Y-%m-%d')} a {datas_validas.max().strftime('%Y-%m-%d')}"
                    else:
                        periodo = "Sem datas válidas"
                except:
                    periodo = "Erro ao processar datas"
                
                resumo_por_loja[loja] = {
                    'registros': len(df_final),
                    'com_uuid': df_final['vendedor_uuid'].notna().sum(),
                    'cobertura_uuid': (df_final['vendedor_uuid'].notna().sum() / len(df_final) * 100) if len(df_final) > 0 else 0,
                    'vendedores_unicos': df_final['vendedor_nome_normalizado'].nunique(),
                    'periodo': periodo
                }
                
                print(f"💾 Arquivo salvo: {arquivo_final}")
                print(f"📈 Cobertura UUID: {resumo_por_loja[loja]['cobertura_uuid']:.1f}%")
                print(f"👥 Vendedores únicos: {resumo_por_loja[loja]['vendedores_unicos']}")
                
            except Exception as e:
                print(f"❌ Erro ao processar {loja}: {e}")
        else:
            print(f"⚠️ Arquivo não encontrado: {arquivo_origem}")
    
    # Gerar arquivo consolidado
    print(f"\n🔄 GERANDO ARQUIVO CONSOLIDADO")
    print("-" * 50)
    
    arquivos_finais = []
    for loja in lojas:
        arquivo = f"{output_dir}/os_entregues_dia_{loja}_FINAL_BANCO.csv"
        if os.path.exists(arquivo):
            df_loja = pd.read_csv(arquivo)
            arquivos_finais.append(df_loja)
    
    if arquivos_finais:
        df_consolidado = pd.concat(arquivos_finais, ignore_index=True)
        arquivo_consolidado = f"{output_dir}/OS_ENTREGUES_DIA_TODAS_LOJAS_FINAL_BANCO.csv"
        df_consolidado.to_csv(arquivo_consolidado, index=False)
        
        print(f"💾 Arquivo consolidado: {arquivo_consolidado}")
        print(f"📊 Total de registros: {len(df_consolidado):,}")
    
    # Relatório final
    print(f"\n📋 RELATÓRIO FINAL")
    print("=" * 60)
    print(f"📊 Total de registros processados: {total_registros:,}")
    print(f"🏪 Lojas processadas: {len(resumo_por_loja)}")
    
    for loja, dados in resumo_por_loja.items():
        print(f"\n🏪 {loja.upper()}:")
        print(f"   📊 Registros: {dados['registros']:,}")
        print(f"   🎯 UUID Coverage: {dados['cobertura_uuid']:.1f}%")
        print(f"   👥 Vendedores: {dados['vendedores_unicos']}")
        print(f"   📅 Período: {dados['periodo']}")
    
    return resumo_por_loja

def listar_arquivos_finais():
    """Lista os arquivos finais gerados"""
    
    output_dir = "data/finais_banco"
    
    print(f"\n📁 ARQUIVOS FINAIS GERADOS")
    print("=" * 60)
    
    if os.path.exists(output_dir):
        arquivos = [f for f in os.listdir(output_dir) if f.endswith('.csv')]
        
        for arquivo in sorted(arquivos):
            caminho = os.path.join(output_dir, arquivo)
            tamanho = os.path.getsize(caminho) / 1024  # KB
            print(f"📄 {arquivo}")
            print(f"   📊 Tamanho: {tamanho:.1f} KB")
            
            # Preview do arquivo
            try:
                df = pd.read_csv(caminho)
                print(f"   📈 Registros: {len(df):,}")
                print(f"   📋 Colunas: {len(df.columns)}")
            except Exception as e:
                print(f"   ❌ Erro ao ler: {e}")
    else:
        print("❌ Diretório não encontrado")

if __name__ == "__main__":
    resumo = gerar_arquivos_finais()
    listar_arquivos_finais()
    
    print(f"\n✅ ARQUIVOS FINAIS PRONTOS PARA O BANCO!")
    print(f"📁 Localização: data/finais_banco/")
    print(f"🎯 Use estes arquivos para subir no Supabase")