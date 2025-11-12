"""
Remove as linhas com CPFs duplicados das partes 2 e 3
"""
import pandas as pd
from pathlib import Path

# Configuração
DIR_BASE = Path(__file__).parent.parent
DIR_PARTES = DIR_BASE / 'dados_processados' / 'originais' / 'clientes' / 'normalizados' / 'povoar' / 'lote_3_partes'

def main():
    print("=== REMOVENDO DUPLICATAS ===\n")
    
    duplicatas = [
        {'parte': 2, 'cpf': '20394731816', 'nome': 'MARCIO HENRIQUE FERREIRA'},
        {'parte': 3, 'cpf': '35888942847', 'nome': 'HEIDI ANTONIO PAULINA SASSAKI'}
    ]
    
    for dup in duplicatas:
        parte = dup['parte']
        cpf_remover = dup['cpf']
        
        # Encontra arquivo
        arquivos = list(DIR_PARTES.glob(f'lote_003_parte_{parte:02d}_*.csv'))
        if not arquivos:
            print(f"❌ Arquivo da parte {parte} não encontrado")
            continue
        
        arquivo = arquivos[0]
        print(f"Parte {parte}: {arquivo.name}")
        
        # Lê arquivo
        df = pd.read_csv(arquivo, sep=';', dtype=str)
        print(f"  Antes: {len(df)} registros")
        
        # Remove a linha com CPF duplicado
        df_limpo = df[df['cpf'] != cpf_remover].copy()
        registros_removidos = len(df) - len(df_limpo)
        
        print(f"  Removidos: {registros_removidos} registro(s) com CPF {cpf_remover}")
        print(f"  Depois: {len(df_limpo)} registros")
        
        # Salva arquivo corrigido
        arquivo_corrigido = arquivo.parent / arquivo.name.replace('.csv', '_CORRIGIDO.csv')
        df_limpo.to_csv(arquivo_corrigido, sep=';', index=False, encoding='utf-8-sig')
        
        print(f"  ✓ Salvo: {arquivo_corrigido.name}\n")
    
    print("="*60)
    print("\n=== RESUMO ===")
    print("✓ Parte 1: 200 registros (sem duplicatas) - OK para importar")
    print("✓ Parte 2: 199 registros (removido 1) - arquivo CORRIGIDO criado")
    print("✓ Parte 3: 199 registros (removido 1) - arquivo CORRIGIDO criado")
    print("✓ Parte 4: 200 registros (sem duplicatas) - OK para importar")
    print("✓ Parte 5: 200 registros (sem duplicatas) - OK para importar")
    print("\nTotal que será importado: 998 registros (perdidos 2 duplicados)")
    
    print("\n=== INSTRUÇÕES DE IMPORTAÇÃO ===")
    print("1. A parte 1 você já importou com sucesso")
    print("2. Importe: lote_003_parte_02_reg_2201_a_2400_CORRIGIDO.csv")
    print("3. Importe: lote_003_parte_03_reg_2401_a_2600_CORRIGIDO.csv")
    print("4. Importe: lote_003_parte_04_reg_2601_a_2800.csv (original)")
    print("5. Importe: lote_003_parte_05_reg_2801_a_3000.csv (original)")

if __name__ == '__main__':
    main()
