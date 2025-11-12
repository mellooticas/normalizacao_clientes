"""
Script para normalizar a coluna COMO CONHECEU no arquivo consolidadas.csv
Remove números do início para padronizar (ex: "01 - Instagram" → "Instagram")
"""

import pandas as pd
import re
from pathlib import Path

def normalizar_como_conheceu(valor):
    """
    Remove números do início do valor
    
    Args:
        valor: String com possível número no início
        
    Returns:
        String sem número no início
    """
    if pd.isna(valor):
        return None
    
    # Converter para string e limpar
    texto = str(valor).strip()
    
    # Se vazio, retornar None
    if not texto or texto == 'nan':
        return None
    
    # Remover número do início seguido de hífen, espaço, etc
    # Padrões: "01 - Texto", "04 TEXTO", "138 - Texto"
    texto_limpo = re.sub(r'^\d+\s*-?\s*', '', texto).strip()
    
    # Se ficou vazio após limpeza, retornar None
    if not texto_limpo:
        return None
    
    # Capitalizar primeira letra de cada palavra (Title Case)
    texto_limpo = texto_limpo.title()
    
    return texto_limpo


def main():
    # Caminhos
    pasta_base = Path('D:/projetos/carne_facil/carne_facil/1_normalizacao')
    arquivo_entrada = pasta_base / 'dados_processados/originais/oss/consolidadas/consolidadas.csv'
    
    print("="*80)
    print("NORMALIZAÇÃO DE 'COMO CONHECEU' - consolidadas.csv")
    print("="*80)
    print()
    
    # Ler arquivo
    print("📖 Lendo arquivo...")
    df = pd.read_csv(arquivo_entrada, sep=';', encoding='utf-8')
    print(f"   Total de registros: {len(df):,}")
    print()
    
    # Identificar coluna
    col_name = 'COMO CONHECEU'
    
    print("="*80)
    print(f"Processando: {col_name}")
    print("="*80)
    
    # Estatísticas ANTES
    valores_antes = df[col_name].dropna().astype(str)
    print(f"\n📊 ANTES:")
    print(f"   Valores preenchidos: {len(valores_antes):,}")
    print(f"   Valores vazios: {df[col_name].isna().sum():,}")
    print(f"   Valores únicos: {valores_antes.nunique():,}")
    
    # Identificar valores com número
    com_numero = valores_antes.str.match(r'^\d+\s*-?\s*.+')
    print(f"   Com número no início: {com_numero.sum():,}")
    
    # Mostrar exemplos ANTES
    print("\n📝 EXEMPLOS ANTES DA NORMALIZAÇÃO:")
    print("-"*80)
    exemplos_antes = valores_antes.value_counts().head(10)
    for i, (val, qtd) in enumerate(exemplos_antes.items(), 1):
        print(f"   {i:2}. [{qtd:4}x] {val}")
    
    # Aplicar normalização
    print(f"\n🔧 Normalizando...")
    df[col_name] = df[col_name].apply(normalizar_como_conheceu)
    
    # Estatísticas DEPOIS
    valores_depois = df[col_name].dropna().astype(str)
    print(f"\n📊 DEPOIS:")
    print(f"   Valores preenchidos: {len(valores_depois):,}")
    print(f"   Valores vazios: {df[col_name].isna().sum():,}")
    print(f"   Valores únicos: {valores_depois.nunique():,}")
    
    # Verificar se ainda tem número
    com_numero_depois = valores_depois.str.match(r'^\d+\s*-?\s*.+')
    print(f"   Com número no início: {com_numero_depois.sum():,}")
    
    # Mostrar exemplos DEPOIS
    print("\n📝 EXEMPLOS DEPOIS DA NORMALIZAÇÃO:")
    print("-"*80)
    exemplos_depois = valores_depois.value_counts().head(10)
    for i, (val, qtd) in enumerate(exemplos_depois.items(), 1):
        print(f"   {i:2}. [{qtd:4}x] {val}")
    
    # Mostrar transformações
    print(f"\n📝 EXEMPLOS DE TRANSFORMAÇÕES:")
    print("-"*80)
    exemplos = [
        ("04 CLIENTES", normalizar_como_conheceu("04 CLIENTES")),
        ("15 - ORÇAMENTO", normalizar_como_conheceu("15 - ORÇAMENTO")),
        ("16 - INDICAÇÃO", normalizar_como_conheceu("16 - INDICAÇÃO")),
        ("138 - SAÚDE DOS OLHOS", normalizar_como_conheceu("138 - SAÚDE DOS OLHOS")),
        ("01 - REDES SOCIAS", normalizar_como_conheceu("01 - REDES SOCIAS")),
        ("77 - AMIGO (IND)", normalizar_como_conheceu("77 - AMIGO (IND)")),
    ]
    for antes, depois in exemplos:
        if depois:
            print(f"   {antes:35} → {depois}")
    print()
    
    # Calcular modificações
    modificados = len(valores_antes) - len(valores_depois)
    if modificados >= 0:
        print(f"✅ {len(valores_antes):,} registros processados")
        if modificados > 0:
            print(f"⚠️  {modificados:,} registros invalidados (ficaram vazios)")
    print()
    
    # Salvar arquivo
    print("="*80)
    print("💾 Salvando arquivo...")
    df.to_csv(arquivo_entrada, sep=';', encoding='utf-8', index=False)
    print(f"   ✅ Arquivo salvo: {arquivo_entrada}")
    print()
    
    print("="*80)
    print("✅ NORMALIZAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*80)
    print()


if __name__ == '__main__':
    main()
