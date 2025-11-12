"""
Remove formatação dos CPFs nas partes do lote 3 e identifica duplicatas
"""
import pandas as pd
from pathlib import Path

# Configuração
DIR_BASE = Path(__file__).parent.parent
DIR_PARTES = DIR_BASE / 'dados_processados' / 'originais' / 'clientes' / 'normalizados' / 'povoar' / 'lote_3_partes'

def limpar_cpf(cpf_str):
    """Remove formatação do CPF"""
    if pd.isna(cpf_str) or cpf_str == 'nan':
        return None
    return str(cpf_str).replace('.', '').replace('-', '').replace(' ', '').strip()

def main():
    print("=== CORRIGINDO FORMATAÇÃO DE CPFs ===\n")
    
    # CPFs que já existem no banco (lotes 1 e 2)
    cpfs_duplicados_encontrados = []
    
    # Processa cada parte
    for i in range(1, 6):
        arquivos = list(DIR_PARTES.glob(f'lote_003_parte_{i:02d}_*.csv'))
        
        if not arquivos:
            continue
            
        arquivo = arquivos[0]
        print(f"Parte {i}: {arquivo.name}")
        
        # Lê o arquivo
        df = pd.read_csv(arquivo, sep=';', dtype=str)
        print(f"  Antes: {len(df)} registros")
        
        # Limpa CPFs
        df['cpf'] = df['cpf'].apply(limpar_cpf)
        
        # Conta CPFs
        cpfs_preenchidos = df['cpf'].notna().sum()
        print(f"  CPFs preenchidos: {cpfs_preenchidos}")
        
        # Verifica se tem os CPFs problemáticos
        cpfs_problema = ['20394731816', '35888942847']
        for cpf in cpfs_problema:
            if cpf in df['cpf'].values:
                match = df[df['cpf'] == cpf]
                print(f"  ⚠️  CPF {cpf} encontrado:")
                for idx, row in match.iterrows():
                    print(f"      Linha {idx}: {row['nome']} (ID: {row['id_legado']})")
                    cpfs_duplicados_encontrados.append({
                        'parte': i,
                        'cpf': cpf,
                        'nome': row['nome'],
                        'id': row['id_legado'],
                        'linha': idx
                    })
        
        # Salva de volta (sobrescreve)
        df.to_csv(arquivo, sep=';', index=False, encoding='utf-8-sig')
        print(f"  ✓ Salvo com CPFs limpos\n")
    
    print("="*60)
    print(f"\n=== DUPLICATAS ENCONTRADAS ===")
    print(f"Total: {len(cpfs_duplicados_encontrados)}\n")
    
    if cpfs_duplicados_encontrados:
        for dup in cpfs_duplicados_encontrados:
            print(f"Parte {dup['parte']}: CPF {dup['cpf']}")
            print(f"  Nome: {dup['nome']}")
            print(f"  ID: {dup['id']}")
            print(f"  Linha: {dup['linha']}")
            print()
        
        print("\n=== PRÓXIMOS PASSOS ===")
        print("1. Esses CPFs já existem nos lotes 1 ou 2")
        print("2. Vamos criar versões CORRIGIDAS removendo essas linhas")
        print("3. Você poderá importar as versões corrigidas")
    else:
        print("Nenhuma duplicata encontrada! (estranho...)")

if __name__ == '__main__':
    main()
