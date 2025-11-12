#!/usr/bin/env python3
"""
TABELA DE PADRONIZAÇÃO DE VENDEDORES
===================================
Cria uma tabela simples para padronização manual dos vendedores
"""

import pandas as pd
import json
from datetime import datetime

def main():
    print("📋 CRIANDO TABELA DE PADRONIZAÇÃO DE VENDEDORES")
    print("=" * 55)
    
    # Dados extraídos do Supabase (consulta 6)
    vendedores_supabase = [
        # Mauá (048)
        {"nome_original": "ANDRESSA DE SOUZA", "loja": "048_MAUA", "loja_nome": "Mauá"},
        {"nome_original": "B ETH", "loja": "048_MAUA", "loja_nome": "Mauá"},
        {"nome_original": "BETH", "loja": "048_MAUA", "loja_nome": "Mauá"},
        {"nome_original": "ERICA DE CASSIA JESUS SILVA", "loja": "048_MAUA", "loja_nome": "Mauá"},
        {"nome_original": "GARANTIA", "loja": "048_MAUA", "loja_nome": "Mauá"},
        {"nome_original": "LARISSA", "loja": "048_MAUA", "loja_nome": "Mauá"},
        {"nome_original": "LUANA", "loja": "048_MAUA", "loja_nome": "Mauá"},
        {"nome_original": "MARIA DA SILVA OZORIO", "loja": "048_MAUA", "loja_nome": "Mauá"},
        {"nome_original": "MARIA ELIZABETH", "loja": "048_MAUA", "loja_nome": "Mauá"},
        {"nome_original": "MARIA ELIZEBETH", "loja": "048_MAUA", "loja_nome": "Mauá"},
        {"nome_original": "RENAN NAZARO", "loja": "048_MAUA", "loja_nome": "Mauá"},
        {"nome_original": "ROGÉRIO", "loja": "048_MAUA", "loja_nome": "Mauá"},
        {"nome_original": "TATY", "loja": "048_MAUA", "loja_nome": "Mauá"},
        {"nome_original": "WEVELLY", "loja": "048_MAUA", "loja_nome": "Mauá"},
        {"nome_original": "WEVILLY", "loja": "048_MAUA", "loja_nome": "Mauá"},
        
        # Perus (009)
        {"nome_original": "ANA", "loja": "009_PERUS", "loja_nome": "Perus"},
        {"nome_original": "ARIANI", "loja": "009_PERUS", "loja_nome": "Perus"},
        {"nome_original": "ERIKA", "loja": "009_PERUS", "loja_nome": "Perus"},
        {"nome_original": "ÉRIKA", "loja": "009_PERUS", "loja_nome": "Perus"},
        {"nome_original": "JOANA", "loja": "009_PERUS", "loja_nome": "Perus"},
        {"nome_original": "LARISSA", "loja": "009_PERUS", "loja_nome": "Perus"},
        {"nome_original": "LUANA", "loja": "009_PERUS", "loja_nome": "Perus"},
        {"nome_original": "MARIA", "loja": "009_PERUS", "loja_nome": "Perus"},
        {"nome_original": "NAN", "loja": "009_PERUS", "loja_nome": "Perus"},
        {"nome_original": "ROGERIO", "loja": "009_PERUS", "loja_nome": "Perus"},
        {"nome_original": "ROGÉRIO", "loja": "009_PERUS", "loja_nome": "Perus"},
        {"nome_original": "SAMUEL", "loja": "009_PERUS", "loja_nome": "Perus"},
        {"nome_original": "SANDY", "loja": "009_PERUS", "loja_nome": "Perus"},
        {"nome_original": "TATY", "loja": "009_PERUS", "loja_nome": "Perus"},
        {"nome_original": "TATY/ERIKA", "loja": "009_PERUS", "loja_nome": "Perus"},
        {"nome_original": "WEVILLY", "loja": "009_PERUS", "loja_nome": "Perus"},
        {"nome_original": "WILLIAM", "loja": "009_PERUS", "loja_nome": "Perus"},
        {"nome_original": "WILLIAN", "loja": "009_PERUS", "loja_nome": "Perus"},
        
        # Rio Pequeno (011)
        {"nome_original": "BRUNO", "loja": "011_RIO_PEQUENO", "loja_nome": "Rio Pequeno"},
        {"nome_original": "GARANTIA", "loja": "011_RIO_PEQUENO", "loja_nome": "Rio Pequeno"},
        {"nome_original": "KEREN", "loja": "011_RIO_PEQUENO", "loja_nome": "Rio Pequeno"},
        {"nome_original": "LARISSA", "loja": "011_RIO_PEQUENO", "loja_nome": "Rio Pequeno"},
        {"nome_original": "MARIA RAMOS", "loja": "011_RIO_PEQUENO", "loja_nome": "Rio Pequeno"},
        {"nome_original": "R0GERIO", "loja": "011_RIO_PEQUENO", "loja_nome": "Rio Pequeno"},
        {"nome_original": "ROGERIO", "loja": "011_RIO_PEQUENO", "loja_nome": "Rio Pequeno"},
        {"nome_original": "ROGÉRIO", "loja": "011_RIO_PEQUENO", "loja_nome": "Rio Pequeno"},
        {"nome_original": "ROSAGELA", "loja": "011_RIO_PEQUENO", "loja_nome": "Rio Pequeno"},
        {"nome_original": "ROSANGELA", "loja": "011_RIO_PEQUENO", "loja_nome": "Rio Pequeno"},
        {"nome_original": "ROSÂNGELA", "loja": "011_RIO_PEQUENO", "loja_nome": "Rio Pequeno"},
        {"nome_original": "ROSÃNGELA", "loja": "011_RIO_PEQUENO", "loja_nome": "Rio Pequeno"},
        {"nome_original": "ROSÃÑGELA", "loja": "011_RIO_PEQUENO", "loja_nome": "Rio Pequeno"},
        {"nome_original": "ROSNGELA", "loja": "011_RIO_PEQUENO", "loja_nome": "Rio Pequeno"},
        {"nome_original": "TATY", "loja": "011_RIO_PEQUENO", "loja_nome": "Rio Pequeno"},
        {"nome_original": "WEVILLY", "loja": "011_RIO_PEQUENO", "loja_nome": "Rio Pequeno"},
        
        # São Mateus (012)
        {"nome_original": "/////////////////////////", "loja": "012_SAO_MATEUS", "loja_nome": "São Mateus"},
        {"nome_original": "ARIANI", "loja": "012_SAO_MATEUS", "loja_nome": "São Mateus"},
        {"nome_original": "CHINASA DORIS", "loja": "012_SAO_MATEUS", "loja_nome": "São Mateus"},
        {"nome_original": "GARANTIA", "loja": "012_SAO_MATEUS", "loja_nome": "São Mateus"},
        {"nome_original": "JOANA", "loja": "012_SAO_MATEUS", "loja_nome": "São Mateus"},
        {"nome_original": "LARISSA", "loja": "012_SAO_MATEUS", "loja_nome": "São Mateus"},
        {"nome_original": "MARIA", "loja": "012_SAO_MATEUS", "loja_nome": "São Mateus"},
        {"nome_original": "ROGERIO", "loja": "012_SAO_MATEUS", "loja_nome": "São Mateus"},
        {"nome_original": "ROGÉRIO", "loja": "012_SAO_MATEUS", "loja_nome": "São Mateus"},
        {"nome_original": "SANDY", "loja": "012_SAO_MATEUS", "loja_nome": "São Mateus"},
        {"nome_original": "TATI", "loja": "012_SAO_MATEUS", "loja_nome": "São Mateus"},
        {"nome_original": "TATY", "loja": "012_SAO_MATEUS", "loja_nome": "São Mateus"},
        {"nome_original": "WEVELLY", "loja": "012_SAO_MATEUS", "loja_nome": "São Mateus"},
        {"nome_original": "WEVILLY", "loja": "012_SAO_MATEUS", "loja_nome": "São Mateus"},
        {"nome_original": "WEVILLY/TATY", "loja": "012_SAO_MATEUS", "loja_nome": "São Mateus"},
        {"nome_original": "WILLAM", "loja": "012_SAO_MATEUS", "loja_nome": "São Mateus"},
        {"nome_original": "WILLIAM", "loja": "012_SAO_MATEUS", "loja_nome": "São Mateus"},
        {"nome_original": "WILLIAN", "loja": "012_SAO_MATEUS", "loja_nome": "São Mateus"},
        
        # Suzano (042)
        {"nome_original": "ARIANE", "loja": "042_SUZANO", "loja_nome": "Suzano"},
        {"nome_original": "ARIANI", "loja": "042_SUZANO", "loja_nome": "Suzano"},
        {"nome_original": "BETH", "loja": "042_SUZANO", "loja_nome": "Suzano"},
        {"nome_original": "FELIPE", "loja": "042_SUZANO", "loja_nome": "Suzano"},
        {"nome_original": "GARANTIA", "loja": "042_SUZANO", "loja_nome": "Suzano"},
        {"nome_original": "GUILHERME SILVA", "loja": "042_SUZANO", "loja_nome": "Suzano"},
        {"nome_original": "JOCI", "loja": "042_SUZANO", "loja_nome": "Suzano"},
        {"nome_original": "JOCXY", "loja": "042_SUZANO", "loja_nome": "Suzano"},
        {"nome_original": "JOCY", "loja": "042_SUZANO", "loja_nome": "Suzano"},
        {"nome_original": "KAYLLAINE", "loja": "042_SUZANO", "loja_nome": "Suzano"},
        {"nome_original": "LARISSA", "loja": "042_SUZANO", "loja_nome": "Suzano"},
        {"nome_original": "NAN", "loja": "042_SUZANO", "loja_nome": "Suzano"},
        {"nome_original": "PIX", "loja": "042_SUZANO", "loja_nome": "Suzano"},
        {"nome_original": "ROGERIO", "loja": "042_SUZANO", "loja_nome": "Suzano"},
        {"nome_original": "ROGÉRIO", "loja": "042_SUZANO", "loja_nome": "Suzano"},
        {"nome_original": "SAMUEL", "loja": "042_SUZANO", "loja_nome": "Suzano"},
        {"nome_original": "TATI", "loja": "042_SUZANO", "loja_nome": "Suzano"},
        {"nome_original": "TATRY", "loja": "042_SUZANO", "loja_nome": "Suzano"},
        {"nome_original": "TATY", "loja": "042_SUZANO", "loja_nome": "Suzano"},
        {"nome_original": "WILLAM", "loja": "042_SUZANO", "loja_nome": "Suzano"},
        {"nome_original": "WILLIAM", "loja": "042_SUZANO", "loja_nome": "Suzano"},
        {"nome_original": "WILLIAN", "loja": "042_SUZANO", "loja_nome": "Suzano"},
        {"nome_original": "ZAINE", "loja": "042_SUZANO", "loja_nome": "Suzano"},
        
        # Suzano 2 (010)
        {"nome_original": "ADRIANA ANSELMO", "loja": "010_SUZANO2", "loja_nome": "Suzano 2"},
        {"nome_original": "CARLA CRISTINA", "loja": "010_SUZANO2", "loja_nome": "Suzano 2"},
        {"nome_original": "ERICA", "loja": "010_SUZANO2", "loja_nome": "Suzano 2"},
        {"nome_original": "ERIKA", "loja": "010_SUZANO2", "loja_nome": "Suzano 2"},
        {"nome_original": "ÉRIKA", "loja": "010_SUZANO2", "loja_nome": "Suzano 2"},
        {"nome_original": "FELIPE", "loja": "010_SUZANO2", "loja_nome": "Suzano 2"},
        {"nome_original": "FELIPE MIRANDA", "loja": "010_SUZANO2", "loja_nome": "Suzano 2"},
        {"nome_original": "FELIPE MIRANDFA", "loja": "010_SUZANO2", "loja_nome": "Suzano 2"},
        {"nome_original": "GARANTIA", "loja": "010_SUZANO2", "loja_nome": "Suzano 2"},
        {"nome_original": "JULIANA CERA", "loja": "010_SUZANO2", "loja_nome": "Suzano 2"},
        {"nome_original": "KAYLANE", "loja": "010_SUZANO2", "loja_nome": "Suzano 2"},
        {"nome_original": "MARIA", "loja": "010_SUZANO2", "loja_nome": "Suzano 2"},
        {"nome_original": "MARIA / GARANTIA", "loja": "010_SUZANO2", "loja_nome": "Suzano 2"},
        {"nome_original": "MARIA DE LOURDES", "loja": "010_SUZANO2", "loja_nome": "Suzano 2"},
        {"nome_original": "NAN", "loja": "010_SUZANO2", "loja_nome": "Suzano 2"},
        {"nome_original": "ROGÉRIO", "loja": "010_SUZANO2", "loja_nome": "Suzano 2"},
        {"nome_original": "SAMUEL", "loja": "010_SUZANO2", "loja_nome": "Suzano 2"},
        {"nome_original": "TATY", "loja": "010_SUZANO2", "loja_nome": "Suzano 2"},
        {"nome_original": "WEVILLY", "loja": "010_SUZANO2", "loja_nome": "Suzano 2"},
        {"nome_original": "WILLIAM", "loja": "010_SUZANO2", "loja_nome": "Suzano 2"},
        {"nome_original": "ZAINE", "loja": "010_SUZANO2", "loja_nome": "Suzano 2"}
    ]
    
    # Criar DataFrame
    df = pd.DataFrame(vendedores_supabase)
    
    # Adicionar colunas para preenchimento
    df['nome_padronizado'] = ''  # Para você preencher
    df['manter'] = 'SIM'  # SIM/NÃO - Para você decidir se mantém o vendedor
    df['observacoes'] = ''  # Campo livre para observações
    
    # Reordenar colunas
    df = df[['nome_original', 'loja', 'loja_nome', 'nome_padronizado', 'manter', 'observacoes']]
    
    # Remover duplicatas
    df = df.drop_duplicates()
    
    # Ordenar por loja e nome
    df = df.sort_values(['loja', 'nome_original']).reset_index(drop=True)
    
    # Salvar como CSV
    nome_arquivo_csv = "PADRONIZACAO_VENDEDORES.csv"
    df.to_csv(nome_arquivo_csv, index=False, encoding='utf-8-sig')
    
    # Salvar como Excel para melhor edição
    nome_arquivo_excel = "PADRONIZACAO_VENDEDORES.xlsx"
    df.to_excel(nome_arquivo_excel, index=False, engine='openpyxl')
    
    print(f"📄 Arquivos criados:")
    print(f"   CSV: {nome_arquivo_csv}")
    print(f"   Excel: {nome_arquivo_excel}")
    
    print(f"\n📊 ESTATÍSTICAS:")
    print(f"   Total de vendedores únicos: {len(df)}")
    print(f"   Por loja:")
    for loja in df['loja'].unique():
        count = len(df[df['loja'] == loja])
        loja_nome = df[df['loja'] == loja]['loja_nome'].iloc[0]
        print(f"      {loja_nome}: {count} vendedores")
    
    print(f"\n📋 INSTRUÇÕES:")
    print(f"1. Abra o arquivo {nome_arquivo_excel}")
    print(f"2. Preencha a coluna 'nome_padronizado' com o nome correto")
    print(f"3. Na coluna 'manter' coloque SIM ou NÃO")
    print(f"4. Use 'observacoes' para comentários adicionais")
    print(f"5. Salve o arquivo e me informe quando estiver pronto")
    
    print(f"\n💡 DICAS:")
    print(f"   • Use nomes padronizados como: BETH, FELIPE, LARISSA, etc.")
    print(f"   • Para GARANTIA, NAN, PIX - coloque NÃO em 'manter'")
    print(f"   • Unifique variações: ROGERIO/ROGÉRIO = ROGÉRIO")
    print(f"   • Para nomes compostos use: TATY/ERIKA = TATY")

if __name__ == "__main__":
    main()