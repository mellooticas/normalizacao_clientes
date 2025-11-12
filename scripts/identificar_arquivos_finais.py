#!/usr/bin/env python3
"""
Identificação dos 3 arquivos finais de vendas para importação definitiva
Limpeza completa + reimportação organizada
"""

from pathlib import Path
import pandas as pd

def identificar_arquivos_finais():
    """Identifica os 3 arquivos finais que devem ser importados"""
    
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    
    print("🎯 === OS 3 ARQUIVOS FINAIS DE VENDAS === 🎯")
    print()
    
    # 1. OSS - Vendas originais processadas
    arquivo_oss = base_dir / "data" / "vendas_para_importar" / "vendas_PRONTO_PARA_IMPORTAR_97pct_LIMPO.csv"
    
    if arquivo_oss.exists():
        oss_df = pd.read_csv(arquivo_oss)
        print(f"📂 1. ARQUIVO OSS (Originais):")
        print(f"   📍 Arquivo: vendas_PRONTO_PARA_IMPORTAR_97pct_LIMPO.csv")
        print(f"   📊 Vendas: {len(oss_df):,}")
        print(f"   💰 Valor: R$ {oss_df['valor_total'].sum():,.2f}")
        print(f"   📅 Período: {oss_df['data_venda'].min()} a {oss_df['data_venda'].max()}")
        print(f"   🏪 Lojas: Todas (6 lojas)")
        print(f"   📋 Fonte: Dados originais OSS normalizados")
        print()
    else:
        print(f"❌ Arquivo OSS não encontrado!")
    
    # 2. VIXEN Carnê - Vendas carnê processadas
    arquivo_vixen_carne = base_dir / "data" / "vendas_para_importar" / "vendas_VIXEN_VENDEDORES_REAIS.csv"
    
    if arquivo_vixen_carne.exists():
        vixen_carne_df = pd.read_csv(arquivo_vixen_carne)
        print(f"📂 2. ARQUIVO VIXEN CARNÊ:")
        print(f"   📍 Arquivo: vendas_VIXEN_VENDEDORES_REAIS.csv")
        print(f"   📊 Vendas: {len(vixen_carne_df):,}")
        print(f"   💰 Valor: R$ {vixen_carne_df['valor_total'].sum():,.2f}")
        print(f"   📅 Período: {vixen_carne_df['data_venda'].min()} a {vixen_carne_df['data_venda'].max()}")
        print(f"   🏪 Lojas: Suzano + Mauá")
        print(f"   📋 Fonte: Trans_financ carnê VIXEN")
        print()
    else:
        print(f"❌ Arquivo VIXEN carnê não encontrado!")
    
    # 3. VIXEN Completo - Dataset completo outros pagamentos
    arquivo_vixen_completo = base_dir / "data" / "vendas_para_importar" / "vendas_COMPLETAS_ESTRUTURA_CORRIGIDA.csv"
    
    if arquivo_vixen_completo.exists():
        vixen_completo_df = pd.read_csv(arquivo_vixen_completo)
        print(f"📂 3. ARQUIVO VIXEN COMPLETO (Outros Pagamentos):")
        print(f"   📍 Arquivo: vendas_COMPLETAS_ESTRUTURA_CORRIGIDA.csv")
        print(f"   📊 Vendas: {len(vixen_completo_df):,}")
        print(f"   💰 Valor: R$ {vixen_completo_df['valor_total'].sum():,.2f}")
        print(f"   📅 Período: {vixen_completo_df['data_venda'].min()} a {vixen_completo_df['data_venda'].max()}")
        print(f"   🏪 Lojas: Suzano + Mauá")
        print(f"   📋 Fonte: Trans_financ outros pagamentos VIXEN (14k+ linhas)")
        print()
    else:
        print(f"❌ Arquivo VIXEN completo não encontrado!")
    
    # 4. Resumo Total
    print(f"🎯 === RESUMO TOTAL === 🎯")
    
    total_vendas = 0
    total_valor = 0
    
    if arquivo_oss.exists():
        total_vendas += len(oss_df)
        total_valor += oss_df['valor_total'].sum()
    
    if arquivo_vixen_carne.exists():
        total_vendas += len(vixen_carne_df)
        total_valor += vixen_carne_df['valor_total'].sum()
        
    if arquivo_vixen_completo.exists():
        total_vendas += len(vixen_completo_df)
        total_valor += vixen_completo_df['valor_total'].sum()
    
    print(f"📊 TOTAL DE VENDAS: {total_vendas:,}")
    print(f"💰 VALOR TOTAL: R$ {total_valor:,.2f}")
    print()
    
    # 5. Verificação de duplicatas potenciais
    print(f"⚠️  === VERIFICAÇÃO DE DUPLICATAS === ⚠️")
    
    if arquivo_oss.exists() and arquivo_vixen_completo.exists():
        # Verificar sobreposição de períodos
        oss_periodo = set(pd.to_datetime(oss_df['data_venda']).dt.year)
        vixen_periodo = set(pd.to_datetime(vixen_completo_df['data_venda']).dt.year)
        sobreposicao = oss_periodo.intersection(vixen_periodo)
        
        if sobreposicao:
            print(f"⚠️  Sobreposição de anos entre OSS e VIXEN: {sorted(sobreposicao)}")
            print(f"⚠️  CUIDADO: Pode haver duplicatas por período!")
        else:
            print(f"✅ Sem sobreposição de períodos entre OSS e VIXEN")
    
    # 6. Comandos para limpeza
    print(f"\n🧹 === COMANDOS PARA LIMPEZA COMPLETA === 🧹")
    print(f"Execute no Supabase:")
    print(f"```sql")
    print(f"-- Limpeza completa da tabela vendas")
    print(f"TRUNCATE TABLE vendas.vendas RESTART IDENTITY CASCADE;")
    print(f"")
    print(f"-- Verificar se está vazia")
    print(f"SELECT COUNT(*) FROM vendas.vendas;")
    print(f"```")
    
    return {
        'oss': arquivo_oss if arquivo_oss.exists() else None,
        'vixen_carne': arquivo_vixen_carne if arquivo_vixen_carne.exists() else None,
        'vixen_completo': arquivo_vixen_completo if arquivo_vixen_completo.exists() else None,
        'total_vendas': total_vendas,
        'total_valor': total_valor
    }

if __name__ == "__main__":
    arquivos = identificar_arquivos_finais()
    
    print(f"\n🎉 === ORDEM DE IMPORTAÇÃO === 🎉")
    print(f"1️⃣ OSS (originais) - Base histórica")
    print(f"2️⃣ VIXEN carnê - Carnês específicos") 
    print(f"3️⃣ VIXEN completo - Dataset completo outros pagamentos")
    print(f"\n💡 Após TRUNCATE, importe nesta ordem para evitar conflitos!")