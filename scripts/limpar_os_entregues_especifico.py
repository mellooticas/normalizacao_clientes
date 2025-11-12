#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Limpeza específica dos dados de OS_ENTREGUES_DIA
Remove headers e dados inválidos
"""

import pandas as pd
import os

def limpar_os_entregues_dia():
    """Limpa dados de OS_ENTREGUES_DIA removendo headers e valores inválidos"""
    
    print("🧹 LIMPEZA ESPECÍFICA: OS_ENTREGUES_DIA")
    print("=" * 50)
    
    pasta_os_entregues = r"d:\projetos\carne_facil\carne_facil\data\originais\cxs\extraidos_corrigidos\os_entregues_dia"
    
    # Headers e valores inválidos a serem removidos
    valores_invalidos = {
        'os': ['OS', 'Entrega de Carne'],
        'vendedor': ['Vendedor', 'Parcelas'],
        'carne': ['CARNE', 'Valor Total']
    }
    
    arquivos_csv = [f for f in os.listdir(pasta_os_entregues) if f.endswith('.csv')]
    
    total_removidos = 0
    
    for arquivo in sorted(arquivos_csv):
        caminho_arquivo = os.path.join(pasta_os_entregues, arquivo)
        
        print(f"🧹 {arquivo}")
        
        # Ler dados
        df = pd.read_csv(caminho_arquivo)
        registros_originais = len(df)
        
        # Remover headers das colunas específicas
        mask_valido = pd.Series([True] * len(df))
        
        for coluna, invalidos in valores_invalidos.items():
            if coluna in df.columns:
                mask_invalido = df[coluna].isin(invalidos)
                mask_valido = mask_valido & ~mask_invalido
                removidos_coluna = mask_invalido.sum()
                if removidos_coluna > 0:
                    print(f"   ✂️  {removidos_coluna} headers removidos de '{coluna}'")
        
        # Remover linhas onde 'os' não é numérico (exceto NaN)
        if 'os' in df.columns:
            # Tentar converter para numérico, inválidos ficam NaN
            os_numerico = pd.to_numeric(df['os'], errors='coerce')
            mask_os_valido = os_numerico.notna()
            
            # Combinar com mask anterior
            mask_final = mask_valido & mask_os_valido
            removidos_os = (~mask_os_valido).sum()
            if removidos_os > 0:
                print(f"   ✂️  {removidos_os} OS não numéricos removidos")
        else:
            mask_final = mask_valido
        
        # Aplicar filtro
        df_limpo = df[mask_final].copy()
        
        # Garantir que 'os' seja numérico
        if 'os' in df_limpo.columns:
            df_limpo['os'] = pd.to_numeric(df_limpo['os'], errors='coerce')
        
        # Remover linhas completamente vazias
        df_limpo = df_limpo.dropna(how='all')
        
        registros_finais = len(df_limpo)
        removidos = registros_originais - registros_finais
        total_removidos += removidos
        
        # Salvar arquivo limpo
        df_limpo.to_csv(caminho_arquivo, index=False)
        
        print(f"   📊 {registros_originais:,} → {registros_finais:,} registros (-{removidos:,})")
    
    print(f"\n✅ LIMPEZA CONCLUÍDA!")
    print(f"🧹 Total de registros inválidos removidos: {total_removidos:,}")
    
    # Verificar resultado final
    print(f"\n📊 VERIFICAÇÃO FINAL:")
    print("-" * 30)
    
    for arquivo in sorted(arquivos_csv):
        caminho_arquivo = os.path.join(pasta_os_entregues, arquivo)
        df = pd.read_csv(caminho_arquivo)
        
        if len(df) > 0:
            # Estatísticas básicas
            os_unicos = df['os'].nunique() if 'os' in df.columns else 0
            vendedores_unicos = df['vendedor'].nunique() if 'vendedor' in df.columns else 0
            
            print(f"📄 {arquivo}: {len(df):,} registros, {os_unicos:,} OS únicas, {vendedores_unicos} vendedores")
            
            # Mostrar amostra dos primeiros registros
            if 'os' in df.columns and 'vendedor' in df.columns:
                amostra = df[['os', 'vendedor', 'carne']].head(3)
                for _, row in amostra.iterrows():
                    print(f"   • OS {row['os']}: {row['vendedor']} - Carnê: {row['carne']}")
        else:
            print(f"📄 {arquivo}: VAZIO")

if __name__ == "__main__":
    limpar_os_entregues_dia()