
-- Execute este comando ANTES da importação das vendas
INSERT INTO vendas.vendedores (
    id, 
    nome, 
    codigo_vendedor, 
    ativo, 
    created_at, 
    updated_at
) VALUES (
    '00000000-0000-0000-0000-000000000001',
    'SISTEMA - IMPORTAÇÃO AUTOMÁTICA',
    'SYS001',
    true,
    NOW(),
    NOW()
) ON CONFLICT (id) DO NOTHING;
