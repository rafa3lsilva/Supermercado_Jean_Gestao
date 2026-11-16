-- ============================================================================
-- SCRIPT DE CRIAÇÃO DAS TABELAS E RLS NO SUPABASE (PROJETO: supermercado_jean)
-- ============================================================================

-- 1. Tabela de Catálogo de Matérias-Primas e Fatores
CREATE TABLE IF NOT EXISTS public.produtos (
    id SERIAL PRIMARY KEY,
    codigo INTEGER NOT NULL,
    descricao TEXT NOT NULL UNIQUE,
    unidade TEXT NOT NULL,
    fator_conversao DOUBLE PRECISION NOT NULL DEFAULT 1.0
);

-- 2. Tabela da Lista da Nota Fiscal
CREATE TABLE IF NOT EXISTS public.nota_fiscal (
    id SERIAL PRIMARY KEY,
    codigo INTEGER,
    descricao TEXT NOT NULL,
    quantidade DOUBLE PRECISION NOT NULL,
    valor_unitario DOUBLE PRECISION NOT NULL,
    valor_total DOUBLE PRECISION NOT NULL,
    data_registro TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Tabela de Estado Atual do Rendimento & Açougue (Rascunho Automático)
CREATE TABLE IF NOT EXISTS public.rendimento_estado (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    dados_json TEXT NOT NULL,
    atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Tabela de Histórico de Fechamentos de Desossa
CREATE TABLE IF NOT EXISTS public.rendimento_historico (
    id SERIAL PRIMARY KEY,
    titulo_fechamento TEXT NOT NULL,
    notas_fiscais TEXT,
    resumo_json TEXT NOT NULL,
    dados_json TEXT NOT NULL,
    data_registro TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Habilitar Row Level Security (RLS) e Políticas de Segurança
ALTER TABLE public.produtos ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.nota_fiscal ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.rendimento_estado ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.rendimento_historico ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Acesso Total Service Role Produtos" ON public.produtos;
CREATE POLICY "Acesso Total Service Role Produtos" ON public.produtos
    FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Acesso Total Service Role Nota Fiscal" ON public.nota_fiscal;
CREATE POLICY "Acesso Total Service Role Nota Fiscal" ON public.nota_fiscal
    FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Acesso Total Service Role Rendimento Estado" ON public.rendimento_estado;
CREATE POLICY "Acesso Total Service Role Rendimento Estado" ON public.rendimento_estado
    FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Acesso Total Service Role Rendimento Historico" ON public.rendimento_historico;
CREATE POLICY "Acesso Total Service Role Rendimento Historico" ON public.rendimento_historico
    FOR ALL TO service_role USING (true) WITH CHECK (true);
