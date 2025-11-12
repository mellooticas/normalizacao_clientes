"""
Script para normalizar a coluna 'CEP' do arquivo clientes_vixen_completo.csv
Formato padrão: 00000-000

Ações:
1. Remove todos os caracteres não numéricos
2. Completa com zeros à esquerda se tiver menos de 8 dígitos
3. Adiciona hífen no formato 00000-000
4. Marca CEPs inválidos (vazios ou muito longos) como None
"""

import pandas as pd
import re
from pathlib import Path

# Caminhos
BASE_DIR = Path(__file__).parent.parent
INPUT_FILE = BASE_DIR / 'dados_processados' / 'originais' / 'vixen' / 'extraidos_corrigidos' / 'clientes_vixen_completo.csv'

def normalizar_cep(valor):
    """Normaliza um CEP para o formato 00000-000"""
    if pd.isna(valor):
        return None
    
    # Converter para string e remover espaços
    cep = str(valor).strip()
    
    # Se for vazio, retornar None
    if not cep:
        return None
    
    # Remover todos os caracteres não numéricos
    apenas_numeros = re.sub(r'\D', '', cep)
    
    # Se não sobrou nada, retornar None
    if not apenas_numeros:
        return None
    
    # Se tem mais de 8 dígitos, está incorreto - manter como está
    if len(apenas_numeros) > 8:
        return None
    
    # Completar com zeros à esquerda se necessário
    if len(apenas_numeros) < 8:
        apenas_numeros = apenas_numeros.zfill(8)
    
    # Formatar no padrão 00000-000
    cep_formatado = f'{apenas_numeros[:5]}-{apenas_numeros[5:]}'
    
    return cep_formatado

def main():
    print("="*80)
    print("NORMALIZAÇÃO DE CEP")
    print("="*80)
    print()
    
    # Ler arquivo
    print(f"Lendo arquivo: {INPUT_FILE.name}")
    df = pd.read_csv(INPUT_FILE, sep=';', encoding='utf-8')
    print(f"  Total de registros: {len(df):,}")
    print()
    
    col_name = 'CEP'
    
    # Estatísticas antes
    print("ANTES da normalização:")
    print(f"  CEPs preenchidos: {df[col_name].notna().sum():,}")
    print(f"  CEPs vazios: {df[col_name].isna().sum():,}")
    print()
    
    # Analisar padrões antes
    ceps = df[col_name].dropna().astype(str)
    formato_correto = ceps.str.match(r'^\d{5}-\d{3}$')
    sem_hifen = ceps.str.match(r'^\d{8}$')
    apenas_digitos = ceps.str.replace(r'\D', '', regex=True)
    incompleto = apenas_digitos.str.len() < 8
    
    print("PADRÕES IDENTIFICADOS:")
    print(f"  Formato correto (00000-000): {formato_correto.sum():,}")
    print(f"  Sem hífen (00000000): {sem_hifen.sum():,}")
    print(f"  Incompleto (< 8 dígitos): {incompleto.sum():,}")
    print()
    
    # Backup da coluna original
    df['CEP_original'] = df[col_name].copy()
    
    # Aplicar normalização
    print("Aplicando normalizações...")
    df[col_name] = df[col_name].apply(normalizar_cep)
    print("  ✓ Concluído")
    print()
    
    # Estatísticas depois
    print("DEPOIS da normalização:")
    print(f"  CEPs preenchidos: {df[col_name].notna().sum():,}")
    print(f"  CEPs vazios: {df[col_name].isna().sum():,}")
    print()
    
    # Análise de mudanças
    mudancas = df[df[col_name] != df['CEP_original']]
    print(f"Total de registros modificados: {len(mudancas):,}")
    print()
    
    # Mostrar exemplos de mudanças
    if len(mudancas) > 0:
        print("EXEMPLOS DE MUDANÇAS (primeiros 20):")
        print("-"*80)
        for i, (idx, row) in enumerate(mudancas.head(20).iterrows(), 1):
            original = row['CEP_original']
            novo = row[col_name]
            original_str = str(original) if pd.notna(original) else 'None'
            novo_str = str(novo) if pd.notna(novo) else 'None'
            print(f"{i:2}. {original_str:20} → {novo_str}")
        print()
    
    # Análise de padrões após normalização
    print("PADRÕES APÓS NORMALIZAÇÃO:")
    print("-"*80)
    
    # Verificar formato 00000-000
    ceps_novos = df[col_name].dropna().astype(str)
    padrao_correto = ceps_novos.str.match(r'^\d{5}-\d{3}$')
    total_ceps = len(ceps_novos)
    
    if total_ceps > 0:
        print(f"CEPs no formato correto (00000-000): {padrao_correto.sum():,} ({padrao_correto.sum()/total_ceps*100:.1f}%)")
        print(f"CEPs em formato diferente: {total_ceps - padrao_correto.sum():,}")
        
        # Mostrar CEPs que não seguem o padrão
        nao_padrao = ceps_novos[~ceps_novos.str.match(r'^\d{5}-\d{3}$')]
        if len(nao_padrao) > 0:
            print(f"\nExemplos fora do padrão (primeiros 10):")
            for i, cep in enumerate(nao_padrao.head(10), 1):
                print(f"  {i}. {cep}")
    
    print()
    
    # Remover coluna backup
    df = df.drop(columns=['CEP_original'])
    
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
