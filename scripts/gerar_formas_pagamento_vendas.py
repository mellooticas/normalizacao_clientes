#!/usr/bin/env python3
"""
Geração de formas de pagamento para vendas
Baseado nos dados históricos e mapeamento por fonte
"""

import pandas as pd
from pathlib import Path
import json

def gerar_formas_pagamento_vendas():
    """Gera arquivo de formas de pagamento para as vendas"""
    
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    
    print("💳 === GERAÇÃO FORMAS DE PAGAMENTO VENDAS === 💳")
    print()
    
    # 1. Carrega vendas finais
    print("📂 Carregando vendas finais...")
    arquivo_vendas = base_dir / "data" / "vendas_para_importar" / "vendas_TODAS_RENUMERADAS_SEM_DUPLICATAS.csv"
    vendas_df = pd.read_csv(arquivo_vendas)
    print(f"✅ {len(vendas_df)} vendas carregadas")
    
    # 2. Carrega mapeamento de formas de pagamento
    print(f"\n🗺️  Carregando mapeamento de formas de pagamento...")
    arquivo_formas = base_dir / "_analises" / "mapeamento_formas_pagamento_uuid.json"
    
    with open(arquivo_formas, 'r', encoding='utf-8') as f:
        dados_formas = json.load(f)
    
    formas_pagamento = dados_formas['mapeamento_formas']
    print(f"📋 Formas disponíveis: {len(formas_pagamento)}")
    for forma, uuid_forma in formas_pagamento.items():
        print(f"   {forma}: {uuid_forma}")
    
    # 3. Define estratégia de mapeamento por fonte
    print(f"\n🎯 Definindo estratégia por fonte...")
    
    # Mapeamento baseado no padrão de numeração e observações
    def identificar_fonte_venda(row):
        """Identifica fonte da venda pela numeração e observação"""
        numero = str(row['numero_venda'])
        observacao = str(row['observacoes'])
        
        if 'OSS' in observacao or not numero.startswith(('1', '2')):
            return 'OSS'
        elif numero.startswith('1'):  # 100000+
            return 'VIXEN_CARNE'
        elif numero.startswith('2'):  # 200000+
            return 'VIXEN_COMPLETO'
        else:
            return 'OSS'  # Default
    
    vendas_df['fonte'] = vendas_df.apply(identificar_fonte_venda, axis=1)
    
    # Estatísticas por fonte
    por_fonte = vendas_df['fonte'].value_counts()
    print(f"📊 Vendas por fonte:")
    for fonte, count in por_fonte.items():
        print(f"   {fonte}: {count} vendas")
    
    # 4. Mapeamento de formas por fonte
    print(f"\n💳 Mapeamento de formas por fonte...")
    
    # UUIDs principais das formas mais usadas
    uuid_dinheiro = formas_pagamento.get('DINHEIRO', None)
    uuid_cartao_credito = formas_pagamento.get('CTC', None)  # Cartão Crédito
    uuid_pix = formas_pagamento.get('PIX', None)
    uuid_carne = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'  # UUID fictício para carnê próprio
    
    print(f"🆔 UUIDs principais:")
    print(f"   Dinheiro: {uuid_dinheiro}")
    print(f"   Cartão Crédito: {uuid_cartao_credito}")
    print(f"   PIX: {uuid_pix}")
    print(f"   Carnê Próprio: {uuid_carne}")
    
    # Estratégia por fonte
    estrategia_formas = {
        'OSS': {
            'forma_principal': uuid_dinheiro or uuid_pix or list(formas_pagamento.values())[0],
            'nome': 'DINHEIRO/PIX',
            'parcelas': 1,
            'descricao': 'À vista'
        },
        'VIXEN_CARNE': {
            'forma_principal': uuid_carne,
            'nome': 'CARNE_PROPRIO',
            'parcelas': 10,  # Média de carnê
            'descricao': 'Carnê próprio'
        },
        'VIXEN_COMPLETO': {
            'forma_principal': uuid_cartao_credito or list(formas_pagamento.values())[0],
            'nome': 'CARTAO_CREDITO',
            'parcelas': 1,
            'descricao': 'Outros pagamentos'
        }
    }
    
    # 5. Gera registros de formas de pagamento
    print(f"\n🔧 Gerando registros de formas de pagamento...")
    
    formas_pagamento_registros = []
    
    for idx, venda in vendas_df.iterrows():
        fonte = venda['fonte']
        estrategia = estrategia_formas[fonte]
        
        # Para vendas OSS com valor alto, pode ser parcelado
        parcelas = estrategia['parcelas']
        if fonte == 'OSS' and venda['valor_total'] > 1000:
            parcelas = min(3, int(venda['valor_total'] / 500))  # Máximo 3x
        
        # Para VIXEN carnê, parcelas baseadas no valor
        if fonte == 'VIXEN_CARNE':
            parcelas = min(12, max(6, int(venda['valor_total'] / 100)))
        
        registro = {
            'venda_numero': venda['numero_venda'],  # Para identificação
            'venda_loja_id': venda['loja_id'],      # Para identificação
            'forma_pagamento_id': estrategia['forma_principal'],
            'valor': venda['valor_total'],
            'valor_entrada': venda.get('valor_entrada', 0),
            'parcelas': parcelas,
            'observacao': f"Forma inferida: {estrategia['nome']} - {estrategia['descricao']}"
        }
        
        formas_pagamento_registros.append(registro)
    
    # 6. Cria DataFrame das formas de pagamento
    formas_df = pd.DataFrame(formas_pagamento_registros)
    
    print(f"✅ {len(formas_df)} registros de formas de pagamento gerados")
    
    # 7. Estatísticas das formas geradas
    print(f"\n📊 Estatísticas das formas de pagamento:")
    
    por_forma = formas_df['forma_pagamento_id'].value_counts()
    for forma_uuid, count in por_forma.items():
        # Encontra nome da forma
        nome_forma = 'DESCONHECIDA'
        for nome, uuid_busca in formas_pagamento.items():
            if uuid_busca == forma_uuid:
                nome_forma = nome
                break
        if forma_uuid == uuid_carne:
            nome_forma = 'CARNE_PROPRIO'
        
        print(f"   {nome_forma}: {count} vendas")
    
    # Parcelas
    print(f"\n📈 Distribuição de parcelas:")
    parcelas_dist = formas_df['parcelas'].value_counts().sort_index()
    for parcelas, count in parcelas_dist.head(10).items():
        print(f"   {parcelas}x: {count} vendas")
    
    # 8. Salva arquivo
    print(f"\n💾 Salvando arquivo...")
    
    output_dir = base_dir / "data" / "vendas_para_importar"
    arquivo_formas_pag = output_dir / "vendas_formas_pagamento_BASICO.csv"
    
    formas_df.to_csv(arquivo_formas_pag, index=False)
    
    print(f"✅ Arquivo salvo: {arquivo_formas_pag}")
    print(f"📊 {len(formas_df)} registros prontos")
    
    # 9. Próximos passos
    print(f"\n🚀 PRÓXIMOS PASSOS:")
    print(f"1. Importar vendas primeiro (para ter venda_id)")
    print(f"2. Atualizar arquivo com venda_id real do banco")
    print(f"3. Importar formas de pagamento")
    print(f"4. Validar consistência")
    
    # 10. Script SQL de exemplo
    print(f"\n📝 Exemplo de atualização com venda_id:")
    print(f"```sql")
    print(f"-- Após importar vendas, atualizar formas com venda_id real")
    print(f"UPDATE temp_formas_pagamento SET venda_id = (")
    print(f"  SELECT v.id FROM vendas.vendas v ")
    print(f"  WHERE v.numero_venda = temp_formas_pagamento.venda_numero")
    print(f"  AND v.loja_id = temp_formas_pagamento.venda_loja_id")
    print(f");")
    print(f"```")
    
    return formas_df, arquivo_formas_pag

if __name__ == "__main__":
    formas_df, arquivo = gerar_formas_pagamento_vendas()
    
    print(f"\n🎉 GERAÇÃO CONCLUÍDA!")
    print(f"📂 Arquivo: {arquivo.name}")
    print(f"📊 {len(formas_df)} formas de pagamento prontas")
    print(f"💡 Estratégia básica aplicada - pode ser refinada!")