#!/usr/bin/env python3
"""
Análise detalhada de duplicatas por constraint uq_vendas_loja_numero
Identifica e resolve todas as duplicatas de numero_venda + loja_id
"""

import pandas as pd
from pathlib import Path

def analisar_constraint_loja_numero():
    """Analisa duplicatas específicas da constraint uq_vendas_loja_numero"""
    
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    vendas_dir = base_dir / "data" / "vendas_para_importar"
    
    print("🔍 === ANÁLISE CONSTRAINT uq_vendas_loja_numero === 🔍")
    print()
    
    # 1. Carrega os 3 arquivos atuais
    print("📂 Carregando arquivos...")
    
    # OSS
    arquivo_oss = vendas_dir / "vendas_PRONTO_PARA_IMPORTAR_97pct_LIMPO.csv"
    oss_df = pd.read_csv(arquivo_oss)
    oss_df['fonte'] = 'OSS'
    print(f"✅ OSS: {len(oss_df)} vendas")
    
    # VIXEN Carnê (limpo)
    arquivo_vixen_carne = vendas_dir / "vendas_VIXEN_CARNE_SEM_DUPLICATAS.csv"
    vixen_carne_df = pd.read_csv(arquivo_vixen_carne)
    vixen_carne_df['fonte'] = 'VIXEN_CARNE'
    print(f"✅ VIXEN Carnê Limpo: {len(vixen_carne_df)} vendas")
    
    # VIXEN Completo
    arquivo_vixen_completo = vendas_dir / "vendas_COMPLETAS_ESTRUTURA_CORRIGIDA.csv"
    vixen_completo_df = pd.read_csv(arquivo_vixen_completo)
    vixen_completo_df['fonte'] = 'VIXEN_COMPLETO'
    print(f"✅ VIXEN Completo: {len(vixen_completo_df)} vendas")
    
    print()
    
    # 2. Combina todos os arquivos
    print("🔗 Combinando todos os arquivos...")
    todos_df = pd.concat([oss_df, vixen_carne_df, vixen_completo_df], ignore_index=True)
    print(f"📊 Total combinado: {len(todos_df)} vendas")
    
    # 3. Cria chave da constraint
    todos_df['chave_constraint'] = todos_df['loja_id'].astype(str) + "_" + todos_df['numero_venda'].astype(str)
    
    # 4. Identifica duplicatas por constraint
    print(f"\n🔍 Analisando constraint uq_vendas_loja_numero...")
    
    duplicatas_constraint = todos_df[todos_df.duplicated(subset=['chave_constraint'], keep=False)]
    duplicatas_constraint = duplicatas_constraint.sort_values(['loja_id', 'numero_venda', 'fonte'])
    
    total_duplicatas = len(duplicatas_constraint)
    grupos_duplicados = duplicatas_constraint.groupby('chave_constraint').size()
    
    print(f"📊 Total de registros duplicados: {total_duplicatas}")
    print(f"🔢 Grupos de duplicatas: {len(grupos_duplicados)}")
    print(f"📈 Registros únicos que serão mantidos: {len(grupos_duplicados)}")
    print(f"🗑️  Registros que serão removidos: {total_duplicatas - len(grupos_duplicados)}")
    
    # 5. Análise detalhada das duplicatas
    print(f"\n📋 === DETALHAMENTO DAS DUPLICATAS === 📋")
    
    if total_duplicatas > 0:
        print(f"Amostra das duplicatas encontradas:")
        for i, (chave, grupo) in enumerate(grupos_duplicados.head(10).items()):
            exemplos = duplicatas_constraint[duplicatas_constraint['chave_constraint'] == chave]
            loja_id = exemplos.iloc[0]['loja_id']
            numero = exemplos.iloc[0]['numero_venda']
            loja_nome = "SUZANO" if "52f92716" in loja_id else "MAUÁ" if "aa7a5646" in loja_id else "OUTRA"
            
            print(f"\n   {i+1}. Loja: {loja_nome} | Número: {numero} | {grupo} duplicatas")
            for j, row in exemplos.iterrows():
                print(f"      - {row['fonte']}: Cliente {row['cliente_id'][:8]}... | Data: {row['data_venda']} | Valor: R$ {row['valor_total']}")
    
    # 6. Análise por fonte
    print(f"\n📊 === DUPLICATAS POR FONTE === 📊")
    
    if total_duplicatas > 0:
        duplicatas_por_fonte = duplicatas_constraint['fonte'].value_counts()
        print(f"Duplicatas por arquivo:")
        for fonte, count in duplicatas_por_fonte.items():
            print(f"   {fonte}: {count} registros duplicados")
        
        # Verificar quais fontes conflitam
        print(f"\n🔄 Conflitos entre fontes:")
        for chave, grupo in grupos_duplicados.items():
            if grupo > 1:
                fontes_conflito = duplicatas_constraint[duplicatas_constraint['chave_constraint'] == chave]['fonte'].unique()
                if len(fontes_conflito) > 1:
                    numero = duplicatas_constraint[duplicatas_constraint['chave_constraint'] == chave].iloc[0]['numero_venda']
                    loja_id = duplicatas_constraint[duplicatas_constraint['chave_constraint'] == chave].iloc[0]['loja_id']
                    loja_nome = "SUZANO" if "52f92716" in loja_id else "MAUÁ" if "aa7a5646" in loja_id else "OUTRA"
                    print(f"   {loja_nome} {numero}: {list(fontes_conflito)}")
    
    # 7. Estratégia de resolução
    print(f"\n💡 === ESTRATÉGIA DE RESOLUÇÃO === 💡")
    
    if total_duplicatas > 0:
        print(f"Prioridades para manter registros:")
        print(f"   1️⃣ OSS (dados mais recentes e confiáveis)")
        print(f"   2️⃣ VIXEN_COMPLETO (dataset mais abrangente)")
        print(f"   3️⃣ VIXEN_CARNE (subset específico)")
        
        # Aplicar estratégia de prioridade
        print(f"\n🧹 Aplicando estratégia de prioridade...")
        
        def prioridade_fonte(fonte):
            if fonte == 'OSS':
                return 1
            elif fonte == 'VIXEN_COMPLETO':
                return 2
            elif fonte == 'VIXEN_CARNE':
                return 3
            else:
                return 4
        
        todos_df['prioridade'] = todos_df['fonte'].apply(prioridade_fonte)
        
        # Remove duplicatas mantendo apenas o de maior prioridade
        todos_limpo = todos_df.sort_values('prioridade').drop_duplicates(
            subset=['chave_constraint'], 
            keep='first'
        )
        
        # Remove colunas temporárias
        todos_limpo = todos_limpo.drop(columns=['fonte', 'chave_constraint', 'prioridade'])
        
        print(f"✅ Registros após limpeza: {len(todos_limpo)}")
        print(f"🗑️  Registros removidos: {len(todos_df) - len(todos_limpo)}")
        
        # 8. Gera arquivo final unificado
        arquivo_final = vendas_dir / "vendas_UNIFICADO_SEM_DUPLICATAS_CONSTRAINT.csv"
        todos_limpo.to_csv(arquivo_final, index=False)
        
        print(f"\n💾 Arquivo final gerado: {arquivo_final}")
        print(f"📊 {len(todos_limpo)} vendas prontas para importação")
        
        # 9. Estatísticas finais
        print(f"\n📊 === ESTATÍSTICAS FINAIS === 📊")
        valor_total = todos_limpo['valor_total'].sum()
        print(f"💰 Valor total: R$ {valor_total:,.2f}")
        
        por_loja = todos_limpo.groupby('loja_id').agg({
            'valor_total': ['count', 'sum']
        })
        
        for loja_id in todos_limpo['loja_id'].unique():
            subset = todos_limpo[todos_limpo['loja_id'] == loja_id]
            count = len(subset)
            valor = subset['valor_total'].sum()
            loja_nome = "SUZANO" if "52f92716" in loja_id else "MAUÁ" if "aa7a5646" in loja_id else "OUTRAS"
            print(f"   {loja_nome}: {count} vendas (R$ {valor:,.2f})")
        
        return todos_limpo, arquivo_final
    
    else:
        print(f"✅ Nenhuma duplicata de constraint encontrada!")
        return None, None

if __name__ == "__main__":
    resultado, arquivo = analisar_constraint_loja_numero()
    
    if resultado is not None:
        print(f"\n🎯 SOLUÇÃO PRONTA!")
        print(f"📂 Use apenas o arquivo: {arquivo.name}")
        print(f"🚀 Este arquivo único substitui os 3 anteriores!")
    else:
        print(f"\n✅ Os arquivos atuais estão prontos para importação!")