"""
Script para recuperar dados perdidos de Suzano 2
1. Limpa .0 da coluna OS N° em consolidadas.csv
2. Faz merge com SUZANO2_consolidado.csv para recuperar DATA DE COMPRA e CONSULTOR
"""

import pandas as pd
from pathlib import Path

def limpar_os_numero(valor):
    """Remove .0 do final do número da OS"""
    if pd.isna(valor):
        return None
    
    os_str = str(valor).strip()
    
    if not os_str or os_str == 'nan':
        return None
    
    # Remover .0 se existir
    if '.' in os_str:
        os_str = os_str.split('.')[0]
    
    return os_str


def main():
    pasta_base = Path('D:/projetos/carne_facil/carne_facil/1_normalizacao')
    arquivo_consolidadas = pasta_base / 'dados_processados/originais/oss/consolidadas/consolidadas.csv'
    arquivo_suzano2 = pasta_base / 'dados_processados/originais/oss/consolidadas/SUZANO2_consolidado.csv'
    
    print("="*80)
    print("RECUPERANDO DADOS PERDIDOS DE SUZANO 2")
    print("="*80)
    print()
    
    # Ler arquivos
    print("📖 Lendo arquivos...")
    consolidadas = pd.read_csv(arquivo_consolidadas, sep=';', encoding='utf-8')
    suzano2 = pd.read_csv(arquivo_suzano2, sep=';', encoding='utf-8')
    
    # Limpar nomes de colunas (remover espaços extras)
    consolidadas.columns = consolidadas.columns.str.strip()
    suzano2.columns = suzano2.columns.str.strip()
    
    print(f"   consolidadas.csv: {len(consolidadas):,} registros")
    print(f"   SUZANO2_consolidado.csv: {len(suzano2):,} registros")
    print()
    
    # Situação ANTES
    print("="*80)
    print("📊 SITUAÇÃO ANTES")
    print("="*80)
    suzano2_mask = consolidadas['LOJA'].astype(str).str.contains('uzano 2', case=False, na=False)
    print(f"Registros Suzano 2 em consolidadas: {suzano2_mask.sum():,}")
    print()
    
    # Verificar colunas DATA DE COMPRA e CONSULTOR
    cols_verificar = ['DATA DE COMPRA', 'CONSULTOR']
    for col in cols_verificar:
        if col in consolidadas.columns:
            preenchidos_total = consolidadas[col].notna().sum()
            preenchidos_suzano2 = consolidadas[suzano2_mask][col].notna().sum()
            vazios_suzano2 = consolidadas[suzano2_mask][col].isna().sum()
            print(f"{col}:")
            print(f"   Total preenchidos: {preenchidos_total:,}")
            print(f"   Suzano 2 preenchidos: {preenchidos_suzano2:,}")
            print(f"   Suzano 2 vazios: {vazios_suzano2:,}")
        else:
            print(f"{col}: COLUNA NÃO ENCONTRADA")
    print()
    
    # PASSO 1: Limpar .0 da OS N° em consolidadas
    print("="*80)
    print("🔧 PASSO 1: Limpando .0 da coluna OS N°")
    print("="*80)
    print("Exemplos ANTES:")
    exemplos_antes = consolidadas[suzano2_mask]['OS N°'].head(5).astype(str)
    for ex in exemplos_antes:
        print(f"   {ex}")
    print()
    
    consolidadas['OS N°'] = consolidadas['OS N°'].apply(limpar_os_numero)
    
    print("Exemplos DEPOIS:")
    exemplos_depois = consolidadas[suzano2_mask]['OS N°'].head(5).astype(str)
    for ex in exemplos_depois:
        print(f"   {ex}")
    print()
    
    # PASSO 2: Preparar dados de suzano2 para merge
    print("="*80)
    print("🔧 PASSO 2: Preparando dados de SUZANO2 para merge")
    print("="*80)
    
    # Limpar OS N° de suzano2 também (por segurança)
    suzano2['OS N°'] = suzano2['OS N°'].apply(limpar_os_numero)
    
    # Selecionar apenas as colunas necessárias
    colunas_merge = ['OS N°', 'DATA DE COMPRA', 'CONSULTOR']
    suzano2_merge = suzano2[colunas_merge].copy()
    
    print(f"Registros em SUZANO2 para merge: {len(suzano2_merge):,}")
    print(f"   DATA DE COMPRA preenchidos: {suzano2_merge['DATA DE COMPRA'].notna().sum():,}")
    print(f"   CONSULTOR preenchidos: {suzano2_merge['CONSULTOR'].notna().sum():,}")
    print()
    
    # PASSO 3: Atualizar dados usando map
    print("="*80)
    print("🔧 PASSO 3: Atualizando dados de Suzano 2")
    print("="*80)
    
    # Criar dicionários de mapeamento OS -> Valor
    os_to_data = dict(zip(suzano2_merge['OS N°'], suzano2_merge['DATA DE COMPRA']))
    os_to_consultor = dict(zip(suzano2_merge['OS N°'], suzano2_merge['CONSULTOR']))
    
    print(f"Mapeamentos criados:")
    print(f"   OS -> DATA DE COMPRA: {len(os_to_data)} registros")
    print(f"   OS -> CONSULTOR: {len(os_to_consultor)} registros")
    print()
    
    # Atualizar apenas registros Suzano 2 que estão vazios
    print("Atualizando registros vazios de Suzano 2...")
    
    # Usar máscara mais flexível para Suzano 2
    mask_suzano2 = consolidadas['LOJA'].astype(str).str.contains('uzano 2', case=False, na=False)
    
    # Para DATA DE COMPRA
    if 'DATA DE COMPRA' in consolidadas.columns:
        mask_suzano2_vazio_data = mask_suzano2 & (consolidadas['DATA DE COMPRA'].isna())
        if mask_suzano2_vazio_data.sum() > 0:
            consolidadas.loc[mask_suzano2_vazio_data, 'DATA DE COMPRA'] = consolidadas.loc[mask_suzano2_vazio_data, 'OS N°'].map(os_to_data)
            print(f"   DATA DE COMPRA: {mask_suzano2_vazio_data.sum()} registros atualizados")
    
    # Para CONSULTOR
    if 'CONSULTOR' in consolidadas.columns:
        mask_suzano2_vazio_consultor = mask_suzano2 & (consolidadas['CONSULTOR'].isna())
        if mask_suzano2_vazio_consultor.sum() > 0:
            consolidadas.loc[mask_suzano2_vazio_consultor, 'CONSULTOR'] = consolidadas.loc[mask_suzano2_vazio_consultor, 'OS N°'].map(os_to_consultor)
            print(f"   CONSULTOR: {mask_suzano2_vazio_consultor.sum()} registros atualizados")
    print()
    
    # PASSO 4: Verificar resultado
    print("="*80)
    print("🔧 PASSO 4: Verificando resultado")
    print("="*80)
    
    print(f"Total de registros: {len(consolidadas):,}")
    print()
    
    # Situação DEPOIS
    print("="*80)
    print("📊 SITUAÇÃO DEPOIS")
    print("="*80)
    suzano2_mask_final = consolidadas['LOJA'].astype(str).str.contains('uzano 2', case=False, na=False)
    print(f"Registros Suzano 2 em consolidadas: {suzano2_mask_final.sum():,}")
    print()
    
    for col in cols_verificar:
        if col in consolidadas.columns:
            preenchidos_total = consolidadas[col].notna().sum()
            preenchidos_suzano2 = consolidadas[suzano2_mask_final][col].notna().sum()
            vazios_suzano2 = consolidadas[suzano2_mask_final][col].isna().sum()
            print(f"{col}:")
            print(f"   Total preenchidos: {preenchidos_total:,}")
            print(f"   Suzano 2 preenchidos: {preenchidos_suzano2:,}")
            print(f"   Suzano 2 vazios: {vazios_suzano2:,}")
    print()
    
    # Salvar arquivo
    print("="*80)
    print("💾 Salvando arquivo...")
    consolidadas.to_csv(arquivo_consolidadas, sep=';', encoding='utf-8', index=False)
    print(f"   ✅ Arquivo salvo: {arquivo_consolidadas}")
    print()
    
    print("="*80)
    print("✅ RECUPERAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*80)
    print()


if __name__ == '__main__':
    main()
