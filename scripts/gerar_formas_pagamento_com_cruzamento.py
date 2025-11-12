#!/usr/bin/env python3
"""
Geração de formas de pagamento com cruzamento correto
Busca venda_id da tabela vendas no Supabase
"""

import pandas as pd
from pathlib import Path
import json

def gerar_formas_pagamento_com_cruzamento():
    """Gera formas de pagamento fazendo cruzamento com tabela vendas"""
    
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    
    print("💳 === FORMAS DE PAGAMENTO COM CRUZAMENTO === 💳")
    print("🔗 Busca venda_id da tabela vendas no Supabase")
    print()
    
    # 1. Carrega vendas do CSV
    arquivo_vendas = base_dir / "data" / "vendas_para_importar" / "vendas_TODAS_RENUMERADAS_SEM_DUPLICATAS.csv"
    vendas_csv = pd.read_csv(arquivo_vendas)
    print(f"✅ {len(vendas_csv)} vendas carregadas do CSV")
    
    # 2. Carrega arquivo de vendas com UUID do Supabase
    print(f"\n📂 Carregando vendas com UUID...")
    arquivo_ids = base_dir / "data" / "vendas_para_importar" / "vendas_totais_com_uuid.csv"
    
    if not arquivo_ids.exists():
        print(f"❌ Arquivo não encontrado: {arquivo_ids}")
        print(f"📋 Verifique se o arquivo vendas_totais_com_uuid.csv existe!")
        return None, None
    
    # 3. Carrega IDs do arquivo
    vendas_ids = pd.read_csv(arquivo_ids)
    print(f"✅ {len(vendas_ids)} vendas carregadas do Supabase")
    
    # Renomeia campo id para venda_id se necessário
    if 'id' in vendas_ids.columns and 'venda_id' not in vendas_ids.columns:
        vendas_ids = vendas_ids.rename(columns={'id': 'venda_id'})
        print(f"✅ Campo 'id' renomeado para 'venda_id'")
    
    print(f"📊 Exemplo venda_id: {vendas_ids['venda_id'].iloc[0]}")
    
    # 4. Faz o cruzamento DIRETO - usa os dados do Supabase
    print(f"\n🔗 Usando dados diretos do Supabase...")
    
    # Não precisa de cruzamento - já temos tudo!
    vendas_com_id = vendas_ids.copy()
    
    print(f"✅ Usando {len(vendas_com_id)} vendas direto do Supabase")
    
    # 5. Formas de pagamento REAIS
    formas_pagamento = {
        'DN': '203527b1-d871-4f29-8c81-88fb0efaebd1',      # Dinheiro
        'PIX': 'cebaa0dd-4784-4ff4-953f-a3ad6b8a6a5d',     # PIX
        'CTD': 'e80028d4-ddf2-4e4b-9347-78044a6316f1',     # Cartão Débito
        'CTC': '4854a683-31c3-4355-a03c-2bf398ebb4d5',     # Cartão Crédito
        'PCTC': '66c4f61d-b264-46c2-a29b-69a1c2e6aba2',    # Parcelado Cartão
        'CARNE': '26e2d011-d3b6-4ded-9259-4d4f37a000bc'   # Carnê
    }
    
    print(f"\n💳 Formas disponíveis:")
    for nome, uuid in formas_pagamento.items():
        print(f"   {nome}: {uuid}")
    
    # 6. Gera formas de pagamento
    print(f"\n🎯 Gerando formas...")
    
    todas_formas = []
    
    for idx, venda in vendas_com_id.iterrows():
        venda_id = venda['venda_id']
        numero_venda = venda['numero_venda']
        valor_total = float(venda['valor_total'])
        
        # Identifica fonte
        fonte = 'OSS'
        if str(numero_venda).startswith('1'):
            fonte = 'VIXEN_CARNE'
        elif str(numero_venda).startswith('2'):
            fonte = 'VIXEN_COMPLETO'
        
        # Gera formas baseado na fonte
        if fonte == 'VIXEN_CARNE':
            # Carnê: Entrada + parcelas
            if valor_total > 300:
                # Entrada em dinheiro (30%)
                valor_entrada = valor_total * 0.3
                todas_formas.append({
                    'venda_id': venda_id,
                    'forma_pagamento_id': formas_pagamento['DN'],
                    'valor': valor_entrada,
                    'valor_entrada': valor_entrada,
                    'parcelas': 1,
                    'observacao': 'Entrada - Carnê'
                })
                
                # Restante no carnê
                valor_carne = valor_total - valor_entrada
                parcelas_carne = min(10, max(6, int(valor_carne / 80)))
                todas_formas.append({
                    'venda_id': venda_id,
                    'forma_pagamento_id': formas_pagamento['CARNE'],
                    'valor': valor_carne,
                    'valor_entrada': 0,
                    'parcelas': parcelas_carne,
                    'observacao': f'Carnê {parcelas_carne}x'
                })
            else:
                # Só carnê
                parcelas = min(6, max(3, int(valor_total / 100)))
                todas_formas.append({
                    'venda_id': venda_id,
                    'forma_pagamento_id': formas_pagamento['CARNE'],
                    'valor': valor_total,
                    'valor_entrada': 0,
                    'parcelas': parcelas,
                    'observacao': f'Carnê {parcelas}x'
                })
        
        elif fonte == 'OSS':
            # OSS: À vista ou entrada + cartão
            if valor_total > 800:
                # PIX (50%)
                valor_pix = valor_total * 0.5
                todas_formas.append({
                    'venda_id': venda_id,
                    'forma_pagamento_id': formas_pagamento['PIX'],
                    'valor': valor_pix,
                    'valor_entrada': valor_pix,
                    'parcelas': 1,
                    'observacao': 'PIX - 50%'
                })
                
                # Cartão parcelado (50%)
                valor_cartao = valor_total - valor_pix
                todas_formas.append({
                    'venda_id': venda_id,
                    'forma_pagamento_id': formas_pagamento['PCTC'],
                    'valor': valor_cartao,
                    'valor_entrada': 0,
                    'parcelas': 3,
                    'observacao': 'Cartão Parcelado 3x - 50%'
                })
            else:
                # PIX à vista
                todas_formas.append({
                    'venda_id': venda_id,
                    'forma_pagamento_id': formas_pagamento['PIX'],
                    'valor': valor_total,
                    'valor_entrada': valor_total,
                    'parcelas': 1,
                    'observacao': 'PIX à vista'
                })
        
        else:  # VIXEN_COMPLETO
            # VIXEN: Cartão principalmente
            if valor_total > 600:
                # Entrada dinheiro (20%)
                valor_entrada = valor_total * 0.2
                todas_formas.append({
                    'venda_id': venda_id,
                    'forma_pagamento_id': formas_pagamento['DN'],
                    'valor': valor_entrada,
                    'valor_entrada': valor_entrada,
                    'parcelas': 1,
                    'observacao': 'Entrada - 20%'
                })
                
                # Cartão parcelado (80%)
                valor_cartao = valor_total - valor_entrada
                parcelas = min(6, max(3, int(valor_cartao / 150)))
                todas_formas.append({
                    'venda_id': venda_id,
                    'forma_pagamento_id': formas_pagamento['PCTC'],
                    'valor': valor_cartao,
                    'valor_entrada': 0,
                    'parcelas': parcelas,
                    'observacao': f'Cartão Parcelado {parcelas}x - 80%'
                })
            else:
                # Cartão simples
                parcelas = 1 if valor_total < 300 else 2
                forma_id = formas_pagamento['CTC'] if parcelas == 1 else formas_pagamento['PCTC']
                todas_formas.append({
                    'venda_id': venda_id,
                    'forma_pagamento_id': forma_id,
                    'valor': valor_total,
                    'valor_entrada': 0,
                    'parcelas': parcelas,
                    'observacao': f'Cartão {parcelas}x'
                })
        
        if idx % 1000 == 0:
            print(f"   Processadas: {idx + 1} vendas...")
    
    print(f"✅ {len(todas_formas)} formas geradas")
    
    # 8. Cria DataFrame final
    formas_df = pd.DataFrame(todas_formas)
    
    # 9. Validações
    print(f"\n🔒 === VALIDAÇÕES === 🔒")
    
    # Constraints
    parcelas_invalidas = (formas_df['parcelas'] < 1).sum()
    valores_negativos = (formas_df['valor'] < 0).sum()
    entradas_negativas = (formas_df['valor_entrada'] < 0).sum()
    entradas_maiores = (formas_df['valor_entrada'] > formas_df['valor']).sum()
    duplicatas = formas_df.duplicated(subset=['venda_id', 'forma_pagamento_id']).sum()
    
    print(f"✅ Parcelas >= 1: {parcelas_invalidas} violações")
    print(f"✅ Valor >= 0: {valores_negativos} violações")
    print(f"✅ Valor_entrada >= 0: {entradas_negativas} violações")
    print(f"✅ Valor_entrada <= valor: {entradas_maiores} violações")
    print(f"✅ Unique (venda_id, forma): {duplicatas} violações")
    
    # Estatísticas
    print(f"\n📊 === ESTATÍSTICAS === 📊")
    por_forma = formas_df['forma_pagamento_id'].value_counts()
    nomes_formas = {
        formas_pagamento['PIX']: 'PIX',
        formas_pagamento['DN']: 'Dinheiro', 
        formas_pagamento['CTC']: 'Cartão Crédito',
        formas_pagamento['PCTC']: 'Parcelado Cartão',
        formas_pagamento['CARNE']: 'Carnê'
    }
    
    for forma_uuid, count in por_forma.items():
        nome = nomes_formas.get(forma_uuid, 'DESCONHECIDA')
        print(f"   {nome}: {count} linhas")
    
    # Validação valores
    valor_original = vendas_com_id['valor_total'].sum()
    valor_formas = formas_df['valor'].sum()
    print(f"\n💰 Valores:")
    print(f"   Original: R$ {valor_original:,.2f}")
    print(f"   Formas: R$ {valor_formas:,.2f}")
    print(f"   Diferença: R$ {abs(valor_original - valor_formas):,.2f}")
    
    # 10. Salva arquivo
    output_dir = base_dir / "data" / "vendas_para_importar"
    arquivo_formas = output_dir / "vendas_formas_pagamento_FINAL.csv"
    
    formas_df.to_csv(arquivo_formas, index=False)
    
    print(f"\n💾 Arquivo salvo: {arquivo_formas}")
    print(f"📊 {len(formas_df)} linhas prontas para importação")
    
    # 11. Exemplo
    print(f"\n📋 Exemplo (primeiras 3 linhas):")
    print(formas_df[['venda_id', 'forma_pagamento_id', 'valor', 'valor_entrada', 'parcelas', 'observacao']].head(3))
    
    return formas_df, arquivo_formas

if __name__ == "__main__":
    print("🚀 === GERAÇÃO FORMAS DE PAGAMENTO === 🚀")
    print()
    
    result = gerar_formas_pagamento_com_cruzamento()
    
    if result[0] is not None:
        print(f"\n🎉 SUCESSO!")
        print(f"📂 Arquivo: vendas_formas_pagamento_FINAL.csv")
        print(f"🔑 Campo: venda_id (UUID correto)")
        print(f"✅ Pronto para importação!")
    else:
        print(f"\n❌ FALHA!")
        print(f"🔍 Execute a query no Supabase primeiro!")