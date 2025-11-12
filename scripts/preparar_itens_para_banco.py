#!/usr/bin/env python3
"""
Script para fazer cruzamento rápido e preparar itens para upload no Supabase
"""

import pandas as pd
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def fazer_cruzamento_rapido():
    """
    Faz cruzamento usando dados já validados e prepara para upload
    """
    print("🎯 === CRUZAMENTO RÁPIDO PARA UPLOAD === 🎯")
    
    # Arquivos necessários
    itens_file = 'data/itens_venda_CLASSIFICADOS_20251105_094225.csv'
    cruzamentos_file = 'data/cruzamentos_completos_dav_vendas_20251105_032132.csv'
    
    try:
        print(f"📄 Carregando itens...")
        df_itens = pd.read_csv(itens_file)
        print(f"📊 Itens: {len(df_itens):,}")
        
        print(f"📄 Carregando cruzamentos...")
        df_cruzamentos = pd.read_csv(cruzamentos_file)
        print(f"📊 Cruzamentos: {len(df_cruzamentos):,}")
        
        # Verificar estrutura dos cruzamentos
        print(f"📋 Colunas cruzamentos: {', '.join(df_cruzamentos.columns)}")
        
        # Fazer merge baseado no DAV
        print(f"\n🔄 Fazendo cruzamento...")
        
        # Converter DAV para numérico para matching
        df_itens['dav_num'] = pd.to_numeric(df_itens['dav_numero'], errors='coerce')
        df_cruzamentos['dav_num'] = pd.to_numeric(df_cruzamentos['numero_os'], errors='coerce')
        
        # Merge
        df_merged = df_itens.merge(
            df_cruzamentos[['dav_num', 'venda_id']], 
            on='dav_num', 
            how='left'
        )
        
        # Preencher venda_id com venda_id onde disponível
        df_merged['venda_id'] = df_merged['venda_id_y'].fillna(df_merged['venda_id_x']).fillna('')
        
        # Estatísticas
        com_venda = (df_merged['venda_id'] != '').sum()
        sem_venda = (df_merged['venda_id'] == '').sum()
        
        print(f"\n📊 === RESULTADOS CRUZAMENTO === 📊")
        print(f"✅ Com venda_id: {com_venda:,} ({com_venda/len(df_merged)*100:.1f}%)")
        print(f"❌ Sem venda_id: {sem_venda:,} ({sem_venda/len(df_merged)*100:.1f}%)")
        
        # Remover colunas auxiliares
        df_final = df_merged.drop(['dav_num', 'venda_id_y'], axis=1)
        
        # Renomear para estrutura final
        if 'venda_id_x' in df_final.columns:
            df_final = df_final.drop('venda_id_x', axis=1)
        
        # Para o banco, só queremos itens COM venda_id
        df_para_banco = df_final[df_final['venda_id'] != ''].copy()
        
        print(f"🎯 Itens para banco: {len(df_para_banco):,}")
        
        # Limpar campos que não existem na tabela
        colunas_tabela = [
            'id', 'venda_id', 'tipo_produto', 'descricao', 'marca', 'modelo',
            'codigo_produto', 'codigo_barras', 'cor', 'tamanho', 'material',
            'fornecedor', 'codigo_fornecedor', 'quantidade', 'valor_unitario',
            'valor_desconto', 'possui_estoque', 'requer_encomenda',
            'data_encomenda', 'data_prevista_chegada', 'observacoes',
            'created_at', 'updated_at', 'deleted_at', 'updated_by'
        ]
        
        # Selecionar apenas colunas da tabela
        df_banco = df_para_banco[colunas_tabela].copy()
        
        # Verificações finais
        print(f"\n✅ === VERIFICAÇÕES === ✅")
        
        # UUIDs válidos
        uuid_validos = df_banco['venda_id'].str.len().eq(36).all() if len(df_banco) > 0 else True
        print(f"   UUIDs venda_id: {'✅' if uuid_validos else '❌'}")
        
        # Valores obrigatórios
        nulos_tipo = df_banco['tipo_produto'].isnull().sum()
        nulos_desc = df_banco['descricao'].isnull().sum()
        nulos_qtd = df_banco['quantidade'].isnull().sum()
        
        print(f"   Tipo produto nulos: {nulos_tipo} ({'✅' if nulos_tipo == 0 else '❌'})")
        print(f"   Descrição nulos: {nulos_desc} ({'✅' if nulos_desc == 0 else '❌'})")
        print(f"   Quantidade nulos: {nulos_qtd} ({'✅' if nulos_qtd == 0 else '❌'})")
        
        # Valores válidos
        qtd_positivas = (df_banco['quantidade'] > 0).all() if len(df_banco) > 0 else True
        valores_positivos = (df_banco['valor_unitario'] >= 0).all() if len(df_banco) > 0 else True
        
        print(f"   Quantidades positivas: {'✅' if qtd_positivas else '❌'}")
        print(f"   Valores positivos: {'✅' if valores_positivos else '❌'}")
        
        # Salvar arquivo para banco
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        arquivo_banco = f'data/ITENS_VENDA_PARA_BANCO_{timestamp}.csv'
        
        df_banco.to_csv(arquivo_banco, index=False)
        
        print(f"\n💾 === ARQUIVO PARA BANCO === 💾")
        print(f"📄 Arquivo: {arquivo_banco}")
        print(f"📊 Registros: {len(df_banco):,}")
        print(f"📋 Colunas: {df_banco.shape[1]} (exatas da tabela)")
        print(f"✅ Status: Pronto para upload no Supabase")
        
        # Análise por tipo de produto
        print(f"\n🔍 === ANÁLISE POR TIPO === 🔍")
        tipos = df_banco['tipo_produto'].value_counts().head(10)
        for tipo, count in tipos.items():
            print(f"   {tipo}: {count:,}")
        
        return arquivo_banco
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print("🎯 === PREPARAÇÃO FINAL PARA BANCO === 🎯")
    
    arquivo_final = fazer_cruzamento_rapido()
    
    if arquivo_final:
        print(f"\n🎉 === PRONTO PARA UPLOAD === 🎉")
        print(f"📄 Arquivo: {arquivo_final}")
        print(f"🚀 Comando: Fazer upload no Supabase tabela itens_venda")
        print(f"⚠️ Importante: Verificar se todas as vendas referenciadas existem")
    else:
        print(f"❌ Falha na preparação")
    
    print(f"📅 Processado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()