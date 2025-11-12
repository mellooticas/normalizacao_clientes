"""
Separa as OS sem match em um arquivo CSV para análise
"""
import pandas as pd
from pathlib import Path
from datetime import datetime

# Configuração
DIR_BASE = Path(__file__).parent.parent
ARQUIVO_OSS_CRUZADO = DIR_BASE / 'dados_processados' / 'originais' / 'vendas' / 'OSS_COM_IDS_CLIENTES_20251109_210100.csv'
DIR_SAIDA = DIR_BASE / 'dados_processados' / 'originais' / 'vendas'

def main():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    print("="*70)
    print("=== SEPARANDO OS SEM MATCH ===")
    print("="*70)
    
    # Lê arquivo cruzado
    print("\n1. Lendo arquivo OSS cruzado...")
    df_oss = pd.read_csv(ARQUIVO_OSS_CRUZADO, sep=';', dtype=str, encoding='utf-8-sig')
    
    print(f"   ✓ {len(df_oss)} OS carregadas")
    
    # Filtra OS sem match
    print("\n2. Filtrando OS sem match (id_cliente_novo vazio)...")
    df_sem_match = df_oss[df_oss['id_cliente_novo'].isna()].copy()
    
    print(f"   ✓ {len(df_sem_match)} OS sem match encontradas")
    
    # Seleciona colunas principais para análise
    colunas_principais = [
        'OS N°',
        'LOJA',
        'DATA DE COMPRA',
        'ID_CLIENTE',
        'NOME:',
        'DT NASC',
        'CPF',
        'RG',
        'TELEFONE :',
        'CELULAR:',
        'EMAIL:',
        'TOTAL',
        'arquivo_origem'
    ]
    
    # Verifica quais colunas existem
    colunas_existentes = [col for col in colunas_principais if col in df_sem_match.columns]
    
    df_sem_match_resumido = df_sem_match[colunas_existentes].copy()
    
    # Salva arquivo completo
    arquivo_completo = DIR_SAIDA / f'OS_SEM_MATCH_COMPLETO_{timestamp}.csv'
    df_sem_match.to_csv(arquivo_completo, sep=';', index=False, encoding='utf-8-sig')
    
    # Salva arquivo resumido
    arquivo_resumido = DIR_SAIDA / f'OS_SEM_MATCH_RESUMIDO_{timestamp}.csv'
    df_sem_match_resumido.to_csv(arquivo_resumido, sep=';', index=False, encoding='utf-8-sig')
    
    print("\n" + "="*70)
    print("=== ARQUIVOS CRIADOS ===")
    
    print(f"\n📁 Arquivo COMPLETO (todas as colunas):")
    print(f"   {arquivo_completo.name}")
    print(f"   {len(df_sem_match)} registros com todas as colunas")
    
    print(f"\n📁 Arquivo RESUMIDO (colunas principais):")
    print(f"   {arquivo_resumido.name}")
    print(f"   {len(df_sem_match_resumido)} registros com {len(colunas_existentes)} colunas")
    
    print(f"\n📍 Localização: {DIR_SAIDA}")
    
    # Análise dos dados sem match
    print("\n" + "="*70)
    print("=== ANÁLISE DOS 117 CLIENTES SEM MATCH ===")
    
    print(f"\nTotal de OS: {len(df_sem_match)}")
    
    # CPFs preenchidos
    cpfs_preenchidos = df_sem_match['CPF'].notna().sum()
    print(f"CPFs preenchidos: {cpfs_preenchidos}")
    print(f"CPFs vazios: {len(df_sem_match) - cpfs_preenchidos}")
    
    # Distribuição por loja
    if 'LOJA' in df_sem_match.columns:
        print(f"\nDistribuição por loja:")
        for loja, count in df_sem_match['LOJA'].value_counts().items():
            print(f"   {loja}: {count}")
    
    # Exemplos de nomes problemáticos
    print(f"\n=== EXEMPLOS DE CASOS SEM MATCH ===")
    print("\nPrimeiros 10 casos:")
    for idx, row in df_sem_match.head(10).iterrows():
        os_num = row.get('OS N°', 'N/A')
        nome = row.get('NOME:', 'N/A')
        cpf = row.get('CPF', 'N/A')
        id_antigo = row.get('ID_CLIENTE', 'N/A')
        
        print(f"\nOS {os_num}:")
        print(f"   Nome: {nome}")
        print(f"   CPF: {cpf}")
        print(f"   ID antigo: {id_antigo}")
    
    # Estatísticas de valores
    if 'TOTAL' in df_sem_match.columns:
        print(f"\n=== ANÁLISE DE VALORES ===")
        
        # Tenta converter TOTAL para float
        df_sem_match['total_num'] = pd.to_numeric(
            df_sem_match['TOTAL'].str.replace(',', '.'), 
            errors='coerce'
        )
        
        totais_validos = df_sem_match['total_num'].notna().sum()
        
        if totais_validos > 0:
            print(f"OS com valor: {totais_validos}")
            print(f"Valor total perdido: R$ {df_sem_match['total_num'].sum():.2f}")
            print(f"Valor médio: R$ {df_sem_match['total_num'].mean():.2f}")
            print(f"Valor mínimo: R$ {df_sem_match['total_num'].min():.2f}")
            print(f"Valor máximo: R$ {df_sem_match['total_num'].max():.2f}")
    
    print("\n" + "="*70)
    print("\n🎯 ARQUIVOS CRIADOS COM SUCESSO!")
    print("\nPróximos passos sugeridos:")
    print("1. Analisar o arquivo RESUMIDO para identificar padrões")
    print("2. Verificar se são nomes compostos/múltiplos (ex: JOÃO/MARIA)")
    print("3. Verificar se CPFs são válidos")
    print("4. Decidir se vale criar registros novos para esses clientes")
    print("\n" + "="*70)

if __name__ == '__main__':
    main()
