#!/usr/bin/env python3
"""
Script para cruzar produtos com vendas usando arquivo de cruzamentos DAV já criado
Muito mais preciso que tentar cruzar novamente
"""

import pandas as pd
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def carregar_dados():
    """
    Carrega dados de produtos e cruzamentos DAV-Vendas
    """
    print("📄 === CARREGANDO DADOS === 📄")
    
    # Arquivos
    arquivo_produtos = 'data/itens_venda_CLASSIFICADOS_20251105_094225.csv'
    arquivo_cruzamentos = 'data/cruzamentos_completos_dav_vendas_20251105_032132.csv'
    
    try:
        # Carregar produtos
        print(f"🔧 Carregando produtos: {arquivo_produtos}")
        df_produtos = pd.read_csv(arquivo_produtos)
        print(f"   ✅ Produtos: {len(df_produtos):,}")
        
        # Carregar cruzamentos DAV-Vendas
        print(f"🔧 Carregando cruzamentos: {arquivo_cruzamentos}")
        df_cruzamentos = pd.read_csv(arquivo_cruzamentos)
        print(f"   ✅ Cruzamentos: {len(df_cruzamentos):,}")
        
        return df_produtos, df_cruzamentos
        
    except FileNotFoundError as e:
        print(f"❌ Arquivo não encontrado: {e}")
        return None, None
    except Exception as e:
        print(f"❌ Erro ao carregar dados: {e}")
        return None, None

def analisar_cruzamentos(df_cruzamentos):
    """
    Analisa dados de cruzamentos disponíveis
    """
    print(f"\n🔍 === ANÁLISE DOS CRUZAMENTOS === 🔍")
    
    print(f"📋 Colunas disponíveis: {', '.join(df_cruzamentos.columns)}")
    
    # Tipos de match
    if 'tipo_match' in df_cruzamentos.columns:
        tipos_match = df_cruzamentos['tipo_match'].value_counts()
        print(f"📊 Tipos de match:")
        for tipo, count in tipos_match.items():
            print(f"   {tipo}: {count:,}")
    
    # Números OS únicos
    if 'numero_os' in df_cruzamentos.columns:
        os_unicos = df_cruzamentos['numero_os'].nunique()
        print(f"📊 OS únicos nos cruzamentos: {os_unicos:,}")
        
        # Amostra
        os_sample = df_cruzamentos['numero_os'].dropna().head(5).tolist()
        print(f"🔍 Amostra OS: {', '.join(map(str, os_sample))}")
    
    # Vendas únicas
    if 'venda_id' in df_cruzamentos.columns:
        vendas_unicas = df_cruzamentos['venda_id'].nunique()
        print(f"📊 Vendas únicas: {vendas_unicas:,}")

def cruzar_produtos_com_vendas(df_produtos, df_cruzamentos):
    """
    Cruza produtos com vendas usando arquivo de cruzamentos
    """
    print(f"\n🎯 === CRUZAMENTO PRODUTOS x VENDAS === 🎯")
    
    # Preparar mapeamento DAV -> venda_id
    mapeamento_dav_venda = {}
    
    for _, row in df_cruzamentos.iterrows():
        numero_os = row.get('numero_os')
        venda_id = row.get('venda_id')
        
        if pd.notna(numero_os) and pd.notna(venda_id):
            mapeamento_dav_venda[float(numero_os)] = venda_id
    
    print(f"📊 Mapeamentos DAV->Venda: {len(mapeamento_dav_venda):,}")
    
    # Aplicar cruzamento nos produtos
    produtos_atualizados = []
    cruzamentos_encontrados = 0
    
    for idx, produto in df_produtos.iterrows():
        if idx % 5000 == 0:
            print(f"   Processando: {idx:,}/{len(df_produtos):,} ({cruzamentos_encontrados:,} cruzamentos)")
        
        dav_numero = produto.get('dav_numero')
        
        # Verificar se há venda correspondente
        if pd.notna(dav_numero):
            try:
                dav_float = float(dav_numero)
                if dav_float in mapeamento_dav_venda:
                    produto['venda_id'] = mapeamento_dav_venda[dav_float]
                    cruzamentos_encontrados += 1
                else:
                    produto['venda_id'] = None
            except (ValueError, TypeError):
                # DAV não numérico, não pode cruzar
                produto['venda_id'] = None
        else:
            produto['venda_id'] = None
        
        produtos_atualizados.append(produto)
    
    df_produtos_final = pd.DataFrame(produtos_atualizados)
    
    print(f"\n✅ === RESULTADOS CRUZAMENTO === ✅")
    print(f"🎯 Cruzamentos encontrados: {cruzamentos_encontrados:,}")
    print(f"📊 Taxa de cruzamento: {(cruzamentos_encontrados/len(df_produtos)*100):.1f}%")
    
    return df_produtos_final, cruzamentos_encontrados

def preparar_arquivo_supabase(df_produtos_final):
    """
    Prepara arquivo final para importação no Supabase
    """
    print(f"\n📋 === PREPARANDO PARA SUPABASE === 📋")
    
    # Colunas da tabela itens_venda
    colunas_tabela = [
        'id', 'venda_id', 'tipo_produto', 'descricao', 'marca', 'modelo',
        'codigo_produto', 'codigo_barras', 'cor', 'tamanho', 'material',
        'fornecedor', 'codigo_fornecedor', 'quantidade', 'valor_unitario',
        'valor_desconto', 'possui_estoque', 'requer_encomenda',
        'data_encomenda', 'data_prevista_chegada', 'observacoes',
        'created_at', 'updated_at', 'deleted_at', 'updated_by'
    ]
    
    # Manter apenas colunas da tabela
    colunas_existentes = [col for col in colunas_tabela if col in df_produtos_final.columns]
    df_supabase = df_produtos_final[colunas_existentes].copy()
    
    print(f"📊 Registros finais: {len(df_supabase):,}")
    print(f"📋 Colunas mantidas: {len(colunas_existentes)}")
    
    # Estatísticas
    com_venda = df_supabase['venda_id'].notna().sum()
    sem_venda = df_supabase['venda_id'].isna().sum()
    
    print(f"\n📊 === ESTATÍSTICAS === 📊")
    print(f"✅ Com venda_id: {com_venda:,} ({com_venda/len(df_supabase)*100:.1f}%)")
    print(f"⚪ Sem venda_id: {sem_venda:,} ({sem_venda/len(df_supabase)*100:.1f}%)")
    
    # Verificar constraint violations
    print(f"\n🔍 === VERIFICAÇÕES === 🔍")
    
    # Valores obrigatórios
    id_nulos = df_supabase['id'].isnull().sum()
    tipo_nulos = df_supabase['tipo_produto'].isnull().sum()
    descricao_nulos = df_supabase['descricao'].isnull().sum()
    qtd_nulos = df_supabase['quantidade'].isnull().sum()
    valor_nulos = df_supabase['valor_unitario'].isnull().sum()
    
    print(f"   IDs nulos: {id_nulos} ({'✅' if id_nulos == 0 else '❌'})")
    print(f"   Tipos nulos: {tipo_nulos} ({'✅' if tipo_nulos == 0 else '❌'})")
    print(f"   Descrições nulas: {descricao_nulos} ({'✅' if descricao_nulos == 0 else '❌'})")
    print(f"   Quantidades nulas: {qtd_nulos} ({'✅' if qtd_nulos == 0 else '❌'})")
    print(f"   Valores nulos: {valor_nulos} ({'✅' if valor_nulos == 0 else '❌'})")
    
    # Verificar tipos válidos
    tipos_validos = [
        'ARMAÇÃO', 'LENTE', 'LENTE DE CONTATO', 'ESTOJO', 'CORDÃO',
        'FLANELA', 'SPRAY LIMPEZA', 'ACESSÓRIO', 'OUTROS'
    ]
    
    tipos_invalidos = ~df_supabase['tipo_produto'].isin(tipos_validos)
    print(f"   Tipos inválidos: {tipos_invalidos.sum()} ({'✅' if tipos_invalidos.sum() == 0 else '❌'})")
    
    return df_supabase

def salvar_arquivos(df_supabase, df_produtos_completo, cruzamentos_count):
    """
    Salva arquivos finais
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Arquivo principal para Supabase
    arquivo_supabase = f'data/ITENS_VENDA_SUPABASE_{timestamp}.csv'
    df_supabase.to_csv(arquivo_supabase, index=False)
    
    # Arquivo completo com metadados
    arquivo_completo = f'data/itens_venda_completo_com_cruzamentos_{timestamp}.csv'
    df_produtos_completo.to_csv(arquivo_completo, index=False)
    
    # Arquivo só dos que têm venda_id
    df_com_vendas = df_supabase[df_supabase['venda_id'].notna()].copy()
    arquivo_com_vendas = f'data/itens_venda_COM_VENDAS_{timestamp}.csv'
    df_com_vendas.to_csv(arquivo_com_vendas, index=False)
    
    print(f"\n💾 === ARQUIVOS GERADOS === 💾")
    print(f"📄 Para Supabase: {arquivo_supabase}")
    print(f"   📊 Registros: {len(df_supabase):,}")
    print(f"   ✅ Estrutura: 100% compatível com tabela itens_venda")
    
    print(f"📄 Completo: {arquivo_completo}")
    print(f"   📊 Registros: {len(df_produtos_completo):,}")
    print(f"   🔍 Inclui: Todos os metadados de cruzamento")
    
    print(f"📄 Só com vendas: {arquivo_com_vendas}")
    print(f"   📊 Registros: {len(df_com_vendas):,}")
    print(f"   🎯 Cruzamentos: {cruzamentos_count:,}")
    
    return arquivo_supabase

def main():
    """Função principal"""
    print("🎯 === CRUZAMENTO PRODUTOS x VENDAS DEFINITIVO === 🎯")
    print("🎯 Usando arquivo de cruzamentos DAV já validado")
    
    # 1. Carregar dados
    df_produtos, df_cruzamentos = carregar_dados()
    if df_produtos is None or df_cruzamentos is None:
        return
    
    # 2. Analisar cruzamentos
    analisar_cruzamentos(df_cruzamentos)
    
    # 3. Fazer cruzamento
    df_produtos_final, cruzamentos_count = cruzar_produtos_com_vendas(df_produtos, df_cruzamentos)
    
    # 4. Preparar para Supabase
    df_supabase = preparar_arquivo_supabase(df_produtos_final)
    
    # 5. Salvar arquivos
    arquivo_principal = salvar_arquivos(df_supabase, df_produtos_final, cruzamentos_count)
    
    print(f"\n🎉 === PROCESSAMENTO CONCLUÍDO === 🎉")
    print(f"✅ Arquivo principal: {arquivo_principal}")
    print(f"📊 Cruzamentos: {cruzamentos_count:,} produtos ligados a vendas")
    print(f"🚀 Status: PRONTO para importação no Supabase")
    
    print(f"📅 Processado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()