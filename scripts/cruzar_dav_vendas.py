#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cruzamento de números de venda entre arquivos
- lista_sem_dav_limpo: números com zeros à esquerda (ex: 0001485)
- vendas_vixen_final e vendas_oss_final: números com .0 (ex: 1485.0)
"""

import pandas as pd

print("="*80)
print("🔍 CRUZAMENTO DE NÚMEROS DE VENDA")
print("="*80)

# Carregar arquivos
print("\n📖 Carregando arquivos...")

df_dav = pd.read_csv('1_normalizacao/dados_processados/originais/controles_gerais/lista_dav/lista_sem_dav_limpo.csv',
                     sep=';', encoding='utf-8')
print(f"   ✅ lista_sem_dav_limpo: {len(df_dav):,} linhas")

df_vixen = pd.read_csv('1_normalizacao/dados_processados/vendas_para_importar/vendas_vixen_final.csv',
                       sep=';', encoding='utf-8')
print(f"   ✅ vendas_vixen_final: {len(df_vixen):,} linhas")

df_oss = pd.read_csv('1_normalizacao/dados_processados/vendas_para_importar/vendas_oss_final.csv',
                     sep=';', encoding='utf-8')
print(f"   ✅ vendas_oss_final: {len(df_oss):,} linhas")

# Função para normalizar números
def normalizar_numero(num):
    """Normaliza número removendo zeros à esquerda, pontos e vírgulas"""
    if pd.isna(num):
        return None
    # Converter para string, remover .0 final, remover zeros à esquerda
    num_str = str(num).replace('.0', '').strip()
    # Remover zeros à esquerda mas manter pelo menos um dígito
    num_normalizado = num_str.lstrip('0') or '0'
    return num_normalizado

print("\n🔧 Normalizando números...")

# Normalizar números em cada arquivo
df_dav['numero_normalizado'] = df_dav['Nro.DAV'].apply(normalizar_numero)
df_vixen['numero_normalizado'] = df_vixen['numero_venda'].apply(normalizar_numero)
df_oss['numero_normalizado'] = df_oss['numero_venda'].apply(normalizar_numero)

print(f"   Exemplos lista_dav: {df_dav['numero_normalizado'].head(5).tolist()}")
print(f"   Exemplos vixen: {df_vixen['numero_normalizado'].head(5).tolist()}")
print(f"   Exemplos oss: {df_oss['numero_normalizado'].head(5).tolist()}")

# Criar sets para cruzamento
set_dav = set(df_dav['numero_normalizado'].dropna())
set_vixen = set(df_vixen['numero_normalizado'].dropna())
set_oss = set(df_oss['numero_normalizado'].dropna())

print(f"\n📊 ESTATÍSTICAS:")
print(f"   Números únicos em lista_dav: {len(set_dav):,}")
print(f"   Números únicos em vixen: {len(set_vixen):,}")
print(f"   Números únicos em oss: {len(set_oss):,}")

# Cruzamentos
print(f"\n🔍 CRUZAMENTOS:")

# DAV x Vixen
dav_em_vixen = set_dav & set_vixen
print(f"\n1. DAV presentes em VIXEN:")
print(f"   Total: {len(dav_em_vixen):,} vendas")
print(f"   Exemplos: {list(dav_em_vixen)[:10]}")

# DAV x OSS
dav_em_oss = set_dav & set_oss
print(f"\n2. DAV presentes em OSS:")
print(f"   Total: {len(dav_em_oss):,} vendas")
print(f"   Exemplos: {list(dav_em_oss)[:10]}")

# DAV em ambos
dav_em_ambos = set_dav & set_vixen & set_oss
print(f"\n3. DAV presentes em VIXEN E OSS:")
print(f"   Total: {len(dav_em_ambos):,} vendas")
if dav_em_ambos:
    print(f"   Exemplos: {list(dav_em_ambos)[:10]}")

# DAV não encontrados
dav_nao_encontrados = set_dav - set_vixen - set_oss
print(f"\n4. DAV NÃO encontrados em nenhum arquivo de vendas:")
print(f"   Total: {len(dav_nao_encontrados):,} vendas")
if dav_nao_encontrados:
    print(f"   Exemplos: {list(dav_nao_encontrados)[:10]}")

# Salvar relatório detalhado
print(f"\n💾 Gerando relatório detalhado...")

# DAVs não encontrados com detalhes
df_nao_encontrados = df_dav[df_dav['numero_normalizado'].isin(dav_nao_encontrados)]
df_nao_encontrados_detalhado = df_nao_encontrados[[
    'Nro.DAV', 'numero_normalizado', 'Cliente', 'Vendedor', 
    'Vl.líquido', 'Status', 'Dh.DAV'
]].copy()

arquivo_relatorio = '1_normalizacao/dados_processados/originais/controles_gerais/lista_dav/relatorio_cruzamento_dav.csv'
df_nao_encontrados_detalhado.to_csv(arquivo_relatorio, index=False, sep=';', encoding='utf-8')

print(f"   ✅ Relatório salvo: {arquivo_relatorio}")

print("\n" + "="*80)
print("✅ CRUZAMENTO CONCLUÍDO!")
print("="*80)

print(f"\n📋 RESUMO:")
print(f"   • Total de DAVs analisados: {len(set_dav):,}")
print(f"   • Encontrados em Vixen: {len(dav_em_vixen):,} ({len(dav_em_vixen)/len(set_dav)*100:.1f}%)")
print(f"   • Encontrados em OSS: {len(dav_em_oss):,} ({len(dav_em_oss)/len(set_dav)*100:.1f}%)")
print(f"   • Encontrados em ambos: {len(dav_em_ambos):,} ({len(dav_em_ambos)/len(set_dav)*100:.1f}%)")
print(f"   • NÃO encontrados: {len(dav_nao_encontrados):,} ({len(dav_nao_encontrados)/len(set_dav)*100:.1f}%)")

print("\n" + "="*80)
