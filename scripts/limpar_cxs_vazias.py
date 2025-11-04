#!/usr/bin/env python3
"""
Limpar Pastas Vazias CXS
========================

Remove pastas vazias desnecessárias da estrutura CXS.
"""

import shutil
from pathlib import Path

def main():
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    cxs_dir = base_dir / "data" / "originais" / "cxs"
    
    print("🧹 LIMPANDO PASTAS VAZIAS CXS")
    print("=" * 40)
    
    # Pastas a remover se estiverem vazias
    pastas_para_limpar = [
        "maua", "perus", "rio_pequeno", "sao_mateus", "suzano", "suzano2",
        "extraidos_por_tipo_backup"
    ]
    
    removidas = 0
    
    for pasta in pastas_para_limpar:
        pasta_path = cxs_dir / pasta
        
        if pasta_path.exists() and pasta_path.is_dir():
            # Verificar se está vazia
            conteudo = list(pasta_path.iterdir())
            
            if not conteudo:
                print(f"🗑️  Removendo pasta vazia: {pasta}")
                pasta_path.rmdir()
                removidas += 1
            else:
                print(f"📁 Mantendo {pasta} (contém {len(conteudo)} itens)")
        else:
            print(f"⚠️  {pasta} não existe")
    
    print(f"\n✅ Limpeza concluída: {removidas} pastas removidas")
    
    # Verificar estrutura final
    print(f"\n📋 ESTRUTURA CXS FINAL:")
    for item in sorted(cxs_dir.iterdir()):
        if item.is_dir():
            if item.name == "extraidos_corrigidos":
                print(f"   📂 {item.name}/ (dados originais)")
                for subitem in sorted(item.iterdir()):
                    if subitem.is_dir():
                        count = len(list(subitem.glob("*.csv")))
                        if count > 0:
                            print(f"      📊 {subitem.name}: {count} arquivos")
            else:
                count = len(list(item.glob("*.csv")))
                print(f"   📂 {item.name}/ ({count} arquivos)")
    
    print(f"\n🎯 CXS ORGANIZADO IGUAL AO OSS!")

if __name__ == "__main__":
    main()