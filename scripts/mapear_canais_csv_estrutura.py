#!/usr/bin/env python3
"""
Script para mapear canais encontrados nos CSVs com a estrutura completa
"""

import json
import os

def mapear_canais_csv_para_estrutura():
    """Mapeia canais encontrados nos CSVs para a estrutura completa"""
    
    print("🔗 MAPEANDO CANAIS DOS CSVS PARA ESTRUTURA COMPLETA")
    print("=" * 60)
    
    # Carregar estrutura completa
    with open('mapeamento_canais_aquisicao_completo.json', 'r', encoding='utf-8') as f:
        estrutura_completa = json.load(f)
    
    # Carregar canais encontrados nos CSVs
    with open('mapeamento_canais_captacao_uuid_final.json', 'r', encoding='utf-8') as f:
        canais_csv = json.load(f)
    
    canais_encontrados = list(canais_csv['canais_captacao_uuid'].keys())
    canais_estrutura = {c['nome']: c for c in estrutura_completa['canais']}
    
    print(f"📊 DADOS PARA MAPEAMENTO:")
    print(f"   • Canais na estrutura completa: {len(canais_estrutura)}")
    print(f"   • Canais encontrados nos CSVs: {len(canais_encontrados)}")
    
    # Mapeamento direto e fuzzy
    mapeamento_final = {}
    nao_mapeados = []
    
    print(f"\n🎯 PROCESSO DE MAPEAMENTO:")
    
    for canal_csv in canais_encontrados:
        canal_limpo = canal_csv.strip()
        
        # Tentar mapeamento direto primeiro
        if canal_limpo in canais_estrutura:
            canal_estrutura = canais_estrutura[canal_limpo]
            mapeamento_final[canal_csv] = {
                'uuid': canal_estrutura['uuid'],
                'codigo': canal_estrutura['codigo'],
                'nome': canal_estrutura['nome'],
                'categoria': canal_estrutura['categoria'],
                'match_type': 'EXATO'
            }
            print(f"   ✅ EXATO: '{canal_csv}' → Código {canal_estrutura['codigo']}")
            continue
        
        # Mapeamentos manuais diretos baseados na análise dos dados
        mapeamentos_diretos = {
            '04 CLIENTES': {'nome': 'JÁ É CLIENTE', 'codigo': 4},
            '15 - ORÇAMENTO': {'nome': 'ORÇAMENTO', 'codigo': 15},
            '16 - INDICAÇÃO': {'nome': 'INDICAÇÃO', 'codigo': 16},
            '17 - ABORDAGEM': {'nome': 'ABORDAGEM', 'codigo': 17},
            '21 - TELEMARKETING': {'nome': 'TELEMARKETING', 'codigo': 21},
            '38 - DIVULGADOR': {'nome': 'DIVULGADOR', 'codigo': 38},
            '55 - CARTÃO DE TODOS': {'nome': 'CARTAO DE TODOS', 'codigo': 55},
            '77 - AMIGO (IND)': {'nome': 'AMIGOS', 'codigo': 77},
            '98 - WHATSAPP': {'nome': 'WHATSAPP', 'codigo': 98},
            '138 - SAÚDE DOS OLHOS': {'nome': 'SAÚDE DOS OLHOS', 'codigo': 138},
            'GOOGLE': {'nome': 'GOOGLE/FACE/INSTA - PATROCÍNIO', 'codigo': 152},
            '01 - REDES SOCIAS': {'nome': 'REDE SOCIAL', 'codigo': 1},
            'NÃO INFORMADO': {'nome': 'OUTROS', 'codigo': 99}
        }
        
        if canal_csv in mapeamentos_diretos:
            direto = mapeamentos_diretos[canal_csv]
            # Buscar na estrutura pelo código
            canal_por_codigo = None
            for c in estrutura_completa['canais']:
                if c['codigo'] == direto['codigo']:
                    canal_por_codigo = c
                    break
            
            if canal_por_codigo:
                mapeamento_final[canal_csv] = {
                    'uuid': canal_por_codigo['uuid'],
                    'codigo': canal_por_codigo['codigo'],
                    'nome': canal_por_codigo['nome'],
                    'categoria': canal_por_codigo['categoria'],
                    'match_type': 'DIRETO'
                }
                print(f"   🎯 DIRETO: '{canal_csv}' → Código {direto['codigo']} ('{direto['nome']}')")
                continue
        
        # Não mapeado
        nao_mapeados.append(canal_csv)
        print(f"   ❌ NÃO MAPEADO: '{canal_csv}'")
    
    print(f"\n📈 RESULTADOS DO MAPEAMENTO:")
    print(f"   • Mapeados com sucesso: {len(mapeamento_final)}")
    print(f"   • Não mapeados: {len(nao_mapeados)}")
    print(f"   • Taxa de sucesso: {(len(mapeamento_final)/len(canais_encontrados))*100:.1f}%")
    
    if nao_mapeados:
        print(f"\n⚠️  CANAIS NÃO MAPEADOS:")
        for canal in nao_mapeados:
            print(f"   • '{canal}'")
    
    # Análise por tipo de match
    tipos_match = {}
    for canal, info in mapeamento_final.items():
        tipo = info['match_type']
        tipos_match[tipo] = tipos_match.get(tipo, 0) + 1
    
    print(f"\n📊 TIPOS DE MAPEAMENTO:")
    for tipo, qtd in tipos_match.items():
        print(f"   • {tipo}: {qtd} canais")
    
    # Salvar mapeamento final
    resultado_final = {
        'data_geracao': '2025-10-29',
        'total_canais_csv': len(canais_encontrados),
        'total_mapeados': len(mapeamento_final),
        'total_nao_mapeados': len(nao_mapeados),
        'taxa_sucesso': (len(mapeamento_final)/len(canais_encontrados))*100,
        'mapeamento': mapeamento_final,
        'nao_mapeados': nao_mapeados,
        'tipos_match': tipos_match
    }
    
    with open('mapeamento_canais_csv_para_estrutura.json', 'w', encoding='utf-8') as f:
        json.dump(resultado_final, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 MAPEAMENTO SALVO:")
    print(f"   • Arquivo: mapeamento_canais_csv_para_estrutura.json")
    print(f"   • {len(mapeamento_final)} canais mapeados")
    
    # Análise por categoria dos mapeados
    print(f"\n🏷️  DISTRIBUIÇÃO POR CATEGORIA (canais mapeados):")
    categorias = {}
    for canal, info in mapeamento_final.items():
        cat = info['categoria']
        categorias[cat] = categorias.get(cat, 0) + 1
    
    for categoria, qtd in sorted(categorias.items(), key=lambda x: x[1], reverse=True):
        print(f"   • {categoria}: {qtd} canais")
    
    return resultado_final

if __name__ == "__main__":
    mapear_canais_csv_para_estrutura()