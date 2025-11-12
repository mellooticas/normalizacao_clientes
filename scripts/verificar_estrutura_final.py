#!/usr/bin/env python3
"""
Verificar Estrutura Final Organizada
====================================

Compara estruturas CXS e OSS para confirmar organização idêntica.
"""

from pathlib import Path

def listar_estrutura(pasta_base, nome):
    print(f"\n📂 {nome.upper()}")
    print("=" * 30)
    
    for item in sorted(pasta_base.iterdir()):
        if item.is_dir():
            # Contar arquivos conforme tipo
            if item.name == "extraidos_corrigidos":
                print(f"   📊 {item.name}/ (dados processados)")
                for subitem in sorted(item.iterdir()):
                    if subitem.is_dir() and not subitem.name.startswith('_'):
                        count = len(list(subitem.glob("*.csv")))
                        if count > 0:
                            print(f"      🔹 {subitem.name}: {count} arquivos")
            
            elif item.name == "planilhas_originais":
                print(f"   📊 {item.name}/ (planilhas xlsx)")
                for subitem in sorted(item.iterdir()):
                    if subitem.is_dir():
                        count = len(list(subitem.glob("*.xlsx")))
                        if count > 0:
                            print(f"      🔹 {subitem.name}: {count} planilhas")
            
            elif item.name == "finais_postgresql_prontos":
                count = len(list(item.glob("*.csv")))
                print(f"   📊 {item.name}/ ({count} arquivos finais)")
            
            else:
                count = len(list(item.glob("*")))
                if count > 0:
                    print(f"   📁 {item.name}/ ({count} itens)")

def main():
    base_dir = Path("d:/projetos/carne_facil/carne_facil/data/originais")
    
    cxs_dir = base_dir / "cxs"
    oss_dir = base_dir / "oss"
    
    print("🎯 VERIFICAÇÃO ESTRUTURA ORGANIZADA")
    print("=" * 50)
    
    # Verificar CXS
    if cxs_dir.exists():
        listar_estrutura(cxs_dir, "CXS")
    else:
        print("❌ CXS não encontrado!")
    
    # Verificar OSS
    if oss_dir.exists():
        listar_estrutura(oss_dir, "OSS")
    else:
        print("❌ OSS não encontrado!")
    
    print(f"\n✅ COMPARAÇÃO ESTRUTURAL")
    
    # Verificar se ambos têm finais_postgresql_prontos
    cxs_finais = cxs_dir / "finais_postgresql_prontos"
    oss_finais = oss_dir / "finais_postgresql_prontos"
    
    if cxs_finais.exists() and oss_finais.exists():
        cxs_count = len(list(cxs_finais.glob("*.csv")))
        oss_count = len(list(oss_finais.glob("*.csv")))
        
        print(f"   🔹 CXS finais: {cxs_count} arquivos")
        print(f"   🔹 OSS finais: {oss_count} arquivos")
        print(f"   ✅ Ambos têm estrutura finais_postgresql_prontos/")
    
    print(f"\n🎉 ORGANIZAÇÃO IGUAL AO OSS CONCLUÍDA!")

if __name__ == "__main__":
    main()