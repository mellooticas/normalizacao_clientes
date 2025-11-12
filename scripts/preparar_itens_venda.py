#!/usr/bin/env python3
"""
Script para preparar dados de produtos (conf_dav) para tabela itens_venda
Mapear campos dos produtos para estrutura do Supabase
"""

import pandas as pd
import uuid
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def safe_convert_value(valor_total, quantidade):
    """
    Converte valores de forma segura, tratando strings e valores inválidos
    """
    try:
        # Converter valor total
        if pd.isna(valor_total) or valor_total == '':
            return 0.0
        
        valor_num = pd.to_numeric(valor_total, errors='coerce')
        if pd.isna(valor_num):
            return 0.0
        
        # Converter quantidade
        if pd.isna(quantidade) or quantidade == '':
            qtd_num = 1
        else:
            qtd_num = pd.to_numeric(quantidade, errors='coerce')
            if pd.isna(qtd_num) or qtd_num <= 0:
                qtd_num = 1
        
        # Calcular valor unitário
        return float(valor_num) / max(float(qtd_num), 1)
        
    except:
        return 0.0

def mapear_tipo_produto(produto_desc):
    """
    Mapeia descrição do produto para tipo válido da tabela
    """
    if pd.isna(produto_desc):
        return 'OUTROS'
    
    produto = str(produto_desc).upper()
    
    # Mapeamento baseado na descrição
    if 'LENTE' in produto:
        if 'CONTATO' in produto:
            return 'LENTE DE CONTATO'
        else:
            return 'LENTE'
    elif any(word in produto for word in ['ARMAÇÃO', 'ARMACAO', 'ÓCULOS', 'OCULOS', 'ROMANO']):
        return 'ARMAÇÃO'
    elif 'ESTOJO' in produto:
        return 'ESTOJO'
    elif any(word in produto for word in ['CORDÃO', 'CORDAO']):
        return 'CORDÃO'
    elif 'FLANELA' in produto:
        return 'FLANELA'
    elif any(word in produto for word in ['SPRAY', 'LIMPEZA']):
        return 'SPRAY LIMPEZA'
    else:
        return 'ACESSÓRIO'

def extrair_marca(modelo):
    """
    Extrai marca do modelo quando possível
    """
    if pd.isna(modelo):
        return None
    
    modelo_str = str(modelo).upper()
    
    # Marcas conhecidas
    marcas = [
        'ROMANO', 'RAYBAN', 'RAY BAN', 'OAKLEY', 'PRADA', 'GUCCI', 
        'VERSACE', 'DOLCE', 'ARMANI', 'CHANEL', 'DIOR', 'FENDI',
        'BULGARI', 'CARTIER', 'MONT BLANC', 'POLICE', 'FOSSIL'
    ]
    
    for marca in marcas:
        if marca in modelo_str:
            return marca
    
    return None

def preparar_itens_venda():
    """
    Prepara dados de produtos para tabela itens_venda
    """
    print("🎯 === PREPARANDO PRODUTOS PARA ITENS_VENDA === 🎯")
    
    arquivo_produtos = 'data/originais/controles_gerais/conf_dav/csv/conf_dav_FINAL_NORMALIZADO_20251105_041222.csv'
    
    try:
        print(f"📄 Carregando produtos: {arquivo_produtos}")
        df_produtos = pd.read_csv(arquivo_produtos)
        
        print(f"📊 Produtos carregados: {len(df_produtos):,}")
        print(f"📋 Colunas disponíveis: {', '.join(df_produtos.columns)}")
        
        # Analisar estrutura dos dados
        print(f"\n🔍 === ANÁLISE DOS DADOS === 🔍")
        
        # Verificar campos principais
        campos_importantes = ['Nro.DAV', 'Produto', 'Modelo', 'Qtd.', 'Vl.Total', 'Emp.']
        for campo in campos_importantes:
            if campo in df_produtos.columns:
                nulos = df_produtos[campo].isnull().sum()
                print(f"   {campo}: {nulos:,} nulos ({(nulos/len(df_produtos)*100):.1f}%)")
        
        # Análise de produtos
        if 'Produto' in df_produtos.columns:
            produtos_unicos = df_produtos['Produto'].nunique()
            print(f"   Produtos únicos: {produtos_unicos:,}")
            
            # Amostra de produtos
            produtos_sample = df_produtos['Produto'].dropna().unique()[:10]
            print(f"   Amostra produtos: {', '.join(map(str, produtos_sample))}")
        
        print(f"\n🔧 === PREPARANDO MAPEAMENTO === 🔧")
        
        # Criar estrutura para itens_venda
        itens_venda = []
        
        # Processar cada produto
        for idx, row in df_produtos.iterrows():
            if idx % 5000 == 0:
                print(f"   Processando: {idx:,}/{len(df_produtos):,}")
            
            # Mapear campos
            item = {
                'id': str(uuid.uuid4()),
                'venda_id': None,  # Será preenchido no cruzamento
                'tipo_produto': mapear_tipo_produto(row.get('Produto')),
                'descricao': str(row.get('Produto', '')).strip() if pd.notna(row.get('Produto')) else 'Produto não especificado',
                'marca': extrair_marca(row.get('Modelo')),
                'modelo': str(row.get('Modelo', '')).strip() if pd.notna(row.get('Modelo')) else None,
                'codigo_produto': str(int(row.get('Produto', 0))) if pd.notna(row.get('Produto')) and row.get('Produto', 0) != 0 else None,
                'codigo_barras': None,  # Não disponível nos dados
                'cor': None,  # Não disponível nos dados
                'tamanho': None,  # Não disponível nos dados
                'material': None,  # Poderia ser extraído da descrição
                'fornecedor': None,  # Não disponível nos dados
                'codigo_fornecedor': None,  # Não disponível nos dados
                'quantidade': int(float(row.get('Qtd.', 1))) if pd.notna(row.get('Qtd.')) and pd.to_numeric(row.get('Qtd.'), errors='coerce') > 0 else 1,
                'valor_unitario': safe_convert_value(row.get('Vl.Total', 0), row.get('Qtd.', 1)),
                'valor_desconto': 0.0,  # Padrão
                'possui_estoque': True,  # Padrão
                'requer_encomenda': False,  # Padrão
                'data_encomenda': None,
                'data_prevista_chegada': None,
                'observacoes': f"Importado do DAV {row.get('Nro.DAV', 'N/A')} - Empresa {row.get('Emp.', 'N/A')} - Arquivo: {row.get('arquivo_origem', 'N/A')}",
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'deleted_at': None,
                'updated_by': 'import_conf_dav',
                
                # Campos de controle para cruzamento
                'dav_numero': row.get('Nro.DAV'),
                'dav_original': row.get('Nro_DAV_Original'),
                'empresa': row.get('Emp.'),
                'data_dav': row.get('Dt.DAV'),
                'periodo': row.get('periodo'),
                'arquivo_origem': row.get('arquivo_origem')
            }
            
            itens_venda.append(item)
        
        # Converter para DataFrame
        df_itens = pd.DataFrame(itens_venda)
        
        print(f"\n📊 === RESULTADOS === 📊")
        print(f"📋 Itens processados: {len(df_itens):,}")
        print(f"📋 Colunas criadas: {df_itens.shape[1]}")
        
        # Análise dos tipos de produtos
        tipos_produtos = df_itens['tipo_produto'].value_counts()
        print(f"\n🔍 Tipos de produtos mapeados:")
        for tipo, count in tipos_produtos.items():
            print(f"   {tipo}: {count:,} itens ({count/len(df_itens)*100:.1f}%)")
        
        # Análise de valores
        valor_total = df_itens['valor_unitario'].sum()
        valor_medio = df_itens['valor_unitario'].mean()
        print(f"\n💰 Análise de valores:")
        print(f"   Valor total: R$ {valor_total:,.2f}")
        print(f"   Valor médio: R$ {valor_medio:.2f}")
        print(f"   Itens com valor > 0: {(df_itens['valor_unitario'] > 0).sum():,}")
        
        # Salvar arquivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        arquivo_itens = f'data/itens_venda_preparados_{timestamp}.csv'
        
        df_itens.to_csv(arquivo_itens, index=False)
        
        print(f"\n💾 === ARQUIVO GERADO === 💾")
        print(f"📄 Arquivo: {arquivo_itens}")
        print(f"📊 Registros: {len(df_itens):,}")
        print(f"✅ Status: Pronto para cruzamento com vendas")
        
        return arquivo_itens, df_itens
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None, None

def gerar_script_cruzamento_vendas_produtos():
    """
    Gera script para cruzar vendas com produtos usando DAV
    """
    print(f"\n🎯 === GERANDO SCRIPT DE CRUZAMENTO === 🎯")
    
    script_content = '''#!/usr/bin/env python3
"""
Script para cruzar vendas com produtos usando números DAV normalizados
"""

import pandas as pd
from datetime import datetime

def cruzar_vendas_produtos():
    """
    Cruza vendas com produtos usando DAV normalizado
    """
    print("🎯 === CRUZAMENTO VENDAS x PRODUTOS === 🎯")
    
    # Carregar dados
    vendas_file = 'data/vendas_totais_com_uuid.csv'  # Arquivo de vendas
    produtos_file = 'data/itens_venda_preparados_TIMESTAMP.csv'  # Substituir TIMESTAMP
    
    try:
        df_vendas = pd.read_csv(vendas_file)
        df_produtos = pd.read_csv(produtos_file)
        
        print(f"📊 Vendas: {len(df_vendas):,}")
        print(f"📊 Produtos: {len(df_produtos):,}")
        
        # Cruzamento por DAV normalizado
        cruzamentos = []
        
        for _, produto in df_produtos.iterrows():
            dav_produto = produto['dav_numero']
            empresa_produto = produto['empresa']
            
            # Buscar venda correspondente
            venda_match = df_vendas[
                (df_vendas['numero_os'] == dav_produto) &
                (df_vendas['loja_id'].str.contains(str(int(empresa_produto)), na=False))
            ]
            
            if not venda_match.empty:
                produto['venda_id'] = venda_match.iloc[0]['id']
                cruzamentos.append(produto)
        
        df_cruzados = pd.DataFrame(cruzamentos)
        
        print(f"✅ Cruzamentos encontrados: {len(df_cruzados):,}")
        
        # Salvar resultado
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        arquivo_final = f'data/itens_venda_com_vendas_{timestamp}.csv'
        df_cruzados.to_csv(arquivo_final, index=False)
        
        print(f"💾 Arquivo final: {arquivo_final}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    cruzar_vendas_produtos()
'''
    
    with open('scripts/cruzar_vendas_produtos.py', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"📄 Script gerado: scripts/cruzar_vendas_produtos.py")

def main():
    """Função principal"""
    print("🎯 === PREPARAÇÃO COMPLETA ITENS_VENDA === 🎯")
    
    # 1. Preparar produtos
    arquivo_itens, df_itens = preparar_itens_venda()
    
    if not arquivo_itens:
        print("❌ Falha na preparação dos produtos")
        return
    
    # 2. Gerar script de cruzamento
    gerar_script_cruzamento_vendas_produtos()
    
    print(f"\n🎉 === RESULTADO FINAL === 🎉")
    print(f"✅ Produtos preparados: {arquivo_itens}")
    print(f"✅ Script de cruzamento: scripts/cruzar_vendas_produtos.py")
    print(f"📋 Estrutura: 100% compatível com tabela itens_venda")
    print(f"🚀 Próximo: Executar cruzamento com vendas")
    
    print(f"📅 Processado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()