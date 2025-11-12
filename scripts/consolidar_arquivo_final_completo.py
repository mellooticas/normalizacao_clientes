"""
Consolida TODOS os lotes em um único arquivo final limpo para importação
Remove duplicatas e cria arquivo único pronto para o banco
"""
import pandas as pd
from pathlib import Path
from datetime import datetime

# Configuração
DIR_BASE = Path(__file__).parent.parent
DIR_LOTES = DIR_BASE / 'dados_processados' / 'originais' / 'clientes' / 'normalizados' / 'povoar'
DIR_LOTE3_PARTES = DIR_LOTES / 'lote_3_partes'
DIR_SAIDA = DIR_BASE / 'dados_processados' / 'originais' / 'clientes' / 'normalizados'

def limpar_cpf(cpf_str):
    """Remove formatação do CPF"""
    if pd.isna(cpf_str) or cpf_str == 'nan':
        return None
    return str(cpf_str).replace('.', '').replace('-', '').replace(' ', '').strip()

def main():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    print("="*70)
    print("=== CONSOLIDAÇÃO FINAL - TODOS OS LOTES ===")
    print("="*70)
    
    dataframes = []
    
    # LOTES 1 e 2
    print("\n1. Lendo Lotes 1 e 2 (já importados)...")
    for i in [1, 2]:
        arquivo = DIR_LOTES / f'lote_{i:03d}_registros_*.csv'
        arquivos = list(DIR_LOTES.glob(f'lote_{i:03d}_*.csv'))
        
        if arquivos:
            df = pd.read_csv(arquivos[0], sep=';', dtype=str)
            df['cpf'] = df['cpf'].apply(limpar_cpf)
            dataframes.append(df)
            print(f"   ✓ Lote {i}: {len(df)} registros")
    
    # LOTE 3 - Partes LIMPAS
    print("\n2. Lendo Lote 3 (5 partes LIMPAS)...")
    for i in range(1, 6):
        # Procura arquivo LIMPO primeiro, depois CORRIGIDO, depois original
        arquivo_limpo = list(DIR_LOTE3_PARTES.glob(f'lote_003_parte_{i:02d}_*_LIMPO.csv'))
        arquivo_corrigido = list(DIR_LOTE3_PARTES.glob(f'lote_003_parte_{i:02d}_*_CORRIGIDO.csv'))
        arquivo_original = list(DIR_LOTE3_PARTES.glob(f'lote_003_parte_{i:02d}_reg_*.csv'))
        
        arquivo = None
        tipo = ""
        
        if arquivo_limpo:
            arquivo = arquivo_limpo[0]
            tipo = "LIMPO"
        elif arquivo_corrigido:
            arquivo = arquivo_corrigido[0]
            tipo = "CORRIGIDO"
        elif arquivo_original:
            arquivo = arquivo_original[0]
            tipo = "ORIGINAL"
        
        if arquivo:
            df = pd.read_csv(arquivo, sep=';', dtype=str)
            df['cpf'] = df['cpf'].apply(limpar_cpf)
            dataframes.append(df)
            print(f"   ✓ Parte {i}: {len(df)} registros ({tipo})")
    
    # LOTES 4 ao 13
    print("\n3. Lendo Lotes 4 ao 13...")
    for i in range(4, 14):
        arquivo = DIR_LOTES / f'lote_{i:03d}_registros_*.csv'
        arquivos = list(DIR_LOTES.glob(f'lote_{i:03d}_*.csv'))
        
        if arquivos:
            df = pd.read_csv(arquivos[0], sep=';', dtype=str)
            df['cpf'] = df['cpf'].apply(limpar_cpf)
            dataframes.append(df)
            print(f"   ✓ Lote {i}: {len(df)} registros")
    
    # CONSOLIDA TUDO
    print("\n" + "="*70)
    print("=== CONSOLIDANDO ===")
    
    df_final = pd.concat(dataframes, ignore_index=True)
    print(f"\nTotal inicial: {len(df_final)} registros")
    
    # Verifica duplicatas de ID
    print(f"\nVerificando ID_LEGADO...")
    ids_duplicados = df_final[df_final.duplicated(subset=['id_legado'], keep=False)]
    if len(ids_duplicados) > 0:
        print(f"   ⚠️  {len(ids_duplicados)} IDs duplicados encontrados")
        print(f"   Removendo duplicatas (mantendo primeira ocorrência)...")
        df_final = df_final.drop_duplicates(subset=['id_legado'], keep='first')
    else:
        print(f"   ✓ Todos os IDs únicos")
    
    # Verifica duplicatas de CPF
    print(f"\nVerificando CPF...")
    cpfs_preenchidos = df_final[df_final['cpf'].notna()]
    cpfs_duplicados = cpfs_preenchidos[cpfs_preenchidos.duplicated(subset=['cpf'], keep=False)]
    
    if len(cpfs_duplicados) > 0:
        print(f"   ⚠️  {len(cpfs_duplicados)} CPFs duplicados encontrados")
        print(f"   Removendo duplicatas (mantendo primeira ocorrência)...")
        
        # Remove duplicatas mantendo primeira ocorrência
        df_final = df_final.drop_duplicates(subset=['cpf'], keep='first')
    else:
        print(f"   ✓ Todos os CPFs únicos")
    
    print(f"\nTotal final: {len(df_final)} registros")
    
    # ESTATÍSTICAS
    print("\n" + "="*70)
    print("=== ESTATÍSTICAS FINAIS ===")
    print(f"\nTotal de registros: {len(df_final)}")
    print(f"IDs únicos: {df_final['id_legado'].nunique()}")
    print(f"CPFs preenchidos: {df_final['cpf'].notna().sum()}")
    print(f"CPFs únicos: {df_final[df_final['cpf'].notna()]['cpf'].nunique()}")
    print(f"Registros sem CPF: {df_final['cpf'].isna().sum()}")
    
    # Contagem por origem
    print(f"\nDistribuição por origem:")
    if 'origem' in df_final.columns:
        for origem, count in df_final['origem'].value_counts().items():
            print(f"   {origem}: {count}")
    
    # SALVA ARQUIVO FINAL
    arquivo_final = DIR_SAIDA / f'CLIENTES_FINAL_CONSOLIDADO_{timestamp}.csv'
    df_final.to_csv(arquivo_final, sep=';', index=False, encoding='utf-8-sig')
    
    print("\n" + "="*70)
    print("=== ARQUIVO FINAL CRIADO ===")
    print(f"\n📁 {arquivo_final.name}")
    print(f"📍 {arquivo_final.parent}")
    print(f"\n✅ {len(df_final)} registros prontos para importação")
    
    print("\n" + "="*70)
    print("=== ARQUIVOS INTERMEDIÁRIOS (PODEM SER APAGADOS) ===")
    print("\n1. Lotes individuais (1-13):")
    print(f"   {DIR_LOTES / 'lote_*.csv'}")
    
    print("\n2. Partes do Lote 3:")
    print(f"   {DIR_LOTE3_PARTES / 'lote_003_parte_*.csv'}")
    
    print("\n3. Arquivos antigos de consolidação:")
    print(f"   CLIENTES_OSS_VIXEN_CONSOLIDADO_*.csv")
    print(f"   CLIENTES_TODAS_BASES_CONSOLIDADO_*.csv")
    print(f"   CLIENTES_SEM_DUPLICATAS_*.csv")
    
    print("\n" + "="*70)
    print("\n🎯 ARQUIVO FINAL ÚNICO PRONTO!")
    print("   Use este arquivo para futuras importações ou backups")
    print("   Você pode apagar manualmente os arquivos intermediários listados acima")
    print("\n" + "="*70)

if __name__ == '__main__':
    main()
