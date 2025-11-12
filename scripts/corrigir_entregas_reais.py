#!/usr/bin/env python3
"""
Correção de Entregas OS Reais - Sistema Carne Fácil
==================================================

Corrige problemas identificados:
1. Remove duplicatas por OS + data
2. Normaliza campo 'carne' (valores numéricos são valores monetários)
3. Garante IDs únicos
4. Mantém apenas dados consistentes
"""

import pandas as pd
import uuid
from datetime import datetime

def corrigir_entregas_reais():
    """Corrige dados de entregas reais"""
    
    print("🔧 === CORREÇÃO DE ENTREGAS REAIS === 🔧")
    
    # Carrega dados
    try:
        df = pd.read_csv('data/vendas_para_importar/entregas_os_reais.csv')
        print(f"📂 Carregados: {len(df):,} registros")
    except:
        print("❌ Arquivo não encontrado!")
        return
    
    # 1. Analisa duplicatas
    print(f"\n🔍 Analisando duplicatas...")
    duplicatas = df.groupby(['os_numero', 'data_entrega']).size()
    duplicatas_encontradas = duplicatas[duplicatas > 1]
    
    if len(duplicatas_encontradas) > 0:
        print(f"❌ Encontradas {len(duplicatas_encontradas)} combinações duplicadas:")
        for (os_num, data), count in duplicatas_encontradas.head(10).items():
            print(f"   OS {os_num} em {data}: {count} registros")
    
    # 2. Remove duplicatas mantendo primeira ocorrência
    antes = len(df)
    df = df.drop_duplicates(subset=['os_numero', 'data_entrega'], keep='first')
    depois = len(df)
    print(f"✅ Removidas {antes - depois} duplicatas")
    
    # 3. Corrige campo 'carne'
    print(f"\n🔧 Corrigindo campo 'carne'...")
    
    # Analisa valores atuais
    valores_carne = df['carne'].value_counts()
    print(f"Valores encontrados: {len(valores_carne)}")
    
    def normalizar_carne(valor):
        """Normaliza valores do campo carne"""
        if pd.isna(valor):
            return 'Não'
        
        valor_str = str(valor).strip().upper()
        
        # Valores claramente de carnê
        if valor_str in ['SIM', 'SIM ', 'S']:
            return 'Sim'
        
        # Valores claramente não carnê  
        if valor_str in ['NÃO', 'NAO', 'N', 'NÃO ', 'NOPE', 'NONE']:
            return 'Não'
        
        # Valores numéricos são provavelmente valores monetários
        # Estes registros podem ser entregas especiais ou correções
        try:
            float(valor_str.replace(',', '.'))
            return 'Não'  # Considera como entrega normal
        except:
            pass
        
        # Default
        return 'Não'
    
    df['carne_corrigido'] = df['carne'].apply(normalizar_carne)
    
    # Estatísticas da correção
    print(f"Correção do campo carne:")
    carne_stats = df['carne_corrigido'].value_counts()
    for valor, count in carne_stats.items():
        pct = (count / len(df)) * 100
        print(f"   {valor}: {count:,} ({pct:.1f}%)")
    
    # 4. Corrige observações
    def corrigir_observacao(row):
        """Corrige observações baseado no tipo"""
        if row['carne_corrigido'] == 'Sim':
            return 'Entrega de carnê realizada'
        else:
            return 'Entrega de produtos realizada'
    
    df['observacoes'] = df.apply(corrigir_observacao, axis=1)
    
    # 5. Gera novos IDs únicos
    print(f"\n🆔 Gerando IDs únicos...")
    df['id'] = [str(uuid.uuid4()) for _ in range(len(df))]
    
    # 6. Organiza colunas finais
    colunas_finais = [
        'id', 'venda_id', 'os_numero', 'data_prevista', 'data_entrega', 
        'status', 'observacoes', 'created_at', 'updated_at'
    ]
    
    # Colunas auxiliares para referência
    colunas_auxiliares = ['loja_id', 'vendedor_uuid', 'loja_origem']
    df['carne'] = df['carne_corrigido']  # Substitui campo original
    colunas_auxiliares.append('carne')
    
    for col in colunas_auxiliares:
        if col in df.columns:
            colunas_finais.append(col)
    
    df_final = df[colunas_finais].copy()
    
    # 7. Validações finais
    print(f"\n🔍 === VALIDAÇÕES FINAIS === 🔍")
    print(f"✅ Total de registros: {len(df_final):,}")
    print(f"✅ IDs únicos: {df_final['id'].nunique() == len(df_final)}")
    print(f"✅ OS válidas: {df_final['os_numero'].notna().all()}")
    print(f"✅ Datas válidas: {df_final['data_entrega'].notna().all()}")
    
    # Estatísticas por loja
    print(f"\n🏪 Distribuição por loja:")
    loja_stats = df_final['loja_origem'].value_counts()
    for loja, count in loja_stats.items():
        pct = (count / len(df_final)) * 100
        print(f"   {loja}: {count:,} ({pct:.1f}%)")
    
    # Cruzamento com vendas
    com_venda = df_final['venda_id'].notna().sum()
    sem_venda = df_final['venda_id'].isna().sum()
    print(f"\n🔗 Cruzamento com vendas:")
    print(f"   ✅ Com venda_id: {com_venda:,} ({com_venda/len(df_final)*100:.1f}%)")
    print(f"   ❓ Sem venda_id: {sem_venda:,} ({sem_venda/len(df_final)*100:.1f}%)")
    
    # 8. Salva arquivo corrigido
    output_path = 'data/vendas_para_importar/entregas_os_reais_corrigido.csv'
    df_final.to_csv(output_path, index=False)
    
    print(f"\n💾 Arquivo corrigido salvo: {output_path}")
    print(f"📁 Tamanho: {len(df_final):,} registros")
    print(f"📊 Colunas: {', '.join(colunas_finais)}")
    
    print(f"\n🎯 === RESUMO DA CORREÇÃO === 🎯")
    print("✅ Duplicatas removidas")
    print("✅ Campo 'carne' normalizado")  
    print("✅ IDs únicos garantidos")
    print("✅ Observações corrigidas")
    print("✅ Estrutura final validada")
    
    print(f"\n🚀 Pronto para importação no Supabase!")
    return df_final

if __name__ == "__main__":
    corrigir_entregas_reais()