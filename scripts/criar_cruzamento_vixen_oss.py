#!/usr/bin/env python3
"""
Criar Pasta Cruzamento VIXEN x OSS
==================================

Cria pasta específica para cruzamento entre clientes VIXEN e OSS das lojas MAUA e SUZANO.
"""

import shutil
from pathlib import Path
import pandas as pd

def main():
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    originais_dir = base_dir / "data" / "originais"
    
    # Criar pasta para cruzamento
    cruzamento_dir = originais_dir / "cruzamento_vixen_oss"
    cruzamento_dir.mkdir(exist_ok=True)
    
    print("🔗 CRIANDO PASTA CRUZAMENTO VIXEN x OSS")
    print("=" * 50)
    
    # Origens dos arquivos
    vixen_dir = originais_dir / "vixen" / "finais_postgresql_prontos"
    oss_dir = originais_dir / "oss" / "finais_postgresql_prontos"
    
    print(f"📂 Pasta criada: {cruzamento_dir}")
    
    # Arquivos a copiar
    arquivos_para_copiar = [
        # VIXEN - Clientes
        (vixen_dir / "clientes_maua_final.csv", "clientes_vixen_maua_original.csv"),
        (vixen_dir / "clientes_suzano_final.csv", "clientes_vixen_suzano_original.csv"),
        
        # OSS - Ordens de Serviço  
        (oss_dir / "MAUA_postgresql_pronto.csv", "oss_maua_original.csv"),
        (oss_dir / "SUZANO_postgresql_pronto.csv", "oss_suzano_original.csv")
    ]
    
    print(f"\n📦 COPIANDO ARQUIVOS PARA CRUZAMENTO:")
    
    arquivos_copiados = 0
    total_registros = 0
    
    for origem, destino_nome in arquivos_para_copiar:
        destino = cruzamento_dir / destino_nome
        
        if origem.exists():
            # Copiar arquivo
            shutil.copy2(str(origem), str(destino))
            
            # Verificar registros
            try:
                df = pd.read_csv(destino)
                registros = len(df)
                total_registros += registros
                
                # Extrair tipo e loja
                if "clientes_vixen" in destino_nome:
                    tipo = "CLIENTES"
                    loja = destino_nome.split("_")[2].upper()
                else:
                    tipo = "OSS"
                    loja = destino_nome.split("_")[1].upper()
                
                print(f"   ✅ {tipo} {loja}: {registros:,} registros → {destino_nome}")
                arquivos_copiados += 1
                
            except Exception as e:
                print(f"   ❌ Erro ao verificar {destino_nome}: {e}")
        else:
            print(f"   ⚠️  Não encontrado: {origem}")
    
    print(f"\n📊 RESUMO DO CRUZAMENTO:")
    print(f"   📁 Arquivos copiados: {arquivos_copiados}")
    print(f"   📈 Total de registros: {total_registros:,}")
    print(f"   📂 Localização: {cruzamento_dir}")
    
    # Verificar estrutura criada
    print(f"\n📋 ESTRUTURA PARA CRUZAMENTO:")
    for arquivo in sorted(cruzamento_dir.glob("*.csv")):
        try:
            df = pd.read_csv(arquivo)
            registros = len(df)
            
            if "clientes_vixen" in arquivo.name:
                tipo_icon = "👥"
                loja = arquivo.name.split("_")[2]
            else:
                tipo_icon = "📋"  
                loja = arquivo.name.split("_")[1]
                
            print(f"   {tipo_icon} {arquivo.name}: {registros:,} registros ({loja.upper()})")
            
        except Exception as e:
            print(f"   ❌ {arquivo.name}: Erro - {e}")
    
    print(f"\n🎯 PRÓXIMO PASSO:")
    print(f"   🔗 Analisar campos em comum entre VIXEN e OSS")
    print(f"   🔗 Identificar chaves de cruzamento (vendedor, cliente, etc)")
    print(f"   🔗 Criar tabela consolidada MAUA e SUZANO")
    print(f"   🔗 Mapear relacionamentos cliente ↔ OS")
    
    print(f"\n✅ PASTA CRUZAMENTO CRIADA E PRONTA!")

if __name__ == "__main__":
    main()