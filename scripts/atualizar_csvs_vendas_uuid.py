#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Atualização dos CSVs de vendas com UUIDs das formas de pagamento
"""

import pandas as pd
import os
import json
from datetime import datetime

def atualizar_formas_pagamento_csv():
    """Atualiza os CSVs de vendas adicionando UUIDs das formas de pagamento"""
    
    print("🔄 ATUALIZANDO CSVs COM UUIDs DAS FORMAS DE PAGAMENTO")
    print("=" * 60)
    
    # Mapeamento baseado nos dados do banco vendas.formas_pagamento
    mapeamento_formas = {
        # Formas principais (maiúsculas)
        'CTC': '4854a683-31c3-4355-a03c-2bf398ebb4d5',      # Cartão de Crédito
        'CTD': 'e80028d4-ddf2-4e4b-9347-78044a6316f1',      # Cartão de Débito
        'PIX': 'cebaa0dd-4784-4ff4-953f-a3ad6b8a6a5d',      # PIX
        'DN': '203527b1-d871-4f29-8c81-88fb0efaebd1',       # Dinheiro
        'PCTC': '66c4f61d-b264-46c2-a29b-69a1c2e6aba2',     # Parcelado no Cartão
        'SS': 'b36056fa-47df-4f7a-b0e0-cda6a1bb5073',       # Sem Sinal
        'GARANTIA': '9c8ce174-8212-41f7-a637-980f581c8ca9',  # Garantia (Sem Custo)
        'CARNE': '26e2d011-d3b6-4ded-9259-4d4f37a000bc',    # Carnê
        'TROCA': '19d5c0b9-21c0-4f57-954e-3c6d0b3f108c',    # Troca
        
        # Variações minúsculas (normalizar para as principais)
        'ctc': '4854a683-31c3-4355-a03c-2bf398ebb4d5',      # → CTC
        'ctd': 'e80028d4-ddf2-4e4b-9347-78044a6316f1',      # → CTD
        'pix': 'cebaa0dd-4784-4ff4-953f-a3ad6b8a6a5d',      # → PIX
        'dn': '203527b1-d871-4f29-8c81-88fb0efaebd1',       # → DN
        'pctc': '66c4f61d-b264-46c2-a29b-69a1c2e6aba2',     # → PCTC
        'ss': 'b36056fa-47df-4f7a-b0e0-cda6a1bb5073',       # → SS
        
        # Variações de capitalização
        'Pix': 'cebaa0dd-4784-4ff4-953f-a3ad6b8a6a5d',      # → PIX
        'Dn': '203527b1-d871-4f29-8c81-88fb0efaebd1',       # → DN
        'Garantia': '9c8ce174-8212-41f7-a637-980f581c8ca9',  # → GARANTIA
        
        # Formas especiais/combinadas
        'CTD/PCTC': 'e80028d4-ddf2-4e4b-9347-78044a6316f1', # → CTD (considerando principal)
        'PERMUTA': '19d5c0b9-21c0-4f57-954e-3c6d0b3f108c',  # → TROCA (similar)
        
        # Valores inválidos/headers
        'Forma de Pgto': None,  # Header da planilha
        'SEM_INFORMACAO': None,  # Valores nulos
        'Coluna3': None,         # Erro de planilha
        '*': None                # Valor inválido
    }
    
    # Definir pastas
    pasta_vendas = r"d:\projetos\carne_facil\carne_facil\data\originais\cxs\extraidos_por_tipo\vendas"
    pasta_backup = os.path.join(pasta_vendas, "backup_antes_uuid")
    pasta_analises = r"d:\projetos\carne_facil\carne_facil\_analises"
    
    # Criar pasta de backup
    os.makedirs(pasta_backup, exist_ok=True)
    os.makedirs(pasta_analises, exist_ok=True)
    
    print(f"📁 Pasta de origem: {pasta_vendas}")
    print(f"💾 Backup será salvo em: {pasta_backup}")
    print()
    
    # Processar arquivo consolidado
    arquivo_consolidado = os.path.join(pasta_vendas, "vendas_todas_lojas.csv")
    
    if not os.path.exists(arquivo_consolidado):
        print("❌ Arquivo consolidado não encontrado!")
        return
    
    print("📊 Processando arquivo consolidado...")
    
    # Fazer backup
    backup_consolidado = os.path.join(pasta_backup, "vendas_todas_lojas_original.csv")
    
    # Ler dados
    df = pd.read_csv(arquivo_consolidado)
    original_count = len(df)
    
    # Fazer backup se não existir
    if not os.path.exists(backup_consolidado):
        df.to_csv(backup_consolidado, index=False)
        print(f"✅ Backup criado: {backup_consolidado}")
    
    # Limpar e normalizar formas de pagamento
    df['forma_de_pgto'] = df['forma_de_pgto'].fillna('SEM_INFORMACAO').astype(str).str.strip()
    
    # Adicionar nova coluna de UUID
    df['forma_pagamento_uuid'] = df['forma_de_pgto'].map(mapeamento_formas)
    
    # Normalizar para forma padrão (maiúscula)
    def normalizar_forma(forma):
        if forma in mapeamento_formas:
            # Encontrar a forma padrão correspondente ao UUID
            uuid_forma = mapeamento_formas[forma]
            if uuid_forma is None:
                return None
            
            # Mapear UUID para forma padrão
            for forma_padrao, uuid_padrao in mapeamento_formas.items():
                if uuid_padrao == uuid_forma and forma_padrao.isupper():
                    return forma_padrao
        return forma
    
    df['forma_pagamento_normalizada'] = df['forma_de_pgto'].apply(normalizar_forma)
    
    # Estatísticas de mapeamento
    print("\n📈 ESTATÍSTICAS DE MAPEAMENTO:")
    print("-" * 40)
    
    total_registros = len(df)
    com_uuid = df['forma_pagamento_uuid'].notna().sum()
    sem_uuid = total_registros - com_uuid
    
    print(f"📊 Total de registros: {total_registros:,}")
    print(f"✅ Com UUID mapeado: {com_uuid:,} ({(com_uuid/total_registros)*100:.1f}%)")
    print(f"❌ Sem UUID: {sem_uuid:,} ({(sem_uuid/total_registros)*100:.1f}%)")
    
    # Mostrar formas não mapeadas
    formas_sem_uuid = df[df['forma_pagamento_uuid'].isna()]['forma_de_pgto'].value_counts()
    if len(formas_sem_uuid) > 0:
        print(f"\n⚠️  FORMAS SEM UUID ({len(formas_sem_uuid)} tipos):")
        for forma, count in formas_sem_uuid.items():
            print(f"   {forma}: {count:,} registros")
    
    # Mostrar distribuição de UUIDs
    print(f"\n📋 DISTRIBUIÇÃO POR FORMA DE PAGAMENTO:")
    print("-" * 50)
    distribuicao = df.groupby(['forma_pagamento_normalizada', 'forma_pagamento_uuid']).size().reset_index(name='quantidade')
    distribuicao = distribuicao.sort_values('quantidade', ascending=False)
    
    for _, row in distribuicao.iterrows():
        forma = row['forma_pagamento_normalizada'] or "SEM_MAPEAMENTO"
        uuid = row['forma_pagamento_uuid'] or "N/A"
        count = row['quantidade']
        print(f"{forma:<15} | {uuid:<36} | {count:>6,}")
    
    # Salvar arquivo atualizado
    df.to_csv(arquivo_consolidado, index=False)
    print(f"\n✅ Arquivo consolidado atualizado com UUID!")
    
    # Processar arquivos individuais por loja
    print(f"\n🏪 PROCESSANDO ARQUIVOS INDIVIDUAIS POR LOJA:")
    print("-" * 50)
    
    arquivos_loja = [f for f in os.listdir(pasta_vendas) if f.startswith('vendas_') and f.endswith('.csv') and f != 'vendas_todas_lojas.csv']
    
    for arquivo in arquivos_loja:
        caminho_arquivo = os.path.join(pasta_vendas, arquivo)
        caminho_backup = os.path.join(pasta_backup, f"{arquivo.replace('.csv', '_original.csv')}")
        
        print(f"📄 Processando: {arquivo}")
        
        # Ler dados da loja
        df_loja = pd.read_csv(caminho_arquivo)
        
        # Fazer backup se não existir
        if not os.path.exists(caminho_backup):
            df_loja.to_csv(caminho_backup, index=False)
        
        # Aplicar mesmas transformações
        df_loja['forma_de_pgto'] = df_loja['forma_de_pgto'].fillna('SEM_INFORMACAO').astype(str).str.strip()
        df_loja['forma_pagamento_uuid'] = df_loja['forma_de_pgto'].map(mapeamento_formas)
        df_loja['forma_pagamento_normalizada'] = df_loja['forma_de_pgto'].apply(normalizar_forma)
        
        # Salvar arquivo atualizado
        df_loja.to_csv(caminho_arquivo, index=False)
        
        # Estatísticas da loja
        com_uuid_loja = df_loja['forma_pagamento_uuid'].notna().sum()
        total_loja = len(df_loja)
        print(f"   ✅ {com_uuid_loja:,}/{total_loja:,} registros com UUID ({(com_uuid_loja/total_loja)*100:.1f}%)")
    
    # Salvar relatório de mapeamento
    relatorio_mapeamento = {
        'timestamp': datetime.now().isoformat(),
        'total_registros_processados': total_registros,
        'registros_com_uuid': int(com_uuid),
        'registros_sem_uuid': int(sem_uuid),
        'percentual_mapeado': round((com_uuid/total_registros)*100, 2),
        'mapeamento_formas': mapeamento_formas,
        'distribuicao_final': distribuicao.to_dict('records'),
        'formas_nao_mapeadas': formas_sem_uuid.to_dict() if len(formas_sem_uuid) > 0 else {},
        'arquivos_processados': [arquivo_consolidado] + [os.path.join(pasta_vendas, arq) for arq in arquivos_loja]
    }
    
    caminho_relatorio = os.path.join(pasta_analises, "mapeamento_formas_pagamento_uuid.json")
    with open(caminho_relatorio, 'w', encoding='utf-8') as f:
        json.dump(relatorio_mapeamento, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Relatório salvo em: {caminho_relatorio}")
    print(f"\n🎉 ATUALIZAÇÃO CONCLUÍDA!")
    print(f"✅ {com_uuid:,} registros mapeados com UUID")
    print(f"✅ {len(arquivos_loja) + 1} arquivos atualizados")
    print(f"✅ Backups salvos em: {pasta_backup}")

if __name__ == "__main__":
    atualizar_formas_pagamento_csv()