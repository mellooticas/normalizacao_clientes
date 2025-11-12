#!/usr/bin/env python3
"""
Limpeza segura da tabela vendas - Remove apenas vendas do dataset VIXEN completo
para permitir reimportação sem conflitos de constraint
"""

import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

# Carrega variáveis de ambiente
load_dotenv()

def conectar_supabase():
    """Conecta ao banco Supabase"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('SUPABASE_HOST'),
            database=os.getenv('SUPABASE_DATABASE'), 
            user=os.getenv('SUPABASE_USER'),
            password=os.getenv('SUPABASE_PASSWORD'),
            port=os.getenv('SUPABASE_PORT', 5432)
        )
        return conn
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return None

def limpar_vendas_vixen_completo():
    """Remove vendas do dataset VIXEN completo para permitir reimportação"""
    
    print("🧹 === LIMPEZA VENDAS VIXEN COMPLETO === 🧹")
    
    conn = conectar_supabase()
    if not conn:
        print("❌ Não foi possível conectar ao banco")
        return False
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # 1. Verificar vendas existentes
        print("🔍 Verificando vendas existentes...")
        
        cursor.execute("""
            SELECT 
                observacoes,
                COUNT(*) as total_vendas,
                SUM(valor_total) as valor_total
            FROM vendas.vendas 
            WHERE deleted_at IS NULL
            GROUP BY observacoes
            ORDER BY total_vendas DESC;
        """)
        
        vendas_existentes = cursor.fetchall()
        print(f"📊 Vendas por fonte:")
        for venda in vendas_existentes:
            print(f"   {venda['observacoes']}: {venda['total_vendas']} vendas (R$ {venda['valor_total']:,.2f})")
        
        # 2. Contar vendas que serão removidas
        cursor.execute("""
            SELECT COUNT(*) as total, SUM(valor_total) as valor
            FROM vendas.vendas 
            WHERE observacoes = 'Importado VIXEN outros pagamentos - Dataset completo 14k linhas'
              AND deleted_at IS NULL;
        """)
        
        resultado = cursor.fetchone()
        vendas_para_remover = resultado['total']
        valor_para_remover = resultado['valor'] or 0
        
        print(f"\n⚠️  VENDAS PARA REMOÇÃO:")
        print(f"   📊 Quantidade: {vendas_para_remover}")
        print(f"   💰 Valor: R$ {valor_para_remover:,.2f}")
        
        if vendas_para_remover == 0:
            print("✅ Nenhuma venda VIXEN completo encontrada. Nada para remover.")
            return True
        
        # 3. Confirmar remoção
        confirmacao = input(f"\n🤔 Confirma a remoção de {vendas_para_remover} vendas? (s/N): ").strip().lower()
        
        if confirmacao not in ['s', 'sim', 'y', 'yes']:
            print("❌ Operação cancelada pelo usuário")
            return False
        
        # 4. Executar soft delete (recomendado)
        print(f"\n🗑️  Executando soft delete...")
        
        cursor.execute("""
            UPDATE vendas.vendas 
            SET 
                deleted_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP,
                updated_by = 'SISTEMA_LIMPEZA_VIXEN_COMPLETO'
            WHERE observacoes = 'Importado VIXEN outros pagamentos - Dataset completo 14k linhas'
              AND deleted_at IS NULL;
        """)
        
        linhas_afetadas = cursor.rowcount
        conn.commit()
        
        print(f"✅ Soft delete executado: {linhas_afetadas} vendas marcadas como deletadas")
        
        # 5. Verificar resultado
        cursor.execute("""
            SELECT 
                'Ativas' as status,
                COUNT(*) as total_vendas,
                COALESCE(SUM(valor_total), 0) as valor_total
            FROM vendas.vendas 
            WHERE deleted_at IS NULL
            UNION ALL
            SELECT 
                'Deletadas' as status,
                COUNT(*) as total_vendas,
                COALESCE(SUM(valor_total), 0) as valor_total
            FROM vendas.vendas 
            WHERE deleted_at IS NOT NULL;
        """)
        
        resultado_final = cursor.fetchall()
        
        print(f"\n📊 RESULTADO FINAL:")
        for linha in resultado_final:
            print(f"   {linha['status']}: {linha['total_vendas']} vendas (R$ {linha['valor_total']:,.2f})")
        
        # 6. Verificar se constraints estão livres
        cursor.execute("""
            SELECT 
                loja_id,
                numero_venda,
                COUNT(*) as duplicatas
            FROM vendas.vendas 
            WHERE deleted_at IS NULL
              AND loja_id IN (
                '52f92716-d2ba-441a-ac3c-94bdfabd9722', -- SUZANO
                'aa7a5646-f7d6-4239-831c-6602fbabb10a'  -- MAUÁ
              )
              AND numero_venda IN ('457.0', '491.0', '510.0', '558.0', '564.0')
            GROUP BY loja_id, numero_venda
            HAVING COUNT(*) > 1;
        """)
        
        duplicatas_restantes = cursor.fetchall()
        
        if duplicatas_restantes:
            print(f"⚠️  ATENÇÃO: Ainda há duplicatas:")
            for dup in duplicatas_restantes:
                print(f"   Loja {dup['loja_id']}, Venda {dup['numero_venda']}: {dup['duplicatas']} duplicatas")
        else:
            print(f"✅ Nenhuma duplicata restante. Pronto para reimportação!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante limpeza: {e}")
        conn.rollback()
        return False
        
    finally:
        cursor.close()
        conn.close()

def opcao_hard_delete():
    """Opção de hard delete (permanente) - apenas se necessário"""
    
    print("\n⚠️  === OPÇÃO HARD DELETE (PERMANENTE) === ⚠️")
    print("⚠️  CUIDADO: Esta opção remove os dados permanentemente!")
    
    confirmacao = input("Tem certeza que quer fazer hard delete? Digite 'CONFIRMO HARD DELETE': ").strip()
    
    if confirmacao != 'CONFIRMO HARD DELETE':
        print("❌ Hard delete cancelado")
        return False
    
    conn = conectar_supabase()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM vendas.vendas 
            WHERE observacoes = 'Importado VIXEN outros pagamentos - Dataset completo 14k linhas';
        """)
        
        linhas_removidas = cursor.rowcount
        conn.commit()
        
        print(f"🗑️  Hard delete executado: {linhas_removidas} vendas removidas PERMANENTEMENTE")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no hard delete: {e}")
        conn.rollback()
        return False
        
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("🧹 LIMPEZA DE VENDAS VIXEN COMPLETO")
    print("=" * 50)
    
    print("\nOpções:")
    print("1. Soft Delete (Recomendado - marca como deletado)")
    print("2. Hard Delete (Remove permanentemente)")
    print("3. Cancelar")
    
    opcao = input("\nEscolha uma opção (1-3): ").strip()
    
    if opcao == "1":
        sucesso = limpar_vendas_vixen_completo()
        if sucesso:
            print("\n🎉 Limpeza concluída! Agora você pode reimportar os dados.")
    elif opcao == "2":
        sucesso = opcao_hard_delete()
        if sucesso:
            print("\n🎉 Hard delete concluído! Agora você pode reimportar os dados.")
    else:
        print("❌ Operação cancelada")