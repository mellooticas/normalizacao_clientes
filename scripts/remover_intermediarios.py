#!/usr/bin/env python3
"""
Remover Arquivos Intermediários
==============================

Remove arquivos intermediários de processamento mantendo apenas:
1. Dados originais extraídos das planilhas (data/originais/cxs/extraidos_corrigidos/)
2. Arquivos finais para o banco (data/finais_banco/)
"""

import os
from pathlib import Path
import shutil

def main():
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    
    # Diretórios a limpar
    diretorios_intermediarios = [
        base_dir / "data" / "originais" / "cxs" / "exportados",
        base_dir / "data" / "originais" / "cxs" / "revisao",
        base_dir / "data" / "originais" / "cxs" / "uuid_aplicados",
        base_dir / "data" / "originais" / "cxs" / "enriquecidos"
    ]
    
    print("🧹 REMOVENDO ARQUIVOS INTERMEDIÁRIOS")
    print("=" * 50)
    
    total_removidos = 0
    total_diretorios = 0
    
    for diretorio in diretorios_intermediarios:
        if diretorio.exists():
            print(f"\n📂 Limpando: {diretorio.name}")
            
            # Contar arquivos antes de remover
            arquivos = list(diretorio.rglob("*"))
            arquivos_count = len([f for f in arquivos if f.is_file()])
            
            if arquivos_count > 0:
                print(f"   🗑️  Removendo {arquivos_count} arquivos...")
                shutil.rmtree(diretorio)
                total_removidos += arquivos_count
                total_diretorios += 1
                print(f"   ✅ Diretório removido")
            else:
                print(f"   ℹ️  Diretório já está vazio")
        else:
            print(f"📂 {diretorio.name}: Não existe")
    
    # Verificar arquivos individuais intermediários no diretório raiz
    print(f"\n📄 Verificando arquivos individuais intermediários...")
    
    padroes_intermediarios = [
        "*_com_uuid_*.csv",
        "*_enriquecido_*.csv", 
        "*_exportado_*.csv",
        "*_revisao_*.csv"
    ]
    
    arquivos_individuais = 0
    for padrao in padroes_intermediarios:
        for arquivo in base_dir.glob(padrao):
            if arquivo.is_file():
                print(f"   🗑️  Removendo: {arquivo.name}")
                arquivo.unlink()
                arquivos_individuais += 1
    
    total_removidos += arquivos_individuais
    
    print(f"\n📊 LIMPEZA CONCLUÍDA")
    print(f"   🗑️  Arquivos removidos: {total_removidos}")
    print(f"   📁 Diretórios removidos: {total_diretorios}")
    
    # Verificar o que sobrou
    print(f"\n📋 ESTRUTURA FINAL LIMPA:")
    
    # Dados originais extraídos
    origem_dir = base_dir / "data" / "originais" / "cxs" / "extraidos_corrigidos"
    if origem_dir.exists():
        print(f"   ✅ Dados extraídos mantidos: {origem_dir}")
        for tabela_dir in sorted(origem_dir.iterdir()):
            if tabela_dir.is_dir():
                arquivos = len(list(tabela_dir.glob("*.csv")))
                print(f"      📊 {tabela_dir.name}: {arquivos} arquivos")
    
    # Arquivos finais para banco
    finais_dir = base_dir / "data" / "finais_banco"
    if finais_dir.exists():
        print(f"   ✅ Arquivos finais mantidos: {finais_dir}")
        arquivos_finais = len(list(finais_dir.glob("*.csv")))
        print(f"      📊 Arquivos finais: {arquivos_finais}")
    
    print(f"\n🎯 WORKSPACE ORGANIZADO!")
    print(f"   📂 Dados originais: Preservados")
    print(f"   📂 Arquivos finais: Prontos para banco")
    print(f"   🧹 Intermediários: Removidos")

if __name__ == "__main__":
    main()