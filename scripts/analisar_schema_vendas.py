#!/usr/bin/env python3
"""
Análise completa do schema VENDAS baseado nos resultados das queries
Gera plano de implementação das próximas tabelas
"""

from pathlib import Path
from datetime import datetime

def analisar_schema_vendas():
    """Analisa os resultados das queries e gera plano de implementação"""
    
    print("📊 === ANÁLISE COMPLETA DO SCHEMA VENDAS === 📊")
    print(f"📅 Análise realizada em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # === TABELAS IDENTIFICADAS ===
    tabelas_base = [
        "entregas_carne",
        "entregas_os", 
        "formas_pagamento",
        "formas_pagamento_venda",
        "itens_venda",
        "recebimentos_carne",
        "restantes_entrada",
        "restituicoes",
        "vendas",
        "vendas_formas_pagamento"
    ]
    
    views = [
        "v_entregas_pendentes",
        "v_garantias", 
        "v_resumo_recebimentos",
        "v_resumo_recebimentos_loja",
        "v_resumo_restituicoes",
        "v_resumo_vendas_loja",
        "v_saldo_a_receber",
        "v_vendas_completas",
        "v_vendas_completo",
        "v_vendas_reais"
    ]

    print(f"🏗️ === ESTRUTURA IDENTIFICADA === 🏗️")
    print(f"📋 Tabelas base: {len(tabelas_base)}")
    print(f"👁️ Views: {len(views)}")
    print()

    for tabela in tabelas_base:
        print(f"   📊 {tabela}")
    print()
    
    for view in views:
        print(f"   👁️ {view}")
    print()

    # === STATUS ATUAL ===
    print(f"✅ === STATUS ATUAL === ✅")
    print(f"🎯 IMPLEMENTADAS E FUNCIONANDO:")
    print(f"   ✅ vendas - 15.281 registros")
    print(f"   ✅ formas_pagamento - 9 registros")  
    print(f"   ✅ vendas_formas_pagamento - 19.737 registros")
    print()

    # === PRÓXIMAS IMPLEMENTAÇÕES ===
    print(f"🚀 === PLANO DE IMPLEMENTAÇÃO (SEQUÊNCIA CORRETA) === 🚀")
    print()
    
    # PRIORIDADE 1 - DADOS COMPLETOS DISPONÍVEIS
    print(f"🔥 PRIORIDADE 1 - DADOS COMPLETOS:")
    print(f"   1️⃣ entregas_os - CONTROLE de entregas")
    print(f"      ✅ Temos todos os dados das vendas (15.281)")
    print(f"      � Falta apenas: data_entrega (calculável)")
    print(f"      🎯 IMPLEMENTAÇÃO: IMEDIATA")
    print(f"      🔗 FK: venda_id → vendas.id")
    print()
    
    print(f"   2️⃣ itens_venda - PRODUTOS das vendas")
    print(f"      ✅ Temos todas as vendas com valores")
    print(f"      🎲 Dados mock baseados em padrões realistas")
    print(f"      📋 Campos: tipo_produto, descricao, marca, modelo, valor_unitario")
    print(f"      🔗 FK: venda_id → vendas.id")
    print()

    # PRIORIDADE 2 - DADOS FINANCEIROS (PENDENTE NORMALIZAÇÃO)
    print(f"💰 PRIORIDADE 2 - DADOS FINANCEIROS:")
    print(f"   3️⃣ recebimentos_carne - PAGAMENTOS do carnê")
    print(f"      ✅ Temos dados VIXEN de carnê processados")
    print(f"      ❓ Faltam dados mov_fin VIXEN (não normalizados)")
    print(f"      🎯 IMPLEMENTAÇÃO: Após normalizar mov_fin")
    print(f"      📋 Campos: venda_id, data_recebimento, valor_recebido")
    print(f"      🔗 FK: venda_id → vendas.id")
    print()

    # PRIORIDADE 3 - DADOS PARCIAIS (PENDENTE CXS)
    print(f"🚚 PRIORIDADE 3 - DADOS PARCIAIS:")
    print(f"   4️⃣ entregas_carne - ENTREGAS físicas do carnê")
    print(f"      ✅ Temos entregas VIXEN processadas")
    print(f"      ❓ Faltam dados pasta CXS (sistema novo)")
    print(f"      🎯 IMPLEMENTAÇÃO: Após processar dados CXS")
    print(f"      📋 Campos: venda_id, os_numero, parcela, data_entrega")
    print(f"      🔗 FK: venda_id → vendas.id")
    print()
    
    print(f"   5️⃣ restantes_entrada - VALORES pendentes")
    print(f"      🎯 Controlar entradas não pagas")
    print(f"      📋 Campos: venda_id, valor_restante, data_vencimento")
    print(f"      🔗 FK: venda_id → vendas.id")
    print()

    # PRIORIDADE 4 - EXTRAS
    print(f"⚡ PRIORIDADE 4 - FUNCIONALIDADES EXTRAS:")
    print(f"   6️⃣ restituicoes - DEVOLUÇÕES e estornos")
    print(f"   7️⃣ formas_pagamento_venda - ALTERNATIVA às vendas_formas_pagamento")
    print()

    # === OBSERVAÇÕES IMPORTANTES ===
    print(f"⚠️ === OBSERVAÇÕES IMPORTANTES === ⚠️")
    print()
    
    print(f"🔍 DUPLICAÇÃO DETECTADA:")
    print(f"   ❓ formas_pagamento_venda vs vendas_formas_pagamento")
    print(f"   📊 Ambas controlam formas de pagamento por venda")
    print(f"   💡 DECISÃO: Usar vendas_formas_pagamento (já implementada)")
    print()
    
    print(f"🎯 CAMPOS IMPORTANTES IDENTIFICADOS:")
    print(f"   📦 itens_venda.requer_encomenda - Produtos sob encomenda")
    print(f"   📅 itens_venda.data_prevista_chegada - Previsão de chegada")
    print(f"   🔢 itens_venda.codigo_barras - Controle de estoque")
    print(f"   🏭 itens_venda.fornecedor - Gestão de fornecedores")
    print()

    # === SCRIPTS A CRIAR ===
    print(f"🛠️ === SCRIPTS A CRIAR === 🛠️")
    print()
    
    scripts_necessarios = [
        {
            "nome": "01_criar_entregas_os.sql",
            "desc": "Cria tabela entregas_os - DADOS COMPLETOS DISPONÍVEIS",
            "prioridade": "🔥 ALTA - IMEDIATA"
        },
        {
            "nome": "02_gerar_entregas_os_mock.py", 
            "desc": "Gera dados de entregas para as 15.281 vendas (datas calculadas)",
            "prioridade": "🔥 ALTA - IMEDIATA"
        },
        {
            "nome": "03_criar_itens_venda.sql",
            "desc": "Cria tabela itens_venda com todos os campos", 
            "prioridade": "🔥 ALTA - IMEDIATA"
        },
        {
            "nome": "04_gerar_itens_vendas_mock.py",
            "desc": "Gera dados mock de itens baseado nos valores das vendas",
            "prioridade": "🔥 ALTA - IMEDIATA"
        },
        {
            "nome": "05_normalizar_mov_fin_vixen.py",
            "desc": "Processa e normaliza dados mov_fin do VIXEN (financeiro)",
            "prioridade": "💰 MÉDIA - DEPENDENTE"
        },
        {
            "nome": "06_criar_recebimentos_carne.sql",
            "desc": "Cria tabela recebimentos_carne para controle financeiro",
            "prioridade": "💰 MÉDIA - APÓS MOV_FIN"
        },
        {
            "nome": "07_processar_entregas_cxs.py",
            "desc": "Processa dados de entregas da pasta CXS (sistema novo)",
            "prioridade": "🚚 BAIXA - DEPENDENTE CXS"
        },
        {
            "nome": "08_criar_entregas_carne.sql",
            "desc": "Cria tabela entregas_carne após processar todos os dados",
            "prioridade": "� BAIXA - APÓS CXS"
        },
        {
            "nome": "09_views_operacionais.sql",
            "desc": "Recria as 10 views identificadas no schema",
            "prioridade": "⚡ FINAL"
        }
    ]
    
    for script in scripts_necessarios:
        print(f"   {script['prioridade']} {script['nome']}")
        print(f"      📝 {script['desc']}")
        print()

    # === ANÁLISE DE DADOS ===
    print(f"📈 === ANÁLISE DOS DADOS ATUAIS === 📈")
    print()
    
    print(f"💳 FORMAS DE PAGAMENTO (19.737 registros):")
    print(f"   🏆 Parcelado Cartão: 6.254 (31.7%)")
    print(f"   💸 PIX: 4.389 (22.2%)")
    print(f"   💳 Cartão Crédito: 3.765 (19.1%)")
    print(f"   💵 Dinheiro: 3.485 (17.7%)")
    print(f"   📋 Carnê: 1.844 (9.3%)")
    print()
    
    print(f"🏪 DISTRIBUIÇÃO POR LOJAS:")
    print(f"   📊 Total de vendas: 15.281")
    print(f"   💰 Valor total: R$ 7.889.566,44")
    print(f"   📈 Valor médio: R$ 516,30")
    print()

    # === RECOMENDAÇÕES ===
    print(f"💡 === RECOMENDAÇÕES === 💡")
    print()
    
    print(f"🎯 PRÓXIMOS PASSOS IMEDIATOS:")
    print(f"   1. Implementar entregas_os (dados completos disponíveis)")
    print(f"   2. Implementar itens_venda (dados mock baseados em vendas)")
    print(f"   3. Normalizar mov_fin VIXEN para recebimentos_carne") 
    print(f"   4. Processar dados CXS para entregas_carne")
    print()
    
    print(f"⚠️ PONTOS DE ATENÇÃO:")
    print(f"   🔄 Manter consistência com vendas_formas_pagamento existente")
    print(f"   📊 entregas_os: Calcular data_entrega baseada em data_venda + prazo")
    print(f"   💰 recebimentos_carne: Aguardar normalização mov_fin VIXEN")
    print(f"   🚚 entregas_carne: Aguardar processamento dados CXS")
    print(f"   🔗 Garantir integridade referencial em todas as FKs")
    print(f"   📊 Criar índices apropriados para performance")
    print()

    return {
        "tabelas_base": tabelas_base,
        "views": views,
        "scripts_necessarios": scripts_necessarios,
        "prioridade_implementacao": [
            "entregas_os",      # PRIORIDADE 1 - Dados completos
            "itens_venda",      # PRIORIDADE 1 - Dados completos  
            "recebimentos_carne", # PRIORIDADE 2 - Após mov_fin
            "entregas_carne",   # PRIORIDADE 3 - Após CXS
            "restantes_entrada" # PRIORIDADE 3 - Complementar
        ]
    }

def gerar_plano_implementacao():
    """Gera documento detalhado do plano de implementação"""
    
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    arquivo_plano = base_dir / f"PLANO_IMPLEMENTACAO_VENDAS_{timestamp}.md"
    
    plano_md = f"""
# PLANO DE IMPLEMENTAÇÃO - SCHEMA VENDAS

**Data:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Objetivo:** Completar implementação do schema vendas com todas as tabelas essenciais

## 🎯 RESUMO EXECUTIVO

✅ **CONCLUÍDO:**
- `vendas` - 15.281 registros
- `formas_pagamento` - 9 registros  
- `vendas_formas_pagamento` - 19.737 registros

🚀 **PRÓXIMAS IMPLEMENTAÇÕES:**
- `itens_venda` - Produtos das vendas
- `entregas_os` - Controle de entregas
- `recebimentos_carne` - Controle financeiro

## 📋 TABELAS IDENTIFICADAS

### 📊 Tabelas Base (10)
1. ✅ `vendas` - IMPLEMENTADA
2. ✅ `formas_pagamento` - IMPLEMENTADA  
3. ✅ `vendas_formas_pagamento` - IMPLEMENTADA
4. 🔥 `itens_venda` - **PRÓXIMA**
5. 🔥 `entregas_os` - **PRÓXIMA**
6. 💰 `recebimentos_carne` - **MÉDIA PRIORIDADE**
7. 💰 `restantes_entrada` - **MÉDIA PRIORIDADE**
8. 🚚 `entregas_carne` - **BAIXA PRIORIDADE**
9. ⚡ `restituicoes` - **EXTRA**
10. ❓ `formas_pagamento_venda` - **DUPLICADA**

### 👁️ Views (10)
- `v_vendas_completas` - Vendas com todos os dados
- `v_vendas_reais` - Vendas válidas/ativas
- `v_entregas_pendentes` - Entregas não realizadas
- `v_resumo_recebimentos` - Resumo financeiro
- `v_saldo_a_receber` - Valores pendentes
- E mais 5 views operacionais...

## 🔥 PRIORIDADE 1 - ESSENCIAIS

### 1️⃣ itens_venda
**Objetivo:** Detalhar produtos de cada venda

```sql
CREATE TABLE vendas.itens_venda (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  venda_id uuid NOT NULL REFERENCES vendas.vendas(id),
  tipo_produto varchar(100) NOT NULL, -- 'OCULOS', 'LENTE', 'ARMACAO'
  descricao varchar(300) NOT NULL,
  marca varchar(100),
  modelo varchar(100), 
  quantidade integer NOT NULL DEFAULT 1,
  valor_unitario numeric(12,2) NOT NULL,
  valor_total numeric(12,2),
  requer_encomenda boolean DEFAULT false,
  data_prevista_chegada date,
  created_at timestamp DEFAULT CURRENT_TIMESTAMP
);
```

**Dados Mock:** Gerar 1-3 itens por venda (principalmente óculos completos)

### 2️⃣ entregas_os  
**Objetivo:** Controlar entregas ao cliente

```sql
CREATE TABLE vendas.entregas_os (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  venda_id uuid NOT NULL REFERENCES vendas.vendas(id),
  data_entrega date NOT NULL,
  tem_carne boolean DEFAULT false,
  created_at timestamp DEFAULT now()
);
```

**Dados Mock:** 80% das vendas já entregues, 20% pendentes

## 💰 PRIORIDADE 2 - FINANCEIRO

### 3️⃣ recebimentos_carne
**Objetivo:** Controlar pagamentos do carnê

```sql
CREATE TABLE vendas.recebimentos_carne (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  venda_id uuid NOT NULL REFERENCES vendas.vendas(id),
  data_recebimento date NOT NULL,
  valor_recebido numeric(12,2) NOT NULL,
  parcela_numero integer,
  created_at timestamp DEFAULT CURRENT_TIMESTAMP
);
```

**Dados Mock:** Baseado nas vendas com forma carnê (1.844 registros)

## 🛠️ SCRIPTS A DESENVOLVER

### Imediatos (Esta Semana)
1. `01_criar_itens_venda.sql` - Estrutura da tabela
2. `02_gerar_itens_vendas_mock.py` - Dados mock realistas  
3. `03_criar_entregas_os.sql` - Estrutura da tabela
4. `04_gerar_entregas_mock.py` - Dados mock de entregas

### Médio Prazo (Próxima Semana)  
5. `05_criar_recebimentos_carne.sql` - Controle financeiro
6. `06_gerar_recebimentos_mock.py` - Dados mock de pagamentos
7. `07_views_operacionais.sql` - Recriar todas as views

## 📊 ANÁLISE DE DADOS ATUAIS

### Vendas (15.281 registros)
- **Valor Total:** R$ 7.889.566,44
- **Valor Médio:** R$ 516,30
- **Status:** 100% ATIVO

### Formas de Pagamento (19.737 registros)
- **Parcelado Cartão:** 6.254 (31.7%)
- **PIX:** 4.389 (22.2%) 
- **Cartão Crédito:** 3.765 (19.1%)
- **Dinheiro:** 3.485 (17.7%)
- **Carnê:** 1.844 (9.3%)

## ⚠️ PONTOS DE ATENÇÃO

1. **Consistência de Dados:** Manter alinhamento com estrutura atual
2. **Performance:** Criar índices apropriados nas novas tabelas
3. **Integridade:** Garantir FKs corretas em todas as relações
4. **Mock Realista:** Dados de teste baseados em padrões reais
5. **Views:** Recriar views que dependem das novas tabelas

## 🎯 CRITÉRIOS DE SUCESSO

✅ **itens_venda implementada** com dados mock realistas  
✅ **entregas_os implementada** com controle de status  
✅ **recebimentos_carne implementada** para controle financeiro  
✅ **Views principais** funcionando corretamente  
✅ **Performance** mantida com novos dados  

## 📅 CRONOGRAMA

- **Semana 1:** itens_venda + entregas_os
- **Semana 2:** recebimentos_carne + restantes_entrada  
- **Semana 3:** entregas_carne + views
- **Semana 4:** Testes e otimizações

---

**Status:** 🚀 Pronto para implementação  
**Próximo Passo:** Criar script `01_criar_itens_venda.sql`
"""

    with open(arquivo_plano, 'w', encoding='utf-8') as f:
        f.write(plano_md)
    
    return arquivo_plano

if __name__ == "__main__":
    print("🔍 === ANÁLISE DO SCHEMA VENDAS === 🔍")
    print()
    
    # Executa análise
    resultado = analisar_schema_vendas()
    
    print(f"\n📋 === GERANDO PLANO DE IMPLEMENTAÇÃO === 📋")
    arquivo_plano = gerar_plano_implementacao()
    
    print(f"\n✅ ANÁLISE CONCLUÍDA!")
    print(f"📂 Plano salvo em: {arquivo_plano.name}")
    print(f"🎯 Próximo passo: Implementar itens_venda")
    print(f"🚀 Vamos começar com a próxima tabela!")