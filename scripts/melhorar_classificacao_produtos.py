#!/usr/bin/env python3
"""
Script para melhorar classificação de tipos de produtos
"""

import pandas as pd
from datetime import datetime

def melhorar_classificacao_produtos():
    """
    Melhora a classificação dos tipos de produtos baseado na descrição
    """
    print("🎯 === MELHORANDO CLASSIFICAÇÃO DE PRODUTOS === 🎯")
    
    arquivo = 'data/itens_venda_preparados_20251105_090114.csv'
    
    try:
        df = pd.read_csv(arquivo)
        print(f"📊 Produtos carregados: {len(df):,}")
        
        def classificar_produto_melhorado(descricao, modelo):
            """Classificação melhorada baseada em palavras-chave"""
            if pd.isna(descricao):
                return 'OUTROS'
            
            texto = str(descricao).upper()
            modelo_str = str(modelo).upper() if pd.notna(modelo) else ''
            texto_completo = f"{texto} {modelo_str}"
            
            # LENTES (mais específico)
            lente_keywords = [
                'LENTE', 'LENTES', 'LENS', 'MULTIFOCAL', 'MONOFOCAL',
                'CR', 'POLI', 'POLICARBONATO', 'TRIVEX', 'ANTI-REFLEXO',
                'ANTIRREFLEXO', 'AR', 'BLUE', 'FOTO', 'TRANSITION',
                'PROGRESSIVA', 'BIFOCAL', 'TRIFOCAL'
            ]
            
            if any(keyword in texto_completo for keyword in lente_keywords):
                # Verificar se é lente de contato
                if any(keyword in texto_completo for keyword in ['CONTATO', 'CONTACT', 'GELATINOSA']):
                    return 'LENTE DE CONTATO'
                else:
                    return 'LENTE'
            
            # ARMAÇÕES
            armacao_keywords = [
                'ARMAÇÃO', 'ARMACAO', 'ARMACÃO', 'ÓCULOS', 'OCULOS',
                'FRAME', 'ROMANO', 'TITANIO', 'METAL', 'ACETATO',
                'WAYFARER', 'AVIADOR', 'GATINHO', 'REDONDO'
            ]
            
            if any(keyword in texto_completo for keyword in armacao_keywords):
                return 'ARMAÇÃO'
            
            # ACESSÓRIOS ESPECÍFICOS
            if any(keyword in texto_completo for keyword in ['ESTOJO', 'CASE', 'CAIXA']):
                return 'ESTOJO'
            elif any(keyword in texto_completo for keyword in ['CORDÃO', 'CORDAO', 'CORRENTE']):
                return 'CORDÃO'
            elif any(keyword in texto_completo for keyword in ['FLANELA', 'PANO', 'TECIDO']):
                return 'FLANELA'
            elif any(keyword in texto_completo for keyword in ['SPRAY', 'LIMPEZA', 'CLEANER']):
                return 'SPRAY LIMPEZA'
            
            # Se tem código numérico, provavelmente é produto catalogado
            if texto.replace('.', '').replace(',', '').isdigit():
                return 'ACESSÓRIO'
            
            return 'OUTROS'
        
        print("🔧 Reclassificando produtos...")
        
        # Aplicar nova classificação
        df['tipo_produto_novo'] = df.apply(
            lambda row: classificar_produto_melhorado(row['descricao'], row['modelo']),
            axis=1
        )
        
        # Comparar classificações
        print("\n📊 === COMPARAÇÃO CLASSIFICAÇÕES === 📊")
        
        print("🔍 Classificação original:")
        original_counts = df['tipo_produto'].value_counts()
        for tipo, count in original_counts.items():
            print(f"   {tipo}: {count:,} ({count/len(df)*100:.1f}%)")
        
        print("\n🔍 Classificação melhorada:")
        nova_counts = df['tipo_produto_novo'].value_counts()
        for tipo, count in nova_counts.items():
            print(f"   {tipo}: {count:,} ({count/len(df)*100:.1f}%)")
        
        # Aplicar nova classificação
        df['tipo_produto'] = df['tipo_produto_novo']
        df = df.drop('tipo_produto_novo', axis=1)
        
        # Algumas amostras para verificação
        print(f"\n🔍 === AMOSTRAS DE CLASSIFICAÇÃO === 🔍")
        
        tipos_interessantes = ['LENTE', 'ARMAÇÃO', 'LENTE DE CONTATO']
        for tipo in tipos_interessantes:
            if tipo in df['tipo_produto'].values:
                amostra = df[df['tipo_produto'] == tipo].head(3)
                print(f"\n{tipo}:")
                for _, row in amostra.iterrows():
                    print(f"   {row['descricao']} | {row['modelo']}")
        
        # Salvar arquivo melhorado
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        arquivo_melhorado = f'data/itens_venda_CLASSIFICADOS_{timestamp}.csv'
        
        df.to_csv(arquivo_melhorado, index=False)
        
        print(f"\n💾 === ARQUIVO MELHORADO === 💾")
        print(f"📄 Arquivo: {arquivo_melhorado}")
        print(f"📊 Registros: {len(df):,}")
        print(f"✅ Classificação: Melhorada com base em palavras-chave")
        
        return arquivo_melhorado
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def main():
    print("🎯 === MELHORIA DE CLASSIFICAÇÃO === 🎯")
    arquivo_melhorado = melhorar_classificacao_produtos()
    
    if arquivo_melhorado:
        print(f"\n🎉 Classificação melhorada salva em: {arquivo_melhorado}")
    else:
        print(f"❌ Falha na melhoria da classificação")

if __name__ == "__main__":
    main()