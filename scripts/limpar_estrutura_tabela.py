#!/usr/bin/env python3
"""
Script para limpar e ajustar arquivos para estrutura EXATA da tabela entregas_os
Removendo colunas extras e mantendo apenas as necessárias
"""

import pandas as pd
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def limpar_estrutura_tabela():
    """
    Limpa arquivos para estrutura exata da tabela entregas_os
    """
    print("🔧 === LIMPANDO ESTRUTURA PARA TABELA REAL === 🔧")
    print("📋 Tabela: vendas.entregas_os")
    print("📋 Colunas obrigatórias: id, venda_id, vendedor_id, data_entrega, tem_carne, created_at, updated_at, deleted_at")
    
    # Estrutura EXATA da tabela
    colunas_tabela = [
        'id',
        'venda_id', 
        'vendedor_id',
        'data_entrega',
        'tem_carne',
        'created_at',
        'updated_at', 
        'deleted_at'
    ]
    
    print(f"\n✅ Colunas da tabela: {', '.join(colunas_tabela)}")
    
    # Arquivos para limpar
    arquivos = [
        'data/entregas_APENAS_NOVAS_20251105_033931.csv',
        'data/entregas_CONSOLIDADO_FINAL_20251105_033931.csv'
    ]
    
    for arquivo in arquivos:
        try:
            print(f"\n🔧 === PROCESSANDO: {arquivo} === 🔧")
            
            # Carregar arquivo
            df = pd.read_csv(arquivo)
            print(f"📊 Arquivo original: {len(df):,} registros, {df.shape[1]} colunas")
            print(f"📋 Colunas atuais: {', '.join(df.columns)}")
            
            # Identificar colunas extras
            colunas_extras = [col for col in df.columns if col not in colunas_tabela]
            colunas_faltantes = [col for col in colunas_tabela if col not in df.columns]
            
            if colunas_extras:
                print(f"🗑️ Colunas extras (serão removidas): {', '.join(colunas_extras)}")
            
            if colunas_faltantes:
                print(f"❌ Colunas faltantes: {', '.join(colunas_faltantes)}")
                continue
            
            # Selecionar apenas colunas da tabela
            df_limpo = df[colunas_tabela].copy()
            
            print(f"✅ Arquivo limpo: {len(df_limpo):,} registros, {df_limpo.shape[1]} colunas")
            
            # Verificações finais
            print(f"\n🔍 === VERIFICAÇÕES === 🔍")
            
            # Verificar valores nulos em campos obrigatórios
            obrigatorios = ['id', 'venda_id', 'data_entrega']
            for campo in obrigatorios:
                nulos = df_limpo[campo].isnull().sum()
                print(f"   {campo}: {nulos} nulos ({'✅' if nulos == 0 else '❌'})")
            
            # Verificar duplicatas
            duplicatas = df_limpo.duplicated(subset=['venda_id', 'data_entrega']).sum()
            print(f"   Duplicatas venda_id+data_entrega: {duplicatas} ({'✅' if duplicatas == 0 else '❌'})")
            
            # Verificar tipos
            print(f"   UUIDs válidos: {'✅' if df_limpo['venda_id'].str.len().eq(36).all() else '❌'}")
            print(f"   Datas válidas: {'✅' if pd.to_datetime(df_limpo['data_entrega'], errors='coerce').notna().all() else '❌'}")
            
            # Salvar arquivo limpo
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nome_base = arquivo.split('/')[-1].replace('.csv', '')
            arquivo_limpo = f'data/{nome_base}_LIMPO_{timestamp}.csv'
            
            df_limpo.to_csv(arquivo_limpo, index=False)
            
            print(f"💾 Arquivo limpo salvo: {arquivo_limpo}")
            
        except FileNotFoundError:
            print(f"❌ Arquivo não encontrado: {arquivo}")
        except Exception as e:
            print(f"❌ Erro processando {arquivo}: {e}")
    
    return True

def verificar_estrutura_existente():
    """
    Verifica estrutura dos arquivos existentes
    """
    print(f"\n🔍 === VERIFICANDO ARQUIVOS EXISTENTES === 🔍")
    
    import glob
    arquivos = glob.glob('data/entregas_*.csv')
    
    print(f"📋 Arquivos encontrados: {len(arquivos)}")
    
    for arquivo in arquivos:
        try:
            df = pd.read_csv(arquivo, nrows=1)  # Só o header
            nome = arquivo.split('/')[-1]
            print(f"\n📄 {nome}:")
            print(f"   Colunas ({len(df.columns)}): {', '.join(df.columns)}")
            
        except Exception as e:
            print(f"❌ Erro lendo {arquivo}: {e}")

def criar_arquivo_final_para_importacao():
    """
    Cria arquivo final específico para importação
    """
    print(f"\n🎯 === CRIANDO ARQUIVO FINAL PARA IMPORTAÇÃO === 🎯")
    
    # Usar o arquivo de apenas novas (493 registros)
    arquivo_fonte = 'data/entregas_APENAS_NOVAS_20251105_033931.csv'
    
    try:
        df = pd.read_csv(arquivo_fonte)
        print(f"📊 Fonte: {len(df):,} registros")
        
        # Estrutura EXATA da tabela
        colunas_finais = [
            'id',
            'venda_id', 
            'vendedor_id',
            'data_entrega',
            'tem_carne',
            'created_at',
            'updated_at', 
            'deleted_at'
        ]
        
        # Selecionar apenas colunas necessárias
        df_final = df[colunas_finais].copy()
        
        # Validações finais
        print(f"\n✅ === VALIDAÇÕES FINAIS === ✅")
        
        # Remover registros com dados obrigatórios nulos
        antes = len(df_final)
        df_final = df_final.dropna(subset=['id', 'venda_id', 'data_entrega'])
        depois = len(df_final)
        
        if antes != depois:
            print(f"🗑️ Removidos {antes-depois} registros com dados nulos")
        
        # Verificar e corrigir tipos
        df_final['tem_carne'] = df_final['tem_carne'].fillna(False)
        df_final['deleted_at'] = None  # Sempre nulo para registros ativos
        
        # Verificação final de duplicatas
        duplicatas = df_final.duplicated(subset=['venda_id', 'data_entrega']).sum()
        if duplicatas > 0:
            print(f"🗑️ Removendo {duplicatas} duplicatas internas")
            df_final = df_final.drop_duplicates(subset=['venda_id', 'data_entrega'])
        
        print(f"📊 Registros finais: {len(df_final):,}")
        print(f"📋 Colunas: {df_final.shape[1]} (exato)")
        
        # Salvar arquivo final
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        arquivo_final = f'data/FINAL_PARA_IMPORTACAO_{timestamp}.csv'
        
        df_final.to_csv(arquivo_final, index=False)
        
        print(f"\n💾 === ARQUIVO FINAL === 💾")
        print(f"📄 Arquivo: {arquivo_final}")
        print(f"📊 Registros: {len(df_final):,}")
        print(f"📋 Estrutura: EXATA da tabela entregas_os")
        print(f"✅ Pronto para importação direta no Supabase")
        
        return arquivo_final
        
    except Exception as e:
        print(f"❌ Erro criando arquivo final: {e}")
        return None

def main():
    """Função principal"""
    print("🎯 === AJUSTE PARA ESTRUTURA EXATA DA TABELA === 🎯")
    
    # 1. Verificar estrutura atual
    verificar_estrutura_existente()
    
    # 2. Limpar estrutura
    limpar_estrutura_tabela()
    
    # 3. Criar arquivo final
    arquivo_final = criar_arquivo_final_para_importacao()
    
    print(f"\n🎉 === RESULTADO === 🎉")
    if arquivo_final:
        print(f"✅ Arquivo final: {arquivo_final}")
        print(f"📋 Estrutura: 100% compatível com tabela entregas_os")
        print(f"🚀 Importação: Deve funcionar sem erros")
    else:
        print(f"❌ Erro na geração do arquivo final")
    
    print(f"📅 Processado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()