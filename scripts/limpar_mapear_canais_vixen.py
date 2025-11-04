#!/usr/bin/env python3
"""
Limpar e Mapear Canais VIXEN com Existentes
===========================================

Limpa dados VIXEN e usa mapeamento existente, gerando SQL para canais realmente novos.
"""

import pandas as pd
import json
from pathlib import Path
from difflib import SequenceMatcher

def limpar_texto(texto):
    """Remove espaços extras e normaliza texto"""
    if pd.isna(texto):
        return ""
    return str(texto).strip()

def similaridade_texto(a, b):
    """Calcula similaridade entre dois textos limpos"""
    a_limpo = limpar_texto(a).upper()
    b_limpo = limpar_texto(b).upper()
    return SequenceMatcher(None, a_limpo, b_limpo).ratio()

def main():
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    vixen_finais_dir = base_dir / "data" / "originais" / "vixen" / "finais_postgresql_prontos"
    
    print("🧹 LIMPANDO E MAPEANDO CANAIS VIXEN COM EXISTENTES")
    print("=" * 60)
    
    # Carregar mapeamento existente
    mapeamento_existente_file = base_dir / "mapeamento_canais_aquisicao_completo.json"
    
    with open(mapeamento_existente_file, 'r', encoding='utf-8') as f:
        mapeamento_existente = json.load(f)
    
    print(f"📊 Mapeamento existente: {mapeamento_existente['total_canais']} canais")
    
    # Criar dicionário para busca rápida (texto limpo -> canal)
    canais_existentes = {}
    for canal in mapeamento_existente['canais']:
        nome_limpo = limpar_texto(canal['nome']).upper()
        canais_existentes[nome_limpo] = canal
    
    # Carregar dados VIXEN
    df_maua = pd.read_csv(vixen_finais_dir / "clientes_maua_final.csv")
    df_suzano = pd.read_csv(vixen_finais_dir / "clientes_suzano_final.csv")
    df_total = pd.concat([df_maua, df_suzano], ignore_index=True)
    
    print(f"📊 Dados VIXEN: {len(df_total):,} registros")
    
    if 'Como nos conheceu' in df_total.columns:
        # Limpar dados VIXEN
        df_total['Como nos conheceu LIMPO'] = df_total['Como nos conheceu'].apply(limpar_texto)
        canais_vixen = df_total['Como nos conheceu LIMPO'].value_counts()
        
        print(f"📊 Canais únicos VIXEN (após limpeza): {len(canais_vixen)}")
        
        # Processar mapeamento
        mapeamento_final = {}
        canais_encontrados = 0
        canais_novos = []
        
        print(f"\n🔍 PROCESSANDO MAPEAMENTO:")
        
        for canal_vixen_limpo, count in canais_vixen.items():
            if not canal_vixen_limpo:  # Ignorar vazios
                continue
                
            canal_vixen_upper = canal_vixen_limpo.upper()
            
            # Busca exata primeiro
            if canal_vixen_upper in canais_existentes:
                canal_existente = canais_existentes[canal_vixen_upper]
                mapeamento_final[canal_vixen_limpo] = {
                    'canal_uuid': canal_existente['uuid'],
                    'canal_codigo': canal_existente['codigo'],
                    'canal_nome': canal_existente['nome'],
                    'canal_categoria': canal_existente['categoria'],
                    'match_type': 'EXATO',
                    'count': count
                }
                canais_encontrados += 1
                print(f"   ✅ '{canal_vixen_limpo}' → EXATO")
                
            else:
                # Busca por similaridade alta (>95%)
                melhor_match = None
                melhor_similaridade = 0.0
                
                for nome_existente, canal_existente in canais_existentes.items():
                    similaridade = similaridade_texto(canal_vixen_limpo, nome_existente)
                    if similaridade > melhor_similaridade:
                        melhor_similaridade = similaridade
                        melhor_match = canal_existente
                
                if melhor_similaridade > 0.95:
                    mapeamento_final[canal_vixen_limpo] = {
                        'canal_uuid': melhor_match['uuid'],
                        'canal_codigo': melhor_match['codigo'],
                        'canal_nome': melhor_match['nome'],
                        'canal_categoria': melhor_match['categoria'],
                        'match_type': 'SIMILARIDADE_ALTA',
                        'similaridade': round(melhor_similaridade, 3),
                        'count': count
                    }
                    canais_encontrados += 1
                    print(f"   ✅ '{canal_vixen_limpo}' → SIMILAR ({melhor_similaridade:.1%})")
                    
                else:
                    # Canal realmente novo
                    canais_novos.append({
                        'nome': canal_vixen_limpo,
                        'count': count,
                        'melhor_similar': melhor_match['nome'] if melhor_match else None,
                        'similaridade': melhor_similaridade
                    })
                    print(f"   🆕 '{canal_vixen_limpo}' → NOVO ({count:,} clientes)")
        
        print(f"\n📊 RESULTADO DO MAPEAMENTO LIMPO:")
        print(f"   ✅ Canais encontrados: {canais_encontrados}")
        print(f"   🆕 Canais novos: {len(canais_novos)}")
        
        # Mostrar canais novos ordenados por quantidade
        if canais_novos:
            canais_novos_ordenados = sorted(canais_novos, key=lambda x: x['count'], reverse=True)
            
            print(f"\n🆕 CANAIS NOVOS (TOP 10):")
            for i, canal in enumerate(canais_novos_ordenados[:10], 1):
                print(f"   {i:2d}. '{canal['nome']}' - {canal['count']:,} clientes")
            
            # Gerar SQL para inserção
            print(f"\n📝 GERANDO SQL PARA CANAIS NOVOS:")
            
            sql_inserts = []
            proximo_codigo = max([c['codigo'] for c in mapeamento_existente['canais']]) + 1
            
            for canal in canais_novos_ordenados:
                # Categorizar canal
                nome_upper = canal['nome'].upper()
                categoria = "OUTROS"
                
                if any(termo in nome_upper for termo in ["INDICAÇÃO", "INDICACAO", "INDICA"]):
                    categoria = "INDICACAO"
                elif any(termo in nome_upper for termo in ["SAÚDE", "SAUDE", "CLINICA", "SUS"]):
                    categoria = "SAUDE"
                elif any(termo in nome_upper for termo in ["ORÇAMENTO", "ORCAMENTO", "1ª COMPRA", "1A COMPRA"]):
                    categoria = "COMERCIAL"
                elif any(termo in nome_upper for termo in ["DIVULGADOR", "ABORDAGEM", "PASSAGEM"]):
                    categoria = "MARKETING"
                elif any(termo in nome_upper for termo in ["JÁ É CLIENTE", "JA E CLIENTE", "CLIENTE"]):
                    categoria = "RETENCAO"
                elif any(termo in nome_upper for termo in ["RADIO", "REDE SOCIAL", "GOOGLE", "FACE", "INSTA"]):
                    categoria = "DIGITAL"
                
                sql_insert = f"""
INSERT INTO marketing.canais_aquisicao (codigo, nome, descricao, categoria, ativo) 
VALUES ('{proximo_codigo:03d}', '{canal['nome']}', 'Canal importado do VIXEN - {canal['count']} clientes', '{categoria}', true);"""
                
                sql_inserts.append(sql_insert)
                proximo_codigo += 1
            
            # Salvar SQL
            sql_file = base_dir / "data" / "originais" / "vixen" / "insert_canais_novos_vixen.sql"
            
            with open(sql_file, 'w', encoding='utf-8') as f:
                f.write("-- Inserção de canais novos do VIXEN\n")
                f.write(f"-- Gerado em: {pd.Timestamp.now()}\n")
                f.write(f"-- Total de canais novos: {len(canais_novos)}\n\n")
                f.write("BEGIN;\n\n")
                
                for sql in sql_inserts:
                    f.write(sql)
                    f.write("\n")
                
                f.write("\nCOMMIT;\n")
            
            print(f"   ✅ SQL salvo: {sql_file}")
        
        # Salvar mapeamento final
        resultado_final = {
            'data_processamento': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
            'canais_mapeados': len(mapeamento_final),
            'canais_novos': len(canais_novos),
            'mapeamento_limpo': mapeamento_final,
            'canais_novos_detalhes': canais_novos
        }
        
        mapeamento_file = base_dir / "data" / "originais" / "vixen" / "mapeamento_canais_vixen_limpo.json"
        
        with open(mapeamento_file, 'w', encoding='utf-8') as f:
            json.dump(resultado_final, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Mapeamento final salvo: {mapeamento_file}")
        
        print(f"\n🎯 PRÓXIMOS PASSOS:")
        print(f"   1️⃣ Executar SQL no banco para inserir canais novos")
        print(f"   2️⃣ Aplicar mapeamento limpo nos arquivos VIXEN")
        print(f"   3️⃣ Normalizar vendedores")
        print(f"   4️⃣ Finalizar estrutura para cruzamentos")
        
    else:
        print(f"❌ Coluna 'Como nos conheceu' não encontrada!")

if __name__ == "__main__":
    main()