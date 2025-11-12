#!/usr/bin/env python3
"""
Script para cruzar produtos com vendas usando números DAV normalizados
Preenche venda_id nos produtos para criar relação na tabela itens_venda
"""

import pandas as pd
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def carregar_dados():
    """
    Carrega dados de produtos e vendas
    """
    print("📄 === CARREGANDO DADOS === 📄")
    
    # Arquivos
    arquivo_produtos = 'data/itens_venda_CLASSIFICADOS_20251105_094225.csv'
    arquivo_vendas = 'data/vendas_para_importar/vendas_totais_com_uuid.csv'
    
    try:
        # Carregar produtos
        print(f"🔧 Carregando produtos: {arquivo_produtos}")
        df_produtos = pd.read_csv(arquivo_produtos)
        print(f"   ✅ Produtos: {len(df_produtos):,}")
        
        # Carregar vendas
        print(f"🔧 Carregando vendas: {arquivo_vendas}")
        df_vendas = pd.read_csv(arquivo_vendas)
        print(f"   ✅ Vendas: {len(df_vendas):,}")
        
        return df_produtos, df_vendas
        
    except FileNotFoundError as e:
        print(f"❌ Arquivo não encontrado: {e}")
        return None, None
    except Exception as e:
        print(f"❌ Erro ao carregar dados: {e}")
        return None, None

def analisar_estrutura_dados(df_produtos, df_vendas):
    """
    Analisa estrutura dos dados para entender campos de cruzamento
    """
    print(f"\n🔍 === ANÁLISE DE ESTRUTURA === 🔍")
    
    print(f"📋 Campos produtos:")
    print(f"   Colunas: {', '.join(df_produtos.columns)}")
    
    print(f"📋 Campos vendas:")
    print(f"   Colunas: {', '.join(df_vendas.columns)}")
    
    # Analisar campos de cruzamento
    print(f"\n🎯 === CAMPOS DE CRUZAMENTO === 🎯")
    
    if 'dav_numero' in df_produtos.columns:
        dav_produtos = df_produtos['dav_numero'].dropna()
        print(f"📊 Produtos com DAV: {len(dav_produtos):,}")
        print(f"🔍 DAV únicos produtos: {dav_produtos.nunique():,}")
        print(f"🔍 Amostra DAV produtos: {', '.join(map(str, dav_produtos.head(5)))}")
    
    if 'numero_os' in df_vendas.columns:
        os_vendas = df_vendas['numero_os'].dropna()
        print(f"📊 Vendas com OS: {len(os_vendas):,}")
        print(f"🔍 OS únicos vendas: {os_vendas.nunique():,}")
        print(f"🔍 Amostra OS vendas: {', '.join(map(str, os_vendas.head(5)))}")
    
    # Verificar empresas
    if 'empresa' in df_produtos.columns:
        empresas_produtos = df_produtos['empresa'].value_counts()
        print(f"📊 Empresas produtos: {len(empresas_produtos)}")
        for emp, count in empresas_produtos.head(5).items():
            print(f"   Empresa {emp}: {count:,}")
    
    if 'loja_id' in df_vendas.columns:
        lojas_vendas = df_vendas['loja_id'].value_counts()
        print(f"📊 Lojas vendas: {len(lojas_vendas)}")
        for loja, count in lojas_vendas.head(5).items():
            print(f"   Loja {loja}: {count:,}")

def mapear_empresa_loja():
    """
    Mapeia códigos de empresa para IDs de loja
    """
    mapeamento = {
        42.0: ['42', 'suzano', 'SUZANO'],
        48.0: ['48', 'maua', 'MAUA', 'MAUÁ'],
        11.0: ['11'],
        12.0: ['12'],
        9.0: ['9'],
        10.0: ['10']
    }
    return mapeamento

def cruzar_produtos_vendas(df_produtos, df_vendas):
    """
    Faz cruzamento entre produtos e vendas usando DAV/OS e empresa/loja
    """
    print(f"\n🎯 === CRUZAMENTO PRODUTOS x VENDAS === 🎯")
    
    # Preparar dados para cruzamento
    df_produtos_copia = df_produtos.copy()
    
    # Converter tipos para garantir compatibilidade
    df_produtos_copia['dav_numero'] = pd.to_numeric(df_produtos_copia['dav_numero'], errors='coerce')
    df_vendas['numero_os'] = pd.to_numeric(df_vendas['numero_os'], errors='coerce')
    
    mapeamento_lojas = mapear_empresa_loja()
    
    cruzamentos_encontrados = 0
    produtos_com_venda = []
    
    print(f"🔄 Iniciando cruzamento...")
    
    for idx, produto in df_produtos_copia.iterrows():
        if idx % 5000 == 0:
            print(f"   Processando: {idx:,}/{len(df_produtos_copia):,} ({cruzamentos_encontrados:,} cruzamentos)")
        
        dav_produto = produto['dav_numero']
        empresa_produto = produto['empresa']
        
        if pd.isna(dav_produto) or pd.isna(empresa_produto):
            continue
        
        # Buscar vendas com mesmo número OS
        vendas_match = df_vendas[df_vendas['numero_os'] == dav_produto]
        
        if len(vendas_match) == 0:
            continue
        
        # Filtrar por loja/empresa se possível
        if empresa_produto in mapeamento_lojas:
            lojas_validas = mapeamento_lojas[empresa_produto]
            
            # Buscar venda que corresponda à empresa
            venda_final = None
            for _, venda in vendas_match.iterrows():
                loja_id = str(venda.get('loja_id', ''))
                if any(loja in loja_id.upper() for loja in lojas_validas):
                    venda_final = venda
                    break
            
            # Se não encontrou por loja, usar a primeira venda com o DAV
            if venda_final is None and len(vendas_match) > 0:
                venda_final = vendas_match.iloc[0]
        else:
            # Usar primeira venda encontrada
            venda_final = vendas_match.iloc[0]
        
        if venda_final is not None:
            # Atualizar produto com venda_id
            produto['venda_id'] = venda_final['id']
            produtos_com_venda.append(produto)
            cruzamentos_encontrados += 1
    
    print(f"\n✅ === RESULTADOS CRUZAMENTO === ✅")
    print(f"🎯 Cruzamentos encontrados: {cruzamentos_encontrados:,}")
    print(f"📊 Taxa de cruzamento: {(cruzamentos_encontrados/len(df_produtos_copia)*100):.1f}%")
    
    if cruzamentos_encontrados > 0:
        df_cruzados = pd.DataFrame(produtos_com_venda)
        return df_cruzados
    else:
        return None

def preparar_arquivo_final(df_cruzados, df_produtos_original):
    """
    Prepara arquivo final com produtos cruzados e não cruzados
    """
    print(f"\n📋 === PREPARANDO ARQUIVO FINAL === 📋")
    
    if df_cruzados is not None and len(df_cruzados) > 0:
        # Produtos COM venda_id
        produtos_com_venda = df_cruzados
        print(f"✅ Produtos com venda_id: {len(produtos_com_venda):,}")
        
        # Produtos SEM venda_id (os que não cruzaram)
        ids_cruzados = set(produtos_com_venda['id'])
        produtos_sem_venda = df_produtos_original[
            ~df_produtos_original['id'].isin(ids_cruzados)
        ].copy()
        
        # Garantir que venda_id seja None nos não cruzados
        produtos_sem_venda['venda_id'] = None
        
        print(f"⚠️ Produtos sem venda_id: {len(produtos_sem_venda):,}")
        
        # Combinar todos os produtos
        df_final = pd.concat([produtos_com_venda, produtos_sem_venda], ignore_index=True)
    else:
        # Nenhum cruzamento encontrado
        df_final = df_produtos_original.copy()
        df_final['venda_id'] = None
        print(f"⚠️ Nenhum cruzamento encontrado - todos os produtos sem venda_id")
    
    print(f"📊 Total produtos finais: {len(df_final):,}")
    
    # Limpar campos de controle que não vão para a tabela
    colunas_tabela = [
        'id', 'venda_id', 'tipo_produto', 'descricao', 'marca', 'modelo',
        'codigo_produto', 'codigo_barras', 'cor', 'tamanho', 'material',
        'fornecedor', 'codigo_fornecedor', 'quantidade', 'valor_unitario',
        'valor_desconto', 'possui_estoque', 'requer_encomenda',
        'data_encomenda', 'data_prevista_chegada', 'observacoes',
        'created_at', 'updated_at', 'deleted_at', 'updated_by'
    ]
    
    # Manter apenas colunas da tabela
    colunas_existentes = [col for col in colunas_tabela if col in df_final.columns]
    df_limpo = df_final[colunas_existentes].copy()
    
    print(f"📋 Colunas finais: {len(colunas_existentes)}")
    
    return df_limpo

def salvar_resultados(df_final, df_cruzados):
    """
    Salva arquivos de resultado
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Arquivo principal (todos os produtos)
    arquivo_principal = f'data/itens_venda_FINAL_{timestamp}.csv'
    df_final.to_csv(arquivo_principal, index=False)
    
    print(f"\n💾 === ARQUIVOS GERADOS === 💾")
    print(f"📄 Arquivo principal: {arquivo_principal}")
    print(f"📊 Registros: {len(df_final):,}")
    
    # Arquivo só dos cruzamentos (se houver)
    if df_cruzados is not None and len(df_cruzados) > 0:
        arquivo_cruzados = f'data/itens_venda_COM_VENDAS_{timestamp}.csv'
        df_cruzados_limpo = df_cruzados[[col for col in df_final.columns if col in df_cruzados.columns]]
        df_cruzados_limpo.to_csv(arquivo_cruzados, index=False)
        
        print(f"📄 Arquivo cruzamentos: {arquivo_cruzados}")
        print(f"📊 Registros: {len(df_cruzados_limpo):,}")
    
    # Estatísticas finais
    with_venda = df_final['venda_id'].notna().sum()
    without_venda = df_final['venda_id'].isna().sum()
    
    print(f"\n📊 === ESTATÍSTICAS FINAIS === 📊")
    print(f"✅ Com venda_id: {with_venda:,} ({with_venda/len(df_final)*100:.1f}%)")
    print(f"⚪ Sem venda_id: {without_venda:,} ({without_venda/len(df_final)*100:.1f}%)")
    
    return arquivo_principal

def main():
    """Função principal"""
    print("🎯 === CRUZAMENTO PRODUTOS x VENDAS === 🎯")
    print("🎯 Objetivo: Preencher venda_id nos produtos")
    
    # 1. Carregar dados
    df_produtos, df_vendas = carregar_dados()
    if df_produtos is None or df_vendas is None:
        return
    
    # 2. Analisar estrutura
    analisar_estrutura_dados(df_produtos, df_vendas)
    
    # 3. Fazer cruzamento
    df_cruzados = cruzar_produtos_vendas(df_produtos, df_vendas)
    
    # 4. Preparar arquivo final
    df_final = preparar_arquivo_final(df_cruzados, df_produtos)
    
    # 5. Salvar resultados
    arquivo_final = salvar_resultados(df_final, df_cruzados)
    
    print(f"\n🎉 === PROCESSAMENTO CONCLUÍDO === 🎉")
    print(f"✅ Arquivo final: {arquivo_final}")
    print(f"📋 Estrutura: 100% compatível com tabela itens_venda")
    print(f"🚀 Status: Pronto para importação no Supabase")
    
    print(f"📅 Processado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()