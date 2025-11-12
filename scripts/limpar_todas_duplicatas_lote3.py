"""
Remove TODAS as duplicatas de CPF do lote 3 comparando com os lotes já importados (1, 2 e parte 1 do lote 3)
"""
import pandas as pd
from pathlib import Path

# Configuração
DIR_BASE = Path(__file__).parent.parent
DIR_PARTES = DIR_BASE / 'dados_processados' / 'originais' / 'clientes' / 'normalizados' / 'povoar' / 'lote_3_partes'
DIR_LOTES = DIR_BASE / 'dados_processados' / 'originais' / 'clientes' / 'normalizados' / 'povoar'

def limpar_cpf(cpf_str):
    """Remove formatação do CPF"""
    if pd.isna(cpf_str) or cpf_str == 'nan':
        return None
    return str(cpf_str).replace('.', '').replace('-', '').replace(' ', '').strip()

def main():
    print("=== IDENTIFICANDO TODOS OS CPFs JÁ IMPORTADOS ===\n")
    
    # Coleta CPFs dos lotes já importados
    cpfs_ja_importados = set()
    
    # Lote 1
    print("Coletando CPFs do Lote 1...")
    lote1 = DIR_LOTES / 'lote_001_registros_1_a_1000.csv'
    if lote1.exists():
        df1 = pd.read_csv(lote1, sep=';', dtype=str)
        df1['cpf'] = df1['cpf'].apply(limpar_cpf)
        cpfs1 = set(df1[df1['cpf'].notna()]['cpf'].unique())
        cpfs_ja_importados.update(cpfs1)
        print(f"  Lote 1: {len(cpfs1)} CPFs únicos")
    
    # Lote 2
    print("Coletando CPFs do Lote 2...")
    lote2 = DIR_LOTES / 'lote_002_registros_1001_a_2000.csv'
    if lote2.exists():
        df2 = pd.read_csv(lote2, sep=';', dtype=str)
        df2['cpf'] = df2['cpf'].apply(limpar_cpf)
        cpfs2 = set(df2[df2['cpf'].notna()]['cpf'].unique())
        cpfs_ja_importados.update(cpfs2)
        print(f"  Lote 2: {len(cpfs2)} CPFs únicos")
    
    # Lote 3 - Parte 1 (já importada)
    print("Coletando CPFs da Parte 1 do Lote 3...")
    parte1 = list(DIR_PARTES.glob('lote_003_parte_01_*.csv'))
    if parte1:
        dfp1 = pd.read_csv(parte1[0], sep=';', dtype=str)
        dfp1['cpf'] = dfp1['cpf'].apply(limpar_cpf)
        cpfs_p1 = set(dfp1[dfp1['cpf'].notna()]['cpf'].unique())
        cpfs_ja_importados.update(cpfs_p1)
        print(f"  Parte 1: {len(cpfs_p1)} CPFs únicos")
    
    print(f"\nTotal de CPFs já importados: {len(cpfs_ja_importados)}")
    
    print("\n" + "="*60)
    print("=== VERIFICANDO PARTES RESTANTES DO LOTE 3 ===\n")
    
    # Verifica partes 2, 3, 4, 5
    todas_duplicatas = []
    
    for parte_num in [2, 3, 4, 5]:
        print(f"Parte {parte_num}:")
        
        # Busca arquivo corrigido ou original
        arquivo_corrigido = list(DIR_PARTES.glob(f'lote_003_parte_{parte_num:02d}_*_CORRIGIDO.csv'))
        arquivo_original = list(DIR_PARTES.glob(f'lote_003_parte_{parte_num:02d}_reg_*.csv'))
        
        if arquivo_corrigido:
            arquivo = arquivo_corrigido[0]
            print(f"  Usando: {arquivo.name}")
        elif arquivo_original:
            arquivo = arquivo_original[0]
            print(f"  Usando: {arquivo.name}")
        else:
            print(f"  ❌ Arquivo não encontrado")
            continue
        
        # Lê arquivo
        df = pd.read_csv(arquivo, sep=';', dtype=str)
        df['cpf'] = df['cpf'].apply(limpar_cpf)
        
        print(f"  Total: {len(df)} registros")
        print(f"  CPFs preenchidos: {df['cpf'].notna().sum()}")
        
        # Identifica duplicatas
        duplicatas = df[df['cpf'].isin(cpfs_ja_importados)]
        
        if len(duplicatas) > 0:
            print(f"  ⚠️  DUPLICATAS ENCONTRADAS: {len(duplicatas)}")
            for idx, row in duplicatas.iterrows():
                cpf_dup = row['cpf']
                nome = row['nome']
                id_legado = row['id_legado']
                print(f"      CPF {cpf_dup}: {nome} (ID: {id_legado})")
                
                todas_duplicatas.append({
                    'parte': parte_num,
                    'cpf': cpf_dup,
                    'nome': nome,
                    'id': id_legado,
                    'arquivo': arquivo.name
                })
            
            # Remove duplicatas e salva versão LIMPA
            df_limpo = df[~df['cpf'].isin(cpfs_ja_importados)].copy()
            
            nome_limpo = arquivo.name.replace('.csv', '').replace('_CORRIGIDO', '') + '_LIMPO.csv'
            arquivo_limpo = arquivo.parent / nome_limpo
            df_limpo.to_csv(arquivo_limpo, sep=';', index=False, encoding='utf-8-sig')
            
            print(f"  ✓ Versão LIMPA: {arquivo_limpo.name}")
            print(f"    {len(df_limpo)} registros (removidos {len(duplicatas)})")
        else:
            print(f"  ✓ Sem duplicatas!")
            
            # Cria versão LIMPA mesmo assim (para padronizar)
            nome_limpo = arquivo.name.replace('.csv', '').replace('_CORRIGIDO', '') + '_LIMPO.csv'
            arquivo_limpo = arquivo.parent / nome_limpo
            df.to_csv(arquivo_limpo, sep=';', index=False, encoding='utf-8-sig')
            print(f"  ✓ Versão LIMPA: {arquivo_limpo.name}")
        
        print()
    
    print("="*60)
    print(f"\n=== RESUMO FINAL ===")
    print(f"Total de duplicatas encontradas: {len(todas_duplicatas)}")
    
    if todas_duplicatas:
        print("\nCPFs duplicados removidos:")
        for dup in todas_duplicatas:
            print(f"  - Parte {dup['parte']}: CPF {dup['cpf']} ({dup['nome']})")
    
    print("\n=== ARQUIVOS PRONTOS PARA IMPORTAÇÃO ===")
    print("Importe na ordem:")
    print("  1. ~~Parte 1~~ (já importada)")
    print("  2. lote_003_parte_02_reg_2201_a_2400_LIMPO.csv")
    print("  3. lote_003_parte_03_reg_2401_a_2600_LIMPO.csv")
    print("  4. lote_003_parte_04_reg_2601_a_2800_LIMPO.csv")
    print("  5. lote_003_parte_05_reg_2801_a_3000_LIMPO.csv")
    print("\nTodos os arquivos estão SEM duplicatas garantidas!")

if __name__ == '__main__':
    main()
