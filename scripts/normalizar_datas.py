"""
Script para normalizar as colunas de data do arquivo clientes_vixen_completo.csv
Formato padrão: dd/mm/yyyy (apenas data, sem hora)

Colunas a normalizar:
- Dt de aniversário (dd/mm/yyyy hh:mm → dd/mm/yyyy)
- Dh.inclusão (dd/mm/yyyy hh:mm → dd/mm/yyyy)
- Dh.alteração (yyyy-mm-dd hh:mm:ss ou /  /       :  :   → dd/mm/yyyy ou None)
"""

import pandas as pd
import re
from datetime import datetime
from pathlib import Path

# Caminhos
BASE_DIR = Path(__file__).parent.parent
INPUT_FILE = BASE_DIR / 'dados_processados' / 'originais' / 'vixen' / 'extraidos_corrigidos' / 'clientes_vixen_completo.csv'

def normalizar_data(valor):
    """Normaliza uma data para o formato dd/mm/yyyy (sem hora)"""
    if pd.isna(valor):
        return None
    
    # Converter para string e remover espaços extras
    data_str = str(valor).strip()
    
    # Se for vazio, retornar None
    if not data_str:
        return None
    
    # Se for o padrão inválido '/  /       :  :' ou similar
    if re.match(r'^/\s+/\s+:', data_str):
        return None
    
    try:
        # Padrão 1: dd/mm/yyyy hh:mm (remover hora)
        match = re.match(r'^(\d{2}/\d{2}/\d{4})\s+\d{2}:\d{2}', data_str)
        if match:
            return match.group(1)
        
        # Padrão 2: dd/mm/yyyy (já está correto)
        if re.match(r'^\d{2}/\d{2}/\d{4}$', data_str):
            return data_str
        
        # Padrão 3: yyyy-mm-dd hh:mm:ss (converter para dd/mm/yyyy)
        match = re.match(r'^(\d{4})-(\d{2})-(\d{2})\s+\d{2}:\d{2}:\d{2}', data_str)
        if match:
            ano, mes, dia = match.groups()
            return f'{dia}/{mes}/{ano}'
        
        # Padrão 4: yyyy-mm-dd (converter para dd/mm/yyyy)
        match = re.match(r'^(\d{4})-(\d{2})-(\d{2})$', data_str)
        if match:
            ano, mes, dia = match.groups()
            return f'{dia}/{mes}/{ano}'
        
        # Se não reconheceu nenhum padrão, retornar None
        return None
        
    except Exception as e:
        print(f"Erro ao processar data '{data_str}': {e}")
        return None

def processar_coluna(df, col_name):
    """Processa uma coluna de data"""
    print(f"\n{'='*80}")
    print(f"PROCESSANDO COLUNA: {col_name}")
    print('='*80)
    
    # Verificar se a coluna existe
    if col_name not in df.columns:
        print(f"  ⚠️  Coluna '{col_name}' não encontrada no arquivo")
        return df, 0
    
    # Estatísticas antes
    print("\nANTES da normalização:")
    print(f"  Valores preenchidos: {df[col_name].notna().sum():,}")
    print(f"  Valores vazios: {df[col_name].isna().sum():,}")
    
    # Mostrar exemplos antes
    valores_antes = df[col_name].dropna().head(5)
    if len(valores_antes) > 0:
        print("\n  Exemplos antes:")
        for i, val in enumerate(valores_antes, 1):
            print(f"    {i}. {val}")
    
    # Backup da coluna original
    backup_col = f'{col_name}_original'
    df[backup_col] = df[col_name].copy()
    
    # Aplicar normalização
    print("\nAplicando normalizações...")
    df[col_name] = df[col_name].apply(normalizar_data)
    print("  ✓ Concluído")
    
    # Estatísticas depois
    print("\nDEPOIS da normalização:")
    print(f"  Valores preenchidos: {df[col_name].notna().sum():,}")
    print(f"  Valores vazios: {df[col_name].isna().sum():,}")
    
    # Mostrar exemplos depois
    valores_depois = df[col_name].dropna().head(5)
    if len(valores_depois) > 0:
        print("\n  Exemplos depois:")
        for i, val in enumerate(valores_depois, 1):
            print(f"    {i}. {val}")
    
    # Análise de mudanças
    mudancas = df[df[col_name] != df[backup_col]]
    qtd_mudancas = len(mudancas)
    print(f"\nTotal de registros modificados: {qtd_mudancas:,}")
    
    # Verificar formato dd/mm/yyyy
    valores_validos = df[col_name].dropna().astype(str)
    padrao_correto = valores_validos.str.match(r'^\d{2}/\d{2}/\d{4}$')
    
    if len(valores_validos) > 0:
        print(f"\nDatas no formato correto (dd/mm/yyyy): {padrao_correto.sum():,} ({padrao_correto.sum()/len(valores_validos)*100:.1f}%)")
        
        # Mostrar datas que não seguem o padrão
        nao_padrao = valores_validos[~valores_validos.str.match(r'^\d{2}/\d{2}/\d{4}$')]
        if len(nao_padrao) > 0:
            print(f"\nDatas fora do padrão (primeiras 5):")
            for i, data in enumerate(nao_padrao.head(5), 1):
                print(f"  {i}. {data}")
    
    # Remover coluna backup
    df = df.drop(columns=[backup_col])
    
    return df, qtd_mudancas

def main():
    print("="*80)
    print("NORMALIZAÇÃO DE DATAS - Formato dd/mm/yyyy (sem hora)")
    print("="*80)
    print()
    
    # Ler arquivo
    print(f"Lendo arquivo: {INPUT_FILE.name}")
    df = pd.read_csv(INPUT_FILE, sep=';', encoding='utf-8')
    print(f"  Total de registros: {len(df):,}")
    
    total_mudancas = 0
    
    # Processar cada coluna de data
    colunas_data = ['Dt de aniversário', 'Dh.inclusão', 'Dh.alteração']
    
    for col in colunas_data:
        df, mudancas = processar_coluna(df, col)
        total_mudancas += mudancas
    
    # Resumo final
    print("\n" + "="*80)
    print("RESUMO FINAL")
    print("="*80)
    print(f"\nTotal geral de mudanças: {total_mudancas:,}")
    
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
