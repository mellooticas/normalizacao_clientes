"""
Script para normalizar as colunas CEP e CEP.1 no arquivo consolidadas.csv
Formato padrão: 00000-000
"""

import pandas as pd
import re
from pathlib import Path

def normalizar_cep(valor):
    """
    Normaliza um CEP para o formato 00000-000
    
    Args:
        valor: CEP em qualquer formato
        
    Returns:
        CEP normalizado no formato 00000-000 ou None se inválido
    """
    if pd.isna(valor):
        return None
    
    # Converter para string e limpar
    cep_str = str(valor).strip()
    
    # Se vazio, retornar None
    if not cep_str or cep_str == 'nan':
        return None
    
    # Remover .0 no final (se vier como float do pandas)
    if cep_str.endswith('.0'):
        cep_str = cep_str[:-2]
    
    # Extrair apenas dígitos
    apenas_digitos = re.sub(r'\D', '', cep_str)
    
    # Se não tem dígitos ou inválido, retornar None
    if not apenas_digitos or len(apenas_digitos) == 0:
        return None
    
    # Se tem menos de 8 dígitos, preencher com zeros à esquerda
    if len(apenas_digitos) < 8:
        apenas_digitos = apenas_digitos.zfill(8)
    
    # Se tem mais de 8 dígitos, pegar apenas os primeiros 8
    if len(apenas_digitos) > 8:
        apenas_digitos = apenas_digitos[:8]
    
    # Formatar: 00000-000
    cep_formatado = f'{apenas_digitos[:5]}-{apenas_digitos[5:]}'
    
    return cep_formatado


def main():
    # Caminhos
    pasta_base = Path('D:/projetos/carne_facil/carne_facil/1_normalizacao')
    arquivo_entrada = pasta_base / 'dados_processados/originais/oss/consolidadas/consolidadas.csv'
    
    print("="*80)
    print("NORMALIZAÇÃO DE CEP - consolidadas.csv")
    print("="*80)
    print()
    
    # Ler arquivo
    print("📖 Lendo arquivo...")
    df = pd.read_csv(arquivo_entrada, sep=';', encoding='utf-8')
    print(f"   Total de registros: {len(df):,}")
    print()
    
    # Identificar colunas CEP
    colunas_cep = [col for col in df.columns if 'CEP' in col.upper()]
    print(f"📍 Colunas CEP encontradas: {len(colunas_cep)}")
    for col in colunas_cep:
        print(f"   - {col}")
    print()
    
    # Normalizar cada coluna CEP
    for col_name in colunas_cep:
        print("="*80)
        print(f"Processando: {col_name}")
        print("="*80)
        
        # Estatísticas ANTES
        valores_antes = df[col_name].dropna().astype(str)
        print(f"\n📊 ANTES:")
        print(f"   CEPs preenchidos: {len(valores_antes):,}")
        print(f"   CEPs vazios: {df[col_name].isna().sum():,}")
        
        # Contar formato correto ANTES
        corretos_antes = valores_antes.str.match(r'^\d{5}-\d{3}$').sum()
        print(f"   Formato correto (00000-000): {corretos_antes:,}")
        
        # Aplicar normalização
        print(f"\n🔧 Normalizando...")
        df[col_name] = df[col_name].apply(normalizar_cep)
        
        # Estatísticas DEPOIS
        valores_depois = df[col_name].dropna().astype(str)
        print(f"\n📊 DEPOIS:")
        print(f"   CEPs preenchidos: {len(valores_depois):,}")
        print(f"   CEPs vazios: {df[col_name].isna().sum():,}")
        
        # Contar formato correto DEPOIS
        corretos_depois = valores_depois.str.match(r'^\d{5}-\d{3}$').sum()
        print(f"   Formato correto (00000-000): {corretos_depois:,}")
        
        # Calcular modificações
        modificados = corretos_depois - corretos_antes
        print(f"\n✅ Registros modificados: {modificados:,}")
        
        # Mostrar exemplos de transformações
        print(f"\n📝 EXEMPLOS DE TRANSFORMAÇÕES:")
        print("-"*80)
        exemplos = [
            ("9370320.0", normalizar_cep("9370320.0")),
            ("931270.0", normalizar_cep("931270.0")),
            ("5210000", normalizar_cep("5210000")),
            ("08452440", normalizar_cep("08452440")),
            ("05210-000", normalizar_cep("05210-000")),
        ]
        for antes, depois in exemplos:
            if depois:
                print(f"   {antes:20} → {depois}")
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
    print("RESUMO FINAL:")
    print("-"*80)
    for col_name in colunas_cep:
        total_preenchidos = df[col_name].notna().sum()
        print(f"   {col_name}: {total_preenchidos:,} CEPs no formato 00000-000")
    print()


if __name__ == '__main__':
    main()
