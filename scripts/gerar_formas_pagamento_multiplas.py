#!/usr/bin/env python3
"""
Geração inteligente de formas de pagamento com múltiplas formas por venda
Inclui cenários realistas de entrada + parcelas com descontos específicos
"""

import pandas as pd
from pathlib import Path
import json
import random

def gerar_formas_pagamento_multiplas():
    """Gera formas de pagamento realistas com múltiplas formas por venda"""
    
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    
    print("💳 === FORMAS DE PAGAMENTO MÚLTIPLAS === 💳")
    print()
    
    # 1. Carrega vendas finais
    arquivo_vendas = base_dir / "data" / "vendas_para_importar" / "vendas_TODAS_RENUMERADAS_SEM_DUPLICATAS.csv"
    vendas_df = pd.read_csv(arquivo_vendas)
    print(f"✅ {len(vendas_df)} vendas carregadas")
    
    # 2. Carrega formas de pagamento disponíveis
    arquivo_formas = base_dir / "_analises" / "mapeamento_formas_pagamento_uuid.json"
    with open(arquivo_formas, 'r', encoding='utf-8') as f:
        dados_formas = json.load(f)
    
    formas_pagamento = dados_formas['mapeamento_formas']
    
    # UUIDs principais
    uuid_dinheiro = formas_pagamento.get('DN', '203527b1-d871-4f29-8c81-88fb0efaebd1')
    uuid_pix = formas_pagamento.get('PIX', 'cebaa0dd-4784-4ff4-953f-a3ad6b8a6a5d')
    uuid_cartao_credito = formas_pagamento.get('CTC', '4854a683-31c3-4355-a03c-2bf398ebb4d5')
    uuid_cartao_debito = formas_pagamento.get('CTD', 'e80028d4-ddf2-4e4b-9347-78044a6316f1')
    uuid_carne = formas_pagamento.get('CARNE', '26e2d011-d3b6-4ded-9259-4d4f37a000bc')
    
    print(f"💳 Formas disponíveis:")
    print(f"   Dinheiro: {uuid_dinheiro}")
    print(f"   PIX: {uuid_pix}")
    print(f"   Cartão Crédito: {uuid_cartao_credito}")
    print(f"   Cartão Débito: {uuid_cartao_debito}")
    print(f"   Carnê: {uuid_carne}")
    
    # 3. Define cenários de pagamento por faixa de valor
    print(f"\n🎯 Definindo cenários por faixa de valor...")
    
    def gerar_formas_por_venda(venda):
        """Gera formas de pagamento realistas para uma venda"""
        
        valor_total = float(venda['valor_total'])
        numero_venda = venda['numero_venda']
        loja_id = venda['loja_id']
        
        formas_venda = []
        
        # Identifica fonte para aplicar estratégia
        fonte = 'OSS'
        if str(numero_venda).startswith('1'):  # 100000+
            fonte = 'VIXEN_CARNE'
        elif str(numero_venda).startswith('2'):  # 200000+
            fonte = 'VIXEN_COMPLETO'
        
        # Estratégias por faixa de valor e fonte
        if fonte == 'VIXEN_CARNE':
            # Vendas carnê - sempre entrada + carnê
            if valor_total > 500:
                # Entrada 20-30% + restante no carnê
                percentual_entrada = random.uniform(0.20, 0.30)
                valor_entrada = valor_total * percentual_entrada
                valor_carne = valor_total - valor_entrada
                
                # Entrada em dinheiro/PIX (desconto 3%)
                desconto_entrada = valor_entrada * 0.03
                valor_entrada_liquido = valor_entrada - desconto_entrada
                
                # Forma 1: Entrada
                formas_venda.append({
                    'venda_numero': numero_venda,
                    'venda_loja_id': loja_id,
                    'forma_pagamento_id': uuid_pix,
                    'valor': valor_entrada,
                    'valor_liquido': valor_entrada_liquido,
                    'desconto': desconto_entrada,
                    'valor_entrada': valor_entrada,
                    'parcelas': 1,
                    'observacao': f'Entrada PIX com desconto 3% (R$ {desconto_entrada:.2f})'
                })
                
                # Forma 2: Carnê
                parcelas_carne = min(12, max(6, int(valor_carne / 80)))
                formas_venda.append({
                    'venda_numero': numero_venda,
                    'venda_loja_id': loja_id,
                    'forma_pagamento_id': uuid_carne,
                    'valor': valor_carne,
                    'valor_liquido': valor_carne,  # Sem desconto no carnê
                    'desconto': 0,
                    'valor_entrada': 0,
                    'parcelas': parcelas_carne,
                    'observacao': f'Carnê {parcelas_carne}x de R$ {valor_carne/parcelas_carne:.2f}'
                })
            else:
                # Valor baixo - só carnê
                parcelas = min(8, max(4, int(valor_total / 100)))
                formas_venda.append({
                    'venda_numero': numero_venda,
                    'venda_loja_id': loja_id,
                    'forma_pagamento_id': uuid_carne,
                    'valor': valor_total,
                    'valor_liquido': valor_total,
                    'desconto': 0,
                    'valor_entrada': 0,
                    'parcelas': parcelas,
                    'observacao': f'Carnê {parcelas}x de R$ {valor_total/parcelas:.2f}'
                })
        
        elif fonte == 'OSS':
            # Vendas OSS - mix de formas
            if valor_total > 1000:
                # Vendas altas - 50% PIX + 50% cartão
                valor_pix = valor_total * 0.5
                valor_cartao = valor_total * 0.5
                
                # PIX com desconto 5%
                desconto_pix = valor_pix * 0.05
                valor_pix_liquido = valor_pix - desconto_pix
                
                formas_venda.extend([
                    {
                        'venda_numero': numero_venda,
                        'venda_loja_id': loja_id,
                        'forma_pagamento_id': uuid_pix,
                        'valor': valor_pix,
                        'valor_liquido': valor_pix_liquido,
                        'desconto': desconto_pix,
                        'valor_entrada': valor_pix,
                        'parcelas': 1,
                        'observacao': f'PIX 50% com desconto 5% (R$ {desconto_pix:.2f})'
                    },
                    {
                        'venda_numero': numero_venda,
                        'venda_loja_id': loja_id,
                        'forma_pagamento_id': uuid_cartao_credito,
                        'valor': valor_cartao,
                        'valor_liquido': valor_cartao,
                        'desconto': 0,
                        'valor_entrada': 0,
                        'parcelas': 3,
                        'observacao': f'Cartão Crédito 3x de R$ {valor_cartao/3:.2f}'
                    }
                ])
            else:
                # Vendas médias - à vista com desconto
                if random.random() < 0.7:  # 70% à vista
                    forma_pagamento = uuid_pix if random.random() < 0.6 else uuid_dinheiro
                    desconto = valor_total * 0.03  # 3% desconto à vista
                    valor_liquido = valor_total - desconto
                    
                    formas_venda.append({
                        'venda_numero': numero_venda,
                        'venda_loja_id': loja_id,
                        'forma_pagamento_id': forma_pagamento,
                        'valor': valor_total,
                        'valor_liquido': valor_liquido,
                        'desconto': desconto,
                        'valor_entrada': valor_total,
                        'parcelas': 1,
                        'observacao': f'À vista com desconto 3% (R$ {desconto:.2f})'
                    })
                else:
                    # 30% parcelado
                    parcelas = 2 if valor_total < 500 else 3
                    formas_venda.append({
                        'venda_numero': numero_venda,
                        'venda_loja_id': loja_id,
                        'forma_pagamento_id': uuid_cartao_credito,
                        'valor': valor_total,
                        'valor_liquido': valor_total,
                        'desconto': 0,
                        'valor_entrada': 0,
                        'parcelas': parcelas,
                        'observacao': f'Cartão {parcelas}x de R$ {valor_total/parcelas:.2f}'
                    })
        
        else:  # VIXEN_COMPLETO
            # Outros pagamentos - principalmente cartão
            if valor_total > 800:
                # Entrada + cartão
                valor_entrada = valor_total * 0.3
                valor_cartao = valor_total * 0.7
                
                formas_venda.extend([
                    {
                        'venda_numero': numero_venda,
                        'venda_loja_id': loja_id,
                        'forma_pagamento_id': uuid_dinheiro,
                        'valor': valor_entrada,
                        'valor_liquido': valor_entrada,
                        'desconto': 0,
                        'valor_entrada': valor_entrada,
                        'parcelas': 1,
                        'observacao': 'Entrada em dinheiro'
                    },
                    {
                        'venda_numero': numero_venda,
                        'venda_loja_id': loja_id,
                        'forma_pagamento_id': uuid_cartao_credito,
                        'valor': valor_cartao,
                        'valor_liquido': valor_cartao,
                        'desconto': 0,
                        'valor_entrada': 0,
                        'parcelas': 6,
                        'observacao': f'Cartão 6x de R$ {valor_cartao/6:.2f}'
                    }
                ])
            else:
                # Só cartão
                parcelas = 1 if valor_total < 300 else (2 if valor_total < 600 else 3)
                formas_venda.append({
                    'venda_numero': numero_venda,
                    'venda_loja_id': loja_id,
                    'forma_pagamento_id': uuid_cartao_credito,
                    'valor': valor_total,
                    'valor_liquido': valor_total,
                    'desconto': 0,
                    'valor_entrada': 0,
                    'parcelas': parcelas,
                    'observacao': f'Cartão {parcelas}x de R$ {valor_total/parcelas:.2f}' if parcelas > 1 else 'Cartão à vista'
                })
        
        return formas_venda
    
    # 4. Gera formas para todas as vendas
    print(f"\n🔧 Gerando formas múltiplas...")
    
    todas_formas = []
    vendas_multiplas = 0
    
    for idx, venda in vendas_df.iterrows():
        formas_venda = gerar_formas_por_venda(venda)
        todas_formas.extend(formas_venda)
        
        if len(formas_venda) > 1:
            vendas_multiplas += 1
        
        if idx % 1000 == 0:
            print(f"   Processadas: {idx + 1} vendas...")
    
    print(f"✅ {len(todas_formas)} registros de formas gerados")
    print(f"📊 {vendas_multiplas} vendas com múltiplas formas")
    print(f"📈 Média: {len(todas_formas)/len(vendas_df):.1f} formas por venda")
    
    # 5. Cria DataFrame
    formas_df = pd.DataFrame(todas_formas)
    
    # 6. Estatísticas
    print(f"\n📊 === ESTATÍSTICAS === 📊")
    
    # Por forma de pagamento
    por_forma = formas_df['forma_pagamento_id'].value_counts()
    print(f"Por forma de pagamento:")
    for forma_uuid, count in por_forma.items():
        nome = 'DESCONHECIDA'
        if forma_uuid == uuid_pix:
            nome = 'PIX'
        elif forma_uuid == uuid_dinheiro:
            nome = 'DINHEIRO'
        elif forma_uuid == uuid_cartao_credito:
            nome = 'CARTÃO CRÉDITO'
        elif forma_uuid == uuid_cartao_debito:
            nome = 'CARTÃO DÉBITO'
        elif forma_uuid == uuid_carne:
            nome = 'CARNÊ'
        
        print(f"   {nome}: {count} registros")
    
    # Descontos
    total_desconto = formas_df['desconto'].sum()
    print(f"\n💰 Descontos:")
    print(f"   Total de descontos: R$ {total_desconto:,.2f}")
    print(f"   Média por registro com desconto: R$ {formas_df[formas_df['desconto'] > 0]['desconto'].mean():.2f}")
    
    # Validação de valores
    print(f"\n✅ Validação:")
    valor_original = vendas_df['valor_total'].sum()
    valor_formas = formas_df['valor'].sum()
    valor_liquido = formas_df['valor_liquido'].sum()
    
    print(f"   Valor original vendas: R$ {valor_original:,.2f}")
    print(f"   Valor soma formas: R$ {valor_formas:,.2f}")
    print(f"   Valor líquido (com descontos): R$ {valor_liquido:,.2f}")
    print(f"   Diferença: R$ {valor_original - valor_formas:,.2f}")
    
    # 7. Salva arquivo
    output_dir = base_dir / "data" / "vendas_para_importar"
    arquivo_formas = output_dir / "vendas_formas_pagamento_MULTIPLAS.csv"
    
    formas_df.to_csv(arquivo_formas, index=False)
    
    print(f"\n💾 Arquivo salvo: {arquivo_formas}")
    print(f"📊 {len(formas_df)} registros prontos para staging")
    
    return formas_df, arquivo_formas

if __name__ == "__main__":
    formas_df, arquivo = gerar_formas_pagamento_multiplas()
    
    print(f"\n🎉 GERAÇÃO CONCLUÍDA!")
    print(f"📂 Arquivo: {arquivo.name}")
    print(f"💳 Formas múltiplas com descontos específicos")
    print(f"🎯 Pronto para staging no Supabase!")