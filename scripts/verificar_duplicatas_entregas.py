#!/usr/bin/env python3
"""
Script para verificar duplicatas e gerar apenas entregas NOVAS
Comparando com entregas já existentes no sistema
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def verificar_e_gerar_novas_entregas():
    """
    Verifica duplicatas e gera apenas entregas novas
    """
    print("🔍 === VERIFICAÇÃO DE DUPLICATAS === 🔍")
    
    # 1. Carregar arquivo atual (535 registros)
    print("\n📊 === CARREGANDO ARQUIVOS === 📊")
    
    arquivo_atual = 'data/entregas_supabase_2247_cruzamentos_20251105_033631.csv'
    df_atual = pd.read_csv(arquivo_atual)
    print(f"📄 Arquivo atual: {len(df_atual):,} registros")
    
    # 2. Carregar arquivo anterior (994 registros)
    arquivo_anterior = 'data/entregas_estrutura_real_20251105_004101.csv'
    try:
        df_anterior = pd.read_csv(arquivo_anterior)
        print(f"📄 Arquivo anterior: {len(df_anterior):,} registros")
        tem_anterior = True
    except FileNotFoundError:
        print(f"⚠️ Arquivo anterior não encontrado: {arquivo_anterior}")
        print(f"📊 Buscando outros arquivos de entregas...")
        
        # Buscar outros arquivos possíveis
        import glob
        arquivos_entregas = glob.glob('data/entregas_*.csv')
        print(f"📋 Arquivos encontrados: {len(arquivos_entregas)}")
        
        for arquivo in arquivos_entregas:
            print(f"   - {arquivo}")
        
        if arquivos_entregas:
            # Usar o mais recente (exceto o atual)
            arquivos_outros = [a for a in arquivos_entregas if a != arquivo_atual]
            if arquivos_outros:
                arquivo_anterior = max(arquivos_outros)
                df_anterior = pd.read_csv(arquivo_anterior)
                print(f"✅ Usando arquivo: {arquivo_anterior}")
                print(f"📄 Registros: {len(df_anterior):,}")
                tem_anterior = True
            else:
                df_anterior = pd.DataFrame()
                tem_anterior = False
        else:
            df_anterior = pd.DataFrame()
            tem_anterior = False
    
    # 3. Análise de duplicatas se há arquivo anterior
    if tem_anterior and len(df_anterior) > 0:
        print(f"\n🔍 === ANÁLISE DE DUPLICATAS === 🔍")
        
        # Criar chaves únicas (venda_id + data_entrega)
        df_atual['chave_unica'] = df_atual['venda_id'] + '|' + df_atual['data_entrega']
        df_anterior['chave_unica'] = df_anterior['venda_id'] + '|' + df_anterior['data_entrega']
        
        # Identificar duplicatas
        chaves_atual = set(df_atual['chave_unica'])
        chaves_anterior = set(df_anterior['chave_unica'])
        
        chaves_duplicadas = chaves_atual & chaves_anterior
        chaves_novas = chaves_atual - chaves_anterior
        
        print(f"🔄 Chaves em comum (duplicatas): {len(chaves_duplicadas):,}")
        print(f"🆕 Chaves novas: {len(chaves_novas):,}")
        print(f"📊 Taxa de novidade: {len(chaves_novas)/len(chaves_atual)*100:.1f}%")
        
        # Filtrar apenas registros novos
        df_novo = df_atual[df_atual['chave_unica'].isin(chaves_novas)].copy()
        df_novo = df_novo.drop('chave_unica', axis=1)
        
        print(f"✅ Registros novos para importar: {len(df_novo):,}")
        
        # Mostrar alguns exemplos de duplicatas
        if len(chaves_duplicadas) > 0:
            print(f"\n📋 === EXEMPLOS DE DUPLICATAS === 📋")
            exemplos_dup = list(chaves_duplicadas)[:5]
            for chave in exemplos_dup:
                venda_id, data = chave.split('|')
                print(f"   {venda_id[:8]}... | {data}")
    
    else:
        print(f"\n⚠️ === SEM ARQUIVO ANTERIOR === ⚠️")
        print(f"📊 Todos os {len(df_atual):,} registros serão considerados novos")
        df_novo = df_atual.copy()
    
    # 4. Análise dos dados novos
    if len(df_novo) > 0:
        print(f"\n📊 === ANÁLISE DOS DADOS NOVOS === 📊")
        
        # Período
        df_novo['data_entrega_dt'] = pd.to_datetime(df_novo['data_entrega'])
        inicio = df_novo['data_entrega_dt'].min().strftime('%Y-%m-%d')
        fim = df_novo['data_entrega_dt'].max().strftime('%Y-%m-%d')
        print(f"📅 Período: {inicio} → {fim}")
        
        # Vendas únicas
        print(f"🛒 Vendas únicas: {df_novo['venda_id'].nunique():,}")
        
        # Vendedores
        vendedores_validos = df_novo['vendedor_id'].dropna()
        print(f"👤 Vendedores: {vendedores_validos.nunique():,} únicos")
        
        # Lentes vs óculos
        carne_dist = df_novo['tem_carne'].value_counts()
        print(f"🥩 Com lentes: {carne_dist.get(True, 0):,}")
        print(f"👓 Com óculos: {carne_dist.get(False, 0):,}")
    
    # 5. Salvar apenas os novos
    if len(df_novo) > 0:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        arquivo_novo = f'data/entregas_APENAS_NOVAS_{timestamp}.csv'
        
        df_novo.to_csv(arquivo_novo, index=False)
        
        print(f"\n💾 === ARQUIVO APENAS NOVOS === 💾")
        print(f"📄 Arquivo: {arquivo_novo}")
        print(f"📊 Registros: {len(df_novo):,}")
        print(f"✅ Livres de duplicatas com banco existente")
        
        # Verificação final
        print(f"\n🔍 === VERIFICAÇÃO FINAL === 🔍")
        
        # Verificar constraint única internamente
        duplicatas_internas = df_novo.duplicated(subset=['venda_id', 'data_entrega']).sum()
        print(f"✅ Duplicatas internas: {duplicatas_internas} (deve ser 0)")
        
        # Verificar UUIDs
        uuids_validos = df_novo['venda_id'].str.len().eq(36).all()
        print(f"✅ UUIDs válidos: {uuids_validos}")
        
        # Verificar datas
        datas_validas = pd.to_datetime(df_novo['data_entrega'], errors='coerce').notna().all()
        print(f"✅ Datas válidas: {datas_validas}")
        
        return arquivo_novo
    
    else:
        print(f"\n⚠️ === NENHUM REGISTRO NOVO === ⚠️")
        print(f"Todos os registros já existem no banco")
        return None

def consolidar_todos_arquivos():
    """
    Consolida todos os arquivos de entregas em um único
    """
    print(f"\n🔗 === CONSOLIDAÇÃO COMPLETA === 🔗")
    
    import glob
    arquivos_entregas = glob.glob('data/entregas_*.csv')
    
    # Excluir arquivos temporários
    arquivos_validos = [a for a in arquivos_entregas if not any(x in a for x in ['backup', 'temp', 'test'])]
    
    print(f"📋 Arquivos para consolidação: {len(arquivos_validos)}")
    
    if len(arquivos_validos) > 1:
        todos_dados = []
        total_registros = 0
        
        for arquivo in arquivos_validos:
            try:
                df = pd.read_csv(arquivo)
                df['fonte_arquivo'] = arquivo
                todos_dados.append(df)
                total_registros += len(df)
                print(f"   ✅ {arquivo}: {len(df):,} registros")
            except Exception as e:
                print(f"   ❌ {arquivo}: {e}")
        
        if todos_dados:
            # Consolidar
            df_consolidado = pd.concat(todos_dados, ignore_index=True, sort=False)
            
            # Remover duplicatas globais
            antes_dup = len(df_consolidado)
            df_consolidado = df_consolidado.drop_duplicates(subset=['venda_id', 'data_entrega'])
            depois_dup = len(df_consolidado)
            
            print(f"\n📊 Consolidação:")
            print(f"   📄 Total antes: {total_registros:,}")
            print(f"   🔄 Após união: {antes_dup:,}")
            print(f"   ✅ Após dedup: {depois_dup:,}")
            print(f"   🗑️ Duplicatas removidas: {antes_dup - depois_dup:,}")
            
            # Salvar consolidado
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            arquivo_consolidado = f'data/entregas_CONSOLIDADO_FINAL_{timestamp}.csv'
            
            # Remover coluna fonte_arquivo para estrutura limpa
            df_final = df_consolidado.drop('fonte_arquivo', axis=1, errors='ignore')
            df_final.to_csv(arquivo_consolidado, index=False)
            
            print(f"💾 Arquivo consolidado: {arquivo_consolidado}")
            print(f"📊 Registros finais: {len(df_final):,}")
            
            return arquivo_consolidado
    
    return None

def main():
    """Função principal"""
    print("🎯 === VERIFICAÇÃO E LIMPEZA DE DUPLICATAS === 🎯")
    
    # 1. Verificar e gerar apenas novos
    arquivo_novos = verificar_e_gerar_novas_entregas()
    
    # 2. Consolidar tudo
    arquivo_consolidado = consolidar_todos_arquivos()
    
    print(f"\n🎉 === RESULTADO FINAL === 🎉")
    
    if arquivo_novos:
        print(f"✅ Arquivo para importação (apenas novos): {arquivo_novos}")
        print(f"🚀 Este arquivo deve importar sem erros de duplicata!")
    else:
        print(f"⚠️ Nenhum registro novo para importar")
    
    if arquivo_consolidado:
        print(f"📦 Arquivo consolidado completo: {arquivo_consolidado}")
        print(f"📊 Contém todos os dados sem duplicatas")
    
    print(f"📅 Processado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()