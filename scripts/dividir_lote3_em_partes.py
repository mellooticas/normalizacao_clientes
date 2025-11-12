"""
Divide o lote 3 em partes menores (200 registros cada) para identificar o problema
"""
import pandas as pd
from pathlib import Path
from datetime import datetime

# Configuração
DIR_BASE = Path(__file__).parent.parent
ARQUIVO_LOTE3 = DIR_BASE / 'dados_processados' / 'originais' / 'clientes' / 'normalizados' / 'povoar' / 'lote_003_registros_2001_a_3000.csv'
DIR_SAIDA = DIR_BASE / 'dados_processados' / 'originais' / 'clientes' / 'normalizados' / 'povoar' / 'lote_3_partes'
TAMANHO_PARTE = 200

def main():
    print("=== DIVIDINDO LOTE 3 EM PARTES MENORES ===\n")
    
    # Cria diretório de saída
    DIR_SAIDA.mkdir(parents=True, exist_ok=True)
    
    # Lê o lote 3
    print(f"Lendo: {ARQUIVO_LOTE3.name}")
    df = pd.read_csv(ARQUIVO_LOTE3, sep=';', dtype={'id_legado': str, 'cpf': str})
    
    print(f"Total de registros: {len(df)}")
    print(f"CPFs preenchidos: {df['cpf'].notna().sum()}\n")
    
    # Calcula número de partes
    num_partes = (len(df) + TAMANHO_PARTE - 1) // TAMANHO_PARTE
    print(f"Dividindo em {num_partes} partes de até {TAMANHO_PARTE} registros\n")
    
    # Divide em partes
    partes_criadas = []
    for i in range(num_partes):
        inicio = i * TAMANHO_PARTE
        fim = min((i + 1) * TAMANHO_PARTE, len(df))
        parte = df.iloc[inicio:fim].copy()
        
        # Nome do arquivo (mantém numeração original dos registros)
        registro_inicio = 2001 + inicio  # Lote 3 começa no registro 2001
        registro_fim = 2001 + fim - 1
        
        id_inicio = parte['id_legado'].iloc[0]
        id_fim = parte['id_legado'].iloc[-1]
        
        nome_arquivo = f'lote_003_parte_{i+1:02d}_reg_{registro_inicio}_a_{registro_fim}.csv'
        arquivo_saida = DIR_SAIDA / nome_arquivo
        
        # Salva parte
        parte.to_csv(arquivo_saida, sep=';', index=False, encoding='utf-8-sig')
        
        cpfs_preenchidos = parte['cpf'].notna().sum()
        
        partes_criadas.append({
            'parte': i + 1,
            'registros': len(parte),
            'registro_inicio': registro_inicio,
            'registro_fim': registro_fim,
            'id_inicio': id_inicio,
            'id_fim': id_fim,
            'cpfs': cpfs_preenchidos,
            'arquivo': nome_arquivo
        })
        
        print(f"✓ Parte {i+1:2d}: {len(parte):3d} registros (reg {registro_inicio:4d}-{registro_fim:4d}) | "
              f"IDs: {id_inicio} → {id_fim} | {cpfs_preenchidos:3d} CPFs | {nome_arquivo}")
    
    print(f"\n=== RESUMO ===")
    print(f"Total de partes: {len(partes_criadas)}")
    print(f"Total de registros: {sum(p['registros'] for p in partes_criadas)}")
    print(f"Total de CPFs: {sum(p['cpfs'] for p in partes_criadas)}")
    print(f"\nArquivos salvos em:")
    print(f"{DIR_SAIDA}")
    
    print(f"\n=== INSTRUÇÕES ===")
    print("1. Importe cada parte sequencialmente (parte_01, parte_02, ...)")
    print("2. Quando encontrar erro, saberemos exatamente qual parte tem o problema")
    print("3. Podemos então investigar apenas aquela parte específica (200 registros)")

if __name__ == '__main__':
    main()
