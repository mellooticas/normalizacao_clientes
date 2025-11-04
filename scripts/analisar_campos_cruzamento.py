#!/usr/bin/env python3
"""
Analisar Campos para Cruzamento VIXEN x OSS
===========================================

Analisa campos em comum entre VIXEN (clientes) e OSS (ordens de serviço) para identificar chaves de cruzamento.
"""

import pandas as pd
from pathlib import Path

def analisar_campos_arquivo(arquivo_path, nome_arquivo):
    print(f"\n📄 {nome_arquivo}:")
    
    try:
        df = pd.read_csv(arquivo_path)
        print(f"   📊 Registros: {len(df):,}")
        print(f"   📊 Colunas: {len(df.columns)}")
        
        print(f"   📋 Campos disponíveis:")
        for i, col in enumerate(df.columns, 1):
            # Verificar exemplos de dados
            valores_unicos = df[col].nunique()
            nulos = df[col].isnull().sum()
            
            # Mostrar amostra do campo se relevante para cruzamento
            amostra = ""
            if col.lower() in ['vendedor', 'cliente', 'nome', 'os', 'os_numero']:
                valores_exemplo = df[col].dropna().head(2).tolist()
                if valores_exemplo:
                    amostra = f" (ex: {valores_exemplo[0]})"
            
            print(f"      {i:2d}. {col:<25} | {valores_unicos:>5,} únicos | {nulos:>4} nulos{amostra}")
        
        return df.columns.tolist()
        
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return []

def identificar_campos_cruzamento(campos_vixen, campos_oss):
    print(f"\n🔗 ANÁLISE DE CAMPOS PARA CRUZAMENTO:")
    
    # Campos que podem ser usados para cruzamento
    campos_possiveis = {
        'vendedor': ['vendedor', 'Vendedor'],
        'cliente': ['cliente', 'Cliente', 'Nome Completo'],
        'os': ['os', 'OS', 'os_numero'],
        'data': ['data', 'Data'],
        'loja': ['loja', 'Loja', 'loja_nome']
    }
    
    print(f"   📊 Campos VIXEN: {len(campos_vixen)}")
    print(f"   📊 Campos OSS: {len(campos_oss)}")
    
    cruzamentos_possiveis = []
    
    for tipo, variações in campos_possiveis.items():
        vixen_match = None
        oss_match = None
        
        # Procurar em VIXEN
        for variacao in variações:
            if variacao in campos_vixen:
                vixen_match = variacao
                break
        
        # Procurar em OSS
        for variacao in variações:
            if variacao in campos_oss:
                oss_match = variacao
                break
        
        if vixen_match and oss_match:
            cruzamentos_possiveis.append({
                'tipo': tipo,
                'vixen_campo': vixen_match,
                'oss_campo': oss_match
            })
            print(f"   ✅ {tipo.upper()}: VIXEN.{vixen_match} ↔ OSS.{oss_match}")
        elif vixen_match:
            print(f"   ⚠️  {tipo.upper()}: Apenas VIXEN.{vixen_match}")
        elif oss_match:
            print(f"   ⚠️  {tipo.upper()}: Apenas OSS.{oss_match}")
        else:
            print(f"   ❌ {tipo.upper()}: Não encontrado")
    
    return cruzamentos_possiveis

def main():
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    cruzamento_dir = base_dir / "data" / "originais" / "cruzamento_vixen_oss"
    
    print("🔍 ANÁLISE DE CAMPOS PARA CRUZAMENTO")
    print("=" * 60)
    
    # Analisar arquivos VIXEN (um exemplo)
    vixen_maua = cruzamento_dir / "clientes_vixen_maua_original.csv"
    campos_vixen = analisar_campos_arquivo(vixen_maua, "VIXEN CLIENTES MAUA")
    
    # Analisar arquivos OSS (um exemplo)
    oss_maua = cruzamento_dir / "oss_maua_original.csv"
    campos_oss = analisar_campos_arquivo(oss_maua, "OSS MAUA")
    
    # Identificar campos para cruzamento
    cruzamentos = identificar_campos_cruzamento(campos_vixen, campos_oss)
    
    print(f"\n🎯 ESTRATÉGIAS DE CRUZAMENTO RECOMENDADAS:")
    
    if cruzamentos:
        for i, cruzamento in enumerate(cruzamentos, 1):
            print(f"   {i}. Por {cruzamento['tipo'].upper()}:")
            print(f"      🔹 VIXEN.{cruzamento['vixen_campo']} = OSS.{cruzamento['oss_campo']}")
    else:
        print(f"   ⚠️  Nenhum campo direto identificado para cruzamento")
    
    print(f"\n💡 OUTRAS POSSIBILIDADES:")
    print(f"   🔹 Cruzamento aproximado por nome do cliente")
    print(f"   🔹 Análise de vendedores em comum")
    print(f"   🔹 Agrupamento por loja para análises separadas")
    print(f"   🔹 Criação de relatórios consolidados por loja")
    
    print(f"\n📊 PRÓXIMOS PASSOS SUGERIDOS:")
    print(f"   1️⃣ Analisar qualidade dos dados de vendedores")
    print(f"   2️⃣ Verificar correspondência de nomes de clientes")
    print(f"   3️⃣ Criar mapeamento de vendedores")
    print(f"   4️⃣ Gerar relatório consolidado por loja")

if __name__ == "__main__":
    main()