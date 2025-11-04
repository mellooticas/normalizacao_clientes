#!/usr/bin/env python3
"""
Verificar completude dos CSVs com UUID dos vendedores
"""

import os
import pandas as pd
from pathlib import Path

def verificar_csvs():
    """Verificar se todos os CSVs têm os campos UUID preenchidos"""
    
    csv_dir = Path("data/originais/oss/normalizadas")
    
    if not csv_dir.exists():
        print(f"❌ Diretório não encontrado: {csv_dir}")
        return
    
    print("🔍 Verificando completude dos CSVs normalizados com UUID...")
    print("=" * 60)
    
    total_arquivos = 0
    total_registros = 0
    total_com_uuid = 0
    total_sem_uuid = 0
    
    for csv_file in csv_dir.glob("*_normalizado_uuid.csv"):
        total_arquivos += 1
        loja = csv_file.stem.replace("_normalizado_uuid", "")
        
        print(f"\n📊 {loja}:")
        
        try:
            # Ler o CSV
            df = pd.read_csv(csv_file, encoding='utf-8')
            
            num_registros = len(df)
            total_registros += num_registros
            
            # Verificar se tem as colunas UUID
            if 'vendedor_uuid' in df.columns and 'vendedor_nome_normalizado' in df.columns:
                # Contar registros com UUID
                com_uuid = df['vendedor_uuid'].notna().sum()
                sem_uuid = num_registros - com_uuid
                
                total_com_uuid += com_uuid
                total_sem_uuid += sem_uuid
                
                print(f"   • Total de registros: {num_registros:,}")
                print(f"   • Com UUID: {com_uuid:,} ({(com_uuid/num_registros)*100:.1f}%)")
                
                if sem_uuid > 0:
                    print(f"   • ⚠️  Sem UUID: {sem_uuid:,} ({(sem_uuid/num_registros)*100:.1f}%)")
                    
                    # Mostrar alguns exemplos sem UUID
                    sem_uuid_df = df[df['vendedor_uuid'].isna()].head(3)
                    if not sem_uuid_df.empty:
                        print("   • Exemplos sem UUID:")
                        for _, row in sem_uuid_df.iterrows():
                            vendedor = row.get('vendedor', 'N/A')
                            os_num = row.get('os', 'N/A')
                            print(f"     - OS {os_num}: Vendedor '{vendedor}'")
                else:
                    print(f"   • ✅ Todos os registros têm UUID!")
                    
            else:
                print(f"   • ❌ Colunas UUID não encontradas!")
                
        except Exception as e:
            print(f"   • ❌ Erro ao processar: {e}")
    
    print("\n" + "=" * 60)
    print("📈 RESUMO GERAL:")
    print(f"   • Arquivos processados: {total_arquivos}")
    print(f"   • Total de registros: {total_registros:,}")
    print(f"   • Com UUID: {total_com_uuid:,} ({(total_com_uuid/total_registros)*100:.1f}%)")
    
    if total_sem_uuid > 0:
        print(f"   • ⚠️  Sem UUID: {total_sem_uuid:,} ({(total_sem_uuid/total_registros)*100:.1f}%)")
    else:
        print(f"   • ✅ Todos os {total_registros:,} registros têm UUID!")

if __name__ == "__main__":
    verificar_csvs()