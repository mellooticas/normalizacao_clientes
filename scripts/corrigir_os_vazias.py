#!/usr/bin/env python3
"""
Script para corrigir valores vazios de OS herdando da linha anterior
Sistema Carne Fácil - Correção de OS vazias
"""

import pandas as pd
import os
import numpy as np

def corrigir_os_vazias_arquivo(caminho_arquivo):
    """
    Corrige valores vazios de OS em um arquivo CSV
    """
    nome_arquivo = os.path.basename(caminho_arquivo)
    print(f"   📄 Processando: {nome_arquivo}")
    
    try:
        # Carregar dados
        df = pd.read_csv(caminho_arquivo)
        
        if 'os' not in df.columns:
            print(f"      ⚠️  Coluna 'os' não encontrada")
            return False
        
        # Contar valores vazios antes
        vazios_antes = df['os'].isna().sum() + (df['os'] == '').sum()
        
        if vazios_antes == 0:
            print(f"      ✅ Nenhuma OS vazia encontrada")
            return True
        
        # Aplicar forward fill para propagar última OS válida
        # Converter para string primeiro para tratar valores mistos
        df['os'] = df['os'].astype(str)
        
        # Substituir strings vazias por NaN
        df['os'] = df['os'].replace('', pd.NA)
        df['os'] = df['os'].replace('nan', pd.NA)
        
        # Forward fill - propagar último valor válido
        df['os'] = df['os'].fillna(method='ffill')
        
        # Contar valores vazios depois
        vazios_depois = df['os'].isna().sum() + (df['os'] == '').sum()
        
        # Salvar arquivo corrigido
        df.to_csv(caminho_arquivo, index=False, encoding='utf-8')
        
        corrigidos = vazios_antes - vazios_depois
        print(f"      ✅ {corrigidos} OS vazias corrigidas ({vazios_antes} → {vazios_depois})")
        
        return True
        
    except Exception as e:
        print(f"      ❌ Erro: {str(e)}")
        return False

def corrigir_pasta_tipo(pasta_tipo, nome_tipo):
    """
    Corrige todos os arquivos CSV de um tipo específico
    """
    print(f"\n📋 CORRIGINDO: {nome_tipo.upper()}")
    print("-" * 40)
    
    if not os.path.exists(pasta_tipo):
        print(f"   ❌ Pasta não encontrada: {pasta_tipo}")
        return
    
    # Listar arquivos CSV
    arquivos_csv = [f for f in os.listdir(pasta_tipo) if f.endswith('.csv')]
    
    if not arquivos_csv:
        print(f"   ⚠️  Nenhum arquivo CSV encontrado")
        return
    
    sucessos = 0
    
    for arquivo in sorted(arquivos_csv):
        caminho_arquivo = os.path.join(pasta_tipo, arquivo)
        if corrigir_os_vazias_arquivo(caminho_arquivo):
            sucessos += 1
    
    print(f"   📊 {sucessos}/{len(arquivos_csv)} arquivos corrigidos com sucesso")

def validar_correcoes(pasta_base):
    """
    Valida se as correções foram aplicadas corretamente
    """
    print(f"\n🔍 VALIDANDO CORREÇÕES")
    print("=" * 30)
    
    tipos_com_os = [
        'recebimento_carne',
        'os_entregues_dia', 
        'entrega_carne'
    ]
    
    resumo_validacao = {}
    
    for tipo in tipos_com_os:
        pasta_tipo = os.path.join(pasta_base, tipo)
        
        if not os.path.exists(pasta_tipo):
            continue
            
        # Verificar arquivo consolidado
        arquivo_consolidado = os.path.join(pasta_tipo, f'{tipo}_todas_lojas.csv')
        
        if os.path.exists(arquivo_consolidado):
            try:
                df = pd.read_csv(arquivo_consolidado)
                
                if 'os' in df.columns:
                    total_registros = len(df)
                    os_vazias = df['os'].isna().sum() + (df['os'] == '').sum()
                    
                    resumo_validacao[tipo] = {
                        'total_registros': total_registros,
                        'os_vazias': os_vazias,
                        'percentual_vazias': (os_vazias / total_registros * 100) if total_registros > 0 else 0
                    }
                    
                    status = "✅" if os_vazias == 0 else "⚠️"
                    print(f"   {status} {tipo}: {os_vazias} vazias de {total_registros} ({(os_vazias/total_registros*100):.1f}%)")
                    
            except Exception as e:
                print(f"   ❌ Erro ao validar {tipo}: {str(e)}")
    
    return resumo_validacao

def analisar_padroes_os(pasta_base):
    """
    Analisa padrões de OS após correção
    """
    print(f"\n📊 ANÁLISE DE PADRÕES DE OS")
    print("=" * 40)
    
    tipos_com_os = [
        'recebimento_carne',
        'os_entregues_dia', 
        'entrega_carne'
    ]
    
    for tipo in tipos_com_os:
        arquivo_consolidado = os.path.join(pasta_base, tipo, f'{tipo}_todas_lojas.csv')
        
        if os.path.exists(arquivo_consolidado):
            try:
                df = pd.read_csv(arquivo_consolidado)
                
                if 'os' in df.columns:
                    # Análise básica
                    os_unicas = df['os'].nunique()
                    total_registros = len(df)
                    
                    print(f"\n   📋 {tipo.upper()}:")
                    print(f"      📈 Total registros: {total_registros}")
                    print(f"      🔢 OS únicas: {os_unicas}")
                    print(f"      📊 Média reg/OS: {total_registros/os_unicas:.1f}")
                    
                    # Top 5 OS com mais registros
                    top_os = df['os'].value_counts().head(5)
                    print(f"      🏆 Top 5 OS com mais registros:")
                    for os_num, count in top_os.items():
                        print(f"         OS {os_num}: {count} registros")
                    
            except Exception as e:
                print(f"   ❌ Erro ao analisar {tipo}: {str(e)}")

def main():
    """Função principal"""
    print("🔄 CORREÇÃO DE OS VAZIAS NOS CSVS")
    print("=" * 60)
    print("💡 Problema: Quando OS está vazia, deve herdar da linha anterior")
    
    # Pasta base dos dados extraídos
    pasta_base = 'data/originais/cxs/extraidos_por_tipo'
    
    if not os.path.exists(pasta_base):
        print(f"❌ Pasta base não encontrada: {pasta_base}")
        return
    
    # Tipos que têm coluna OS
    tipos_com_os = [
        ('recebimento_carne', 'Recebimento de Carnês'),
        ('os_entregues_dia', 'OS Entregues no Dia'),
        ('entrega_carne', 'Entrega de Carnês')
    ]
    
    print(f"\n📋 Tipos a corrigir:")
    for tipo_pasta, tipo_nome in tipos_com_os:
        print(f"   • {tipo_nome}")
    
    # Corrigir cada tipo
    for tipo_pasta, tipo_nome in tipos_com_os:
        pasta_tipo = os.path.join(pasta_base, tipo_pasta)
        corrigir_pasta_tipo(pasta_tipo, tipo_nome)
    
    # Validar correções
    resumo = validar_correcoes(pasta_base)
    
    # Analisar padrões
    analisar_padroes_os(pasta_base)
    
    print(f"\n✅ CORREÇÃO DE OS VAZIAS CONCLUÍDA!")
    print(f"📁 Arquivos atualizados em: {pasta_base}")
    print(f"🎯 Próximo passo: Verificar se todas as OS foram herdadas corretamente")

if __name__ == "__main__":
    main()