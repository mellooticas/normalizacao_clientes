"""
Script para normalizar a coluna 'CPF' do arquivo consolidadas.csv
Formato padrão: 000.000.000-00

Problemas identificados:
- CPFs com .0 no final (formato float)
- CPFs sem formatação (apenas números)
- CPFs incompletos (< 11 dígitos)
- CPFs muito longos (> 11 dígitos)
- CPFs com espaços
"""

import pandas as pd
import re
from pathlib import Path

# Caminhos
BASE_DIR = Path(__file__).parent.parent
INPUT_FILE = BASE_DIR / 'dados_processados' / 'originais' / 'oss' / 'consolidadas' / 'consolidadas.csv'

def normalizar_cpf(valor):
    """Normaliza um CPF para o formato 000.000.000-00"""
    if pd.isna(valor):
        return None
    
    # Converter para string e remover espaços
    cpf_str = str(valor).strip()
    
    # Se for vazio, retornar None
    if not cpf_str:
        return None
    
    # Remover tudo após ponto decimal (.0)
    if '.' in cpf_str and cpf_str.endswith('.0'):
        cpf_str = cpf_str.split('.')[0]
    
    # Remover todos os caracteres não numéricos
    apenas_numeros = re.sub(r'\D', '', cpf_str)
    
    # Se não sobrou nada, retornar None
    if not apenas_numeros:
        return None
    
    # Se tem menos de 11 dígitos, completar com zeros à esquerda
    if len(apenas_numeros) < 11:
        apenas_numeros = apenas_numeros.zfill(11)
    
    # Se tem mais de 11 dígitos, pegar apenas os primeiros 11
    if len(apenas_numeros) > 11:
        apenas_numeros = apenas_numeros[:11]
    
    # Formatar no padrão 000.000.000-00
    cpf_formatado = f'{apenas_numeros[:3]}.{apenas_numeros[3:6]}.{apenas_numeros[6:9]}-{apenas_numeros[9:]}'
    
    return cpf_formatado

def main():
    print("="*80)
    print("NORMALIZAÇÃO DA COLUNA 'CPF'")
    print("="*80)
    print()
    
    # Ler arquivo
    print(f"Lendo arquivo: {INPUT_FILE.name}")
    df = pd.read_csv(INPUT_FILE, sep=';', encoding='utf-8')
    print(f"  Total de registros: {len(df):,}")
    print()
    
    col_name = 'CPF'
    
    # Estatísticas antes
    print("ANTES da normalização:")
    print(f"  CPFs preenchidos: {df[col_name].notna().sum():,}")
    print(f"  CPFs vazios: {df[col_name].isna().sum():,}")
    print()
    
    # Análise de padrões antes
    valores = df[col_name].dropna().astype(str)
    formato_correto = valores.str.match(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$')
    sem_formatacao = valores.str.match(r'^\d{11}$')
    apenas_digitos = valores.str.replace(r'\D', '', regex=True)
    incompleto = apenas_digitos.str.len() < 11
    muito_longo = apenas_digitos.str.len() > 11
    
    print("PADRÕES IDENTIFICADOS:")
    print(f"  Formato correto (000.000.000-00): {formato_correto.sum():,}")
    print(f"  Sem formatação (00000000000): {sem_formatacao.sum():,}")
    print(f"  Incompleto (< 11 dígitos): {incompleto.sum():,}")
    print(f"  Muito longo (> 11 dígitos): {muito_longo.sum():,}")
    print()
    
    # Mostrar exemplos antes
    print("EXEMPLOS ANTES DA NORMALIZAÇÃO (primeiros 10):")
    print("-"*80)
    for i, val in enumerate(valores.head(10), 1):
        num_digitos = len(re.sub(r'\D', '', val))
        print(f"  {i:2}. {val:30} ({num_digitos} dígitos)")
    print()
    
    # Backup da coluna original
    df['CPF_original'] = df[col_name].copy()
    
    # Aplicar normalização
    print("Aplicando normalizações...")
    df[col_name] = df[col_name].apply(normalizar_cpf)
    print("  ✓ Concluído")
    print()
    
    # Estatísticas depois
    print("DEPOIS da normalização:")
    print(f"  CPFs preenchidos: {df[col_name].notna().sum():,}")
    print(f"  CPFs vazios: {df[col_name].isna().sum():,}")
    print()
    
    # Mostrar exemplos depois
    valores_depois = df[col_name].dropna().astype(str)
    print("EXEMPLOS DEPOIS DA NORMALIZAÇÃO (primeiros 10):")
    print("-"*80)
    for i, val in enumerate(valores_depois.head(10), 1):
        print(f"  {i:2}. {val}")
    print()
    
    # Análise de mudanças
    mudancas = df[df[col_name] != df['CPF_original']]
    print(f"Total de registros modificados: {len(mudancas):,}")
    print()
    
    # Mostrar exemplos de mudanças
    if len(mudancas) > 0:
        print("EXEMPLOS DE MUDANÇAS (primeiros 20):")
        print("-"*80)
        for i, (idx, row) in enumerate(mudancas.head(20).iterrows(), 1):
            original = row['CPF_original']
            novo = row[col_name]
            original_str = str(original)[:30] if pd.notna(original) else 'None'
            novo_str = str(novo) if pd.notna(novo) else 'None'
            print(f"{i:2}. {original_str:30} → {novo_str}")
        print()
    
    # Verificar se todos estão no formato correto agora
    valores_finais = df[col_name].dropna().astype(str)
    formato_final = valores_finais.str.match(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$')
    
    print("RESULTADO FINAL:")
    print("-"*80)
    print(f"  CPFs no formato correto: {formato_final.sum():,} ({formato_final.sum()/len(valores_finais)*100:.1f}%)")
    
    # Verificar se algum ficou fora do padrão
    nao_padrao = valores_finais[~valores_finais.str.match(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$')]
    if len(nao_padrao) > 0:
        print(f"  CPFs fora do padrão: {len(nao_padrao):,}")
        print("\n  Exemplos de CPFs inválidos:")
        for i, val in enumerate(nao_padrao.head(10), 1):
            print(f"    {i}. {val}")
    else:
        print("  ✓ Todos os CPFs estão no formato correto!")
    
    print()
    
    # Remover coluna backup
    df = df.drop(columns=['CPF_original'])
    
    # Salvar arquivo (sobrescrever)
    print(f"Salvando alterações no arquivo original...")
    df.to_csv(INPUT_FILE, sep=';', index=False, encoding='utf-8')
    print("  ✓ Arquivo atualizado com sucesso")
    print()
    
    print("="*80)
    print("NORMALIZAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*80)
    print()
    print(f"📄 Arquivo atualizado: {INPUT_FILE}")
    print()

if __name__ == '__main__':
    main()
