#!/usr/bin/env python3
"""
Usar Mapeamento Existente de Canais - VIXEN
===========================================

Usa o mapeamento de canais já existente em vez de criar novo.
"""

import pandas as pd
import json
from pathlib import Path
from difflib import SequenceMatcher

def similaridade_texto(a, b):
    """Calcula similaridade entre dois textos"""
    return SequenceMatcher(None, a.upper(), b.upper()).ratio()

def main():
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    vixen_finais_dir = base_dir / "data" / "originais" / "vixen" / "finais_postgresql_prontos"
    
    print("🔗 USANDO MAPEAMENTO EXISTENTE DE CANAIS - VIXEN")
    print("=" * 60)
    
    # Carregar mapeamento existente
    mapeamento_existente_file = base_dir / "mapeamento_canais_aquisicao_completo.json"
    
    if not mapeamento_existente_file.exists():
        print(f"❌ Mapeamento existente não encontrado: {mapeamento_existente_file}")
        return
    
    with open(mapeamento_existente_file, 'r', encoding='utf-8') as f:
        mapeamento_existente = json.load(f)
    
    print(f"📊 Mapeamento existente carregado: {mapeamento_existente['total_canais']} canais")
    
    # Carregar dados VIXEN
    df_maua = pd.read_csv(vixen_finais_dir / "clientes_maua_final.csv")
    df_suzano = pd.read_csv(vixen_finais_dir / "clientes_suzano_final.csv")
    df_total = pd.concat([df_maua, df_suzano], ignore_index=True)
    
    print(f"📊 Dados VIXEN: {len(df_total):,} registros")
    
    # Analisar canais VIXEN
    if 'Como nos conheceu' in df_total.columns:
        canais_vixen = df_total['Como nos conheceu'].value_counts()
        print(f"📊 Canais únicos VIXEN: {len(canais_vixen)}")
        
        # Criar mapeamento por similaridade
        print(f"\n🔍 CRIANDO MAPEAMENTO POR SIMILARIDADE:")
        
        mapeamento_vixen = {}
        canais_mapeados = 0
        canais_novos = []
        
        for canal_vixen, count in canais_vixen.items():
            melhor_match = None
            melhor_similaridade = 0.0
            
            # Procurar por similaridade nos canais existentes
            for canal_existente in mapeamento_existente['canais']:
                nome_existente = canal_existente['nome']
                similaridade = similaridade_texto(canal_vixen, nome_existente)
                
                if similaridade > melhor_similaridade:
                    melhor_similaridade = similaridade
                    melhor_match = canal_existente
            
            # Se similaridade for alta (>80%), usar canal existente
            if melhor_similaridade > 0.8:
                mapeamento_vixen[canal_vixen] = {
                    'canal_uuid': melhor_match['uuid'],
                    'canal_codigo': melhor_match['codigo'],
                    'canal_nome': melhor_match['nome'],
                    'canal_categoria': melhor_match['categoria'],
                    'similaridade': round(melhor_similaridade, 3),
                    'mapeamento': 'EXISTENTE',
                    'count': count
                }
                canais_mapeados += 1
                print(f"   ✅ '{canal_vixen}' → '{melhor_match['nome']}' ({melhor_similaridade:.1%})")
            
            # Se similaridade for média (50-80%), mostrar para análise
            elif melhor_similaridade > 0.5:
                print(f"   ⚠️  '{canal_vixen}' → '{melhor_match['nome']}' ({melhor_similaridade:.1%}) - VERIFICAR")
                canais_novos.append({
                    'vixen': canal_vixen,
                    'sugestao': melhor_match['nome'],
                    'similaridade': melhor_similaridade,
                    'count': count
                })
            
            # Se similaridade for baixa (<50%), é canal novo
            else:
                canais_novos.append({
                    'vixen': canal_vixen,
                    'sugestao': None,
                    'similaridade': 0.0,
                    'count': count
                })
        
        print(f"\n📊 RESULTADO DO MAPEAMENTO:")
        print(f"   ✅ Canais mapeados automaticamente: {canais_mapeados}")
        print(f"   🆕 Canais novos/verificar: {len(canais_novos)}")
        
        # Mostrar canais novos/verificar
        if canais_novos:
            print(f"\n🆕 CANAIS PARA ANÁLISE MANUAL:")
            for i, canal in enumerate(canais_novos[:10], 1):  # Top 10
                if canal['sugestao']:
                    print(f"   {i:2d}. '{canal['vixen']}' ({canal['count']:,}) → '{canal['sugestao']}' ({canal['similaridade']:.1%})")
                else:
                    print(f"   {i:2d}. '{canal['vixen']}' ({canal['count']:,}) → NOVO CANAL")
        
        # Salvar mapeamento
        resultado_mapeamento = {
            'data_geracao': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
            'canais_mapeados': len(mapeamento_vixen),
            'canais_novos': len(canais_novos),
            'mapeamento_automatico': mapeamento_vixen,
            'canais_para_analise': canais_novos
        }
        
        output_file = base_dir / "data" / "originais" / "vixen" / "mapeamento_canais_vixen_existente.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(resultado_mapeamento, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resultado salvo: {output_file}")
        
        print(f"\n🎯 PRÓXIMOS PASSOS:")
        print(f"   1️⃣ Revisar canais com similaridade 50-80%")
        print(f"   2️⃣ Decidir sobre canais novos")
        print(f"   3️⃣ Aplicar mapeamento nos arquivos VIXEN")
        print(f"   4️⃣ Normalizar vendedores")
        
    else:
        print(f"❌ Coluna 'Como nos conheceu' não encontrada!")

if __name__ == "__main__":
    main()