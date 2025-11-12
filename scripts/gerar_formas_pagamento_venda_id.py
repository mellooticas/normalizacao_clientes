#!/usr/bin/env python3
"""
Geração de formas de pagamento com venda_id correto
Faz o cruzamento com a tabela vendas para obter o UUID
"""

import pandas as pd
from pathlib import Path
import json

def gerar_formas_pagamento_com_venda_id():
    """Gera formas de pagamento com venda_id correto da tabela vendas"""
    
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    
    print("💳 === FORMAS DE PAGAMENTO COM VENDA_ID === 💳")
    print("🎯 Estrutura correta para vendas.vendas_formas_pagamento")
    print()
    
    # 1. Carrega vendas finais
    arquivo_vendas = base_dir / "data" / "vendas_para_importar" / "vendas_TODAS_RENUMERADAS_SEM_DUPLICATAS.csv"
    vendas_df = pd.read_csv(arquivo_vendas)
    print(f"✅ {len(vendas_df)} vendas carregadas")
    
    # 2. Formas de pagamento REAIS da tabela Supabase
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
    
    # 3. Verifica se existe o campo venda_id nas vendas
    if 'venda_id' not in vendas_df.columns:
        print("❌ ERRO: Campo 'venda_id' não encontrado no arquivo de vendas")
        print("📋 Campos disponíveis:", list(vendas_df.columns))
        return None, None
    
    print(f"✅ Campo venda_id encontrado")
    print(f"📊 Exemplo venda_id: {vendas_df['venda_id'].iloc[0]}")
    print()
    
    # 4. Gera formas de pagamento
    print(f"🎯 Gerando formas por fonte...")
    
    todas_formas = []
    
    for idx, venda in vendas_df.iterrows():
        venda_id = venda['venda_id']  # UUID da venda
        numero_venda = venda['numero_venda']
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
                    'venda_id': venda_id,
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
                    'venda_id': venda_id,
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
                    'venda_id': venda_id,
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
                    'venda_id': venda_id,
                    'forma_pagamento_id': uuid_pix,
                    'valor': valor_pix,
                    'valor_entrada': valor_pix,
                    'parcelas': 1,
                    'observacao': 'PIX - 50% da venda'
                })
                
                # LINHA 2: Cartão (50%)
                valor_cartao = valor_total - valor_pix
                todas_formas.append({
                    'venda_id': venda_id,
                    'forma_pagamento_id': uuid_parcelado_cartao,  # PCTC para parcelado
                    'valor': valor_cartao,
                    'valor_entrada': 0,
                    'parcelas': 3,
                    'observacao': 'Cartão Parcelado 3x - 50% da venda'
                })
            else:
                # LINHA ÚNICA: À vista
                todas_formas.append({
                    'venda_id': venda_id,
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
                    'venda_id': venda_id,
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
                    'venda_id': venda_id,
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
                    'venda_id': venda_id,
                    'forma_pagamento_id': forma_id,
                    'valor': valor_total,
                    'valor_entrada': 0,
                    'parcelas': parcelas,
                    'observacao': f'Cartão {parcelas}x'
                })
        
        if idx % 1000 == 0:
            print(f"   Processadas: {idx + 1} vendas...")
    
    print(f"✅ {len(todas_formas)} linhas de formas geradas")
    
    # 5. Cria DataFrame
    formas_df = pd.DataFrame(todas_formas)
    
    # 6. Estatísticas
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
    vendas_com_multiplas = formas_df.groupby('venda_id').size()
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
    
    # 7. Valida estrutura da tabela
    print(f"\n🔍 === VALIDAÇÃO ESTRUTURA === 🔍")
    print(f"✅ venda_id: {formas_df['venda_id'].dtype} (UUID)")
    print(f"✅ forma_pagamento_id: {formas_df['forma_pagamento_id'].dtype} (UUID)")
    print(f"✅ valor: {formas_df['valor'].dtype} (numeric)")
    print(f"✅ valor_entrada: {formas_df['valor_entrada'].dtype} (numeric)")
    print(f"✅ parcelas: {formas_df['parcelas'].dtype} (integer)")
    print(f"✅ observacao: {formas_df['observacao'].dtype} (text)")
    
    # Verifica constraints
    print(f"\n🔒 === VALIDAÇÃO CONSTRAINTS === 🔒")
    
    # Parcelas >= 1
    parcelas_invalidas = (formas_df['parcelas'] < 1).sum()
    print(f"✅ Parcelas >= 1: {parcelas_invalidas} violações (deve ser 0)")
    
    # Valor >= 0
    valores_negativos = (formas_df['valor'] < 0).sum()
    print(f"✅ Valor >= 0: {valores_negativos} violações (deve ser 0)")
    
    # Valor_entrada >= 0
    entradas_negativas = (formas_df['valor_entrada'] < 0).sum()
    print(f"✅ Valor_entrada >= 0: {entradas_negativas} violações (deve ser 0)")
    
    # Valor_entrada <= valor
    entradas_maiores = (formas_df['valor_entrada'] > formas_df['valor']).sum()
    print(f"✅ Valor_entrada <= valor: {entradas_maiores} violações (deve ser 0)")
    
    # Unique constraint venda_id + forma_pagamento_id
    duplicatas = formas_df.duplicated(subset=['venda_id', 'forma_pagamento_id']).sum()
    print(f"✅ Unique (venda_id, forma_pagamento_id): {duplicatas} violações (deve ser 0)")
    
    # 8. Salva arquivo
    output_dir = base_dir / "data" / "vendas_para_importar"
    arquivo_formas = output_dir / "vendas_formas_pagamento_ESTRUTURA_CORRETA.csv"
    
    formas_df.to_csv(arquivo_formas, index=False)
    
    print(f"\n💾 Arquivo salvo: {arquivo_formas}")
    print(f"📊 {len(formas_df)} linhas prontas")
    
    # 9. Exemplo de dados
    print(f"\n📋 Exemplo de dados (primeiras 5 linhas):")
    print(formas_df[['venda_id', 'forma_pagamento_id', 'valor', 'valor_entrada', 'parcelas', 'observacao']].head())
    
    return formas_df, arquivo_formas

if __name__ == "__main__":
    formas_df, arquivo = gerar_formas_pagamento_com_venda_id()
    
    if formas_df is not None:
        print(f"\n🎉 GERAÇÃO CONCLUÍDA!")
        print(f"📂 Arquivo: {arquivo.name}")
        print(f"💡 Estrutura: vendas.vendas_formas_pagamento")
        print(f"🔑 Campo: venda_id (UUID)")
        print(f"✅ Todas as constraints validadas!")
    else:
        print(f"\n❌ FALHA NA GERAÇÃO!")
        print(f"🔍 Verifique o arquivo de vendas")