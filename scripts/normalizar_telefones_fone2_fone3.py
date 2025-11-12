"""
Script para normalizar as colunas 'Fone.2' e 'Fone.3' do arquivo clientes_vixen_completo.csv
Formato padrão: (XX)XXXXXXXXX

Ações:
1. Remove espaços em branco
2. Remove prefixos (CEL:, RES:, FAX:, COM:, FIXO:)
3. Remove código país (55)
4. Corrige DDD duplicado (11)11 -> (11)
5. Adiciona DDD (11) quando ausente
6. Remove hífens
7. Padroniza formato (XX)XXXXXXXXX
"""

import pandas as pd
import re
from pathlib import Path

# Caminhos
BASE_DIR = Path(__file__).parent.parent
INPUT_FILE = BASE_DIR / 'dados_processados' / 'originais' / 'vixen' / 'extraidos_corrigidos' / 'clientes_vixen_completo.csv'

def limpar_telefone(valor):
    """Limpa e normaliza um número de telefone"""
    if pd.isna(valor):
        return None
    
    # Converter para string e remover espaços
    telefone = str(valor).strip()
    
    # Se for vazio após strip, retornar None
    if not telefone:
        return None
    
    # Remover prefixos (CEL:, RES:, FAX:, COM:, FIXO:, etc)
    telefone = re.sub(r'^(CEL|RES|FAX|COM|FIXO|FONE):\s*', '', telefone, flags=re.IGNORECASE)
    
    # Remover código país 55
    telefone = re.sub(r'55\s*', '', telefone)
    
    # Remover todos os caracteres não numéricos
    apenas_numeros = re.sub(r'\D', '', telefone)
    
    # Se não sobrou nada, retornar None
    if not apenas_numeros:
        return None
    
    # Corrigir DDD duplicado (começando com 1111)
    if apenas_numeros.startswith('1111'):
        apenas_numeros = '11' + apenas_numeros[4:]
    
    # Determinar DDD e número
    if len(apenas_numeros) == 11:
        # Formato: DDXXXXXXXXX (com 9 dígitos no número)
        ddd = apenas_numeros[:2]
        numero = apenas_numeros[2:]
    elif len(apenas_numeros) == 10:
        # Formato: DDXXXXXXXX (sem 9 inicial, telefone fixo)
        ddd = apenas_numeros[:2]
        numero = apenas_numeros[2:]
    elif len(apenas_numeros) == 9:
        # Apenas número sem DDD (celular), assumir DDD 11
        ddd = '11'
        numero = apenas_numeros
    elif len(apenas_numeros) == 8:
        # Apenas número sem DDD (fixo), assumir DDD 11
        ddd = '11'
        numero = apenas_numeros
    elif len(apenas_numeros) > 11:
        # Muito longo, tentar extrair os últimos 11 dígitos
        apenas_numeros = apenas_numeros[-11:]
        ddd = apenas_numeros[:2]
        numero = apenas_numeros[2:]
    elif len(apenas_numeros) < 8:
        # Muito curto, número inválido - manter como está com DDD 11
        ddd = '11'
        numero = apenas_numeros
    else:
        # Casos intermediários, assumir DDD 11
        ddd = '11'
        numero = apenas_numeros
    
    # Formatar no padrão (XX)XXXXXXXXX
    telefone_formatado = f'({ddd}){numero}'
    
    return telefone_formatado

def processar_coluna(df, col_name):
    """Processa uma coluna de telefone"""
    print(f"\n{'='*80}")
    print(f"PROCESSANDO COLUNA: {col_name}")
    print('='*80)
    
    # Verificar se a coluna existe
    if col_name not in df.columns:
        print(f"  ⚠️  Coluna '{col_name}' não encontrada no arquivo")
        return df, 0
    
    # Estatísticas antes
    print("\nANTES da normalização:")
    print(f"  Registros com telefone: {df[col_name].notna().sum():,}")
    print(f"  Registros vazios: {df[col_name].isna().sum():,}")
    
    # Backup da coluna original
    backup_col = f'{col_name}_original'
    df[backup_col] = df[col_name].copy()
    
    # Aplicar normalização
    print("\nAplicando normalizações...")
    df[col_name] = df[col_name].apply(limpar_telefone)
    print("  ✓ Concluído")
    
    # Estatísticas depois
    print("\nDEPOIS da normalização:")
    print(f"  Registros com telefone: {df[col_name].notna().sum():,}")
    print(f"  Registros vazios: {df[col_name].isna().sum():,}")
    
    # Análise de mudanças
    mudancas = df[df[col_name] != df[backup_col]]
    qtd_mudancas = len(mudancas)
    print(f"\nTotal de registros modificados: {qtd_mudancas:,}")
    
    # Mostrar exemplos de mudanças
    if len(mudancas) > 0:
        print("\nEXEMPLOS DE MUDANÇAS (primeiros 15):")
        print("-"*80)
        for i, (idx, row) in enumerate(mudancas.head(15).iterrows(), 1):
            original = row[backup_col]
            novo = row[col_name]
            original_str = str(original)[:40] if pd.notna(original) else 'None'
            novo_str = str(novo) if pd.notna(novo) else 'None'
            print(f"{i:2}. {original_str:40} → {novo_str}")
    
    # Análise de padrões
    print("\nPADRÕES APÓS NORMALIZAÇÃO:")
    print("-"*80)
    
    # Verificar formato (XX)XXXXXXXXX
    padrao_correto = df[col_name].dropna().apply(lambda x: bool(re.match(r'^\(\d{2}\)\d{8,9}$', str(x))))
    total_telefones = len(df[col_name].dropna())
    if total_telefones > 0:
        print(f"  Telefones no formato correto: {padrao_correto.sum():,} ({padrao_correto.sum()/total_telefones*100:.1f}%)")
        print(f"  Telefones em formato diferente: {total_telefones - padrao_correto.sum():,}")
        
        # Mostrar alguns telefones que não seguem o padrão
        nao_padrao = df[col_name].dropna()[~df[col_name].dropna().apply(lambda x: bool(re.match(r'^\(\d{2}\)\d{8,9}$', str(x))))]
        if len(nao_padrao) > 0:
            print(f"\n  Exemplos fora do padrão (primeiros 5):")
            for i, tel in enumerate(nao_padrao.head(5), 1):
                print(f"    {i}. {tel}")
    
    # Remover coluna backup
    df = df.drop(columns=[backup_col])
    
    return df, qtd_mudancas

def main():
    print("="*80)
    print("NORMALIZAÇÃO DE TELEFONES - Fone.2 e Fone.3")
    print("="*80)
    print()
    
    # Ler arquivo
    print(f"Lendo arquivo: {INPUT_FILE.name}")
    df = pd.read_csv(INPUT_FILE, sep=';', encoding='utf-8')
    print(f"  Total de registros: {len(df):,}")
    
    total_mudancas = 0
    
    # Processar Fone.2
    df, mudancas_fone2 = processar_coluna(df, 'Fone.2')
    total_mudancas += mudancas_fone2
    
    # Processar Fone.3
    df, mudancas_fone3 = processar_coluna(df, 'Fone.3')
    total_mudancas += mudancas_fone3
    
    # Resumo final
    print("\n" + "="*80)
    print("RESUMO FINAL")
    print("="*80)
    print(f"\nTotal de mudanças em Fone.2: {mudancas_fone2:,}")
    print(f"Total de mudanças em Fone.3: {mudancas_fone3:,}")
    print(f"Total geral de mudanças: {total_mudancas:,}")
    
    # Salvar arquivo
    print(f"\nSalvando alterações no arquivo original...")
    df.to_csv(INPUT_FILE, sep=';', index=False, encoding='utf-8')
    print("  ✓ Arquivo atualizado com sucesso")
    
    print("\n" + "="*80)
    print("NORMALIZAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*80)
    print(f"\n📄 Arquivo atualizado: {INPUT_FILE}")
    print()

if __name__ == '__main__':
    main()
