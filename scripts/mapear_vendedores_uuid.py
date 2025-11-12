#!/usr/bin/env python3
"""
Script para mapear vendedores UUID baseado na loja da venda
Estratégia: Para cada consultor, buscar UUID da loja correspondente
Se não encontrar, usar qualquer UUID do consultor como fallback
"""

import pandas as pd
import json
from pathlib import Path

def criar_mapeamento_vendedores():
    """
    Cria mapeamento de consultores para UUIDs baseado na loja
    """
    
    # Dicionário com os UUIDs de vendedores por consultor e loja
    # Baseado na Query 8 do arquivo consultas_vendedores_supabase.sql
    vendedores_mapping = {
        'BETH': {
            # UUID por loja_id
            '52f92716-d2ba-441a-ac3c-94bdfabd9722': '70559d08-b0e6-4f35-8f92-363e287367e8',  # Suzano
            '9a22ccf1-36fe-4b9f-9391-ca31433dc31e': '52e39d37-863c-4357-9509-24684e841a81',  # Mauá
            # Fallback (primeiro UUID encontrado)
            'fallback': '52e39d37-863c-4357-9509-24684e841a81'
        },
        'FELIPE': {
            '52f92716-d2ba-441a-ac3c-94bdfabd9722': 'a95b631e-b28e-410a-90ee-95f69bb01391',  # Suzano
            'aa7a5646-f7d6-4239-831c-6602fbabb10a': '12b38538-ef1d-4703-909c-f3c56e21605e',  # Suzano 2
            'fallback': '12b38538-ef1d-4703-909c-f3c56e21605e'
        },
        'LARISSA': {
            '4e94f51f-3b0f-4e0f-ba73-64982b870f2c': 'd9e18eee-c304-42ef-b5c4-7cbce900ed61',  # Rio Pequeno
            '52f92716-d2ba-441a-ac3c-94bdfabd9722': '39a1e217-ff8f-4cb1-9a0a-ef19f6228661',  # Suzano
            'da3978c9-bba2-431a-91b7-970a406d3acf': 'd8e4dee6-b890-4d13-9e31-82c15e7b485f',  # Perus
            '1c35e0ad-3066-441e-85cc-44c0eb9b3ab4': 'fa5349d2-1f56-43a8-bb75-3d2c4e412688',  # São Mateus
            '9a22ccf1-36fe-4b9f-9391-ca31433dc31e': '3a4d103f-ffe8-4e41-9315-4468f7c199a0',  # Mauá
            'fallback': 'fa5349d2-1f56-43a8-bb75-3d2c4e412688'
        },
        'TATY': {
            '4e94f51f-3b0f-4e0f-ba73-64982b870f2c': '68a501bc-9d4f-4053-b431-94f7cb2d1438',  # Rio Pequeno
            'da3978c9-bba2-431a-91b7-970a406d3acf': '56e4e9d9-6fa9-428b-a791-0a4995601c25',  # Perus
            '9a22ccf1-36fe-4b9f-9391-ca31433dc31e': 'cfb63f0a-704d-4516-8914-e6f1e6c3ee4d',  # Mauá
            '1c35e0ad-3066-441e-85cc-44c0eb9b3ab4': 'b2b47e57-6273-4c47-8d7e-bd5f0e407c40',  # São Mateus
            '52f92716-d2ba-441a-ac3c-94bdfabd9722': '56a56b51-4e26-41ea-b539-ef8e16b477de',  # Suzano
            'aa7a5646-f7d6-4239-831c-6602fbabb10a': 'b292be85-0d60-47aa-b36b-19a647496b04',  # Suzano 2
            'fallback': 'cfb63f0a-704d-4516-8914-e6f1e6c3ee4d'
        },
        'WEVILLY': {
            '1c35e0ad-3066-441e-85cc-44c0eb9b3ab4': 'a8bdcfb9-ace9-4e34-802a-6275c7629761',  # São Mateus
            '4e94f51f-3b0f-4e0f-ba73-64982b870f2c': 'ac0244dd-6356-4d19-88b0-2b01e3b9e0ac',  # Rio Pequeno
            'aa7a5646-f7d6-4239-831c-6602fbabb10a': '0d6b6515-a548-47a6-b847-8a6aab21ecc4',  # Suzano 2
            '9a22ccf1-36fe-4b9f-9391-ca31433dc31e': '143dc77e-f690-43c4-a60f-f68bd4b106fb',  # Mauá
            'da3978c9-bba2-431a-91b7-970a406d3acf': '73f2eee1-b8dd-4b82-bef0-032370a612bc',  # Perus
            'fallback': '73f2eee1-b8dd-4b82-bef0-032370a612bc'
        },
        'ERIKA': {
            'da3978c9-bba2-431a-91b7-970a406d3acf': 'c7b7f501-d028-4c09-b7d3-e6158799f972',  # Perus
            'aa7a5646-f7d6-4239-831c-6602fbabb10a': '7765bfa5-5879-43ab-9ce8-e3c132f3bcd1',  # Suzano 2
            'fallback': 'c7b7f501-d028-4c09-b7d3-e6158799f972'
        },
        'ROGÉRIO': {
            'da3978c9-bba2-431a-91b7-970a406d3acf': '31e51089-f7d4-4596-98f8-431096c6a098',  # Perus
            '52f92716-d2ba-441a-ac3c-94bdfabd9722': 'e6417905-e42b-459d-89c7-c9ce7bfd3a60',  # Suzano
            '1c35e0ad-3066-441e-85cc-44c0eb9b3ab4': '9dfe3659-8c52-4d33-ab40-03d50f2c6464',  # São Mateus
            '4e94f51f-3b0f-4e0f-ba73-64982b870f2c': 'a372478f-4731-4462-a1db-2a877de7f4f4',  # Rio Pequeno
            '9a22ccf1-36fe-4b9f-9391-ca31433dc31e': '622b7b77-8c8b-4737-aa40-c1038663fb25',  # Mauá
            'aa7a5646-f7d6-4239-831c-6602fbabb10a': 'e407dc34-ecc5-46e1-a232-d337bc055f9a',  # Suzano 2
            'fallback': '31e51089-f7d4-4596-98f8-431096c6a098'
        }
    }
    
    # Mapeamento de loja_uuid para nome (para debug)
    lojas_nomes = {
        '52f92716-d2ba-441a-ac3c-94bdfabd9722': 'Suzano',
        '9a22ccf1-36fe-4b9f-9391-ca31433dc31e': 'Mauá', 
        'da3978c9-bba2-431a-91b7-970a406d3acf': 'Perus',
        '4e94f51f-3b0f-4e0f-ba73-64982b870f2c': 'Rio Pequeno',
        '1c35e0ad-3066-441e-85cc-44c0eb9b3ab4': 'São Mateus',
        'aa7a5646-f7d6-4239-831c-6602fbabb10a': 'Suzano 2'
    }
    
    return vendedores_mapping, lojas_nomes

def mapear_vendedor_uuid(consultor, loja_uuid, vendedores_mapping):
    """
    Mapeia consultor para UUID de vendedor baseado na loja
    """
    if consultor not in vendedores_mapping:
        return None
    
    consultor_map = vendedores_mapping[consultor]
    
    # Tenta encontrar UUID específico para a loja
    if loja_uuid in consultor_map:
        return consultor_map[loja_uuid]
    
    # Usa fallback se não encontrar para a loja específica
    return consultor_map.get('fallback', None)

def processar_arquivos_normalizados():
    """
    Processa todos os arquivos normalizados adicionando UUIDs de vendedores
    """
    vendedores_mapping, lojas_nomes = criar_mapeamento_vendedores()
    
    # Diretório com dados normalizados
    dir_normalizados = Path("data/originais/oss/normalizadas")
    dir_saida = Path("data/originais/oss/normalizadas_com_vendedor_uuid")
    dir_saida.mkdir(exist_ok=True)
    
    # Estatísticas
    stats = {
        'arquivos_processados': 0,
        'total_vendas': 0,
        'vendas_com_uuid': 0,
        'vendas_sem_uuid': 0,
        'consultores_mapeados': {},
        'erros': []
    }
    
    # Processar cada arquivo normalizado
    for arquivo in dir_normalizados.glob("*.csv"):
        print(f"\n=== Processando {arquivo.name} ===")
        
        try:
            # Ler arquivo
            df = pd.read_csv(arquivo)
            stats['total_vendas'] += len(df)
            
            print(f"Total de registros: {len(df)}")
            print(f"Consultores únicos: {df['consultor'].unique()}")
            
            # Adicionar coluna vendedor_uuid
            df['vendedor_uuid'] = df.apply(
                lambda row: mapear_vendedor_uuid(
                    row['consultor'], 
                    row['loja_uuid'], 
                    vendedores_mapping
                ), 
                axis=1
            )
            
            # Contar mapeamentos
            vendas_com_uuid = df['vendedor_uuid'].notna().sum()
            vendas_sem_uuid = df['vendedor_uuid'].isna().sum()
            
            stats['vendas_com_uuid'] += vendas_com_uuid
            stats['vendas_sem_uuid'] += vendas_sem_uuid
            
            print(f"Vendas com UUID mapeado: {vendas_com_uuid}")
            print(f"Vendas sem UUID: {vendas_sem_uuid}")
            
            # Estatísticas por consultor
            for consultor in df['consultor'].unique():
                if consultor not in stats['consultores_mapeados']:
                    stats['consultores_mapeados'][consultor] = 0
                stats['consultores_mapeados'][consultor] += len(df[df['consultor'] == consultor])
            
            # Salvar arquivo com UUIDs
            arquivo_saida = dir_saida / arquivo.name
            df.to_csv(arquivo_saida, index=False)
            print(f"Salvo: {arquivo_saida}")
            
            stats['arquivos_processados'] += 1
            
        except Exception as e:
            erro = f"Erro ao processar {arquivo.name}: {str(e)}"
            print(f"❌ {erro}")
            stats['erros'].append(erro)
    
    # Relatório final
    print(f"\n" + "="*60)
    print("RELATÓRIO FINAL - MAPEAMENTO DE VENDEDORES")
    print(f"="*60)
    print(f"Arquivos processados: {stats['arquivos_processados']}")
    print(f"Total de vendas: {stats['total_vendas']}")
    print(f"Vendas com UUID: {stats['vendas_com_uuid']}")
    print(f"Vendas sem UUID: {stats['vendas_sem_uuid']}")
    print(f"Taxa de sucesso: {(stats['vendas_com_uuid']/stats['total_vendas']*100):.1f}%")
    
    print(f"\nConsultores mapeados:")
    for consultor, quantidade in sorted(stats['consultores_mapeados'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {consultor}: {quantidade} vendas")
    
    if stats['erros']:
        print(f"\nErros encontrados:")
        for erro in stats['erros']:
            print(f"  ❌ {erro}")
    
    # Salvar relatório
    with open(dir_saida / "relatorio_mapeamento.json", 'w') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    print(f"\nRelatório detalhado salvo em: {dir_saida / 'relatorio_mapeamento.json'}")
    print(f"Arquivos com UUIDs salvos em: {dir_saida}")

def verificar_mapeamento():
    """
    Verifica se o mapeamento está funcionando corretamente
    """
    vendedores_mapping, lojas_nomes = criar_mapeamento_vendedores()
    
    print("TESTE DE MAPEAMENTO DE VENDEDORES")
    print("="*50)
    
    # Casos de teste
    casos_teste = [
        ('BETH', '52f92716-d2ba-441a-ac3c-94bdfabd9722'),  # Suzano
        ('BETH', '9a22ccf1-36fe-4b9f-9391-ca31433dc31e'),   # Mauá
        ('FELIPE', 'aa7a5646-f7d6-4239-831c-6602fbabb10a'), # Suzano 2
        ('LARISSA', 'da3978c9-bba2-431a-91b7-970a406d3acf'), # Perus
        ('TATY', '1c35e0ad-3066-441e-85cc-44c0eb9b3ab4'),   # São Mateus
        ('WEVILLY', '4e94f51f-3b0f-4e0f-ba73-64982b870f2c'), # Rio Pequeno
        ('ERIKA', 'da3978c9-bba2-431a-91b7-970a406d3acf'),  # Perus
        ('ROGÉRIO', '9a22ccf1-36fe-4b9f-9391-ca31433dc31e'), # Mauá
        ('INEXISTENTE', '52f92716-d2ba-441a-ac3c-94bdfabd9722'), # Teste falha
    ]
    
    for consultor, loja_uuid in casos_teste:
        uuid_vendedor = mapear_vendedor_uuid(consultor, loja_uuid, vendedores_mapping)
        loja_nome = lojas_nomes.get(loja_uuid, 'DESCONHECIDA')
        
        status = "✅" if uuid_vendedor else "❌"
        print(f"{status} {consultor} @ {loja_nome}: {uuid_vendedor}")

if __name__ == "__main__":
    print("SCRIPT DE MAPEAMENTO DE VENDEDORES UUID")
    print("="*50)
    
    # Verificar mapeamento
    verificar_mapeamento()
    
    # Processar arquivos
    print(f"\n{'='*50}")
    resposta = input("Deseja processar todos os arquivos normalizados? (s/n): ")
    
    if resposta.lower() in ['s', 'sim', 'y', 'yes']:
        processar_arquivos_normalizados()
    else:
        print("Processamento cancelado.")