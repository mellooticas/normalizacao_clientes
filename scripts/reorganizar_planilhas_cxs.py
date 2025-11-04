#!/usr/bin/env python3
"""
Reorganizar Planilhas Originais CXS
===================================

Move as planilhas originais para pasta específica mantendo organização.
"""

import shutil
from pathlib import Path

def main():
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    cxs_dir = base_dir / "data" / "originais" / "cxs"
    planilhas_dir = cxs_dir / "planilhas_originais"
    
    print("📊 REORGANIZANDO PLANILHAS ORIGINAIS CXS")
    print("=" * 50)
    
    # Criar diretório para planilhas
    planilhas_dir.mkdir(exist_ok=True)
    
    # Lojas para processar
    lojas = ["maua", "perus", "rio_pequeno", "sao_mateus", "suzano", "suzano2"]
    
    total_planilhas = 0
    
    for loja in lojas:
        loja_origem = cxs_dir / loja
        loja_destino = planilhas_dir / loja
        
        if loja_origem.exists() and loja_origem.is_dir():
            # Verificar se tem planilhas
            planilhas = list(loja_origem.glob("*.xlsx"))
            
            if planilhas:
                # Criar pasta da loja no destino
                loja_destino.mkdir(exist_ok=True)
                
                print(f"📂 {loja.upper()}: {len(planilhas)} planilhas")
                
                # Mover planilhas
                for planilha in planilhas:
                    destino = loja_destino / planilha.name
                    shutil.move(str(planilha), str(destino))
                    print(f"   📄 {planilha.name}")
                    total_planilhas += 1
                
                # Remover pasta vazia da origem
                if not any(loja_origem.iterdir()):
                    loja_origem.rmdir()
                    print(f"   🗑️ Pasta {loja} removida")
            else:
                print(f"📂 {loja.upper()}: Sem planilhas")
    
    # Processar backup se existir
    backup_origem = cxs_dir / "extraidos_por_tipo_backup"
    if backup_origem.exists():
        backup_destino = planilhas_dir / "backup"
        if any(backup_origem.iterdir()):
            backup_destino.mkdir(exist_ok=True)
            shutil.move(str(backup_origem), str(backup_destino))
            print(f"📦 Backup movido para planilhas_originais/backup/")
        else:
            backup_origem.rmdir()
            print(f"🗑️ Pasta backup vazia removida")
    
    print(f"\n✅ REORGANIZAÇÃO CONCLUÍDA")
    print(f"   📊 Total de planilhas: {total_planilhas}")
    
    # Verificar estrutura final
    print(f"\n📋 ESTRUTURA CXS FINAL ORGANIZADA:")
    for item in sorted(cxs_dir.iterdir()):
        if item.is_dir():
            if item.name == "extraidos_corrigidos":
                print(f"   📂 {item.name}/ (dados processados)")
                for subitem in sorted(item.iterdir()):
                    if subitem.is_dir():
                        count = len(list(subitem.glob("*.csv")))
                        if count > 0:
                            print(f"      📊 {subitem.name}: {count} arquivos")
            elif item.name == "planilhas_originais":
                print(f"   📂 {item.name}/ (planilhas xlsx)")
                for subitem in sorted(item.iterdir()):
                    if subitem.is_dir():
                        count = len(list(subitem.glob("*.xlsx")))
                        print(f"      📊 {subitem.name}: {count} planilhas")
            else:
                count = len(list(item.glob("*.csv")))
                print(f"   📂 {item.name}/ ({count} arquivos)")
    
    print(f"\n🎯 CXS PERFEITAMENTE ORGANIZADO!")
    print(f"   📂 planilhas_originais/ → arquivos xlsx por loja")
    print(f"   📂 extraidos_corrigidos/ → dados processados")
    print(f"   📂 finais_postgresql_prontos/ → dados finais")

if __name__ == "__main__":
    main()