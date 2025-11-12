#!/usr/bin/env python3
"""
Análise detalhada de duplicatas entre os 3 arquivos finais de vendas
Foco especial em VIXEN carnê vs VIXEN completo
"""

import pandas as pd
from pathlib import Path
import numpy as np

def analisar_duplicatas_arquivos_finais():
    """Analisa duplicatas entre os 3 arquivos finais"""
    
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    vendas_dir = base_dir / "data" / "vendas_para_importar"
    
    print("🔍 === ANÁLISE DE DUPLICATAS - 3 ARQUIVOS FINAIS === 🔍")
    print()
    
    # 1. Carrega os 3 arquivos
    print("📂 Carregando arquivos...")
    
    # Arquivo 1: OSS
    arquivo_oss = vendas_dir / "vendas_PRONTO_PARA_IMPORTAR_97pct_LIMPO.csv"
    oss_df = pd.read_csv(arquivo_oss)
    oss_df['fonte'] = 'OSS'
    print(f"✅ OSS: {len(oss_df)} vendas")
    
    # Arquivo 2: VIXEN Carnê
    arquivo_vixen_carne = vendas_dir / "vendas_VIXEN_VENDEDORES_REAIS.csv"
    vixen_carne_df = pd.read_csv(arquivo_vixen_carne)
    vixen_carne_df['fonte'] = 'VIXEN_CARNE'
    print(f"✅ VIXEN Carnê: {len(vixen_carne_df)} vendas")
    
    # Arquivo 3: VIXEN Completo
    arquivo_vixen_completo = vendas_dir / "vendas_COMPLETAS_ESTRUTURA_CORRIGIDA.csv"
    vixen_completo_df = pd.read_csv(arquivo_vixen_completo)
    vixen_completo_df['fonte'] = 'VIXEN_COMPLETO'
    print(f"✅ VIXEN Completo: {len(vixen_completo_df)} vendas")
    
    print(f"📊 Total carregado: {len(oss_df) + len(vixen_carne_df) + len(vixen_completo_df)} vendas")
    print()
    
    # 2. Análise de períodos
    print("📅 === ANÁLISE DE PERÍODOS === 📅")
    
    def analisar_periodo(df, nome):
        df['data_venda'] = pd.to_datetime(df['data_venda'])
        anos = sorted(df['data_venda'].dt.year.unique())
        print(f"   {nome}: {min(anos)}-{max(anos)} (anos: {anos})")
        return anos
    
    anos_oss = analisar_periodo(oss_df, "OSS")
    anos_vixen_carne = analisar_periodo(vixen_carne_df, "VIXEN Carnê")
    anos_vixen_completo = analisar_periodo(vixen_completo_df, "VIXEN Completo")
    
    # Sobreposições
    print(f"\n🔄 Sobreposições:")
    sobreposicao_2_3 = set(anos_vixen_carne).intersection(set(anos_vixen_completo))
    sobreposicao_1_2 = set(anos_oss).intersection(set(anos_vixen_carne))
    sobreposicao_1_3 = set(anos_oss).intersection(set(anos_vixen_completo))
    
    print(f"   VIXEN Carnê ∩ VIXEN Completo: {sorted(sobreposicao_2_3)} ⚠️")
    print(f"   OSS ∩ VIXEN Carnê: {sorted(sobreposicao_1_2)}")
    print(f"   OSS ∩ VIXEN Completo: {sorted(sobreposicao_1_3)}")
    print()
    
    # 3. Análise detalhada VIXEN Carnê vs VIXEN Completo
    print("🎯 === FOCO: VIXEN CARNÊ vs VIXEN COMPLETO === 🎯")
    
    # Criar chaves de comparação
    def criar_chave_comparacao(df):
        """Cria chaves para identificar duplicatas"""
        df = df.copy()
        df['chave_cliente_data_valor'] = (
            df['cliente_id'].astype(str) + "_" + 
            df['data_venda'].astype(str) + "_" + 
            df['valor_total'].astype(str)
        )
        df['chave_numero_loja'] = (
            df['numero_venda'].astype(str) + "_" + 
            df['loja_id'].astype(str)
        )
        return df
    
    vixen_carne_comp = criar_chave_comparacao(vixen_carne_df)
    vixen_completo_comp = criar_chave_comparacao(vixen_completo_df)
    
    # Duplicatas por cliente+data+valor
    print("🔍 Duplicatas por Cliente + Data + Valor:")
    chaves_carne = set(vixen_carne_comp['chave_cliente_data_valor'])
    chaves_completo = set(vixen_completo_comp['chave_cliente_data_valor'])
    duplicatas_cliente_data_valor = chaves_carne.intersection(chaves_completo)
    
    print(f"   VIXEN Carnê: {len(chaves_carne)} chaves únicas")
    print(f"   VIXEN Completo: {len(chaves_completo)} chaves únicas")
    print(f"   🔄 DUPLICATAS: {len(duplicatas_cliente_data_valor)} vendas")
    
    if duplicatas_cliente_data_valor:
        print(f"\n📋 Amostra de duplicatas (cliente+data+valor):")
        for i, chave in enumerate(list(duplicatas_cliente_data_valor)[:5]):
            venda_carne = vixen_carne_comp[vixen_carne_comp['chave_cliente_data_valor'] == chave].iloc[0]
            venda_completo = vixen_completo_comp[vixen_completo_comp['chave_cliente_data_valor'] == chave].iloc[0]
            print(f"   {i+1}. Cliente: {venda_carne['cliente_id'][:8]}... | Data: {venda_carne['data_venda']} | Valor: R$ {venda_carne['valor_total']}")
    
    # Duplicatas por número+loja
    print(f"\n🔍 Duplicatas por Número + Loja:")
    chaves_numero_carne = set(vixen_carne_comp['chave_numero_loja'])
    chaves_numero_completo = set(vixen_completo_comp['chave_numero_loja'])
    duplicatas_numero_loja = chaves_numero_carne.intersection(chaves_numero_completo)
    
    print(f"   VIXEN Carnê: {len(chaves_numero_carne)} números únicos")
    print(f"   VIXEN Completo: {len(chaves_numero_completo)} números únicos")
    print(f"   🔄 DUPLICATAS: {len(duplicatas_numero_loja)} números")
    
    if duplicatas_numero_loja:
        print(f"\n📋 Amostra de duplicatas (número+loja):")
        for i, chave in enumerate(list(duplicatas_numero_loja)[:5]):
            venda_carne = vixen_carne_comp[vixen_carne_comp['chave_numero_loja'] == chave].iloc[0]
            venda_completo = vixen_completo_comp[vixen_completo_comp['chave_numero_loja'] == chave].iloc[0]
            print(f"   {i+1}. Número: {venda_carne['numero_venda']} | Loja: {venda_carne['loja_id'][:8]}...")
    
    # 4. Análise por lojas
    print(f"\n🏪 === ANÁLISE POR LOJA === 🏪")
    
    def analisar_por_loja(df, nome):
        por_loja = df.groupby('loja_id').agg({
            'valor_total': ['count', 'sum']
        }).round(2)
        print(f"   {nome}:")
        for loja_id in df['loja_id'].unique():
            count = df[df['loja_id'] == loja_id]['valor_total'].count()
            soma = df[df['loja_id'] == loja_id]['valor_total'].sum()
            loja_nome = "SUZANO" if "52f92716" in loja_id else "MAUÁ" if "aa7a5646" in loja_id else "OUTRA"
            print(f"     {loja_nome}: {count} vendas (R$ {soma:,.2f})")
    
    analisar_por_loja(vixen_carne_df, "VIXEN Carnê")
    analisar_por_loja(vixen_completo_df, "VIXEN Completo")
    
    # 5. Recomendações
    print(f"\n💡 === RECOMENDAÇÕES === 💡")
    
    total_duplicatas = max(len(duplicatas_cliente_data_valor), len(duplicatas_numero_loja))
    
    if total_duplicatas > 0:
        percentual = (total_duplicatas / len(vixen_carne_df)) * 100
        print(f"⚠️  DUPLICATAS ENCONTRADAS:")
        print(f"   📊 {total_duplicatas} duplicatas ({percentual:.1f}% do VIXEN Carnê)")
        print(f"   🎯 AÇÃO: Remover duplicatas do arquivo menor (VIXEN Carnê)")
        print(f"   ✅ Manter: VIXEN Completo (mais abrangente)")
        
        # Criar arquivo VIXEN Carnê sem duplicatas
        print(f"\n🧹 Gerando VIXEN Carnê limpo...")
        
        vixen_carne_limpo = vixen_carne_comp[
            ~vixen_carne_comp['chave_cliente_data_valor'].isin(duplicatas_cliente_data_valor)
        ].copy()
        
        # Remove colunas temporárias
        vixen_carne_limpo = vixen_carne_limpo.drop(columns=['fonte', 'chave_cliente_data_valor', 'chave_numero_loja'])
        
        arquivo_limpo = vendas_dir / "vendas_VIXEN_CARNE_SEM_DUPLICATAS.csv"
        vixen_carne_limpo.to_csv(arquivo_limpo, index=False)
        
        print(f"💾 Arquivo limpo: {arquivo_limpo}")
        print(f"📊 Vendas restantes: {len(vixen_carne_limpo)} (eram {len(vixen_carne_df)})")
        print(f"🗑️  Removidas: {len(vixen_carne_df) - len(vixen_carne_limpo)} duplicatas")
        
        novo_total = len(oss_df) + len(vixen_carne_limpo) + len(vixen_completo_df)
        print(f"\n🎯 NOVO TOTAL APÓS LIMPEZA: {novo_total} vendas")
        
    else:
        print(f"✅ NENHUMA DUPLICATA ENCONTRADA!")
        print(f"🎉 Os 3 arquivos podem ser importados sem modificação")
    
    return {
        'duplicatas_encontradas': total_duplicatas > 0,
        'total_duplicatas': total_duplicatas,
        'arquivos_limpos': total_duplicatas > 0
    }

if __name__ == "__main__":
    resultado = analisar_duplicatas_arquivos_finais()
    
    if resultado['duplicatas_encontradas']:
        print(f"\n⚠️  AÇÃO NECESSÁRIA: Use o arquivo VIXEN Carnê limpo gerado!")
    else:
        print(f"\n✅ TUDO PRONTO: Pode importar os 3 arquivos originais!")