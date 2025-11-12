#!/usr/bin/env python3
"""
Script para corrigir estrutura OSS para tabela vendas.itens_venda real
"""

import pandas as pd
import uuid
from pathlib import Path
from datetime import datetime
import re

def classificar_tipo_produto(codigo, descricao):
    """Classifica o tipo de produto baseado no código e descrição"""
    if pd.isna(codigo) and pd.isna(descricao):
        return 'OUTROS'
    
    codigo_str = str(codigo).upper() if not pd.isna(codigo) else ''
    desc_str = str(descricao).upper() if not pd.isna(descricao) else ''
    texto_completo = f"{codigo_str} {desc_str}"
    
    # Classificação por padrões
    if any(palavra in texto_completo for palavra in ['ARMACAO', 'ARMAÇÃO', 'ARO', 'OCULOS', 'ÓCULOS', 'METAL', 'ACETATO', 'NYLON']):
        return 'ARMAÇÃO'
    elif any(palavra in texto_completo for palavra in ['LENTE', 'BLUE', 'CR', 'AR', 'MULTI', 'FOTO', 'SOLAR', 'COLORIDA', 'INCOLOR']):
        return 'LENTE'
    elif any(palavra in texto_completo for palavra in ['ESTOJO', 'CASE']):
        return 'ESTOJO'
    elif any(palavra in texto_completo for palavra in ['CORDAO', 'CORDÃO']):
        return 'CORDÃO'
    elif any(palavra in texto_completo for palavra in ['FLANELA', 'PANO']):
        return 'FLANELA'
    elif any(palavra in texto_completo for palavra in ['SPRAY', 'LIMPEZA']):
        return 'SPRAY LIMPEZA'
    elif any(palavra in texto_completo for palavra in ['CONCERTO', 'AJUSTE', 'PASSAGEM']):
        return 'ACESSÓRIO'
    else:
        return 'OUTROS'

def extrair_marca_modelo(codigo, descricao):
    """Extrai marca e modelo quando possível"""
    if pd.isna(descricao):
        descricao = ''
    
    desc_str = str(descricao).upper()
    
    # Marcas conhecidas
    marcas_conhecidas = [
        'MELLO', 'BELLATIS', 'TNG', 'BULGET', 'VICTORIA SECRET', 'SATO',
        'RAYBAN', 'OAKLEY', 'CHILLI BEANS', 'GUESS', 'CALVIN KLEIN'
    ]
    
    marca = None
    for marca_conhecida in marcas_conhecidas:
        if marca_conhecida in desc_str:
            marca = marca_conhecida
            break
    
    # Se não encontrou marca específica, usar primeira palavra
    if not marca and desc_str:
        primeira_palavra = desc_str.split()[0] if desc_str.split() else None
        if primeira_palavra and len(primeira_palavra) > 2:
            marca = primeira_palavra
    
    return marca, None  # Modelo será None por enquanto

def main():
    print("=== CORREÇÃO ESTRUTURA PARA TABELA REAL ===")
    print(f"Início: {datetime.now()}")
    
    # Carregar arquivo atual
    arquivo_atual = "data/processados/OSS_ITENS_FINAL_SUPABASE_20251105_142709.csv"
    print(f"\n1. Carregando: {arquivo_atual}")
    df_oss = pd.read_csv(arquivo_atual, dtype=str, low_memory=False)
    print(f"   - {len(df_oss)} itens carregados")
    
    # Carregar dados completos para obter informações adicionais
    arquivo_completo = "data/processados/OSS_ITENS_CRUZADOS_POR_NUMERO_20251105_142151.csv"
    if Path(arquivo_completo).exists():
        print(f"2. Carregando dados completos: {arquivo_completo}")
        df_completo = pd.read_csv(arquivo_completo, dtype=str, low_memory=False)
        print(f"   - {len(df_completo)} registros completos")
        
        # Fazer merge para obter dados adicionais
        df_merged = df_oss.merge(
            df_completo[['item_venda_uuid', 'loja_nome', 'cliente_nome', 'data_compra']],
            on='item_venda_uuid',
            how='left'
        )
    else:
        df_merged = df_oss.copy()
        df_merged['loja_nome'] = None
        df_merged['cliente_nome'] = None
        df_merged['data_compra'] = None
    
    print(f"\n3. Mapeando para estrutura da tabela...")
    
    # Criar DataFrame com estrutura correta
    df_final = pd.DataFrame()
    
    # Campos obrigatórios da tabela
    df_final['id'] = df_merged['item_venda_uuid']  # UUID do item
    df_final['venda_id'] = df_merged['venda_id'].str.replace('venda_', '').str.replace('.0', '')  # Limpar venda_id
    
    # Classificar tipo de produto
    print("   - Classificando tipos de produto...")
    df_final['tipo_produto'] = df_merged.apply(
        lambda row: classificar_tipo_produto(row['produto_codigo'], row['produto_descricao']), 
        axis=1
    )
    
    # Descrição (obrigatório)
    df_final['descricao'] = df_merged['produto_descricao'].fillna(
        df_merged['produto_codigo'].astype(str)
    ).str[:300]  # Limitar a 300 caracteres
    
    # Extrair marca e modelo
    print("   - Extraindo marcas e modelos...")
    marcas_modelos = df_merged.apply(
        lambda row: extrair_marca_modelo(row['produto_codigo'], row['produto_descricao']), 
        axis=1
    )
    df_final['marca'] = [mm[0] for mm in marcas_modelos]
    df_final['modelo'] = [mm[1] for mm in marcas_modelos]
    
    # Códigos de produto
    df_final['codigo_produto'] = df_merged['produto_codigo'].str[:100]
    df_final['codigo_barras'] = None  # Não temos essa informação
    
    # Campos adicionais (opcionais)
    df_final['cor'] = None
    df_final['tamanho'] = None
    df_final['material'] = None
    df_final['fornecedor'] = None
    df_final['codigo_fornecedor'] = None
    
    # Quantidade e valores (obrigatórios)
    df_final['quantidade'] = pd.to_numeric(df_merged['quantidade'], errors='coerce').fillna(1).astype(int)
    df_final['valor_unitario'] = pd.to_numeric(df_merged['valor_unitario'], errors='coerce').fillna(0)
    df_final['valor_desconto'] = pd.to_numeric(df_merged['desconto'], errors='coerce').fillna(0)
    
    # Campos de estoque e encomenda
    df_final['possui_estoque'] = True
    df_final['requer_encomenda'] = False
    df_final['data_encomenda'] = None
    df_final['data_prevista_chegada'] = None
    
    # Observações
    df_final['observacoes'] = df_merged['observacoes']
    
    # Timestamps
    timestamp_now = datetime.now().isoformat()
    df_final['created_at'] = df_merged['created_at'].fillna(timestamp_now)
    df_final['updated_at'] = df_merged['updated_at'].fillna(timestamp_now)
    df_final['deleted_at'] = None
    df_final['updated_by'] = 'IMPORTACAO_OSS'
    
    print(f"\n4. Validando estrutura...")
    
    # Validações obrigatórias
    erros = []
    
    # Campos obrigatórios não podem ser nulos
    campos_obrigatorios = ['id', 'venda_id', 'tipo_produto', 'descricao', 'quantidade', 'valor_unitario']
    for campo in campos_obrigatorios:
        nulos = df_final[campo].isna().sum()
        if nulos > 0:
            erros.append(f"{campo}: {nulos} valores nulos")
        else:
            print(f"   ✅ {campo}: OK")
    
    # Validar tipos de produto permitidos
    tipos_validos = ['ARMAÇÃO', 'LENTE', 'LENTE DE CONTATO', 'ESTOJO', 'CORDÃO', 'FLANELA', 'SPRAY LIMPEZA', 'ACESSÓRIO', 'OUTROS']
    tipos_invalidos = df_final[~df_final['tipo_produto'].isin(tipos_validos)]['tipo_produto'].unique()
    if len(tipos_invalidos) > 0:
        erros.append(f"Tipos de produto inválidos: {tipos_invalidos}")
    else:
        print(f"   ✅ tipos_produto: OK")
    
    # Validar valores positivos
    if (df_final['quantidade'] <= 0).any():
        erros.append("Quantidades <= 0 encontradas")
    else:
        print(f"   ✅ quantidade: OK")
    
    if (df_final['valor_unitario'] < 0).any():
        erros.append("Valores unitários negativos encontrados")
    else:
        print(f"   ✅ valor_unitario: OK")
    
    if (df_final['valor_desconto'] < 0).any():
        erros.append("Valores de desconto negativos encontrados")
    else:
        print(f"   ✅ valor_desconto: OK")
    
    # Validar UUIDs únicos
    if df_final['id'].nunique() != len(df_final):
        erros.append("IDs não são únicos")
    else:
        print(f"   ✅ id únicos: OK")
    
    if erros:
        print(f"\n❌ ERROS ENCONTRADOS:")
        for erro in erros:
            print(f"   - {erro}")
        return
    
    print(f"\n=== ESTATÍSTICAS FINAIS ===")
    print(f"Total de itens: {len(df_final)}")
    print(f"Tipos de produto:")
    tipo_counts = df_final['tipo_produto'].value_counts()
    for tipo, count in tipo_counts.items():
        print(f"  - {tipo}: {count}")
    
    print(f"Marcas principais:")
    marca_counts = df_final['marca'].value_counts().head(10)
    for marca, count in marca_counts.items():
        if marca:
            print(f"  - {marca}: {count}")
    
    valor_total = df_final['valor_unitario'].sum()
    print(f"Valor total: R$ {valor_total:,.2f}")
    
    # Salvar arquivo final
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    arquivo_final = Path("data/processados") / f"OSS_ITENS_TABELA_REAL_{timestamp}.csv"
    
    # Reordenar colunas conforme tabela
    colunas_tabela = [
        'id', 'venda_id', 'tipo_produto', 'descricao', 'marca', 'modelo',
        'codigo_produto', 'codigo_barras', 'cor', 'tamanho', 'material',
        'fornecedor', 'codigo_fornecedor', 'quantidade', 'valor_unitario',
        'valor_desconto', 'possui_estoque', 'requer_encomenda',
        'data_encomenda', 'data_prevista_chegada', 'observacoes',
        'created_at', 'updated_at', 'deleted_at', 'updated_by'
    ]
    
    df_final_ordenado = df_final[colunas_tabela]
    df_final_ordenado.to_csv(arquivo_final, index=False, encoding='utf-8')
    
    print(f"\n✅ ARQUIVO CORRIGIDO SALVO: {arquivo_final}")
    
    print(f"\n📋 COMANDO SQL PARA IMPORTAÇÃO:")
    print(f"```sql")
    print(f"COPY vendas.itens_venda (")
    print(f"    id, venda_id, tipo_produto, descricao, marca, modelo,")
    print(f"    codigo_produto, codigo_barras, cor, tamanho, material,")
    print(f"    fornecedor, codigo_fornecedor, quantidade, valor_unitario,")
    print(f"    valor_desconto, possui_estoque, requer_encomenda,")
    print(f"    data_encomenda, data_prevista_chegada, observacoes,")
    print(f"    created_at, updated_at, deleted_at, updated_by")
    print(f") FROM '{arquivo_final.name}'")
    print(f"WITH (FORMAT CSV, HEADER);")
    print(f"```")
    
    print(f"\n🎉 PRONTO PARA IMPORTAÇÃO NA TABELA REAL!")
    print(f"Fim: {datetime.now()}")
    
    return arquivo_final

if __name__ == "__main__":
    main()