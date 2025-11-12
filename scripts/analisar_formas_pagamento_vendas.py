#!/usr/bin/env python3
"""
Análise de formas de pagamento nos dados históricos
Para povoar vendas.vendas_formas_pagamento
"""

import pandas as pd
from pathlib import Path
import re

def analisar_formas_pagamento_historicas():
    """Analisa formas de pagamento nos dados históricos"""
    
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    
    print("💳 === ANÁLISE FORMAS DE PAGAMENTO === 💳")
    print()
    
    # 1. Buscar arquivos com formas de pagamento
    print("🔍 Procurando dados de formas de pagamento...")
    
    # Verificar diretórios relevantes
    diretorios_busca = [
        base_dir / "data" / "originais",
        base_dir / "data" / "originais" / "controles_gerais" / "trans_financ",
        base_dir / "_analises"
    ]
    
    arquivos_relevantes = []
    
    for diretorio in diretorios_busca:
        if diretorio.exists():
            # Buscar arquivos com "pagamento", "forma", "financ" no nome
            for arquivo in diretorio.rglob("*"):
                if arquivo.is_file() and arquivo.suffix in ['.csv', '.json']:
                    nome_lower = arquivo.name.lower()
                    if any(termo in nome_lower for termo in ['pagamento', 'forma', 'financ', 'payment']):
                        arquivos_relevantes.append(arquivo)
    
    print(f"📂 Arquivos encontrados:")
    for arquivo in arquivos_relevantes[:10]:  # Primeiros 10
        print(f"   {arquivo.relative_to(base_dir)}")
    
    # 2. Analisar arquivo principal de formas de pagamento
    print(f"\n🔍 Analisando arquivo principal...")
    
    arquivo_formas = base_dir / "_analises" / "mapeamento_formas_pagamento_uuid.json"
    if arquivo_formas.exists():
        import json
        with open(arquivo_formas, 'r', encoding='utf-8') as f:
            formas_pagamento = json.load(f)
        
        print(f"📋 Formas de pagamento disponíveis:")
        for forma, dados in formas_pagamento.items():
            uuid_forma = dados.get('uuid', 'N/A')
            print(f"   {forma}: {uuid_forma}")
    
    # 3. Analisar dados trans_financ originais
    print(f"\n💰 Analisando dados trans_financ...")
    
    trans_financ_dir = base_dir / "data" / "originais" / "controles_gerais" / "trans_financ"
    
    if trans_financ_dir.exists():
        # Buscar arquivos CSV no diretório trans_financ
        arquivos_trans = list(trans_financ_dir.rglob("*.csv"))
        
        print(f"📂 Arquivos trans_financ encontrados: {len(arquivos_trans)}")
        
        # Analisar alguns arquivos para entender estrutura
        for arquivo in arquivos_trans[:3]:
            print(f"\n📄 Analisando: {arquivo.name}")
            try:
                df = pd.read_csv(arquivo, nrows=5)  # Só primeiras linhas
                print(f"   Colunas: {list(df.columns)}")
                
                # Procurar colunas relevantes para formas de pagamento
                colunas_relevantes = []
                for col in df.columns:
                    col_lower = col.lower()
                    if any(termo in col_lower for termo in ['pagamento', 'forma', 'tipo', 'valor', 'entrada', 'parcela']):
                        colunas_relevantes.append(col)
                
                if colunas_relevantes:
                    print(f"   Colunas relevantes: {colunas_relevantes}")
                
            except Exception as e:
                print(f"   Erro ao ler: {e}")
    
    # 4. Analisar arquivo com outros pagamentos (base principal)
    print(f"\n🎯 Analisando arquivo principal outros pagamentos...")
    
    arquivo_outros_pag = base_dir / "data" / "originais" / "controles_gerais" / "trans_financ" / "separados_por_pagamento" / "ordem_servico_pdv_outros_pagamentos_com_uuid_normalizado.csv"
    
    if arquivo_outros_pag.exists():
        df_outros = pd.read_csv(arquivo_outros_pag, nrows=1000)  # Amostra
        print(f"📊 Colunas no arquivo outros pagamentos:")
        for i, col in enumerate(df_outros.columns):
            print(f"   {i+1}. {col}")
        
        print(f"\n🔍 Analisando formas de pagamento...")
        
        # Verificar se tem coluna de forma de pagamento
        colunas_forma_pag = [col for col in df_outros.columns if 'pagamento' in col.lower() or 'forma' in col.lower()]
        
        if colunas_forma_pag:
            for col in colunas_forma_pag:
                print(f"\n📋 Coluna: {col}")
                valores_unicos = df_outros[col].value_counts().head(10)
                print(f"   Valores únicos (top 10):")
                for valor, count in valores_unicos.items():
                    print(f"     {valor}: {count} ocorrências")
        
        # Verificar colunas de valor
        colunas_valor = [col for col in df_outros.columns if 'valor' in col.lower() or 'vl.' in col.lower()]
        print(f"\n💰 Colunas de valor encontradas: {colunas_valor}")
    
    # 5. Estratégia para vendas.vendas_formas_pagamento
    print(f"\n💡 === ESTRATÉGIA PARA FORMAS DE PAGAMENTO === 💡")
    
    print(f"🎯 Abordagens possíveis:")
    print(f"   1️⃣ Analisar arquivos trans_financ por tipo de pagamento")
    print(f"   2️⃣ Usar dados de carnê vs outros pagamentos")
    print(f"   3️⃣ Inferir forma de pagamento pela fonte dos dados")
    print(f"   4️⃣ Criar formas padrão baseadas no conhecimento do negócio")
    
    print(f"\n🔧 Estrutura necessária:")
    print(f"   - venda_id (UUID da venda)")
    print(f"   - forma_pagamento_id (UUID da forma)")
    print(f"   - valor (valor específico desta forma)")
    print(f"   - valor_entrada (se aplicável)")
    print(f"   - parcelas (número de parcelas)")
    
    return arquivos_relevantes

def mapear_formas_pagamento_por_fonte():
    """Mapeia formas de pagamento baseado na fonte dos dados"""
    
    print(f"\n🗺️  === MAPEAMENTO POR FONTE === 🗺️")
    
    # Mapeamento baseado no conhecimento dos dados
    mapeamento_fonte = {
        'OSS': {
            'forma_principal': 'DINHEIRO',  # Assumindo que OSS é principalmente dinheiro
            'descricao': 'Vendas do sistema OSS - predominantemente à vista'
        },
        'VIXEN_CARNE': {
            'forma_principal': 'CARNE_PROPRIO',  # Carnê próprio
            'descricao': 'Vendas VIXEN carnê - parcelamento próprio'
        },
        'VIXEN_COMPLETO': {
            'forma_principal': 'CARTAO_CREDITO',  # Outros pagamentos, assumindo cartão
            'descricao': 'Vendas VIXEN outros pagamentos - cartão/outros'
        }
    }
    
    print(f"📋 Mapeamento por fonte de dados:")
    for fonte, dados in mapeamento_fonte.items():
        print(f"   {fonte}:")
        print(f"     Forma principal: {dados['forma_principal']}")
        print(f"     Descrição: {dados['descricao']}")
    
    return mapeamento_fonte

def propor_estrategia_implementacao():
    """Propõe estratégia de implementação"""
    
    print(f"\n🚀 === ESTRATÉGIA DE IMPLEMENTAÇÃO === 🚀")
    
    print(f"Fase 1 - Mapeamento Básico:")
    print(f"   1. Carregar vendas finais (15.281 vendas)")
    print(f"   2. Identificar fonte pela observação/numeração")
    print(f"   3. Aplicar forma de pagamento padrão por fonte")
    print(f"   4. Gerar registros para vendas.vendas_formas_pagamento")
    
    print(f"\nFase 2 - Refinamento:")
    print(f"   1. Analisar arquivos trans_financ detalhadamente")
    print(f"   2. Extrair formas específicas quando disponível")
    print(f"   3. Identificar vendas com múltiplas formas")
    print(f"   4. Aplicar regras de negócio específicas")
    
    print(f"\nFase 3 - Validação:")
    print(f"   1. Verificar consistência valor_total vs soma formas")
    print(f"   2. Validar foreign keys")
    print(f"   3. Testar importação")
    
    return True

if __name__ == "__main__":
    print("💳 ANÁLISE DE FORMAS DE PAGAMENTO PARA VENDAS")
    print("=" * 60)
    
    arquivos = analisar_formas_pagamento_historicas()
    mapeamento = mapear_formas_pagamento_por_fonte()
    estrategia = propor_estrategia_implementacao()
    
    print(f"\n🎯 PRÓXIMOS PASSOS:")
    print(f"1. Implementar mapeamento básico por fonte")
    print(f"2. Criar arquivo vendas_formas_pagamento.csv")
    print(f"3. Testar importação no banco")
    print(f"4. Refinar com dados específicos de trans_financ")