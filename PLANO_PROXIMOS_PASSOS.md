# 🚀 PLANO DE PRÓXIMOS PASSOS - SISTEMA CARNE FÁCIL

## ✅ SITUAÇÃO ATUAL (COMPLETADA)

### 🎯 **Normalização e Preparação de Dados:**
- ✅ 171 canais de aquisição categorizados com UUIDs
- ✅ 38 vendedores únicos normalizados 
- ✅ 6 lojas operacionais mapeadas
- ✅ 5,228 ordens de serviço com UUIDs completos
- ✅ Datas normalizadas para PostgreSQL (ISO 8601)
- ✅ Arquivos limpos e organizados

### 📁 **Estrutura Final:**
```
data/originais/oss/finais_postgresql_prontos/
├── MAUA_postgresql_pronto.csv (439 KB)
├── PERUS_postgresql_pronto.csv (353 KB)
├── RIO_PEQUENO_postgresql_pronto.csv (247 KB)
├── SAO_MATEUS_postgresql_pronto.csv (101 KB)
├── SUZANO2_postgresql_pronto.csv (144 KB)
└── SUZANO_postgresql_pronto.csv (1.7 MB)
```

### 💾 **Scripts SQL Prontos:**
- ✅ `database/12_estrutura_canais_aquisicao.sql` (171 canais)

---

## 🎯 PRÓXIMOS PASSOS

### 1️⃣ **PROCESSAMENTO DOS DADOS DE CAIXA** 🆕

#### 📋 **1.1 Análise Estrutural Concluída**
- ✅ **133 arquivos Excel** identificados (6 lojas, 2023-2025)
- ✅ **Estrutura padronizada** mapeada:
  - Abas numéricas (01-31): Movimentação diária
  - Aba `resumo_cx`: Fechamento mensal  
  - Aba `base`: Tipos de pagamento
  - Aba `base_OS`: OSs vinculadas
- ✅ **~4.650 tabelas estruturadas** identificadas
- ✅ **Padrão consistente** entre todas as lojas

#### 📋 **1.2 Extração e Normalização dos Dados**
```python
# Script para extrair dados de caixa
python extrair_dados_caixa.py
  # - Copiar arquivos relevantes para data/originais/cxs/
  # - Extrair movimentações diárias (abas 01-31)
  # - Consolidar fechamentos mensais (aba resumo_cx)
  # - Mapear tipos de pagamento (aba base)
  # - Vincular OSs (aba base_OS)
```

#### 📋 **1.3 Integração com Dados de OS**
- Reconciliar vendas vs movimentações de caixa
- Validar consistência entre sistemas
- Identificar discrepâncias para auditoria

### 2️⃣ **CRIAÇÃO DA ESTRUTURA COMPLETA DO BANCO**

#### 📋 **2.2 Criar Schema Financeiro** 🆕
```sql
-- Schema para dados de caixa
CREATE SCHEMA IF NOT EXISTS financeiro;

-- Tabela de tipos de pagamento
CREATE TABLE financeiro.tipos_pagamento (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    codigo VARCHAR(20) UNIQUE NOT NULL,
    descricao VARCHAR(100) NOT NULL,
    permite_parcelas BOOLEAN DEFAULT false,
    ativo BOOLEAN DEFAULT true
);

-- Tabela de movimentações diárias de caixa
CREATE TABLE financeiro.movimentacoes_caixa (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    loja_id UUID REFERENCES vendas.lojas(id),
    data_movimento DATE NOT NULL,
    tipo_movimento VARCHAR(20) CHECK (tipo_movimento IN ('ENTRADA', 'SAIDA')),
    tipo_pagamento_id UUID REFERENCES financeiro.tipos_pagamento(id),
    valor DECIMAL(12,2) NOT NULL,
    os_vinculada VARCHAR(50),
    descricao TEXT,
    arquivo_origem VARCHAR(100),
    linha_arquivo INTEGER,
    criado_em TIMESTAMP DEFAULT NOW()
);

-- Tabela de fechamentos mensais
CREATE TABLE financeiro.fechamentos_mensais (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    loja_id UUID REFERENCES vendas.lojas(id),
    ano_mes VARCHAR(7) NOT NULL, -- formato: 2025-01
    saldo_inicial DECIMAL(12,2) DEFAULT 0,
    total_vendas DECIMAL(12,2) DEFAULT 0,
    total_entradas DECIMAL(12,2) DEFAULT 0,
    total_despesas DECIMAL(12,2) DEFAULT 0,
    saldo_final DECIMAL(12,2) DEFAULT 0,
    arquivo_origem VARCHAR(100),
    criado_em TIMESTAMP DEFAULT NOW(),
    UNIQUE(loja_id, ano_mes)
);

-- Índices para performance
CREATE INDEX idx_movimentacoes_loja_data ON financeiro.movimentacoes_caixa(loja_id, data_movimento);
CREATE INDEX idx_movimentacoes_os ON financeiro.movimentacoes_caixa(os_vinculada);
CREATE INDEX idx_fechamentos_loja_mes ON financeiro.fechamentos_mensais(loja_id, ano_mes);
```

#### 📋 **2.1 Criar Schema e Tabelas Base** (OS - já mapeado)
```sql
-- Criar schemas
CREATE SCHEMA IF NOT EXISTS vendas;
CREATE SCHEMA IF NOT EXISTS marketing;

-- Tabela de lojas
CREATE TABLE vendas.lojas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    codigo VARCHAR(20) UNIQUE NOT NULL,
    nome VARCHAR(100) NOT NULL,
    endereco TEXT,
    ativo BOOLEAN DEFAULT true,
    criado_em TIMESTAMP DEFAULT NOW()
);

-- Tabela de vendedores
CREATE TABLE vendas.vendedores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome_normalizado VARCHAR(100) NOT NULL,
    ativo BOOLEAN DEFAULT true,
    criado_em TIMESTAMP DEFAULT NOW()
);

-- Relacionamento N:N vendedores-lojas
CREATE TABLE vendas.vendedores_lojas (
    vendedor_id UUID REFERENCES vendas.vendedores(id),
    loja_id UUID REFERENCES vendas.lojas(id),
    ativo BOOLEAN DEFAULT true,
    criado_em TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (vendedor_id, loja_id)
);
```

#### 📋 **2.3 Executar SQL de Canais de Aquisição** (já preparado)
- ✅ Executar: `database/12_estrutura_canais_aquisicao.sql`

#### 📋 **2.4 Criar Tabela Principal de Ordens de Serviço** (estrutura definida)
```sql
CREATE TABLE vendas.ordens_servico (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    numero_os VARCHAR(50) NOT NULL,
    os_chave VARCHAR(100) UNIQUE NOT NULL,
    
    -- Relacionamentos
    loja_id UUID REFERENCES vendas.lojas(id),
    vendedor_id UUID REFERENCES vendas.vendedores(id),
    canal_aquisicao_id UUID REFERENCES marketing.canais_aquisicao(id),
    
    -- Dados do cliente
    cliente_nome VARCHAR(200),
    cliente_cpf VARCHAR(14),
    cliente_data_nascimento DATE,
    
    -- Dados da venda
    data_compra DATE NOT NULL,
    valor_total DECIMAL(10,2),
    forma_pagamento VARCHAR(50),
    previsao_entrega DATE,
    
    -- Dados técnicos
    dados_receita JSONB, -- Para armazenar dados técnicos da receita
    observacoes TEXT,
    
    -- Auditoria
    criado_em TIMESTAMP DEFAULT NOW(),
    atualizado_em TIMESTAMP DEFAULT NOW(),
    
    -- Índices
    CREATE INDEX idx_os_loja ON vendas.ordens_servico(loja_id);
    CREATE INDEX idx_os_vendedor ON vendas.ordens_servico(vendedor_id);
    CREATE INDEX idx_os_canal ON vendas.ordens_servico(canal_aquisicao_id);
    CREATE INDEX idx_os_data_compra ON vendas.ordens_servico(data_compra);
    CREATE INDEX idx_os_cliente_cpf ON vendas.ordens_servico(cliente_cpf);
);
```

### 3️⃣ **POPULAÇÃO INICIAL DO BANCO**

#### 📋 **3.1 Popular Lojas** (dados prontos)
```sql
INSERT INTO vendas.lojas (id, codigo, nome) VALUES
('9a22ccf1-36fe-4b9f-9391-ca31433dc31e', 'MAUA', 'Mauá'),
('7c8d4e2f-91a6-4b3c-8d7e-f2a5b6c9d3e1', 'PERUS', 'Perus'),
('3e5f7a9b-2c4d-6e8f-1a3b-5c7d9e2f4a6b', 'RIO_PEQUENO', 'Rio Pequeno'),
('8b1c3d5e-7f9a-2b4c-6d8e-1f3a5b7c9d2e', 'SAO_MATEUS', 'São Mateus'),
('2a4b6c8d-5e7f-9a1b-3c5d-7e9f2a4b6c8d', 'SUZANO2', 'Suzano 2'),
('6c8d1e3f-9a2b-4c6d-8e1f-3a5b7c9d2e4f', 'SUZANO', 'Suzano');
```

#### 📋 **3.2 Popular Vendedores** (estrutura definida)
- Extrair lista de 38 vendedores únicos dos CSVs
- Inserir com UUIDs correspondentes

#### 📋 **3.3 Popular Relacionamentos Vendedores-Lojas** (mapeamento pronto)
- Mapear quais vendedores trabalham em quais lojas

#### 📋 **3.4 Popular Tipos de Pagamento** 🆕
```sql
-- Extrair tipos de pagamento das abas 'base' dos arquivos de caixa
INSERT INTO financeiro.tipos_pagamento (codigo, descricao, permite_parcelas) VALUES
('DN', 'Dinheiro', false),
('CTC', 'Cartão de Crédito', true),
('CTD', 'Cartão de Débito', false),
('PIX', 'PIX', false),
('BOLETO', 'Boleto Bancário', false),
-- ... outros tipos identificados nos dados
;
```

### 4️⃣ **IMPORTAÇÃO DOS DADOS PRINCIPAIS**

#### 📋 **4.1 Preparar Script de Importação OS** (CSVs prontos)
```sql
-- Configurar PostgreSQL para importação
SET datestyle = 'ISO, DMY';
SET timezone = 'America/Sao_Paulo';

-- Importar cada arquivo CSV
COPY vendas.ordens_servico (
    loja_id, vendedor_id, canal_aquisicao_id,
    numero_os, cliente_nome, cliente_cpf,
    data_compra, data_nascimento, previsao_entrega,
    -- demais campos...
) FROM 'path/MAUA_postgresql_pronto.csv' 
WITH (FORMAT CSV, HEADER true);
```

#### 📋 **4.2 Importar Dados de Caixa** 🆕
```sql
-- Importar movimentações de caixa (após extração)
COPY financeiro.movimentacoes_caixa (
    loja_id, data_movimento, tipo_movimento,
    tipo_pagamento_id, valor, os_vinculada,
    descricao, arquivo_origem
) FROM 'path/movimentacoes_caixa_consolidadas.csv' 
WITH (FORMAT CSV, HEADER true);

-- Importar fechamentos mensais
COPY financeiro.fechamentos_mensais (
    loja_id, ano_mes, saldo_inicial,
    total_vendas, total_entradas, total_despesas,
    saldo_final, arquivo_origem
) FROM 'path/fechamentos_mensais_consolidados.csv' 
WITH (FORMAT CSV, HEADER true);
```

#### 📋 **4.3 Validação Pós-Importação** (expandida)
```sql
```sql
-- Verificar contagens OS
SELECT COUNT(*) FROM vendas.ordens_servico; -- Deve ser 5,228
SELECT COUNT(*) FROM marketing.canais_aquisicao; -- Deve ser 171
SELECT COUNT(*) FROM vendas.vendedores; -- Deve ser 38
SELECT COUNT(*) FROM vendas.lojas; -- Deve ser 6

-- Verificar contagens CAIXA 🆕
SELECT COUNT(*) FROM financeiro.movimentacoes_caixa; -- Estimado: ~50.000
SELECT COUNT(*) FROM financeiro.fechamentos_mensais; -- Estimado: ~150
SELECT COUNT(*) FROM financeiro.tipos_pagamento; -- Estimado: ~20

-- Verificar integridade referencial
SELECT COUNT(*) FROM vendas.ordens_servico 
WHERE loja_id NOT IN (SELECT id FROM vendas.lojas);

-- Verificar reconciliação vendas vs caixa 🆕
SELECT 
    l.nome as loja,
    DATE_TRUNC('month', os.data_compra) as mes,
    SUM(os.valor_total) as total_vendas_os,
    SUM(mc.valor) as total_entradas_caixa,
    SUM(os.valor_total) - SUM(mc.valor) as diferenca
FROM vendas.ordens_servico os
JOIN vendas.lojas l ON os.loja_id = l.id
LEFT JOIN financeiro.movimentacoes_caixa mc ON 
    mc.loja_id = os.loja_id AND 
    mc.data_movimento = os.data_compra AND
    mc.tipo_movimento = 'ENTRADA'
GROUP BY l.nome, DATE_TRUNC('month', os.data_compra)
ORDER BY l.nome, mes;

-- Verificar distribuição por loja
SELECT l.nome, COUNT(*) as total_os
FROM vendas.ordens_servico os
JOIN vendas.lojas l ON os.loja_id = l.id
GROUP BY l.nome
ORDER BY total_os DESC;
```

### 5️⃣ **DESENVOLVIMENTO DA APLICAÇÃO WEB**

#### 📋 **5.1 Atualizar Modelos de Dados** (expandido)
- Atualizar `app/models/` para nova estrutura
- Implementar relacionamentos SQLAlchemy
- Criar queries otimizadas
- **🆕 Adicionar modelos financeiros** (movimentações, fechamentos)
- **🆕 Implementar reconciliação** vendas vs caixa

#### 📋 **5.2 Desenvolver Dashboard Analítico** (expandido)
- Gráficos por canal de aquisição
- Performance por vendedor
- Análise temporal de vendas
- Comparativo entre lojas
- **🆕 Dashboard financeiro** (fluxo de caixa, reconciliação)
- **🆕 Análise de performance** por forma de pagamento
- **🆕 Relatórios de auditoria** (diferenças vendas vs caixa)

#### 📋 **5.3 Implementar Funcionalidades Avançadas** (expandido)
- Filtros dinâmicos
- Exportação de relatórios
- Sistema de alertas
- Análise preditiva
- **🆕 Módulo de reconciliação** automática
- **🆕 Alertas de discrepâncias** financeiras
- **🆕 Análise de tendências** de fluxo de caixa

### 6️⃣ **OTIMIZAÇÃO E MONITORAMENTO**

#### 📋 **6.1 Performance**
- Criar índices adicionais conforme uso
- Implementar cache de queries frequentes
- Otimizar consultas complexas

#### 📋 **6.2 Backup e Segurança**
- Configurar backup automático
- Implementar logs de auditoria
- Configurar permissões por usuário

---

## 🎯 **ENTREGÁVEIS IMEDIATOS**

1. **Script SQL completo** para criação da estrutura (OS + Financeiro)
2. **Script de população** das tabelas base
3. **Script de importação** dos CSVs (OS + Caixa)
4. **Script de extração** dos dados de caixa 🆕
5. **Dashboard atualizado** com módulo financeiro 🆕
6. **Documentação** da arquitetura final

---

## 📈 **BENEFÍCIOS ESPERADOS**

- ✅ **Performance**: Consultas 10x mais rápidas
- ✅ **Integridade**: Relacionamentos garantidos
- ✅ **Escalabilidade**: Estrutura preparada para crescimento
- ✅ **Análises**: Insights mais profundos
- ✅ **Manutenção**: Código mais limpo e organizado
- ✅ **🆕 Reconciliação**: Validação automática vendas vs caixa
- ✅ **🆕 Auditoria**: Controle financeiro completo
- ✅ **🆕 Performance Financeira**: KPIs em tempo real

---

**🚀 PRONTO PARA IMPLEMENTAÇÃO COMPLETA!**

### 📊 **Status Atual**:
- ✅ **Dados de OS**: 5,228 registros normalizados e prontos
- ✅ **Estrutura de Caixa**: 133 arquivos mapeados e analisados  
- ✅ **UUIDs**: Integração completa entre vendedores, lojas e canais
- ✅ **PostgreSQL**: Datas normalizadas e estrutura definida
- 🔄 **Próximo**: Extração e integração dos dados de caixa