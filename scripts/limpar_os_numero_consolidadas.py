"""
Script para limpar a coluna OS N° no arquivo consolidadas.csv
Remove tudo após vírgula ou ponto (ex: "4028.0" → "4028")
"""

import pandas as pd
import re
from pathlib import Path

def limpar_os_numero(valor):
    """
    Remove tudo após vírgula ou ponto, mantendo apenas a parte inteira
    
    Args:
        valor: Número de OS em qualquer formato
        
    Returns:
        Número inteiro da OS
    """
    if pd.isna(valor):
        return None
    
    # Converter para string
    os_str = str(valor).strip()
    
    # Se vazio, retornar None
    if not os_str or os_str == 'nan':
        return None
    
    # Pegar apenas a parte antes da vírgula ou ponto
    # Se tiver vírgula, pegar antes dela
    if ',' in os_str:
        os_str = os_str.split(',')[0]
    
    # Se tiver ponto, pegar antes dele
    if '.' in os_str:
        os_str = os_str.split('.')[0]
    
    # Remover espaços
    os_str = os_str.strip()
    
    # Se ficou vazio, retornar None
    if not os_str:
        return None
    
    return os_str


def main():
    # Caminhos
    pasta_base = Path('D:/projetos/carne_facil/carne_facil/1_normalizacao')
    arquivo_entrada = pasta_base / 'dados_processados/originais/oss/consolidadas/consolidadas.csv'
    
    print("="*80)
    print("LIMPEZA DE OS N° - consolidadas.csv")
    print("="*80)
    print()
    
    # Ler arquivo
    print("📖 Lendo arquivo...")
    df = pd.read_csv(arquivo_entrada, sep=';', encoding='utf-8')
    print(f"   Total de registros: {len(df):,}")
    print()
    
    col_name = 'OS N°'
    
    # Estatísticas ANTES
    valores_antes = df[col_name].dropna().astype(str)
    print("="*80)
    print("📊 ANTES DA LIMPEZA")
    print("="*80)
    print(f"OS preenchidas: {len(valores_antes):,}")
    print(f"OS vazias: {df[col_name].isna().sum():,}")
    print()
    
    # Contar padrões
    com_ponto = valores_antes.str.contains(r'\.', na=False, regex=True).sum()
    com_virgula = valores_antes.str.contains(',', na=False).sum()
    apenas_digitos = valores_antes.str.match(r'^\d+$').sum()
    
    print("PADRÕES:")
    print("-"*80)
    print(f"   Com ponto (.0, etc): {com_ponto:,}")
    print(f"   Com vírgula: {com_virgula:,}")
    print(f"   Apenas dígitos (correto): {apenas_digitos:,}")
    print()
    
    # Mostrar exemplos ANTES
    print("📝 EXEMPLOS ANTES:")
    print("-"*80)
    for i, val in enumerate(valores_antes.head(10), 1):
        print(f"   {i:2}. {val}")
    print()
    
    # Aplicar limpeza
    print("🔧 Limpando OS N°...")
    df[col_name] = df[col_name].apply(limpar_os_numero)
    
    # Estatísticas DEPOIS
    valores_depois = df[col_name].dropna().astype(str)
    print()
    print("="*80)
    print("📊 DEPOIS DA LIMPEZA")
    print("="*80)
    print(f"OS preenchidas: {len(valores_depois):,}")
    print(f"OS vazias: {df[col_name].isna().sum():,}")
    print()
    
    # Verificar padrões
    apenas_digitos_depois = valores_depois.str.match(r'^\d+$').sum()
    com_ponto_depois = valores_depois.str.contains(r'\.', na=False, regex=True).sum()
    
    print("PADRÕES:")
    print("-"*80)
    print(f"   Apenas dígitos (correto): {apenas_digitos_depois:,}")
    print(f"   Com ponto: {com_ponto_depois:,}")
    print()
    
    # Mostrar exemplos DEPOIS
    print("📝 EXEMPLOS DEPOIS:")
    print("-"*80)
    for i, val in enumerate(valores_depois.head(10), 1):
        print(f"   {i:2}. {val}")
    print()
    
    # Mostrar transformações
    print("📝 EXEMPLOS DE TRANSFORMAÇÕES:")
    print("-"*80)
    exemplos = [
        ("4028.0", limpar_os_numero("4028.0")),
        ("12345.0", limpar_os_numero("12345.0")),
        ("999,5", limpar_os_numero("999,5")),
        ("123", limpar_os_numero("123")),
    ]
    for antes, depois in exemplos:
        if depois:
            print(f"   {antes:15} → {depois}")
    print()
    
    # Calcular modificações
    modificados = com_ponto + com_virgula
    print(f"✅ {modificados:,} registros limpos")
    print()
    
    # Salvar arquivo
    print("="*80)
    print("💾 Salvando arquivo...")
    df.to_csv(arquivo_entrada, sep=';', encoding='utf-8', index=False)
    print(f"   ✅ Arquivo salvo: {arquivo_entrada}")
    print()
    
    print("="*80)
    print("✅ LIMPEZA CONCLUÍDA COM SUCESSO!")
    print("="*80)
    print()


if __name__ == '__main__':
    main()
