#!/usr/bin/env python3
"""
Reorganizar Estrutura CXS igual OSS
===================================

Move todos os dados de CXS para dentro da pasta cxs, organizando igual fizemos com oss.
"""

import shutil
from pathlib import Path
import os

def main():
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    
    print("📁 REORGANIZANDO ESTRUTURA CXS")
    print("=" * 50)
    
    # Diretórios origem e destino
    cxs_dir = base_dir / "data" / "originais" / "cxs"
    finais_banco_atual = base_dir / "data" / "finais_banco"
    finais_banco_novo = cxs_dir / "finais_postgresql_prontos"
    
    print(f"📂 Estrutura atual:")
    print(f"   🔹 CXS: {cxs_dir}")
    print(f"   🔹 Finais (atual): {finais_banco_atual}")
    print(f"   🔹 Finais (novo): {finais_banco_novo}")
    
    # Verificar se diretório origem existe
    if not finais_banco_atual.exists():
        print(f"❌ Diretório {finais_banco_atual} não existe!")
        return
    
    # Criar diretório destino
    finais_banco_novo.mkdir(parents=True, exist_ok=True)
    print(f"✅ Criado: {finais_banco_novo}")
    
    # Mover arquivos
    arquivos_movidos = 0
    print(f"\n📦 Movendo arquivos finais...")
    
    for arquivo in finais_banco_atual.glob("*.csv"):
        destino = finais_banco_novo / arquivo.name
        print(f"   📄 {arquivo.name} → finais_postgresql_prontos/")
        shutil.move(str(arquivo), str(destino))
        arquivos_movidos += 1
    
    # Remover diretório antigo se estiver vazio
    if finais_banco_atual.exists() and not any(finais_banco_atual.iterdir()):
        finais_banco_atual.rmdir()
        print(f"🗑️  Removido diretório vazio: {finais_banco_atual}")
    
    print(f"\n✅ REORGANIZAÇÃO CONCLUÍDA")
    print(f"   📁 Arquivos movidos: {arquivos_movidos}")
    
    # Verificar estrutura final
    print(f"\n📋 ESTRUTURA FINAL:")
    print(f"   📂 data/originais/cxs/")
    
    for subdir in sorted(cxs_dir.iterdir()):
        if subdir.is_dir():
            arquivos = len(list(subdir.glob("*.csv"))) if subdir.name != "extraidos_corrigidos" else "multiple"
            if subdir.name == "extraidos_corrigidos":
                print(f"      🔹 {subdir.name}/ (dados originais)")
                for tabela_dir in sorted(subdir.iterdir()):
                    if tabela_dir.is_dir():
                        count = len(list(tabela_dir.glob("*.csv")))
                        print(f"         📊 {tabela_dir.name}: {count} arquivos")
            else:
                print(f"      🔹 {subdir.name}/ ({arquivos} arquivos)")
    
    print(f"\n🎯 AGORA TEMOS ORGANIZAÇÃO IGUAL AO OSS!")
    print(f"   📂 cxs/extraidos_corrigidos/ → dados originais")
    print(f"   📂 cxs/finais_postgresql_prontos/ → dados finais")

if __name__ == "__main__":
    main()