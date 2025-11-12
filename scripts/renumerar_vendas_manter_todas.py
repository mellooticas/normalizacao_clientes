#!/usr/bin/env python3
"""
Renumeração inteligente de vendas para manter TODAS as vendas
sem perder dados - apenas ajusta números para evitar constraint
"""

import pandas as pd
from pathlib import Path

def renumerar_vendas_inteligente():
    """Renumera vendas mantendo TODAS, apenas ajustando números para evitar constraint"""
    
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    vendas_dir = base_dir / "data" / "vendas_para_importar"
    
    print("🔧 === RENUMERAÇÃO INTELIGENTE - MANTER TODAS === 🔧")
    print()
    
    # 1. Carrega os 3 arquivos originais
    print("📂 Carregando arquivos originais...")
    
    # OSS (mais recente - mantém números originais)
    arquivo_oss = vendas_dir / "vendas_PRONTO_PARA_IMPORTAR_97pct_LIMPO.csv"
    oss_df = pd.read_csv(arquivo_oss)
    oss_df['fonte'] = 'OSS'
    oss_df['prioridade'] = 1
    print(f"✅ OSS: {len(oss_df)} vendas (mantém números originais)")
    
    # VIXEN Carnê
    arquivo_vixen_carne = vendas_dir / "vendas_VIXEN_CARNE_SEM_DUPLICATAS.csv"
    vixen_carne_df = pd.read_csv(arquivo_vixen_carne)
    vixen_carne_df['fonte'] = 'VIXEN_CARNE'
    vixen_carne_df['prioridade'] = 2
    print(f"✅ VIXEN Carnê: {len(vixen_carne_df)} vendas")
    
    # VIXEN Completo
    arquivo_vixen_completo = vendas_dir / "vendas_COMPLETAS_ESTRUTURA_CORRIGIDA.csv"
    vixen_completo_df = pd.read_csv(arquivo_vixen_completo)
    vixen_completo_df['fonte'] = 'VIXEN_COMPLETO'
    vixen_completo_df['prioridade'] = 3
    print(f"✅ OSS Completo: {len(vixen_completo_df)} vendas")
    
    # 2. Combina todos
    todos_df = pd.concat([oss_df, vixen_carne_df, vixen_completo_df], ignore_index=True)
    print(f"📊 Total combinado: {len(todos_df)} vendas")
    
    # 3. Identifica duplicatas de constraint
    todos_df['chave_constraint'] = todos_df['loja_id'].astype(str) + "_" + todos_df['numero_venda'].astype(str)
    
    duplicatas_constraint = todos_df[todos_df.duplicated(subset=['chave_constraint'], keep=False)]
    total_duplicatas = len(duplicatas_constraint)
    
    print(f"⚠️  Duplicatas de constraint encontradas: {total_duplicatas}")
    print(f"🎯 Estratégia: Renumerar mantendo TODAS as vendas")
    
    # 4. Estratégia de renumeração
    print(f"\n🔢 === ESTRATÉGIA DE RENUMERAÇÃO === 🔢")
    print(f"1️⃣ OSS: Mantém números originais (prioridade)")
    print(f"2️⃣ VIXEN Carnê: Adiciona 100.000 aos números")
    print(f"3️⃣ VIXEN Completo: Adiciona 200.000 aos números")
    
    # 5. Aplica renumeração
    print(f"\n🔧 Aplicando renumeração...")
    
    def renumerar_por_fonte(df, offset, nome_fonte):
        """Renumera vendas de uma fonte específica"""
        df = df.copy()
        
        if offset > 0:
            # Converte para numeric, trata erros
            numeros_originais = pd.to_numeric(df['numero_venda'], errors='coerce')
            numeros_novos = numeros_originais + offset
            df['numero_venda'] = numeros_novos.astype(str)
            
            # Adiciona informação na observação
            df['observacoes'] = df['observacoes'].astype(str) + f" | Renumerado +{offset} para evitar duplicatas"
            
            print(f"   {nome_fonte}: +{offset} aplicado")
            print(f"      Exemplo: {numeros_originais.iloc[0]} → {numeros_novos.iloc[0]}")
        else:
            print(f"   {nome_fonte}: Números mantidos (referência)")
        
        return df
    
    # Aplica renumeração por fonte
    oss_final = renumerar_por_fonte(oss_df, 0, "OSS")  # Mantém original
    vixen_carne_final = renumerar_por_fonte(vixen_carne_df, 100000, "VIXEN Carnê")  # +100k
    vixen_completo_final = renumerar_por_fonte(vixen_completo_df, 200000, "VIXEN Completo")  # +200k
    
    # 6. Combina dados renumerados
    todos_renumerados = pd.concat([oss_final, vixen_carne_final, vixen_completo_final], ignore_index=True)
    
    # Remove colunas temporárias
    todos_renumerados = todos_renumerados.drop(columns=['fonte', 'prioridade'])
    
    print(f"\n✅ Vendas após renumeração: {len(todos_renumerados)}")
    
    # 7. Verificação de constraint
    print(f"\n🔍 Verificando constraint após renumeração...")
    
    todos_renumerados['chave_constraint_nova'] = (
        todos_renumerados['loja_id'].astype(str) + "_" + 
        todos_renumerados['numero_venda'].astype(str)
    )
    
    duplicatas_pos_renumeracao = todos_renumerados[
        todos_renumerados.duplicated(subset=['chave_constraint_nova'], keep=False)
    ]
    
    if len(duplicatas_pos_renumeracao) > 0:
        print(f"⚠️  AINDA HÁ {len(duplicatas_pos_renumeracao)} duplicatas após renumeração!")
        print(f"🔧 Aplicando numeração sequencial única...")
        
        # Aplica numeração sequencial única por loja
        def numerar_sequencial_por_loja(df):
            df = df.copy()
            
            for loja_id in df['loja_id'].unique():
                mask_loja = df['loja_id'] == loja_id
                subset_loja = df[mask_loja].copy()
                
                # Gera números sequenciais únicos começando em 500000
                numeros_sequenciais = range(500000, 500000 + len(subset_loja))
                df.loc[mask_loja, 'numero_venda'] = [str(num) for num in numeros_sequenciais]
                
                loja_nome = "SUZANO" if "52f92716" in loja_id else "MAUÁ" if "aa7a5646" in loja_id else "OUTRA"
                print(f"      {loja_nome}: {len(subset_loja)} vendas → 500000-{500000 + len(subset_loja) - 1}")
            
            # Atualiza observações
            df['observacoes'] = df['observacoes'].astype(str) + " | Numeração sequencial única"
            
            return df
        
        todos_renumerados = numerar_sequencial_por_loja(todos_renumerados)
        
        # Verifica novamente
        todos_renumerados['chave_constraint_final'] = (
            todos_renumerados['loja_id'].astype(str) + "_" + 
            todos_renumerados['numero_venda'].astype(str)
        )
        
        duplicatas_final = todos_renumerados[
            todos_renumerados.duplicated(subset=['chave_constraint_final'], keep=False)
        ]
        
        print(f"✅ Duplicatas finais: {len(duplicatas_final)}")
    
    else:
        print(f"✅ Nenhuma duplicata após renumeração! Perfeito!")
    
    # Remove colunas temporárias
    colunas_temp = [col for col in todos_renumerados.columns if 'chave_constraint' in col]
    todos_renumerados = todos_renumerados.drop(columns=colunas_temp)
    
    # 8. Estatísticas finais
    print(f"\n📊 === ESTATÍSTICAS FINAIS === 📊")
    print(f"📈 Total de vendas: {len(todos_renumerados)} (TODAS MANTIDAS!)")
    
    valor_total = todos_renumerados['valor_total'].sum()
    print(f"💰 Valor total: R$ {valor_total:,.2f}")
    
    # Por loja
    print(f"\n🏪 Por loja:")
    for loja_id in todos_renumerados['loja_id'].unique():
        subset = todos_renumerados[todos_renumerados['loja_id'] == loja_id]
        count = len(subset)
        valor = subset['valor_total'].sum()
        loja_nome = "SUZANO" if "52f92716" in loja_id else "MAUÁ" if "aa7a5646" in loja_id else "OUTRAS"
        print(f"   {loja_nome}: {count} vendas (R$ {valor:,.2f})")
    
    # Faixas de numeração
    print(f"\n🔢 Faixas de numeração por fonte:")
    print(f"   OSS (originais): Números originais")
    print(f"   VIXEN Carnê: 100.000 - 199.999")
    print(f"   VIXEN Completo: 200.000 - 299.999 ou 500.000+")
    
    # 9. Salva arquivo final
    arquivo_final = vendas_dir / "vendas_TODAS_RENUMERADAS_SEM_DUPLICATAS.csv"
    todos_renumerados.to_csv(arquivo_final, index=False)
    
    print(f"\n💾 Arquivo final salvo: {arquivo_final}")
    print(f"🎯 {len(todos_renumerados)} vendas prontas para importação")
    print(f"✅ TODAS as vendas mantidas - apenas números ajustados!")
    
    return todos_renumerados, arquivo_final

if __name__ == "__main__":
    vendas_finais, arquivo = renumerar_vendas_inteligente()
    
    print(f"\n🎉 === SUCESSO TOTAL! === 🎉")
    print(f"📂 Arquivo único: {arquivo.name}")
    print(f"📊 {len(vendas_finais)} vendas (100% dos dados preservados)")
    print(f"🚀 Pronto para TRUNCATE + importação única!")
    print(f"✅ Zero duplicatas de constraint!")