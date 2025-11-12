#!/usr/bin/env python3
"""
Gerador de Entregas OS - Sistema Carne Fácil
==========================================

Gera dados completos de entregas_os baseado nas vendas existentes.
Calcula datas de entrega realistas baseadas em:
- Tipo de pagamento (carnê = mais rápido)
- Dia da semana (evita fins de semana)
- Sazonalidade (dezembro mais lento)

Dados: 15.281 vendas → 15.281 entregas
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import uuid
import random
from pathlib import Path

def calcular_data_entrega(data_venda, forma_pagamento_principal, valor_venda):
    """
    Calcula data de entrega baseada em critérios realistas
    
    Regras:
    - Carnê: 1-3 dias (pagamento garantido)
    - PIX/Dinheiro: 1-5 dias (pagamento à vista)
    - Cartão: 2-7 dias (processamento)
    - Valores altos: +1-2 dias extras
    - Fins de semana: pula para segunda
    - Dezembro: +2-3 dias extras
    """
    
    # Prazo base por forma de pagamento
    prazos_base = {
        'Carnê': (1, 3),
        'PIX': (1, 5),
        'Dinheiro': (1, 4),
        'Cartão Crédito': (2, 7),
        'Parcelado Cartão': (3, 8),
        'Cartão Débito': (1, 5),
        'Cheque': (5, 10),
        'Transferência': (2, 6)
    }
    
    # Prazo base
    prazo_min, prazo_max = prazos_base.get(forma_pagamento_principal, (2, 6))
    
    # Ajuste por valor (produtos caros demoram mais)
    if valor_venda > 1000:
        prazo_max += 2
    elif valor_venda > 500:
        prazo_max += 1
    
    # Ajuste sazonal (dezembro mais lento)
    if data_venda.month == 12:
        prazo_max += 3
    elif data_venda.month in [1, 7]:  # Janeiro e julho (férias)
        prazo_max += 1
    
    # Gera prazo aleatório
    prazo_dias = random.randint(prazo_min, prazo_max)
    
    # Calcula data inicial
    data_entrega = data_venda + timedelta(days=prazo_dias)
    
    # Ajusta para evitar fins de semana
    while data_entrega.weekday() >= 5:  # 5=sábado, 6=domingo
        data_entrega += timedelta(days=1)
    
    return data_entrega

def gerar_status_entrega(data_venda, data_entrega):
    """
    Gera status realista baseado nas datas
    
    Status possíveis:
    - 'entregue': Maioria das entregas antigas
    - 'pendente': Algumas entregas recentes
    - 'em_transporte': Muito poucas, só recentes
    - 'cancelada': Raras exceções
    """
    
    hoje = datetime.now().date()
    dias_desde_entrega = (hoje - data_entrega.date()).days
    
    # Entregas muito antigas (>30 dias): sempre entregues
    if dias_desde_entrega > 30:
        return 'entregue'
    
    # Entregas antigas (7-30 dias): 95% entregues
    elif dias_desde_entrega > 7:
        return random.choices(
            ['entregue', 'pendente', 'cancelada'],
            weights=[95, 4, 1]
        )[0]
    
    # Entregas recentes (1-7 dias): mix realista
    elif dias_desde_entrega > 0:
        return random.choices(
            ['entregue', 'em_transporte', 'pendente'],
            weights=[70, 20, 10]
        )[0]
    
    # Entregas futuras: sempre pendentes
    else:
        return 'pendente'

def main():
    """Gera arquivo CSV completo de entregas_os"""
    
    print("🚚 === GERADOR DE ENTREGAS OS === 🚚")
    print("📊 Processando 15.281 vendas...")
    
    # Carrega dados das vendas
    try:
        vendas_df = pd.read_csv('data/vendas_para_importar/vendas_totais_com_uuid.csv')
        print(f"✅ Carregadas {len(vendas_df):,} vendas")
    except FileNotFoundError:
        print("❌ Arquivo vendas_totais_com_uuid.csv não encontrado!")
        return
    
    # Carrega formas de pagamento para obter forma principal
    try:
        formas_df = pd.read_csv('data/vendas_para_importar/vendas_formas_pagamento_FINAL.csv')
        print(f"✅ Carregadas {len(formas_df):,} formas de pagamento")
        
        # Mapeamento de forma_pagamento_id para nome
        forma_pagamento_map = {
            'cebaa0dd-4784-4ff4-953f-a3ad6b8a6a5d': 'PIX',
            '203527b1-d871-4f29-8c81-88fb0efaebd1': 'Dinheiro',
            '66c4f61d-b264-46c2-a29b-69a1c2e6aba2': 'Parcelado Cartão',
            '4854a683-31c3-4355-a03c-2bf398ebb4d5': 'Cartão Crédito',
            'e80028d4-ddf2-4e4b-9347-78044a6316f1': 'Cartão Débito',
            '26e2d011-d3b6-4ded-9259-4d4f37a000bc': 'Carnê',
            'b36056fa-47df-4f7a-b0e0-cda6a1bb5073': 'Transferência',
            '9c8ce174-8212-41f7-a637-980f581c8ca9': 'Garantia',
            '6e8f3b21-8a9c-4d5e-b2f7-1c3e7d9a0b8f': 'Cheque'
        }
        
        # Adiciona nome da forma de pagamento
        formas_df['forma_pagamento'] = formas_df['forma_pagamento_id'].map(forma_pagamento_map)
        formas_df['forma_pagamento'] = formas_df['forma_pagamento'].fillna('PIX')
        
        # Identifica forma principal por venda (maior valor)
        forma_principal = formas_df.loc[formas_df.groupby('venda_id')['valor'].idxmax()]
        forma_principal = forma_principal[['venda_id', 'forma_pagamento']].rename(
            columns={'forma_pagamento': 'forma_principal'}
        )
        
    except FileNotFoundError:
        print("⚠️ Arquivo formas de pagamento não encontrado, usando dados padrão")
        forma_principal = pd.DataFrame({
            'venda_id': vendas_df['id'],
            'forma_principal': 'PIX'  # Padrão
        })
    
    # Merge com vendas
    vendas_df = vendas_df.merge(forma_principal, left_on='id', right_on='venda_id', how='left')
    vendas_df['forma_principal'] = vendas_df['forma_principal'].fillna('PIX')
    
    print("🔄 Gerando dados de entregas...")
    
    # Converte data_venda
    vendas_df['data_venda'] = pd.to_datetime(vendas_df['data_venda'])
    
    # Lista para armazenar entregas
    entregas = []
    
    # Processa cada venda
    for idx, venda in vendas_df.iterrows():
        if idx % 1000 == 0:
            print(f"   Processando {idx:,}/{len(vendas_df):,} vendas...")
        
        # Calcula data de entrega
        data_entrega = calcular_data_entrega(
            venda['data_venda'],
            venda['forma_principal'],
            venda['valor_total']
        )
        
        # Gera status
        status = gerar_status_entrega(venda['data_venda'], data_entrega)
        
        # Gera observações realistas
        observacoes_opcoes = [
            None,  # Maioria sem observações
            'Entrega realizada no horário',
            'Cliente não estava, reagendado',
            'Endereço conferido',
            'Entrega expressa solicitada',
            'Produto conferido na entrega',
            'Cliente satisfeito',
            'Reagendamento solicitado',
        ]
        
        # 70% sem observações, 30% com observações
        observacao = random.choices(
            observacoes_opcoes,
            weights=[70, 5, 5, 5, 3, 5, 4, 3]
        )[0]
        
        # Cria registro de entrega
        entrega = {
            'id': str(uuid.uuid4()),
            'venda_id': venda['id'],
            'os_numero': venda['os_numero'],
            'data_prevista': data_entrega.strftime('%Y-%m-%d'),
            'data_entrega': data_entrega.strftime('%Y-%m-%d') if status == 'entregue' else None,
            'status': status,
            'observacoes': observacao,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Ajusta data_entrega para entregas não realizadas
        if status in ['pendente', 'em_transporte']:
            entrega['data_entrega'] = None
        elif status == 'cancelada':
            # Canceladas podem ter data de cancelamento
            entrega['data_entrega'] = None
            entrega['observacoes'] = 'Entrega cancelada a pedido do cliente'
        
        entregas.append(entrega)
    
    # Cria DataFrame
    entregas_df = pd.DataFrame(entregas)
    
    print(f"✅ Geradas {len(entregas_df):,} entregas")
    
    # Estatísticas
    print("\n📊 === ESTATÍSTICAS === 📊")
    status_stats = entregas_df['status'].value_counts()
    for status, count in status_stats.items():
        pct = (count / len(entregas_df)) * 100
        print(f"   {status}: {count:,} ({pct:.1f}%)")
    
    print(f"\n📅 Período de entregas:")
    print(f"   Primeira: {entregas_df['data_prevista'].min()}")
    print(f"   Última: {entregas_df['data_prevista'].max()}")
    
    # Observações com dados
    obs_com_dados = entregas_df['observacoes'].notna().sum()
    pct_obs = (obs_com_dados / len(entregas_df)) * 100
    print(f"\n📝 Observações: {obs_com_dados:,} ({pct_obs:.1f}%) com dados")
    
    # Salva arquivo
    output_path = 'data/vendas_para_importar/entregas_os_completas.csv'
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    entregas_df.to_csv(output_path, index=False)
    print(f"\n💾 Arquivo salvo: {output_path}")
    print(f"📁 Tamanho: {len(entregas_df):,} registros")
    
    # Validações finais
    print("\n🔍 === VALIDAÇÕES === 🔍")
    print(f"✅ Todas as vendas têm entrega: {len(entregas_df) == len(vendas_df)}")
    print(f"✅ IDs únicos: {entregas_df['id'].nunique() == len(entregas_df)}")
    print(f"✅ Venda_IDs válidos: {entregas_df['venda_id'].notna().all()}")
    print(f"✅ OS números válidos: {entregas_df['os_numero'].notna().all()}")
    
    # Verifica integridade com vendas
    vendas_sem_entrega = set(vendas_df['id']) - set(entregas_df['venda_id'])
    entregas_sem_venda = set(entregas_df['venda_id']) - set(vendas_df['id'])
    
    print(f"✅ Vendas sem entrega: {len(vendas_sem_entrega)}")
    print(f"✅ Entregas sem venda: {len(entregas_sem_venda)}")
    
    if len(vendas_sem_entrega) == 0 and len(entregas_sem_venda) == 0:
        print("\n🎯 === SUCESSO TOTAL === 🎯")
        print("✅ Integridade 100% garantida!")
        print("✅ Dados realistas gerados!")
        print("✅ Pronto para importação no Supabase!")
    
    print(f"\n🚀 Arquivo final: {output_path}")
    print("📊 Estrutura: id, venda_id, os_numero, data_prevista, data_entrega, status, observacoes, created_at, updated_at")

if __name__ == "__main__":
    random.seed(42)  # Para resultados reproduzíveis
    main()