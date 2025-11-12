"""
Script para normalizar colunas de telefone/celular no arquivo consolidadas.csv
Formato padrão: (XX) XXXXXXXXX
"""

import pandas as pd
import re
from pathlib import Path

def limpar_telefone(valor):
    """
    Remove caracteres não numéricos e textos desnecessários do telefone
    
    Args:
        valor: Telefone em qualquer formato
        
    Returns:
        String contendo apenas dígitos ou None se inválido
    """
    if pd.isna(valor):
        return None
    
    # Converter para string e limpar espaços
    tel_str = str(valor).strip().upper()
    
    # Se vazio ou nan, retornar None
    if not tel_str or tel_str == 'NAN':
        return None
    
    # Remover textos comuns que aparecem nos dados
    textos_remover = [
        'LIGAR', 'RECADO', 'REC', 'MARCOS', 'NAMORADA', 'PAI', 'ROMULO',
        'WASGHINTON', 'WASHINGTON', 'FIXO', 'CELULAR', 'TEL', 'TELEFONE',
        '-', '.', '/', '(', ')', '[', ']', ' '
    ]
    
    for texto in textos_remover:
        tel_str = tel_str.replace(texto, '')
    
    # Extrair apenas dígitos
    apenas_digitos = re.sub(r'\D', '', tel_str)
    
    return apenas_digitos if apenas_digitos else None


def normalizar_telefone(valor):
    """
    Normaliza um telefone para o formato (XX) XXXXXXXXX
    
    Args:
        valor: Telefone em qualquer formato
        
    Returns:
        Telefone normalizado no formato (XX) XXXXXXXXX ou None se inválido
    """
    # Limpar telefone
    apenas_digitos = limpar_telefone(valor)
    
    # Se não tem dígitos ou inválido, retornar None
    if not apenas_digitos:
        return None
    
    # Validar quantidade de dígitos
    num_digitos = len(apenas_digitos)
    
    # Se tem menos de 8 dígitos, considerar inválido
    if num_digitos < 8:
        return None
    
    # Se tem 8 dígitos (telefone fixo sem DDD), assumir DDD 11 (São Paulo)
    if num_digitos == 8:
        apenas_digitos = '11' + apenas_digitos
        num_digitos = 10
    
    # Se tem 9 dígitos (celular sem DDD), assumir DDD 11 (São Paulo)
    if num_digitos == 9:
        apenas_digitos = '11' + apenas_digitos
        num_digitos = 11
    
    # Se tem 10 dígitos (telefone fixo com DDD)
    if num_digitos == 10:
        ddd = apenas_digitos[:2]
        numero = apenas_digitos[2:]
        return f'({ddd}) {numero}'
    
    # Se tem 11 dígitos (celular com DDD)
    if num_digitos == 11:
        ddd = apenas_digitos[:2]
        numero = apenas_digitos[2:]
        return f'({ddd}) {numero}'
    
    # Se tem 12 dígitos (pode ter 0 inicial ou dígito extra)
    if num_digitos == 12:
        # Remover primeiro 0 se for 0
        if apenas_digitos[0] == '0':
            apenas_digitos = apenas_digitos[1:]
            ddd = apenas_digitos[:2]
            numero = apenas_digitos[2:]
            return f'({ddd}) {numero}'
        # Caso contrário, pegar os últimos 11 dígitos
        else:
            apenas_digitos = apenas_digitos[-11:]
            ddd = apenas_digitos[:2]
            numero = apenas_digitos[2:]
            return f'({ddd}) {numero}'
    
    # Se tem 13 dígitos, pegar os últimos 11
    if num_digitos == 13:
        apenas_digitos = apenas_digitos[-11:]
        ddd = apenas_digitos[:2]
        numero = apenas_digitos[2:]
        return f'({ddd}) {numero}'
    
    # Se tem mais de 13 dígitos, considerar inválido
    if num_digitos > 13:
        return None
    
    return None


def main():
    # Caminhos
    pasta_base = Path('D:/projetos/carne_facil/carne_facil/1_normalizacao')
    arquivo_entrada = pasta_base / 'dados_processados/originais/oss/consolidadas/consolidadas.csv'
    
    print("="*80)
    print("NORMALIZAÇÃO DE TELEFONES - consolidadas.csv")
    print("="*80)
    print()
    
    # Ler arquivo
    print("📖 Lendo arquivo...")
    df = pd.read_csv(arquivo_entrada, sep=';', encoding='utf-8')
    print(f"   Total de registros: {len(df):,}")
    print()
    
    # Identificar colunas de telefone
    colunas_tel = [col for col in df.columns if 'TELEFONE' in col.upper() or 'CELULAR' in col.upper() or 'FONE' in col.upper()]
    print(f"📞 Colunas de telefone encontradas: {len(colunas_tel)}")
    for col in colunas_tel:
        print(f"   - {col}")
    print()
    
    # Normalizar cada coluna
    for col_name in colunas_tel:
        print("="*80)
        print(f"Processando: {col_name}")
        print("="*80)
        
        # Estatísticas ANTES
        valores_antes = df[col_name].dropna().astype(str)
        print(f"\n📊 ANTES:")
        print(f"   Telefones preenchidos: {len(valores_antes):,}")
        print(f"   Telefones vazios: {df[col_name].isna().sum():,}")
        
        # Contar formato correto ANTES
        corretos_antes = valores_antes.str.match(r'^\(\d{2}\) \d{8,9}$').sum()
        print(f"   Formato correto (XX) XXXXXXXXX: {corretos_antes:,}")
        
        # Aplicar normalização
        print(f"\n🔧 Normalizando...")
        df[col_name] = df[col_name].apply(normalizar_telefone)
        
        # Estatísticas DEPOIS
        valores_depois = df[col_name].dropna().astype(str)
        print(f"\n📊 DEPOIS:")
        print(f"   Telefones preenchidos: {len(valores_depois):,}")
        print(f"   Telefones vazios: {df[col_name].isna().sum():,}")
        
        # Contar formato correto DEPOIS
        corretos_depois = valores_depois.str.match(r'^\(\d{2}\) \d{8,9}$').sum()
        print(f"   Formato correto (XX) XXXXXXXXX: {corretos_depois:,}")
        
        # Calcular modificações
        modificados = corretos_depois - corretos_antes
        invalidos = len(valores_antes) - len(valores_depois)
        print(f"\n✅ Registros modificados: {modificados:,}")
        if invalidos > 0:
            print(f"⚠️  Registros invalidados: {invalidos:,}")
        
        # Mostrar exemplos de transformações
        print(f"\n📝 EXEMPLOS DE TRANSFORMAÇÕES:")
        print("-"*80)
        exemplos = [
            ("11942405279", normalizar_telefone("11942405279")),
            ("119777-7376", normalizar_telefone("119777-7376")),
            ("45452880", normalizar_telefone("45452880")),
            ("FIXO 2357 7192", normalizar_telefone("FIXO 2357 7192")),
            ("pai romulo 11 958674002", normalizar_telefone("pai romulo 11 958674002")),
        ]
        for antes, depois in exemplos:
            if depois:
                print(f"   {antes:30} → {depois}")
            else:
                print(f"   {antes:30} → [INVÁLIDO]")
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
    for col_name in colunas_tel:
        total_preenchidos = df[col_name].notna().sum()
        print(f"   {col_name}: {total_preenchidos:,} telefones no formato (XX) XXXXXXXXX")
    print()


if __name__ == '__main__':
    main()
