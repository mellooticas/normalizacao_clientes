#!/usr/bin/env python3
"""
Normalização das vendas para o modelo da tabela vendas.vendas
Inclui cruzamento com clientes UUID e vendedores UUID
"""

import pandas as pd
from pathlib import Path
import uuid
from datetime import datetime
import re

def carregar_mapeamentos():
    """Carrega os mapeamentos de clientes e vendedores UUID"""
    print("🔄 Carregando mapeamentos...")
    
    # Carregar clientes UUID de todas as lojas
    clientes_uuid = {}
    clientes_dir = Path("data/clientes_uuid")
    
    for file in clientes_dir.glob("clientes_*.csv"):
        try:
            df_cliente = pd.read_csv(file)
            print(f"   📁 {file.name}: {len(df_cliente)} clientes")
            
            # Criar mapeamento por nome e id_legado
            for _, row in df_cliente.iterrows():
                cliente_id = row.get('cliente_id_y') or row.get('cliente_id_x')
                id_legado = row.get('id_legado')
                nome = row.get('Nome Completo', '').strip().upper()
                
                if pd.notna(cliente_id):
                    # Mapear por nome
                    if nome:
                        clientes_uuid[nome] = cliente_id
                    # Mapear por id_legado
                    if pd.notna(id_legado):
                        clientes_uuid[str(int(id_legado))] = cliente_id
                        
        except Exception as e:
            print(f"   ❌ Erro ao carregar {file.name}: {e}")
    
    print(f"   ✅ Total clientes mapeados: {len(clientes_uuid)}")
    
    # Carregar vendedores UUID
    vendedores_uuid = {}
    try:
        df_vendedores = pd.read_csv("VENDEDORES_UNICOS_UUID.csv")
        for _, row in df_vendedores.iterrows():
            nome_padronizado = str(row['nome_padronizado']).strip().upper()
            uuid_vendedor = row['uuid']
            vendedores_uuid[nome_padronizado] = uuid_vendedor
        print(f"   ✅ Total vendedores mapeados: {len(vendedores_uuid)}")
    except Exception as e:
        print(f"   ❌ Erro ao carregar vendedores: {e}")
    
    return clientes_uuid, vendedores_uuid

def normalizar_nome(nome):
    """Normaliza nome para busca"""
    if pd.isna(nome):
        return ""
    nome = str(nome).strip().upper()
    # Remove caracteres especiais e números
    nome = re.sub(r'[^\w\s]', '', nome)
    nome = re.sub(r'\d+', '', nome)
    nome = re.sub(r'\s+', ' ', nome).strip()
    return nome

def buscar_cliente_id(nome_cliente, clientes_uuid):
    """Busca UUID do cliente"""
    if not nome_cliente:
        return None
        
    nome_norm = normalizar_nome(nome_cliente)
    
    # Busca exata
    if nome_norm in clientes_uuid:
        return clientes_uuid[nome_norm]
    
    # Busca aproximada (primeiras palavras)
    palavras = nome_norm.split()
    if len(palavras) >= 2:
        nome_parcial = ' '.join(palavras[:2])
        for cliente_nome, cliente_id in clientes_uuid.items():
            if cliente_nome.startswith(nome_parcial):
                return cliente_id
    
    return None

def buscar_vendedor_id(loja_id, vendedores_uuid):
    """Busca UUID do vendedor baseado na loja"""
    # Mapeamento padrão por loja (pode ser ajustado)
    vendedor_padrao_loja = {
        "52f92716-d2ba-441a-ac3c-94bdfabd9722": "VENDEDOR NÃO INFORMADO - SUZANO",  # SUZANO
        "9a22ccf1-36fe-4b9f-9391-ca31433dc31e": "VENDEDOR NÃO INFORMADO - MAUA",    # MAUA
        # Adicionar outros mapeamentos conforme necessário
    }
    
    if loja_id in vendedor_padrao_loja:
        vendedor_nome = vendedor_padrao_loja[loja_id]
        return vendedores_uuid.get(vendedor_nome)
    
    return None

def gerar_vendas_core_final():
    print("🔄 NORMALIZANDO VENDAS PARA TABELA vendas.vendas")
    print("=" * 60)
    
    # Carregar mapeamentos
    clientes_uuid, vendedores_uuid = carregar_mapeamentos()
    
    # Diretórios
    vendas_dir = Path("data/originais/cxs/finais_postgresql_prontos")
    output_dir = Path("data/vendas_para_importar")
    output_dir.mkdir(exist_ok=True)
    
    # Listar arquivos de vendas
    vendas_files = list(vendas_dir.glob("vendas_*_final.csv"))
    print(f"📁 Arquivos encontrados: {len(vendas_files)}")
    
    todas_vendas = []
    stats_cruzamento = {
        'total_vendas': 0,
        'clientes_encontrados': 0,
        'vendedores_encontrados': 0
    }
    
    for file in vendas_files:
        try:
            print(f"🔍 Processando: {file.name}")
            df = pd.read_csv(file)
            
            # Converter tipos de dados
            df['nn_venda'] = pd.to_numeric(df['nn_venda'], errors='coerce')
            df['valor_venda'] = pd.to_numeric(df['valor_venda'], errors='coerce').fillna(0)
            df['entrada'] = pd.to_numeric(df['entrada'], errors='coerce').fillna(0)
            
            # Converter datas com formato flexível
            df['data_movimento'] = pd.to_datetime(df['data_movimento'], format='mixed', dayfirst=True, errors='coerce')
            
            # Remover registros sem número de venda
            df_clean = df.dropna(subset=['nn_venda']).copy()
            
            print(f"   📊 {len(df)} registros -> {len(df_clean)} válidos")
            
            # Agrupar vendas parceladas (mesmo nn_venda)
            vendas_agrupadas = df_clean.groupby(['nn_venda', 'loja_id']).agg({
                'cliente': 'first',
                'forma_de_pgto': lambda x: ', '.join(x.dropna().unique()) if len(x.dropna().unique()) > 1 else x.iloc[0],
                'valor_venda': 'first',  # Valor total da venda (mesmo para todas as parcelas)
                'entrada': 'sum',  # Soma todas as entradas
                'data_movimento': 'first',  # Data da primeira entrada
                'loja_nome': 'first'
            }).reset_index()
            
            print(f"   📊 {len(df_clean)} registros -> {len(vendas_agrupadas)} vendas únicas")
            
            # Normalizar para o modelo da tabela
            vendas_normalizadas = []
            
            for _, row in vendas_agrupadas.iterrows():
                # Buscar cliente_id
                cliente_id = buscar_cliente_id(row['cliente'], clientes_uuid)
                if cliente_id:
                    stats_cruzamento['clientes_encontrados'] += 1
                
                # Buscar vendedor_id  
                vendedor_id = buscar_vendedor_id(row['loja_id'], vendedores_uuid)
                if vendedor_id:
                    stats_cruzamento['vendedores_encontrados'] += 1
                
                # Determinar tipo de operação
                forma_pgto = str(row['forma_de_pgto']).upper()
                tipo_operacao = 'GARANTIA' if 'GARANTIA' in forma_pgto else 'VENDA'
                
                # Corrigir valores (entrada não pode ser maior que total)
                valor_total = float(row['valor_venda'])
                valor_entrada = float(row['entrada'])
                if valor_entrada > valor_total and valor_total > 0:
                    valor_entrada = valor_total  # Limitar entrada ao valor total
                
                venda = {
                    'id': str(uuid.uuid4()),
                    'numero_venda': f"{row['loja_nome']}_{int(row['nn_venda'])}",
                    'cliente_id': cliente_id,
                    'loja_id': row['loja_id'],
                    'vendedor_id': vendedor_id,
                    'data_venda': row['data_movimento'].strftime('%Y-%m-%d'),
                    'valor_total': valor_total,
                    'valor_entrada': valor_entrada,
                    'valor_restante': valor_total - valor_entrada,
                    'nome_cliente_temp': row['cliente'] if pd.notna(row['cliente']) else None,
                    'observacoes': None,
                    'status': 'ATIVO',
                    'cancelado': False,
                    'data_cancelamento': None,
                    'motivo_cancelamento': None,
                    'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'created_by': 'SISTEMA_MIGRACAO',
                    'updated_by': 'SISTEMA_MIGRACAO',
                    'deleted_at': None,
                    'version': 1,
                    'tipo_operacao': tipo_operacao,
                    'is_garantia': tipo_operacao == 'GARANTIA',
                    'forma_pagamento': row['forma_de_pgto'] if pd.notna(row['forma_de_pgto']) else None
                }
                
                vendas_normalizadas.append(venda)
                stats_cruzamento['total_vendas'] += 1
            
            todas_vendas.extend(vendas_normalizadas)
            print(f"   ✅ {len(vendas_normalizadas)} vendas normalizadas")
            
        except Exception as e:
            print(f"   ❌ Erro ao processar {file.name}: {e}")
    
    # Criar DataFrame final
    df_final = pd.DataFrame(todas_vendas)
    
    print(f"\n📊 RESUMO FINAL:")
    print(f"   📦 Total de vendas: {len(df_final):,}")
    print(f"   💰 Valor total: R$ {df_final['valor_total'].sum():,.2f}")
    print(f"   💳 Entradas: R$ {df_final['valor_entrada'].sum():,.2f}")
    print(f"   💸 Restante: R$ {df_final['valor_restante'].sum():,.2f}")
    
    # Estatísticas de cruzamento
    print(f"\n🔗 ESTATÍSTICAS DE CRUZAMENTO:")
    print(f"   👥 Clientes encontrados: {stats_cruzamento['clientes_encontrados']:,}/{stats_cruzamento['total_vendas']:,} ({stats_cruzamento['clientes_encontrados']/stats_cruzamento['total_vendas']*100:.1f}%)")
    print(f"   👤 Vendedores encontrados: {stats_cruzamento['vendedores_encontrados']:,}/{stats_cruzamento['total_vendas']:,} ({stats_cruzamento['vendedores_encontrados']/stats_cruzamento['total_vendas']*100:.1f}%)")
    
    # Distribuição por loja
    print(f"\n📊 DISTRIBUIÇÃO POR LOJA:")
    distribuicao = df_final.groupby('loja_id').agg({
        'id': 'count',
        'valor_total': 'sum',
        'cliente_id': lambda x: x.notna().sum(),
        'vendedor_id': lambda x: x.notna().sum()
    }).round(2)
    
    # Mapear nomes das lojas
    loja_nomes = df_final.groupby('loja_id')['numero_venda'].first().str.split('_').str[0]
    
    for loja_id, stats in distribuicao.iterrows():
        loja_nome = loja_nomes[loja_id] if loja_id in loja_nomes.index else 'DESCONHECIDA'
        print(f"   📍 {loja_nome:12} | {stats['id']:5,} vendas | R$ {stats['valor_total']:10,.2f} | {stats['cliente_id']:4,} clientes | {stats['vendedor_id']:4,} vendedores")
    
    # Verificar tipos de operação
    print(f"\n📊 TIPOS DE OPERAÇÃO:")
    tipos = df_final['tipo_operacao'].value_counts()
    for tipo, count in tipos.items():
        print(f"   📋 {tipo:10} | {count:5,} vendas ({count/len(df_final)*100:.1f}%)")
    
    # Verificar formas de pagamento mais comuns
    print(f"\n💳 FORMAS DE PAGAMENTO (Top 10):")
    formas = df_final['forma_pagamento'].value_counts().head(10)
    for forma, count in formas.items():
        print(f"   💳 {forma:15} | {count:5,} vendas ({count/len(df_final)*100:.1f}%)")
    
    # Salvar arquivo final
    output_file = output_dir / "vendas_core_final.csv"
    df_final.to_csv(output_file, index=False)
    print(f"\n💾 Arquivo salvo: {output_file}")
    print(f"📏 Tamanho do arquivo: {output_file.stat().st_size / 1024 / 1024:.2f} MB")
    
    # Verificar constraints da tabela
    print(f"\n🔍 VERIFICAÇÃO DE CONSTRAINTS:")
    
    # 1. Unique constraint (loja_id, numero_venda)
    duplicates = df_final.duplicated(subset=['loja_id', 'numero_venda']).sum()
    print(f"   ✅ Constraint unique (loja_id, numero_venda): {duplicates} duplicatas")
    
    # 2. Check valor_total >= 0
    valores_negativos = (df_final['valor_total'] < 0).sum()
    print(f"   ✅ Constraint valor_total >= 0: {valores_negativos} violações")
    
    # 3. Check valor_entrada >= 0
    entradas_negativas = (df_final['valor_entrada'] < 0).sum()
    print(f"   ✅ Constraint valor_entrada >= 0: {entradas_negativas} violações")
    
    # 4. Check valor_entrada <= valor_total
    entradas_maiores = (df_final['valor_entrada'] > df_final['valor_total']).sum()
    print(f"   ✅ Constraint valor_entrada <= valor_total: {entradas_maiores} violações")
    
    # 5. Check tipo_operacao válidos
    tipos_validos = ['VENDA', 'GARANTIA', 'TROCA', 'DEVOLUCAO', 'CORTESIA']
    tipos_invalidos = (~df_final['tipo_operacao'].isin(tipos_validos)).sum()
    print(f"   ✅ Constraint tipo_operacao válido: {tipos_invalidos} violações")
    
    if duplicates == 0 and valores_negativos == 0 and entradas_negativas == 0 and entradas_maiores == 0 and tipos_invalidos == 0:
        print(f"\n🎉 TODAS AS CONSTRAINTS VALIDADAS COM SUCESSO!")
    else:
        print(f"\n⚠️  ALGUMAS CONSTRAINTS FALHARAM - VERIFICAR DADOS")
    
    return df_final

if __name__ == "__main__":
    df_vendas = gerar_vendas_core_final()