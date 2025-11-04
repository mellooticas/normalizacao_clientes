#!/usr/bin/env python3
"""
Script para trazer os arquivos de caixa da loja MAUA que estavam faltando
Sistema Carne Fácil - Completar organização MAUA
"""

import os
import shutil

def copiar_arquivos_maua():
    """
    Copia todos os arquivos Excel de caixa da loja MAUA
    """
    print("📁 COPIANDO ARQUIVOS DE CAIXA - LOJA MAUA")
    print("=" * 50)
    
    # Diretórios
    origem_maua = r'D:\OneDrive - Óticas Taty Mello\LOJAS\MAUA\CAIXA'
    destino_maua = 'data/originais/cxs/maua'
    
    # Criar pasta destino se não existir
    os.makedirs(destino_maua, exist_ok=True)
    
    arquivos_copiados = []
    
    if os.path.exists(origem_maua):
        print(f"📂 Origem: {origem_maua}")
        print(f"📂 Destino: {destino_maua}")
        
        # Buscar recursivamente em todas as subpastas da MAUA/CAIXA
        for root, dirs, files in os.walk(origem_maua):
            for file in files:
                if file.endswith(('.xlsx', '.xls')):
                    caminho_origem = os.path.join(root, file)
                    caminho_destino = os.path.join(destino_maua, file)
                    
                    try:
                        # Copiar arquivo
                        shutil.copy2(caminho_origem, caminho_destino)
                        arquivos_copiados.append(file)
                        print(f"   ✅ {file}")
                    except Exception as e:
                        print(f"   ❌ Erro ao copiar {file}: {str(e)}")
    else:
        print(f"❌ Pasta origem não encontrada: {origem_maua}")
        return False
    
    print(f"\n📊 RESUMO MAUA:")
    print(f"   ✅ Arquivos copiados: {len(arquivos_copiados)}")
    
    # Listar arquivos copiados
    if arquivos_copiados:
        print(f"   📄 Arquivos:")
        for arquivo in sorted(arquivos_copiados):
            print(f"      - {arquivo}")
    
    return len(arquivos_copiados) > 0

def verificar_estrutura_completa():
    """
    Verifica se agora todas as lojas estão com arquivos
    """
    print(f"\n🔍 VERIFICAÇÃO ESTRUTURA COMPLETA:")
    
    lojas = ['maua', 'perus', 'rio_pequeno', 'sao_mateus', 'suzano', 'suzano2']
    total_geral = 0
    
    for loja in lojas:
        pasta_loja = f'data/originais/cxs/{loja}'
        if os.path.exists(pasta_loja):
            arquivos = [f for f in os.listdir(pasta_loja) if f.endswith('.xlsx')]
            total_geral += len(arquivos)
            print(f"   📁 {loja}: {len(arquivos)} arquivos")
        else:
            print(f"   ❌ {loja}: pasta não encontrada")
    
    print(f"   📋 Total geral: {total_geral} arquivos")
    return total_geral

def main():
    """Função principal"""
    print("🔄 COMPLETANDO ORGANIZAÇÃO - MAUA")
    print("=" * 60)
    
    # Copiar arquivos MAUA
    sucesso = copiar_arquivos_maua()
    
    if sucesso:
        # Verificar estrutura completa
        total = verificar_estrutura_completa()
        
        print(f"\n✅ MAUA ADICIONADA COM SUCESSO!")
        print(f"📊 Total de arquivos: {total}")
        print(f"🎯 Estrutura completa para todas as 6 lojas")
    else:
        print(f"\n❌ ERRO AO ADICIONAR MAUA!")

if __name__ == "__main__":
    main()