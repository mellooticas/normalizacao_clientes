#!/usr/bin/env python3
"""
Script para organizar arquivos de caixa por lojas
Sistema Carne Fácil - Reorganização de arquivos CX
"""

import os
import shutil
import re
from pathlib import Path

def identificar_loja_por_arquivo(nome_arquivo):
    """
    Identifica a loja baseada no nome do arquivo
    """
    nome_arquivo = nome_arquivo.lower()
    
    # Mapeamento de padrões para lojas
    padroes_lojas = {
        'maua': ['maua', 'mauá'],
        'perus': ['perus'],
        'rio_pequeno': ['rio_pequeno', 'rio pequeno', 'riopequeno'],
        'sao_mateus': ['sao_mateus', 'sao mateus', 'saomateus'],
        'suzano': ['suzano1', 'suzano 1', 'suzano_1'],
        'suzano2': ['suzano2', 'suzano 2', 'suzano_2']
    }
    
    for loja, padroes in padroes_lojas.items():
        for padrao in padroes:
            if padrao in nome_arquivo:
                return loja
    
    return None

def identificar_loja_por_caminho(caminho_completo):
    """
    Identifica a loja baseada no caminho do arquivo
    """
    caminho_str = str(caminho_completo).upper()
    
    # Verificar se há indicação de loja no caminho
    if '\\MAUA\\' in caminho_str or '\\MAUÁ\\' in caminho_str:
        return 'maua'
    elif '\\PERUS\\' in caminho_str:
        return 'perus'
    elif '\\RIO_PEQUENO\\' in caminho_str:
        return 'rio_pequeno'
    elif '\\SAO_MATEUS\\' in caminho_str:
        return 'sao_mateus'
    elif '\\SUZANO2\\' in caminho_str:
        return 'suzano2'
    elif '\\SUZANO\\' in caminho_str:
        return 'suzano'
    
    return None

def listar_arquivos_caixa():
    """
    Lista todos os arquivos Excel de caixa encontrados nas pastas das lojas no OneDrive
    """
    # Diretório base das lojas
    diretorio_base = r'D:\OneDrive - Óticas Taty Mello\LOJAS'
    
    # Pastas das lojas
    lojas_diretorios = ['SUZANO', 'SUZANO2', 'MAUA', 'PERUS', 'RIO_PEQUENO', 'SAO_MATEUS']
    
    arquivos_encontrados = []
    
    if os.path.exists(diretorio_base):
        print(f"📁 Buscando arquivos em: {diretorio_base}")
        
        for loja_dir in lojas_diretorios:
            caminho_loja = os.path.join(diretorio_base, loja_dir)
            
            if os.path.exists(caminho_loja):
                print(f"   🔍 Verificando {loja_dir}...")
                
                # Verificar se tem pasta CAIXA dentro da loja
                pasta_caixa = os.path.join(caminho_loja, 'CAIXA')
                if os.path.exists(pasta_caixa):
                    print(f"      📁 Encontrada pasta CAIXA")
                    
                    # Buscar recursivamente em todas as subpastas da pasta CAIXA
                    for root, dirs, files in os.walk(pasta_caixa):
                        for file in files:
                            if file.endswith(('.xlsx', '.xls')):
                                caminho_completo = os.path.join(root, file)
                                arquivos_encontrados.append(caminho_completo)
                                print(f"         ✅ {file}")
                else:
                    # Buscar arquivos de caixa diretamente na pasta da loja
                    for root, dirs, files in os.walk(caminho_loja):
                        for file in files:
                            if file.endswith(('.xlsx', '.xls')):
                                # Verificar se é arquivo de caixa (contém palavras relacionadas)
                                nome_lower = file.lower()
                                if any(palavra in nome_lower for palavra in ['caixa', 'cx', 'movimento', 'diario', 'mensal']):
                                    caminho_completo = os.path.join(root, file)
                                    arquivos_encontrados.append(caminho_completo)
                                    print(f"      ✅ {file}")
            else:
                print(f"   ⚠️  {loja_dir} não encontrada")
                
        print(f"📋 Total encontrado: {len(arquivos_encontrados)} arquivos Excel de caixa")
    else:
        print(f"❌ Diretório base não encontrado: {diretorio_base}")
    
    return arquivos_encontrados

def organizar_arquivos_por_loja():
    """
    Organiza todos os arquivos de caixa por loja
    """
    print("📁 ORGANIZANDO ARQUIVOS DE CAIXA POR LOJA")
    print("=" * 50)
    
    # Listar todos os arquivos
    arquivos = listar_arquivos_caixa()
    print(f"📋 Encontrados {len(arquivos)} arquivos Excel")
    
    if not arquivos:
        print("❌ Nenhum arquivo Excel encontrado nos diretórios de caixa")
        return
    
    # Estatísticas
    arquivos_organizados = {
        'maua': [],
        'perus': [],
        'rio_pequeno': [],
        'sao_mateus': [],
        'suzano': [],
        'suzano2': [],
        'nao_identificados': []
    }
    
    # Organizar cada arquivo
    for arquivo in arquivos:
        nome_arquivo = os.path.basename(arquivo)
        
        # Tentar identificar a loja
        loja = identificar_loja_por_arquivo(nome_arquivo)
        if not loja:
            loja = identificar_loja_por_caminho(arquivo)
        
        if loja:
            # Definir destino
            destino_dir = f'data/originais/cx/{loja}'
            destino_arquivo = os.path.join(destino_dir, nome_arquivo)
            
            try:
                # Copiar arquivo para nova estrutura
                shutil.copy2(arquivo, destino_arquivo)
                arquivos_organizados[loja].append(nome_arquivo)
                print(f"   ✅ {nome_arquivo} → {loja}")
            except Exception as e:
                print(f"   ❌ Erro ao copiar {nome_arquivo}: {str(e)}")
        else:
            arquivos_organizados['nao_identificados'].append(nome_arquivo)
            print(f"   ⚠️  {nome_arquivo} → NÃO IDENTIFICADO")
    
    # Relatório final
    print(f"\n📊 RESUMO DA ORGANIZAÇÃO:")
    total_organizados = 0
    for loja, arquivos_loja in arquivos_organizados.items():
        if loja != 'nao_identificados' and arquivos_loja:
            print(f"   🏪 {loja.upper()}: {len(arquivos_loja)} arquivos")
            total_organizados += len(arquivos_loja)
    
    if arquivos_organizados['nao_identificados']:
        print(f"   ⚠️  NÃO IDENTIFICADOS: {len(arquivos_organizados['nao_identificados'])} arquivos")
        for arquivo in arquivos_organizados['nao_identificados']:
            print(f"      - {arquivo}")
    
    print(f"\n🎯 RESULTADO:")
    print(f"   ✅ Organizados: {total_organizados} arquivos")
    print(f"   ⚠️  Não identificados: {len(arquivos_organizados['nao_identificados'])} arquivos")
    print(f"   📁 Estrutura criada em: data/originais/cx/")
    
    return arquivos_organizados

def verificar_estrutura_criada():
    """
    Verifica a estrutura criada
    """
    print(f"\n🔍 VERIFICANDO ESTRUTURA CRIADA:")
    
    lojas = ['maua', 'perus', 'rio_pequeno', 'sao_mateus', 'suzano', 'suzano2']
    
    for loja in lojas:
        caminho_loja = f'data/originais/cx/{loja}'
        if os.path.exists(caminho_loja):
            arquivos = [f for f in os.listdir(caminho_loja) if f.endswith(('.xlsx', '.xls'))]
            print(f"   📁 {loja}: {len(arquivos)} arquivos")
            
            if arquivos:
                # Mostrar alguns exemplos
                exemplos = arquivos[:3]
                for arquivo in exemplos:
                    print(f"      - {arquivo}")
                if len(arquivos) > 3:
                    print(f"      ... e mais {len(arquivos) - 3} arquivos")

def main():
    """Função principal"""
    print("🔄 REORGANIZAÇÃO DE ARQUIVOS DE CAIXA")
    print("=" * 60)
    
    # Verificar se existem arquivos para organizar
    arquivos = listar_arquivos_caixa()
    if not arquivos:
        print("❌ Nenhum arquivo encontrado para organizar.")
        print("📁 Verifique se existem arquivos de caixa nas pastas:")
        print("   - D:\\OneDrive - Óticas Taty Mello\\LOJAS\\SUZANO\\")
        print("   - D:\\OneDrive - Óticas Taty Mello\\LOJAS\\SUZANO2\\")
        print("   - D:\\OneDrive - Óticas Taty Mello\\LOJAS\\MAUA\\")
        print("   - D:\\OneDrive - Óticas Taty Mello\\LOJAS\\PERUS\\")
        print("   - D:\\OneDrive - Óticas Taty Mello\\LOJAS\\RIO_PEQUENO\\")
        print("   - D:\\OneDrive - Óticas Taty Mello\\LOJAS\\SAO_MATEUS\\")
        return
    
    # Organizar arquivos
    resultado = organizar_arquivos_por_loja()
    
    # Verificar resultado
    verificar_estrutura_criada()
    
    print(f"\n✅ REORGANIZAÇÃO CONCLUÍDA!")
    print(f"🎯 Próximo passo: Processar dados por loja individual")

if __name__ == "__main__":
    main()