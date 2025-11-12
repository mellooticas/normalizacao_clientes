#!/usr/bin/env python3
"""
Analisar Canais de Aquisição VIXEN
==================================

Analisa os valores de "Como nos conheceu" para mapear com marketing.canais_aquisicao.
"""

import pandas as pd
from pathlib import Path
import uuid

def gerar_uuid():
    """Gera UUID único"""
    return str(uuid.uuid4())

def normalizar_canal(canal):
    """Normaliza nome do canal"""
    if pd.isna(canal) or canal == "":
        return "NAO_INFORMADO"
    return str(canal).strip().upper()

def main():
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    vixen_finais_dir = base_dir / "data" / "originais" / "vixen" / "finais_postgresql_prontos"
    
    print("📞 ANALISANDO CANAIS DE AQUISIÇÃO VIXEN")
    print("=" * 60)
    
    # Carregar dados de ambas as lojas
    df_maua = pd.read_csv(vixen_finais_dir / "clientes_maua_final.csv")
    df_suzano = pd.read_csv(vixen_finais_dir / "clientes_suzano_final.csv")
    
    # Combinar dados para análise
    df_total = pd.concat([df_maua, df_suzano], ignore_index=True)
    
    print(f"📊 Total de registros analisados: {len(df_total):,}")
    print(f"   🏪 MAUA: {len(df_maua):,}")
    print(f"   🏪 SUZANO: {len(df_suzano):,}")
    
    # Analisar canais de aquisição
    print(f"\n📞 ANÁLISE DOS CANAIS DE AQUISIÇÃO:")
    
    if 'Como nos conheceu' in df_total.columns:
        canais = df_total['Como nos conheceu'].value_counts()
        print(f"   📊 Total de canais únicos: {len(canais)}")
        
        print(f"\n📋 TOP 20 CANAIS:")
        for i, (canal, count) in enumerate(canais.head(20).items(), 1):
            percentual = (count / len(df_total)) * 100
            print(f"   {i:2d}. {canal:<35} | {count:>6,} ({percentual:5.1f}%)")
        
        # Criar estrutura para marketing.canais_aquisicao
        print(f"\n🗃️  CRIANDO ESTRUTURA PARA BANCO:")
        
        canais_para_banco = []
        
        for i, (canal, count) in enumerate(canais.items(), 1):
            canal_normalizado = normalizar_canal(canal)
            
            # Categorizar canal
            categoria = "OUTROS"
            if any(termo in canal_normalizado for termo in ["INDICAÇÃO", "INDICA"]):
                categoria = "INDICACAO"
            elif any(termo in canal_normalizado for termo in ["SAÚDE", "SAUDE", "CLINICA", "SUS"]):
                categoria = "SAUDE"
            elif any(termo in canal_normalizado for termo in ["ORÇAMENTO", "ORCAMENTO", "1ª COMPRA"]):
                categoria = "COMERCIAL"
            elif any(termo in canal_normalizado for termo in ["DIVULGADOR", "ABORDAGEM", "PASSAGEM"]):
                categoria = "MARKETING"
            elif any(termo in canal_normalizado for termo in ["JÁ É CLIENTE", "JA E CLIENTE"]):
                categoria = "RETENCAO"
            
            canal_dados = {
                'id': gerar_uuid(),
                'codigo': f"VIXEN_{i:03d}",
                'nome': canal[:100],  # Limite da coluna nome
                'descricao': f"Canal importado do VIXEN: {canal}",
                'categoria': categoria,
                'ativo': True,
                'total_clientes': count,
                'percentual': round((count / len(df_total)) * 100, 2)
            }
            
            canais_para_banco.append(canal_dados)
        
        # Criar DataFrame para exportação
        df_canais = pd.DataFrame(canais_para_banco)
        
        # Salvar estrutura de canais
        canais_output = vixen_finais_dir.parent / "canais_aquisicao_vixen.csv"
        df_canais.to_csv(canais_output, index=False)
        
        print(f"   ✅ Estrutura salva: {canais_output}")
        print(f"   📊 Total de canais: {len(df_canais)}")
        
        # Mostrar resumo por categoria
        print(f"\n📊 RESUMO POR CATEGORIA:")
        categoria_resumo = df_canais.groupby('categoria').agg({
            'total_clientes': 'sum',
            'codigo': 'count'
        }).rename(columns={'codigo': 'quantidade_canais'})
        
        for categoria, dados in categoria_resumo.iterrows():
            total = dados['total_clientes']
            qtd = dados['quantidade_canais']
            percentual = (total / len(df_total)) * 100
            print(f"   🔹 {categoria:<12} | {qtd:2d} canais | {total:>6,} clientes ({percentual:5.1f}%)")
        
        # Criar mapeamento para aplicação nos dados
        print(f"\n🔗 CRIANDO MAPEAMENTO PARA APLICAÇÃO:")
        
        mapeamento_canais = {}
        for _, row in df_canais.iterrows():
            mapeamento_canais[row['nome']] = {
                'canal_uuid': row['id'],
                'canal_codigo': row['codigo'],
                'canal_categoria': row['categoria']
            }
        
        # Salvar mapeamento
        mapeamento_output = vixen_finais_dir.parent / "mapeamento_canais_vixen.json"
        
        import json
        with open(mapeamento_output, 'w', encoding='utf-8') as f:
            # Converter para formato serializável
            mapeamento_serializable = {}
            for nome, dados in mapeamento_canais.items():
                mapeamento_serializable[nome] = dados
            
            json.dump(mapeamento_serializable, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Mapeamento salvo: {mapeamento_output}")
        
        print(f"\n🎯 PRÓXIMOS PASSOS:")
        print(f"   1️⃣ Aplicar UUIDs de canais nos arquivos VIXEN")
        print(f"   2️⃣ Inserir canais na tabela marketing.canais_aquisicao")
        print(f"   3️⃣ Normalizar vendedores")
        print(f"   4️⃣ Preparar para cruzamentos")
        
    else:
        print(f"❌ Coluna 'Como nos conheceu' não encontrada!")

if __name__ == "__main__":
    main()