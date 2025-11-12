"""
Script para remover linhas onde nn_venda não é um número válido
Remove linhas completas quando nn_venda contém texto, vazios, etc.
"""

import pandas as pd
from pathlib import Path
import numpy as np

# Diretório das vendas
diretorio_vendas = Path('D:/projetos/carne_facil/carne_facil/1_normalizacao/dados_processados/originais/cxs/finais_postgresql_prontos/vendas')

# Listar todos os arquivos
arquivos = sorted(diretorio_vendas.glob('vendas_*_final.csv'))

print("=" * 80)
print("REMOÇÃO DE LINHAS COM nn_venda NÃO NUMÉRICO")
print("=" * 80)

total_geral_removido = 0
total_geral_mantido = 0

for arquivo in arquivos:
    print(f"\n{'=' * 80}")
    print(f"ARQUIVO: {arquivo.name}")
    print("=" * 80)
    
    # Ler arquivo
    try:
        df = pd.read_csv(arquivo, sep=',', dtype=str, encoding='utf-8-sig')
    except Exception as e:
        print(f"❌ Erro ao ler arquivo: {e}")
        continue
    
    total_antes = len(df)
    print(f"\n📊 Total de registros ANTES: {total_antes}")
    
    # Criar função para verificar se é número
    def is_numeric(value):
        if pd.isna(value):
            return False
        if value in ['nan', '', ' ']:
            return False
        try:
            # Tenta converter para número
            float(str(value).strip())
            return True
        except (ValueError, TypeError):
            return False
    
    # Identificar linhas válidas (onde nn_venda É número)
    mask_valido = df['nn_venda'].apply(is_numeric)
    
    # Linhas que serão removidas
    linhas_invalidas = df[~mask_valido]
    total_invalido = len(linhas_invalidas)
    
    print(f"🔴 Linhas com nn_venda NÃO numérico: {total_invalido}")
    
    if total_invalido > 0:
        # Mostrar exemplos
        print(f"\n📋 Exemplos de nn_venda inválidos (primeiros 10):")
        exemplos = linhas_invalidas['nn_venda'].head(10).tolist()
        for idx, valor in enumerate(exemplos, 1):
            print(f"   {idx}. '{valor}'")
        
        # Filtrar apenas linhas válidas
        df_limpo = df[mask_valido].copy()
        
        total_depois = len(df_limpo)
        total_removido = total_antes - total_depois
        
        print(f"\n✅ Linhas MANTIDAS (nn_venda numérico): {total_depois}")
        print(f"❌ Linhas REMOVIDAS: {total_removido}")
        
        # Atualizar contadores gerais
        total_geral_removido += total_removido
        total_geral_mantido += total_depois
        
        # Salvar arquivo limpo
        print(f"\n💾 Salvando arquivo limpo...")
        df_limpo.to_csv(arquivo, sep=',', index=False, encoding='utf-8-sig')
        print(f"✅ Arquivo salvo: {arquivo.name}")
        
        # Mostrar estatísticas
        print(f"\n📊 RESUMO:")
        print(f"   - Antes: {total_antes} registros")
        print(f"   - Depois: {total_depois} registros")
        print(f"   - Removidos: {total_removido} registros ({total_removido/total_antes*100:.1f}%)")
    else:
        print("✅ Nenhuma linha inválida encontrada!")
        total_geral_mantido += total_antes

print(f"\n{'=' * 80}")
print("✅ PROCESSAMENTO CONCLUÍDO!")
print("=" * 80)
print(f"\n📊 ESTATÍSTICAS GERAIS:")
print(f"   - Total de linhas mantidas: {total_geral_mantido:,}")
print(f"   - Total de linhas removidas: {total_geral_removido:,}")
if total_geral_removido > 0:
    taxa_remocao = total_geral_removido / (total_geral_mantido + total_geral_removido) * 100
    print(f"   - Taxa de remoção: {taxa_remocao:.2f}%")
