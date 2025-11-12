"""
Normaliza telefones no arquivo telefone_uuid.csv
"""
import pandas as pd
from pathlib import Path
import re

DIR_BASE = Path(__file__).parent.parent
ARQUIVO = DIR_BASE / 'dados_processados' / 'telefones_para_importar' / 'telefone_uuid.csv'

def limpar_numero(numero_str):
    if pd.isna(numero_str) or str(numero_str).strip() == '':
        return None
    numero = re.sub(r'[^0-9]', '', str(numero_str))
    if not numero or numero == '':
        return None
    return numero

def corrigir_numero(numero_limpo, tipo):
    if not numero_limpo:
        return None
    
    tamanho = len(numero_limpo)
    
    if tamanho < 8 or tamanho > 12:
        return None
    
    if tamanho == 8:
        if tipo == 'CELULAR':
            return '119' + numero_limpo
        else:
            return '11' + numero_limpo
    
    if tamanho == 9:
        return '11' + numero_limpo
    
    if tamanho == 10:
        if numero_limpo.startswith('11'):
            if tipo == 'CELULAR':
                return '119' + numero_limpo[2:]
            else:
                return numero_limpo
        else:
            if tipo == 'CELULAR':
                ddd = numero_limpo[:2]
                resto = numero_limpo[2:]
                return ddd + '9' + resto
            else:
                return numero_limpo
    
    if tamanho == 11:
        return numero_limpo
    
    if tamanho == 12:
        if numero_limpo[2] == '9':
            return numero_limpo[:11]
        else:
            return numero_limpo[:11]
    
    return numero_limpo

def main():
    print("="*70)
    print("NORMALIZANDO TELEFONES")
    print("="*70)
    
    print("\n1. Criando backup...")
    df = pd.read_csv(ARQUIVO, sep=';', dtype=str)
    backup = ARQUIVO.parent / (ARQUIVO.stem + '_BACKUP.csv')
    df.to_csv(backup, sep=';', index=False, encoding='utf-8-sig')
    print(f"   Backup: {backup.name}")
    
    print(f"\n2. Analisando {len(df)} telefones...")
    numeros_validos_antes = df['numero'].notna().sum()
    print(f"   Numeros preenchidos: {numeros_validos_antes}")
    
    print("\n3. Limpando e corrigindo...")
    df['numero_limpo'] = df['numero'].apply(limpar_numero)
    df['numero_corrigido'] = df.apply(lambda row: corrigir_numero(row['numero_limpo'], row['tipo']), axis=1)
    
    numeros_antes = df['numero'].copy()
    numeros_depois = df['numero_corrigido'].copy()
    mudou = (numeros_antes.fillna('') != numeros_depois.fillna(''))
    removidos = df['numero_corrigido'].isna() & df['numero'].notna()
    
    print(f"   Corrigidos: {mudou.sum()}")
    print(f"   Removidos (invalidos): {removidos.sum()}")
    
    df['numero'] = df['numero_corrigido']
    df = df.drop(columns=['numero_limpo', 'numero_corrigido'])
    
    print("\n4. Removendo registros sem numero...")
    antes_remocao = len(df)
    df = df[df['numero'].notna()].copy()
    removidos_total = antes_remocao - len(df)
    print(f"   {removidos_total} registros removidos")
    
    print("\n5. Validacao final...")
    df['tamanho'] = df['numero'].str.len()
    print(f"\n   Distribuicao por tamanho:")
    for tam, count in df['tamanho'].value_counts().sort_index().items():
        print(f"     {int(tam)} digitos: {count}")
    
    numeros_ok = len(df[(df['tamanho'] == 11) | (df['tamanho'] == 10)])
    numeros_problema = len(df[(df['tamanho'] != 11) & (df['tamanho'] != 10)])
    print(f"\n   Numeros OK (10-11 digitos): {numeros_ok}")
    print(f"   Numeros com problema: {numeros_problema}")
    
    df = df.drop(columns=['tamanho'])
    
    print("\n6. Salvando arquivo corrigido...")
    arquivo_saida = ARQUIVO.parent / 'telefone_uuid_NORMALIZADO.csv'
    df.to_csv(arquivo_saida, sep=';', index=False, encoding='utf-8-sig')
    print(f"   {len(df)} telefones salvos em: {arquivo_saida.name}")
    
    print("\n" + "="*70)
    print("RESUMO")
    print(f"Antes: {numeros_validos_antes} numeros")
    print(f"Depois: {len(df)} numeros")
    print(f"Removidos: {numeros_validos_antes - len(df)}")
    print(f"Taxa de correcao: {(len(df) / numeros_validos_antes * 100):.1f}%")
    print("\nNORMALIZACAO CONCLUIDA!")
    print(f"\nARQUIVO NOVO: {arquivo_saida.name}")
    print(f"Localizacao: {arquivo_saida.parent}")
    print(f"Backup: {backup.name}")
    print("\nSUBSTITUA o arquivo telefone_uuid.csv pelo NORMALIZADO")
    print("="*70)

if __name__ == '__main__':
    main()
