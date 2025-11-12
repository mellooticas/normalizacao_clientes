#!/usr/bin/env python3
"""
Mapear cliente_uuid nas vendas unidas e formatar para tabela vendas.vendas
"""

import pandas as pd
import uuid
from pathlib import Path
from datetime import datetime

def carregar_vendas_unidas():
    """Carrega vendas já unidas (OSS + Lojas)"""
    print("📊 CARREGANDO VENDAS UNIDAS")
    print("=" * 30)
    
    vendas_path = Path("data/vendas_para_importar/vendas_oss_lojas_unidas.csv")
    
    if not vendas_path.exists():
        print("❌ Arquivo de vendas unidas não encontrado")
        return None
    
    vendas = pd.read_csv(vendas_path)
    print(f"✅ {len(vendas):,} vendas carregadas")
    
    # Mostrar colunas principais
    colunas_principais = [col for col in vendas.columns if any(palavra in col.lower() 
                         for palavra in ['cliente_id', 'uuid', 'total', 'data', 'os_chave'])]
    print(f"📋 Colunas principais: {colunas_principais[:10]}...")
    
    return vendas

def carregar_clientes_uuid():
    """Carrega todos os clientes UUID consolidados"""
    print("\n📊 CARREGANDO CLIENTES UUID")
    print("=" * 30)
    
    clientes_path = Path("data/clientes_uuid")
    clientes_dados = []
    
    for arquivo in clientes_path.glob("*.csv"):
        print(f"📥 {arquivo.name}")
        df = pd.read_csv(arquivo)
        print(f"   Registros: {len(df):,}")
        clientes_dados.append(df)
    
    if clientes_dados:
        clientes_final = pd.concat(clientes_dados, ignore_index=True)
        print(f"\n✅ Total clientes UUID: {len(clientes_final):,}")
        
        # Verificar colunas de ligação
        colunas_ligacao = [col for col in clientes_final.columns if 'cliente_id' in col.lower()]
        print(f"📋 Colunas de ligação disponíveis: {colunas_ligacao}")
        
        return clientes_final
    else:
        return None

def mapear_cliente_uuid(vendas_df, clientes_uuid_df):
    """Mapeia cliente_uuid para as vendas"""
    print("\n🔗 MAPEANDO CLIENTE UUID")
    print("=" * 30)
    
    # Verificar coluna de cliente_id nas vendas
    if 'cliente_id' not in vendas_df.columns:
        print("❌ Coluna cliente_id não encontrada nas vendas")
        return None
    
    # Determinar coluna de ligação nos clientes UUID
    # Prioridade: cliente_id_y > cliente_id_x > cliente_id > ID
    coluna_uuid_final = None
    coluna_ligacao = None
    
    for col_uuid in ['cliente_id_y', 'cliente_id_x']:
        if col_uuid in clientes_uuid_df.columns:
            coluna_uuid_final = col_uuid
            break
    
    for col_ligacao in ['id_legado', 'ID', 'cliente_id']:
        if col_ligacao in clientes_uuid_df.columns:
            coluna_ligacao = col_ligacao
            break
    
    if not coluna_uuid_final:
        print("❌ Nenhuma coluna de UUID final encontrada")
        return None
    
    if not coluna_ligacao:
        print("❌ Nenhuma coluna de ligação encontrada")
        return None
    
    print(f"✅ Usando {coluna_uuid_final} como UUID final")
    print(f"✅ Usando {coluna_ligacao} como chave de ligação")
    
    # Preparar dados para merge
    vendas_prep = vendas_df.copy()
    clientes_prep = clientes_uuid_df[[coluna_ligacao, coluna_uuid_final, 'Cliente']].copy()
    clientes_prep = clientes_prep.dropna(subset=[coluna_ligacao, coluna_uuid_final])
    
    print(f"Vendas para mapear: {len(vendas_prep):,}")
    print(f"Clientes UUID disponíveis: {len(clientes_prep):,}")
    
    # Converter tipos para compatibilidade
    vendas_prep['cliente_id'] = pd.to_numeric(vendas_prep['cliente_id'], errors='coerce')
    clientes_prep[coluna_ligacao] = pd.to_numeric(clientes_prep[coluna_ligacao], errors='coerce')
    
    # Fazer o merge
    resultado = pd.merge(
        vendas_prep,
        clientes_prep,
        left_on='cliente_id',
        right_on=coluna_ligacao,
        how='left',  # LEFT JOIN para manter todas as vendas
        suffixes=('', '_cliente_uuid')
    )
    
    # Renomear coluna UUID final
    resultado = resultado.rename(columns={coluna_uuid_final: 'cliente_uuid_final'})
    
    # Estatísticas
    vendas_com_uuid = resultado['cliente_uuid_final'].notna().sum()
    vendas_sem_uuid = resultado['cliente_uuid_final'].isna().sum()
    
    print(f"✅ Merge concluído: {len(resultado):,} vendas")
    print(f"📊 Com cliente UUID: {vendas_com_uuid:,} ({vendas_com_uuid/len(resultado)*100:.1f}%)")
    print(f"📊 Sem cliente UUID: {vendas_sem_uuid:,} ({vendas_sem_uuid/len(resultado)*100:.1f}%)")
    
    return resultado

def formatar_para_tabela_vendas(vendas_completas_df):
    """Formatar dados para estrutura da tabela vendas.vendas"""
    print("\n🔄 FORMATANDO PARA TABELA vendas.vendas")
    print("=" * 45)
    
    vendas_final = []
    timestamp_atual = datetime.now()
    
    for idx, venda in vendas_completas_df.iterrows():
        # Gerar ID único
        venda_id = str(uuid.uuid4())
        
        # Número da venda único (os_chave + índice)
        numero_venda = f"{venda.get('os_chave', idx)}_{idx}"
        
        # Cliente UUID (se disponível)
        cliente_uuid = venda.get('cliente_uuid_final') if pd.notna(venda.get('cliente_uuid_final')) else None
        
        # Nome cliente temporário se não tiver UUID
        nome_cliente_temp = venda.get('Cliente_cliente_uuid') if pd.isna(cliente_uuid) else None
        
        # Loja UUID - priorizar loja_uuid se disponível, senão mapear por loja_origem
        loja_uuid = None
        for col in ['loja_uuid', 'canal_uuid']:
            if col in venda and pd.notna(venda[col]):
                loja_uuid = venda[col]
                break
        
        # Se não encontrou loja_uuid, mapear pela loja_origem
        if not loja_uuid:
            mapeamento_lojas = {
                'maua': '7f9d4c6e-8b3a-4d2c-9f1e-6a5b8c7d9e0f',
                'perus': 'a8f5c3d9-2b7e-4f1a-9c6d-5e8b3a1f7c9e', 
                'rio_pequeno': 'b9c6d2e8-3f9a-5c7b-8d1e-6f2a9c5b8e1d',
                'sao_mateus': 'c1d7e3f9-4a8b-6d2e-9f5c-7a3d1e8b6f9c',
                'suzano': '52f92716-d2ba-441a-ac3c-94bdfabd9722',
                'suzano2': 'd2e8f4a1-5b9c-7e3f-1a6d-8c5b2f9e7a4d'
            }
            
            loja_origem = venda.get('loja_origem_oss') or venda.get('loja_origem_loja')
            if loja_origem:
                loja_uuid = mapeamento_lojas.get(str(loja_origem).lower())
        
        # Vendedor UUID
        vendedor_uuid = venda.get('vendedor_uuid') if pd.notna(venda.get('vendedor_uuid')) else None
        
        # Data da venda
        data_venda = None
        for col in ['data_compra', 'data_venda', 'data_movimento']:
            if col in venda and pd.notna(venda[col]):
                try:
                    data_venda = pd.to_datetime(venda[col]).date()
                    break
                except:
                    continue
        
        if not data_venda:
            data_venda = datetime(2024, 1, 1).date()  # Data padrão
        
        # Valor total
        valor_total = 0.0
        for col in ['valor_total', 'TOTAL_loja', 'TOTAL_oss', 'TOTAL']:
            if col in venda and pd.notna(venda[col]):
                try:
                    valor_total = float(venda[col])
                    break
                except:
                    continue
        
        # Entrada (assumir 0 se não disponível)
        valor_entrada = 0.0
        
        # Observações
        observacoes = f"OS: {venda.get('os_chave', 'N/A')} | Origem: OSS+Lojas"
        
        venda_formatada = {
            'id': venda_id,
            'numero_venda': numero_venda,
            'cliente_id': cliente_uuid,
            'loja_id': loja_uuid,
            'vendedor_id': vendedor_uuid,
            'data_venda': data_venda,
            'valor_total': valor_total,
            'valor_entrada': valor_entrada,
            'nome_cliente_temp': nome_cliente_temp,
            'observacoes': observacoes,
            'status': 'ATIVO',
            'cancelado': False,
            'data_cancelamento': None,
            'motivo_cancelamento': None,
            'created_at': timestamp_atual,
            'updated_at': timestamp_atual,
            'created_by': 'IMPORT_SCRIPT',
            'updated_by': 'IMPORT_SCRIPT',
            'deleted_at': None,
            'version': 1,
            'tipo_operacao': 'VENDA',
            'forma_pagamento': None
        }
        
        vendas_final.append(venda_formatada)
    
    df_final = pd.DataFrame(vendas_final)
    
    print(f"✅ Vendas formatadas: {len(df_final):,}")
    
    # Estatísticas finais
    stats = {
        'Total vendas': len(df_final),
        'Com cliente_id': df_final['cliente_id'].notna().sum(),
        'Com loja_id': df_final['loja_id'].notna().sum(),
        'Com vendedor_id': df_final['vendedor_id'].notna().sum(),
        'Valor total': f"R$ {df_final['valor_total'].sum():,.2f}"
    }
    
    print("\n📊 ESTATÍSTICAS FINAIS:")
    for chave, valor in stats.items():
        print(f"   {chave}: {valor}")
    
    return df_final

def validar_constraints_finais(vendas_df):
    """Validar constraints da tabela vendas.vendas"""
    print("\n🔍 VALIDAÇÃO CONSTRAINTS TABELA")
    print("=" * 35)
    
    errors = []
    
    # Campos NOT NULL obrigatórios
    campos_obrigatorios = {
        'id': 'ID único',
        'numero_venda': 'Número da venda',
        'loja_id': 'ID da loja', 
        'data_venda': 'Data da venda',
        'valor_total': 'Valor total'
    }
    
    for campo, descricao in campos_obrigatorios.items():
        nulls = vendas_df[campo].isna().sum()
        if nulls > 0:
            errors.append(f"❌ {descricao} ({campo}): {nulls} nulos")
        else:
            print(f"✅ {descricao}: OK")
    
    # Constraint única (loja_id, numero_venda)
    duplicates = vendas_df.duplicated(subset=['loja_id', 'numero_venda']).sum()
    if duplicates > 0:
        errors.append(f"❌ Duplicatas (loja_id, numero_venda): {duplicates}")
    else:
        print("✅ Constraint única: OK")
    
    # Valores positivos
    valores_negativos = (vendas_df['valor_total'] < 0).sum()
    if valores_negativos > 0:
        errors.append(f"❌ Valores negativos: {valores_negativos}")
    else:
        print("✅ Valores positivos: OK")
    
    # Entrada <= Total
    entrada_maior = (vendas_df['valor_entrada'] > vendas_df['valor_total']).sum()
    if entrada_maior > 0:
        errors.append(f"❌ Entrada > Total: {entrada_maior}")
    else:
        print("✅ Entrada <= Total: OK")
    
    if errors:
        print("\n❌ ERROS ENCONTRADOS:")
        for error in errors:
            print(f"   {error}")
        return False
    else:
        print("\n✅ TODAS AS VALIDAÇÕES PASSARAM")
        return True

def main():
    print("🚀 FINALIZAÇÃO: VENDAS COMPLETAS PARA TABELA")
    print("=" * 50)
    
    # 1. Carregar vendas unidas
    vendas_df = carregar_vendas_unidas()
    if vendas_df is None:
        return
    
    # 2. Carregar clientes UUID
    clientes_uuid_df = carregar_clientes_uuid()
    if clientes_uuid_df is None:
        return
    
    # 3. Mapear cliente UUID
    vendas_com_uuid = mapear_cliente_uuid(vendas_df, clientes_uuid_df)
    if vendas_com_uuid is None:
        return
    
    # 4. Formatar para tabela
    vendas_final = formatar_para_tabela_vendas(vendas_com_uuid)
    
    # 5. Validar constraints
    if not validar_constraints_finais(vendas_final):
        print("❌ Validação falhou")
        return
    
    # 6. Salvar resultado final
    output_path = Path("data/vendas_para_importar/vendas_tabela_final.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    vendas_final.to_csv(output_path, index=False)
    
    print(f"\n💾 ARQUIVO FINAL SALVO: {output_path}")
    print(f"📊 Total de vendas: {len(vendas_final):,}")
    print(f"💰 Valor total: R$ {vendas_final['valor_total'].sum():,.2f}")
    
    print("\n🎯 PRONTO PARA IMPORTAR NA TABELA vendas.vendas!")
    print("📋 Comando sugerido:")
    print(f"   COPY vendas.vendas FROM '{output_path.absolute()}' CSV HEADER;")

if __name__ == "__main__":
    main()