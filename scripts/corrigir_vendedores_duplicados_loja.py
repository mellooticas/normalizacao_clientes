#!/usr/bin/env python3
"""
Script para corrigir vendedores duplicados na mesma loja
REGRA: Cada vendedor deve ser ÚNICO por loja
OBJETIVO: Escolher 1 registro por vendedor/loja e mapear os demais
"""

import pandas as pd
import json
from pathlib import Path

def analisar_duplicacoes_por_loja():
    """Analisa e corrige duplicações na mesma loja"""
    
    # Ler arquivo editado
    df = pd.read_excel('PADRONIZACAO_VENDEDORES_COMPLETA.xlsx')
    
    # Encontrar duplicações por loja
    duplicacoes = df.groupby(['nome_padronizado', 'loja_nome']).size().reset_index(name='count')
    duplicados = duplicacoes[duplicacoes['count'] > 1]
    
    print("🚨 PROBLEMA IDENTIFICADO:")
    print(f"   • {len(duplicados)} casos de vendedores duplicados na mesma loja")
    print(f"   • Total de registros problemáticos: {duplicados['count'].sum()}")
    print()
    
    # Criar tabela corrigida
    df_corrigido = []
    mapeamento_uuid = {}
    
    # Processar cada combinação vendedor/loja
    for (nome_padronizado, loja_nome), grupo in df.groupby(['nome_padronizado', 'loja_nome']):
        
        if len(grupo) == 1:
            # Apenas 1 registro - mantém como está
            registro_principal = grupo.iloc[0]
            df_corrigido.append({
                'nome_padronizado': nome_padronizado,
                'loja_nome': loja_nome,
                'loja_id': registro_principal['loja_id'],
                'codigo_vendedor_principal': registro_principal['codigo_vendedor'],
                'nome_original_principal': registro_principal['nome_original'],
                'registros_consolidados': 1,
                'nomes_originais_unidos': [registro_principal['nome_original']],
                'codigos_unidos': [registro_principal['codigo_vendedor']]
            })
            
        else:
            # Múltiplos registros - escolher 1 principal e mapear os outros
            # Critério: primeiro por código não-nulo, depois alfabético
            grupo_ordenado = grupo.sort_values(['codigo_vendedor'], na_position='last')
            registro_principal = grupo_ordenado.iloc[0]
            
            # Coletar todos os nomes e códigos para mapeamento
            nomes_originais = grupo['nome_original'].tolist()
            codigos = [c for c in grupo['codigo_vendedor'].tolist() if pd.notna(c) and c != '']
            
            df_corrigido.append({
                'nome_padronizado': nome_padronizado,
                'loja_nome': loja_nome,
                'loja_id': registro_principal['loja_id'],
                'codigo_vendedor_principal': registro_principal['codigo_vendedor'],
                'nome_original_principal': registro_principal['nome_original'],
                'registros_consolidados': len(grupo),
                'nomes_originais_unidos': nomes_originais,
                'codigos_unidos': codigos
            })
            
            # Criar mapeamento para os registros secundários
            chave_principal = f"{nome_padronizado}_{loja_nome}"
            mapeamento_uuid[chave_principal] = {
                'vendedor_principal': registro_principal['nome_original'],
                'codigo_principal': registro_principal['codigo_vendedor'],
                'vendedores_secundarios': []
            }
            
            for _, registro_sec in grupo.iterrows():
                if registro_sec['nome_original'] != registro_principal['nome_original']:
                    mapeamento_uuid[chave_principal]['vendedores_secundarios'].append({
                        'nome_original': registro_sec['nome_original'],
                        'codigo_vendedor': registro_sec['codigo_vendedor']
                    })
    
    return pd.DataFrame(df_corrigido), mapeamento_uuid, duplicados

def criar_tabela_final_vendedores():
    """Cria tabela final com vendedores únicos por loja"""
    
    df_corrigido, mapeamento_uuid, duplicados = analisar_duplicacoes_por_loja()
    
    # Estatísticas
    total_original = pd.read_excel('PADRONIZACAO_VENDEDORES_COMPLETA.xlsx').shape[0]
    total_corrigido = df_corrigido.shape[0]
    total_consolidacoes = duplicados['count'].sum() - len(duplicados)
    
    print("📊 ESTATÍSTICAS DA CORREÇÃO:")
    print(f"   • Registros originais: {total_original}")
    print(f"   • Registros finais (únicos por loja): {total_corrigido}")
    print(f"   • Registros consolidados: {total_consolidacoes}")
    print(f"   • Taxa de consolidação: {(total_consolidacoes/total_original*100):.1f}%")
    print()
    
    # Salvar tabela corrigida
    excel_path = "VENDEDORES_UNICOS_POR_LOJA.xlsx"
    
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df_corrigido.to_excel(writer, sheet_name='Vendedores_Unicos', index=False)
        
        # Ajustar largura das colunas
        worksheet = writer.sheets['Vendedores_Unicos']
        column_widths = {
            'A': 40,  # nome_padronizado
            'B': 20,  # loja_nome
            'C': 40,  # loja_id
            'D': 20,  # codigo_vendedor_principal
            'E': 40,  # nome_original_principal
            'F': 15,  # registros_consolidados
            'G': 50,  # nomes_originais_unidos
            'H': 30   # codigos_unidos
        }
        
        for col, width in column_widths.items():
            worksheet.column_dimensions[col].width = width
    
    # Salvar mapeamento UUID
    json_path = "MAPEAMENTO_VENDEDORES_UUID.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(mapeamento_uuid, f, ensure_ascii=False, indent=2)
    
    # CSV também
    csv_path = "VENDEDORES_UNICOS_POR_LOJA.csv"
    df_corrigido.to_csv(csv_path, index=False, encoding='utf-8-sig')
    
    return df_corrigido, mapeamento_uuid, excel_path, json_path, csv_path

def mostrar_casos_consolidados(df_corrigido):
    """Mostra os casos que foram consolidados"""
    
    consolidados = df_corrigido[df_corrigido['registros_consolidados'] > 1]
    
    print("🔧 CASOS CONSOLIDADOS (múltiplos registros → 1 único):")
    print("=" * 80)
    
    for _, row in consolidados.iterrows():
        print(f"✅ {row['nome_padronizado']} em {row['loja_nome']}")
        print(f"   📍 Registros consolidados: {row['registros_consolidados']}")
        print(f"   🎯 Principal: {row['nome_original_principal']} ({row['codigo_vendedor_principal']})")
        print(f"   📝 Todos os nomes: {', '.join(row['nomes_originais_unidos'])}")
        print(f"   🔢 Todos os códigos: {', '.join([str(c) for c in row['codigos_unidos'] if pd.notna(c)])}")
        print()

def main():
    """Função principal"""
    print("🔧 CORRIGINDO VENDEDORES DUPLICADOS NA MESMA LOJA")
    print("=" * 60)
    print("REGRA: Cada vendedor deve ser ÚNICO por loja")
    print("ESTRATÉGIA: 1 registro principal + mapeamento dos secundários")
    print()
    
    # Processar correções
    df_corrigido, mapeamento_uuid, excel_path, json_path, csv_path = criar_tabela_final_vendedores()
    
    # Mostrar casos consolidados
    mostrar_casos_consolidados(df_corrigido)
    
    print("💾 ARQUIVOS CRIADOS:")
    print(f"   📊 Excel: {excel_path}")
    print(f"   🗂️ CSV: {csv_path}")
    print(f"   🔗 Mapeamento UUID: {json_path}")
    print()
    
    print("🎯 PRÓXIMOS PASSOS:")
    print("   1. Revisar tabela de vendedores únicos por loja")
    print("   2. Usar mapeamento UUID para conectar com dados Vixen")
    print("   3. Aplicar mapeamento nas importações futuras")
    print("   4. Garantir que novos registros sejam únicos por loja")
    
    return df_corrigido, mapeamento_uuid

if __name__ == "__main__":
    df_result, mapping_result = main()