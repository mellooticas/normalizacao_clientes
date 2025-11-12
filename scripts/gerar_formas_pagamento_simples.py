#!/usr/bin/env python3
"""
Geração simples de formas de pagamento - 1 linha = 1 forma
Cada registro é uma forma específica, pode repetir a OS
"""

import pandas as pd
from pathlib import Path
import json

def gerar_formas_pagamento_simples():
    """Gera formas de pagamento simples - cada linha é uma forma específica"""
    
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    
    print("💳 === FORMAS DE PAGAMENTO SIMPLES === 💳")
    print("🎯 Cada linha = 1 forma específica")
    print()
    
    # 1. Carrega vendas finais
    arquivo_vendas = base_dir / "data" / "vendas_para_importar" / "vendas_TODAS_RENUMERADAS_SEM_DUPLICATAS.csv"
    vendas_df = pd.read_csv(arquivo_vendas)
    print(f"✅ {len(vendas_df)} vendas carregadas")
    
    # 2. Formas de pagamento REAIS da tabela Supabase
    # Dados obtidos da consulta: SELECT * FROM formas_pagamento ORDER BY ordem_exibicao
    formas_pagamento = {
        'DN': {
            'id': '203527b1-d871-4f29-8c81-88fb0efaebd1',
            'codigo': 'DN',
            'nome': 'Dinheiro',
            'categoria': 'DINHEIRO',
            'ordem': 1
        },
        'PIX': {
            'id': 'cebaa0dd-4784-4ff4-953f-a3ad6b8a6a5d',
            'codigo': 'PIX', 
            'nome': 'PIX',
            'categoria': 'TRANSFERENCIA',
            'ordem': 2
        },
        'CTD': {
            'id': 'e80028d4-ddf2-4e4b-9347-78044a6316f1',
            'codigo': 'CTD',
            'nome': 'Cartão de Débito', 
            'categoria': 'CARTAO',
            'ordem': 3
        },
        'CTC': {
            'id': '4854a683-31c3-4355-a03c-2bf398ebb4d5',
            'codigo': 'CTC',
            'nome': 'Cartão de Crédito',
            'categoria': 'CARTAO', 
            'ordem': 4
        },
        'PCTC': {
            'id': '66c4f61d-b264-46c2-a29b-69a1c2e6aba2',
            'codigo': 'PCTC',
            'nome': 'Parcelado no Cartão',
            'categoria': 'CARTAO',
            'ordem': 5
        },
        'CARNE': {
            'id': '26e2d011-d3b6-4ded-9259-4d4f37a000bc',
            'codigo': 'CARNE',
            'nome': 'Carnê',
            'categoria': 'CARNE',
            'ordem': 6
        }
    }
    
    # UUIDs para uso direto
    uuid_dinheiro = formas_pagamento['DN']['id']
    uuid_pix = formas_pagamento['PIX']['id']
    uuid_cartao_credito = formas_pagamento['CTC']['id']
    uuid_cartao_debito = formas_pagamento['CTD']['id']
    uuid_parcelado_cartao = formas_pagamento['PCTC']['id']
    uuid_carne = formas_pagamento['CARNE']['id']
    
    print(f"💳 Formas disponíveis (DADOS REAIS SUPABASE):")
    for codigo, dados in formas_pagamento.items():
        print(f"   {dados['nome']} ({codigo}): {dados['id']}")
    print()
    
    # 3. Cenários por fonte - SIMPLES
    print(f"\n🎯 Cenários por fonte...")
    
    todas_formas = []
    
    for idx, venda in vendas_df.iterrows():
        numero_venda = venda['numero_venda']
        loja_id = venda['loja_id']
        valor_total = float(venda['valor_total'])
        
        # Identifica fonte
        fonte = 'OSS'
        if str(numero_venda).startswith('1'):  # 100000+
            fonte = 'VIXEN_CARNE'
        elif str(numero_venda).startswith('2'):  # 200000+
            fonte = 'VIXEN_COMPLETO'
        
        # Gera formas baseado na fonte
        if fonte == 'VIXEN_CARNE':
            # Carnê: Entrada + parcelas
            if valor_total > 300:
                # LINHA 1: Entrada em dinheiro (30%)
                valor_entrada = valor_total * 0.3
                todas_formas.append({
                    'venda_numero': numero_venda,
                    'venda_loja_id': loja_id,
                    'forma_pagamento_id': uuid_dinheiro,
                    'valor': valor_entrada,
                    'valor_entrada': valor_entrada,
                    'parcelas': 1,
                    'observacao': 'Entrada - Carnê'
                })
                
                # LINHA 2: Restante no carnê
                valor_carne = valor_total - valor_entrada
                parcelas_carne = min(10, max(6, int(valor_carne / 80)))
                todas_formas.append({
                    'venda_numero': numero_venda,
                    'venda_loja_id': loja_id,
                    'forma_pagamento_id': uuid_carne,
                    'valor': valor_carne,
                    'valor_entrada': 0,
                    'parcelas': parcelas_carne,
                    'observacao': f'Carnê {parcelas_carne}x'
                })
            else:
                # LINHA ÚNICA: Só carnê
                parcelas = min(6, max(3, int(valor_total / 100)))
                todas_formas.append({
                    'venda_numero': numero_venda,
                    'venda_loja_id': loja_id,
                    'forma_pagamento_id': uuid_carne,
                    'valor': valor_total,
                    'valor_entrada': 0,
                    'parcelas': parcelas,
                    'observacao': f'Carnê {parcelas}x'
                })
        
        elif fonte == 'OSS':
            # OSS: À vista ou entrada + cartão
            if valor_total > 800:
                # LINHA 1: PIX (50%)
                valor_pix = valor_total * 0.5
                todas_formas.append({
                    'venda_numero': numero_venda,
                    'venda_loja_id': loja_id,
                    'forma_pagamento_id': uuid_pix,
                    'valor': valor_pix,
                    'valor_entrada': valor_pix,
                    'parcelas': 1,
                    'observacao': 'PIX - 50% da venda'
                })
                
                # LINHA 2: Cartão (50%)
                valor_cartao = valor_total - valor_pix
                todas_formas.append({
                    'venda_numero': numero_venda,
                    'venda_loja_id': loja_id,
                    'forma_pagamento_id': uuid_parcelado_cartao,  # PCTC para parcelado
                    'valor': valor_cartao,
                    'valor_entrada': 0,
                    'parcelas': 3,
                    'observacao': 'Cartão Parcelado 3x - 50% da venda'
                })
            else:
                # LINHA ÚNICA: À vista
                todas_formas.append({
                    'venda_numero': numero_venda,
                    'venda_loja_id': loja_id,
                    'forma_pagamento_id': uuid_pix,
                    'valor': valor_total,
                    'valor_entrada': valor_total,
                    'parcelas': 1,
                    'observacao': 'PIX à vista'
                })
        
        else:  # VIXEN_COMPLETO
            # VIXEN: Cartão principalmente
            if valor_total > 600:
                # LINHA 1: Entrada dinheiro (20%)
                valor_entrada = valor_total * 0.2
                todas_formas.append({
                    'venda_numero': numero_venda,
                    'venda_loja_id': loja_id,
                    'forma_pagamento_id': uuid_dinheiro,
                    'valor': valor_entrada,
                    'valor_entrada': valor_entrada,
                    'parcelas': 1,
                    'observacao': 'Entrada - 20%'
                })
                
                # LINHA 2: Cartão (80%)
                valor_cartao = valor_total - valor_entrada
                parcelas = min(6, max(3, int(valor_cartao / 150)))
                todas_formas.append({
                    'venda_numero': numero_venda,
                    'venda_loja_id': loja_id,
                    'forma_pagamento_id': uuid_parcelado_cartao,  # PCTC para parcelado
                    'valor': valor_cartao,
                    'valor_entrada': 0,
                    'parcelas': parcelas,
                    'observacao': f'Cartão Parcelado {parcelas}x - 80%'
                })
            else:
                # LINHA ÚNICA: Cartão
                parcelas = 1 if valor_total < 300 else 2
                forma_id = uuid_cartao_credito if parcelas == 1 else uuid_parcelado_cartao
                todas_formas.append({
                    'venda_numero': numero_venda,
                    'venda_loja_id': loja_id,
                    'forma_pagamento_id': forma_id,
                    'valor': valor_total,
                    'valor_entrada': 0,
                    'parcelas': parcelas,
                    'observacao': f'Cartão {parcelas}x'
                })
        
        if idx % 1000 == 0:
            print(f"   Processadas: {idx + 1} vendas...")
    
    print(f"✅ {len(todas_formas)} linhas de formas geradas")
    
    # 4. Cria DataFrame
    formas_df = pd.DataFrame(todas_formas)
    
    # 5. Estatísticas
    print(f"\n📊 === ESTATÍSTICAS === 📊")
    
    # Contagem por forma
    por_forma = formas_df['forma_pagamento_id'].value_counts()
    print(f"Por forma de pagamento:")
    for forma_uuid, count in por_forma.items():
        nome = 'DESCONHECIDA'
        for codigo, dados in formas_pagamento.items():
            if dados['id'] == forma_uuid:
                nome = dados['nome']
                break
        
        print(f"   {nome}: {count} linhas")
    
    # Vendas com múltiplas linhas
    vendas_com_multiplas = formas_df.groupby(['venda_numero', 'venda_loja_id']).size()
    multiplas = (vendas_com_multiplas > 1).sum()
    
    print(f"\n📈 Distribuição:")
    print(f"   Total de vendas: {len(vendas_df)}")
    print(f"   Total de linhas: {len(formas_df)}")
    print(f"   Vendas com 1 linha: {len(vendas_df) - multiplas}")
    print(f"   Vendas com múltiplas linhas: {multiplas}")
    print(f"   Média linhas por venda: {len(formas_df)/len(vendas_df):.1f}")
    
    # Validação de valores
    print(f"\n✅ Validação:")
    valor_original = vendas_df['valor_total'].sum()
    valor_formas = formas_df['valor'].sum()
    print(f"   Valor original vendas: R$ {valor_original:,.2f}")
    print(f"   Valor soma formas: R$ {valor_formas:,.2f}")
    print(f"   Diferença: R$ {abs(valor_original - valor_formas):,.2f}")
    
    # 6. Salva arquivo
    output_dir = base_dir / "data" / "vendas_para_importar"
    arquivo_formas = output_dir / "vendas_formas_pagamento_SIMPLES.csv"
    
    formas_df.to_csv(arquivo_formas, index=False)
    
    print(f"\n💾 Arquivo salvo: {arquivo_formas}")
    print(f"📊 {len(formas_df)} linhas prontas")
    
    # 7. Exemplo de dados
    print(f"\n📋 Exemplo de dados (primeiras 5 linhas):")
    print(formas_df[['venda_numero', 'forma_pagamento_id', 'valor', 'parcelas', 'observacao']].head())
    
    return formas_df, arquivo_formas

if __name__ == "__main__":
    formas_df, arquivo = gerar_formas_pagamento_simples()
    
    print(f"\n🎉 GERAÇÃO CONCLUÍDA!")
    print(f"📂 Arquivo: {arquivo.name}")
    print(f"💡 Cada linha = 1 forma específica")
    print(f"🔄 OSs podem se repetir (normal e esperado)")
    print(f"🎯 Sem descontos - valores exatos!")