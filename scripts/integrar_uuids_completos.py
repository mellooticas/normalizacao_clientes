#!/usr/bin/env python3
"""
Script para criar arquivos finais com UUIDs das LOJAS E VENDEDORES
Integra os dois sistemas de UUID em um arquivo completo
"""

import pandas as pd
import json
from pathlib import Path

def carregar_mapeamento_vendedores():
    """Carrega o mapeamento de vendedores UUID"""
    with open('mapeamento_vendedores_csvs_completo.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['vendedores_uuid']

def normalizar_consultor(consultor):
    """Normaliza nome do consultor para busca no mapeamento"""
    if pd.isna(consultor) or consultor is None:
        return ''
    
    nome = str(consultor).strip().upper()
    
    # Normalizações específicas
    normalizacoes = {
        'BETH': 'MARIA ELIZABETH',
        'TATY': 'TATIANA MELLO DE CAMARGO',
        'TATIANA': 'TATIANA MELLO DE CAMARGO',
        'BRUNA': 'BRUNA',
        'THIAGO': 'THIAGO',
        'RENAN': 'RENAN  NAZARO',
        'ARIANI': 'ARIANI DIAS FERNANDES CARDOSO',
        'ROGERIO': 'ROGERIO APARECIDO DE MORAIS',
        'ROGÉRIO': 'ROGERIO APARECIDO DE MORAIS',
        'ERICA': 'ERICA DE CASSIA JESUS SILVA',
        'WEVILLY': 'WEVILLY',
        'ANDRESSA': 'ANDRESSA DE SOUZA',
        'FELIPE': 'FELIPE MIRANDA',
        'JOCY': 'JOCICREIDE BARBOSA',
        'ERIKA': 'ÉRIKA'
    }
    
    return normalizacoes.get(nome, nome)

def integrar_uuids_completos():
    """Integra UUIDs de lojas e vendedores nos CSVs finais"""
    
    # Diretórios
    origem_dir = Path("data/originais/oss/normalizadas")
    destino_dir = Path("data/originais/oss/finais_com_uuids")
    destino_dir.mkdir(exist_ok=True)
    
    # Carregar mapeamento de vendedores
    vendedores_uuid = carregar_mapeamento_vendedores()
    
    print("🔗 INTEGRAÇÃO DE UUIDs COMPLETOS - LOJAS E VENDEDORES")
    print("=" * 60)
    
    # Estatísticas
    total_arquivos = 0
    total_registros = 0
    total_com_vendedor_uuid = 0
    total_sem_vendedor_uuid = 0
    
    # Processar cada arquivo
    for csv_file in origem_dir.glob("*_normalizado_uuid.csv"):
        if csv_file.name.startswith('.'):
            continue
            
        total_arquivos += 1
        loja_nome = csv_file.stem.replace("_normalizado_uuid", "")
        
        print(f"\n📊 Processando {loja_nome}...")
        
        try:
            # Ler CSV atual (que já tem loja_id)
            df = pd.read_csv(csv_file, encoding='utf-8')
            
            num_registros = len(df)
            total_registros += num_registros
            
            # Adicionar colunas de vendedor UUID se não existirem
            if 'vendedor_uuid' not in df.columns:
                df['vendedor_uuid'] = ''
            if 'vendedor_nome_normalizado' not in df.columns:
                df['vendedor_nome_normalizado'] = ''
            
            # Processar cada linha
            com_uuid = 0
            sem_uuid = 0
            
            for idx, row in df.iterrows():
                consultor_original = row.get('             CONSULTOR  ', '')
                consultor_normalizado = normalizar_consultor(consultor_original)
                
                # Buscar UUID do vendedor
                vendedor_uuid = vendedores_uuid.get(consultor_normalizado)
                
                if vendedor_uuid:
                    df.at[idx, 'vendedor_uuid'] = vendedor_uuid
                    df.at[idx, 'vendedor_nome_normalizado'] = consultor_normalizado
                    com_uuid += 1
                else:
                    sem_uuid += 1
                    if consultor_original.strip():  # Se não está vazio
                        print(f"   ⚠️  Vendedor sem UUID: '{consultor_original}' -> '{consultor_normalizado}'")
            
            total_com_vendedor_uuid += com_uuid
            total_sem_vendedor_uuid += sem_uuid
            
            # Salvar arquivo final
            arquivo_final = destino_dir / f"{loja_nome}_final_completo.csv"
            df.to_csv(arquivo_final, index=False, encoding='utf-8-sig')
            
            print(f"   • Registros: {num_registros:,}")
            print(f"   • Com vendedor UUID: {com_uuid:,} ({(com_uuid/num_registros)*100:.1f}%)")
            if sem_uuid > 0:
                print(f"   • Sem vendedor UUID: {sem_uuid:,} ({(sem_uuid/num_registros)*100:.1f}%)")
            print(f"   • ✅ Salvo: {arquivo_final}")
            
        except Exception as e:
            print(f"   • ❌ Erro: {e}")
    
    print("\n" + "=" * 60)
    print("📈 RELATÓRIO FINAL:")
    print(f"   • Arquivos processados: {total_arquivos}")
    print(f"   • Total de registros: {total_registros:,}")
    print(f"   • Com vendedor UUID: {total_com_vendedor_uuid:,} ({(total_com_vendedor_uuid/total_registros)*100:.1f}%)")
    
    if total_sem_vendedor_uuid > 0:
        print(f"   • ⚠️  Sem vendedor UUID: {total_sem_vendedor_uuid:,} ({(total_sem_vendedor_uuid/total_registros)*100:.1f}%)")
    else:
        print(f"   • ✅ Todos os registros têm UUIDs completos!")
    
    print(f"\n📁 Arquivos finais salvos em: {destino_dir}")
    
    # Verificar estrutura final
    exemplo_file = list(destino_dir.glob("*_final_completo.csv"))[0] if destino_dir.glob("*_final_completo.csv") else None
    if exemplo_file:
        print(f"\n🔍 ESTRUTURA DO ARQUIVO FINAL ({exemplo_file.name}):")
        df_exemplo = pd.read_csv(exemplo_file, nrows=1)
        for col in df_exemplo.columns:
            if 'uuid' in col.lower() or 'loja' in col.lower():
                print(f"   • {col}")

if __name__ == "__main__":
    integrar_uuids_completos()