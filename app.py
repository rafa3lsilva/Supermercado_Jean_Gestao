import os
import streamlit as st
import pandas as pd
import json
import data_manager
import rendimento_engine as reng

# --- Configurações da Página ---
st.set_page_config(
    page_title="Supermercado Jean - Gestão de Preço Médio & Rendimento",
    page_icon="🥩",
    layout="wide",
    initial_sidebar_state="expanded"
)


def obter_senha_sistema() -> str:
    senha_env = os.environ.get("APP_PASSWORD", "").strip()
    if senha_env:
        return senha_env
    try:
        if "APP_PASSWORD" in st.secrets:
            return str(st.secrets["APP_PASSWORD"]).strip()
    except Exception:
        pass
    return "jean2026"

# Inicializa bancos de dados e migrações
data_manager.init_db()
reng.init_rendimento_tables()

if "rend_state" not in st.session_state:
    st.session_state.rend_state = reng.load_state()


def salvar_estado_rendimento():
    reng.save_state(st.session_state.rend_state)


# --- CSS Dark Mode Executivo & Visual de Aplicativo Profissional ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600;700&display=swap');

    .stApp {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: #0B0F17 !important;
        color: #F8FAFC !important;
    }

    /* Badges de Categoria */
    .app-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        background: rgba(56, 189, 248, 0.12);
        color: #38BDF8;
        border: 1px solid rgba(56, 189, 248, 0.25);
        margin-bottom: 0.4rem;
    }

    /* Títulos Executivos */
    .app-title {
        font-family: 'Outfit', sans-serif !important;
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        line-height: 1.2;
        margin-bottom: 0.25rem;
        color: #FFFFFF;
    }

    .app-subtitle {
        font-size: 0.96rem;
        font-weight: 450;
        color: #94A3B8;
        line-height: 1.5;
        margin-bottom: 1.2rem;
    }

    /* KPI Mini Cards */
    .kpi-box {
        background: linear-gradient(145deg, #131B2A 0%, #0F172A 100%);
        border: 1px solid rgba(255, 255, 255, 0.09);
        border-radius: 12px;
        padding: 14px 16px;
        min-height: 94px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .kpi-box-accent {
        background: linear-gradient(145deg, #132238 0%, #0F172A 100%);
        border: 1px solid rgba(56, 189, 248, 0.4);
        border-radius: 12px;
        padding: 14px 16px;
        min-height: 94px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 0 4px 20px rgba(56, 189, 248, 0.12);
    }
    .kpi-label {
        font-size: 0.74rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #94A3B8;
        margin-bottom: 4px;
    }
    .kpi-val {
        font-family: 'Outfit', sans-serif !important;
        font-size: 1.45rem;
        font-weight: 800;
        color: #F8FAFC;
        line-height: 1.15;
    }
    .kpi-sub {
        font-size: 0.78rem;
        color: #38BDF8;
        font-family: 'JetBrains Mono', monospace;
        margin-top: 3px;
    }

    /* Cards Modulares de Entrada */
    .item-number-badge {
        font-family: 'Outfit', sans-serif !important;
        font-size: 0.95rem;
        font-weight: 750;
        color: #38BDF8;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* Painel Resumo Financeiro (Executive Summary) */
    .summary-card {
        background: linear-gradient(145deg, #131B2A 0%, #0F172A 100%);
        border: 1px solid rgba(56, 189, 248, 0.35);
        border-radius: 16px;
        padding: 1.6rem 1.8rem;
        box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.5), 0 0 20px -3px rgba(56, 189, 248, 0.15);
        position: relative;
        overflow: hidden;
    }

    .summary-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #38BDF8 0%, #818CF8 50%, #34D399 100%);
        box-shadow: 0 0 15px #38BDF8;
    }

    .summary-title {
        font-family: 'Outfit', sans-serif !important;
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #38BDF8;
        margin-bottom: 0.4rem;
    }

    .summary-highlight-val {
        font-family: 'Outfit', sans-serif !important;
        font-size: 2.7rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        color: #FFFFFF;
        line-height: 1.1;
        margin-bottom: 0.2rem;
    }

    .summary-unit-tag {
        font-size: 0.88rem;
        font-weight: 500;
        color: #94A3B8;
        margin-bottom: 1.4rem;
    }

    .metric-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        font-size: 0.92rem;
    }

    .metric-row-label {
        color: #94A3B8;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    .metric-row-val {
        font-weight: 700;
        color: #F8FAFC;
        font-family: 'JetBrains Mono', monospace;
    }

    /* Barra Lateral */
    [data-testid="stSidebar"] {
        background-color: #0E1420 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }

    /* Botões Modernos e Alinhamento Perfeito de Caixas de Texto */
    .stButton > button,
    .stDownloadButton > button,
    [data-testid="stFormSubmitButton"] > button {
        font-weight: 700 !important;
        border-radius: 9px !important;
        letter-spacing: -0.01em !important;
        min-height: 42px !important;
        height: 42px !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button[kind="primary"],
    .stDownloadButton > button[kind="primary"],
    [data-testid="stFormSubmitButton"] > button[kind="primary"] {
        background: linear-gradient(135deg, #0284C7 0%, #38BDF8 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(2, 132, 199, 0.4) !important;
    }

    .stButton > button[kind="primary"]:hover,
    .stDownloadButton > button[kind="primary"]:hover,
    [data-testid="stFormSubmitButton"] > button[kind="primary"]:hover {
        box-shadow: 0 6px 22px rgba(56, 189, 248, 0.6) !important;
        transform: translateY(-1px) !important;
    }

    /* Rótulos (Labels) padronizados em 1 linha para nunca desalinhar caixas lado a lado */
    [data-testid="stWidgetLabel"] {
        min-height: 24px !important;
        margin-bottom: 4px !important;
        display: flex !important;
        align-items: center !important;
    }
    [data-testid="stWidgetLabel"] p {
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        font-size: 0.84rem !important;
        font-weight: 600 !important;
        color: #CBD5E1 !important;
        margin: 0 !important;
    }

    /* Altura uniforme nas caixas de texto, números e seletores */
    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input {
        min-height: 42px !important;
        height: 42px !important;
    }
    [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        min-height: 42px !important;
    }

    /* Inputs e Containers */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #131B2A !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Tela de Login / Controle de Acesso ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    col_l_pad, col_login, col_r_pad = st.columns([3, 4, 3])
    with col_login:
        st.markdown("<div style='height: 60px;'></div>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("""
            <div style="text-align: center; padding: 10px 0 18px 0;">
                <div class="app-badge">🔒 ACESSO RESTRITO</div>
                <div style="font-family: 'Outfit', sans-serif; font-size: 1.8rem; font-weight: 800; color: #FFFFFF; margin-top: 6px;">
                    🛒 Supermercado Jean
                </div>
                <div style="font-size: 0.9rem; color: #94A3B8; margin-top: 4px;">
                    Central de Rendimento, Desossa & Preço Médio
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.form("form_login_acesso"):
                usuario_input = st.text_input("👤 Usuário / Operador:", value="admin", placeholder="Digite seu usuário")
                senha_input = st.text_input("🔑 Senha de Acesso:", type="password", placeholder="Digite a senha do sistema")
                btn_entrar = st.form_submit_button("🔓 Entrar no Sistema", type="primary", use_container_width=True)

                if btn_entrar:
                    if senha_input.strip() == obter_senha_sistema():
                        st.session_state.autenticado = True
                        st.session_state.operador_logado = usuario_input.strip() or "Operador"
                        st.rerun()
                    else:
                        st.error("❌ Senha incorreta. Verifique com a gerência.")
    st.stop()

# --- Barra Lateral ---
with st.sidebar:
    supa_ativo = data_manager.is_supabase_configured()
    status_db_label = "☁️ Supabase Conectado (supermercado_jean)" if supa_ativo else "💾 SQLite Local (database.db)"
    status_db_cor = "#34D399" if supa_ativo else "#38BDF8"
    st.markdown(f"""
    <div style="padding: 0.5rem 0 0.8rem 0;">
        <div style="font-family: 'Outfit', sans-serif; font-size: 1.5rem; font-weight: 800; color: #FFFFFF; display: flex; align-items: center; gap: 8px;">
            🛒 Supermercado Jean
        </div>
        <div style="font-size: 0.82rem; color: #94A3B8; font-weight: 500;">
            Preço Médio, Desossa & Rendimento
        </div>
        <div style="margin-top: 8px; display: inline-flex; align-items: center; gap: 6px; padding: 3px 10px; border-radius: 999px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); font-size: 0.72rem; color: {status_db_cor}; font-weight: 700;">
            {status_db_label}
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🔒 Sair / Bloquear Tela", use_container_width=True):
        st.session_state.autenticado = False
        st.rerun()
    st.divider()

    aba_selecionada = st.radio(
        "Módulos Operacionais:",
        [
            "🥩 Rendimento & Desossa",
            "📦 Gestão de Caixaria",
            "🧮 Calculadora de Preço Médio",
            "📋 Catálogo de Produtos & Custos",
            "📑 Consolidação de Nota Fiscal",
            "☁️ Backup & Sincronização"
        ]
    )

    st.divider()
    st.markdown("""
    <div style="background: rgba(56, 189, 248, 0.08); border: 1px solid rgba(56, 189, 248, 0.25); border-radius: 10px; padding: 12px;">
        <div style="font-weight: 700; font-size: 0.82rem; color: #38BDF8; margin-bottom: 4px;">⚡ Lançamento Multiponto</div>
        <div style="font-size: 0.78rem; color: #CBD5E1; line-height: 1.45;">
            Nos campos de <b>Pesagens</b>, insira múltiplos pesos separados por <b>espaço</b> ou <b>+</b> (ex: <code>12,67 6,305 10,95</code>). O sistema contabiliza e soma as pesagens automaticamente.
        </div>
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# FUNÇÕES AUXILIARES DE FEEDBACK ABAIXO DOS FORMULÁRIOS E PAINEL DE DESOSSA
# ==============================================================================
def set_feedback_abaixo(chave: str, tipo: str, msg: str):
    st.session_state[f"_fb_{chave}"] = {"tipo": tipo, "msg": msg}


def render_feedback_abaixo(chave: str):
    fb = st.session_state.pop(f"_fb_{chave}", None)
    if fb:
        if fb["tipo"] == "success":
            st.success(fb["msg"])
        elif fb["tipo"] == "error":
            st.error(fb["msg"])
        else:
            st.warning(fb["msg"])


def render_painel_desossa(chave_desossa: str, part_base: str = "rendimento"):
    state = st.session_state.rend_state
    dados_peca = state["desossas"][chave_desossa]
    calc = reng.calcular_desossa(dados_peca, part_base=part_base)

    # 1. Cabeçalho Editável da Carcaça / Peça
    with st.container(border=True):
        st.markdown(f"##### ⚙️ Parâmetros de Entrada do Lote — **{dados_peca['titulo']}**")
        c1, c2, c3, c4, c5 = st.columns([3, 2, 3, 2, 2], vertical_alignment="bottom")
        with c1:
            novo_peso_str = st.text_input(
                "⚖️ Peso de Entrada da Peça/Carcaça (KG):",
                value=str(dados_peca.get("peso_peca_str", "")),
                key=f"peso_peca_{chave_desossa}",
                placeholder="Ex: 527,40 + 478,00",
                help="Informe o peso total ou múltiplos lotes separados por espaço ou +"
            )
        with c2:
            custo_atual_peca = float(dados_peca.get("custo_kg", 0.0) or 0.0)
            novo_custo_kg_in = st.number_input(
                "💵 Custo de Aquisição / KG (R$):",
                min_value=0.0,
                value=custo_atual_peca if custo_atual_peca > 0 else None,
                step=0.01,
                format="%.2f",
                placeholder="Ex: 38,93",
                key=f"custo_kg_{chave_desossa}"
            )
            novo_custo_kg = float(novo_custo_kg_in or 0.0)
        with c3:
            nova_perda_str = st.text_input(
                "🦴 Descarte / Limpeza Apontada (KG):",
                value=str(dados_peca.get("perda_apontada_str", "")),
                key=f"perda_ap_{chave_desossa}",
                placeholder="Ex: 6,455 + 9,045",
                help="Informe as pesagens de osso, sebo e aparas descartadas"
            )
        with c4:
            novas_notas = st.text_input(
                "🧾 Nº Nota(s) Fiscal(is):",
                value=str(dados_peca.get("notas", "")),
                key=f"notas_{chave_desossa}",
                placeholder="Ex: 16774"
            )
        with c5:
            if st.button("🧹 Limpar Lote", key=f"btn_zerar_{chave_desossa}", use_container_width=True, help="Redefine apenas as pesagens deste corte para iniciar um novo lote"):
                for c in dados_peca["cortes"]:
                    c["pesagens"] = ""
                dados_peca["perda_apontada_str"] = ""
                dados_peca["peso_peca_str"] = ""
                salvar_estado_rendimento()
                st.toast("Pesagens do lote redefinidas!", icon="🧹")
                st.rerun()

        if (
            novo_peso_str != dados_peca.get("peso_peca_str")
            or novo_custo_kg != float(dados_peca.get("custo_kg", 0.0))
            or nova_perda_str != dados_peca.get("perda_apontada_str")
            or novas_notas != dados_peca.get("notas")
        ):
            dados_peca["peso_peca_str"] = novo_peso_str
            dados_peca["custo_kg"] = novo_custo_kg
            dados_peca["perda_apontada_str"] = nova_perda_str
            dados_peca["notas"] = novas_notas
            salvar_estado_rendimento()
            st.rerun()

    # 2. Barra de KPIs Executivos da Desossa
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    with k1:
        st.html(f"""
        <div class="kpi-box">
            <div class="kpi-label">📦 Peso de Entrada</div>
            <div class="kpi-val">{calc['peso_peca']:,.3f} kg</div>
            <div class="kpi-sub">Custo Total: R$ {calc['custo_total_entrada']:,.2f}</div>
        </div>
        """)
    with k2:
        st.html(f"""
        <div class="kpi-box-accent">
            <div class="kpi-label">🥩 Rendimento Líquido</div>
            <div class="kpi-val" style="color:#34D399;">{calc['rendimento_total']:,.3f} kg</div>
            <div class="kpi-sub">Aproveitamento: {calc['rendimento_pct']*100:.2f}%</div>
        </div>
        """)
    with k3:
        st.html(f"""
        <div class="kpi-box">
            <div class="kpi-label">🦴 Quebra Apontada</div>
            <div class="kpi-val" style="color:#FBBF24;">{calc['perda_apontada']:,.3f} kg</div>
            <div class="kpi-sub">{calc['perda_apontada_pct']*100:.2f}% ({calc['qtd_pesagens_perda']} pesagens)</div>
        </div>
        """)
    with k4:
        cor_verif = "#F87171" if abs(calc["perda_verificada_pct"]) > 0.05 else "#A5B4FC"
        st.html(f"""
        <div class="kpi-box">
            <div class="kpi-label">🔍 Quebra Operacional</div>
            <div class="kpi-val" style="color:{cor_verif};">{calc['perda_verificada']:,.3f} kg</div>
            <div class="kpi-sub">{calc['perda_verificada_pct']*100:.2f}% (Não apontada)</div>
        </div>
        """)
    with k5:
        st.html(f"""
        <div class="kpi-box">
            <div class="kpi-label">💰 Receita Projetada</div>
            <div class="kpi-val" style="color:#38BDF8;">R$ {calc['venda_total']:,.2f}</div>
            <div class="kpi-sub">Faturamento Estimado</div>
        </div>
        """)
    with k6:
        st.html(f"""
        <div class="kpi-box-accent">
            <div class="kpi-label">📈 Markup / Margem</div>
            <div class="kpi-val">{calc['mkp_pct']*100:.2f}%</div>
            <div class="kpi-sub">Margem Bruta: {calc['mkd_pct']*100:.2f}%</div>
        </div>
        """)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # 3. Lançador Rápido de Etiqueta / Balança (PDV Style)
    opcoes_cortes = [f"{c['codigo']} - {c['corte']}" for c in dados_peca["cortes"]]
    opcoes_cortes.append("🦴 QUEBRA / DESCARTE APONTADO (OSSO/SEBO)")

    with st.form(key=f"form_bip_{chave_desossa}", clear_on_submit=True, border=True):
        c_bip1, c_bip2, c_bip3 = st.columns([4, 4, 2], vertical_alignment="bottom")
        with c_bip1:
            corte_bip = st.selectbox(
                "⚡ 1. Selecionar Corte para Pesagem:",
                options=opcoes_cortes,
                key=f"bip_sel_{chave_desossa}"
            )
        with c_bip2:
            peso_bip_str = st.text_input(
                "⚖️ 2. Informar Peso(s) da Balança (KG) [Enter]:",
                placeholder="Ex: 12,450  ou  12,45 9,80 11,20",
                help="Digite um ou mais pesos separados por espaço e pressione Enter para acumular no corte selecionado."
            )
        with c_bip3:
            submitted_bip = st.form_submit_button("➕ Registrar Peso", type="primary", use_container_width=True)

        if submitted_bip:
            texto_bip = str(peso_bip_str or "").strip()
            soma_bip, qtd_bip, _, _ = reng.parse_pesagens(texto_bip)
            if not texto_bip or reng.tem_token_invalido_pesagem(texto_bip) or soma_bip <= 0:
                set_feedback_abaixo(
                    f"bip_{chave_desossa}",
                    "error",
                    f"❌ Peso inválido ({texto_bip or 'vazio'}). Digite valores numéricos maiores que zero (ex: 12,450 ou ,874)."
                )
            else:
                if corte_bip.startswith("🦴"):
                    dados_peca["perda_apontada_str"] = reng.append_pesagem(
                        dados_peca.get("perda_apontada_str", ""), texto_bip
                    )
                else:
                    cod_alvo = int(corte_bip.split(" - ")[0])
                    for c in dados_peca["cortes"]:
                        if int(c["codigo"]) == cod_alvo:
                            c["pesagens"] = reng.append_pesagem(c.get("pesagens", ""), texto_bip)
                            break
                salvar_estado_rendimento()
                set_feedback_abaixo(
                    f"bip_{chave_desossa}",
                    "success",
                    f"✅ +{soma_bip:.3f} kg ({qtd_bip} pesagem/ns) registrado com sucesso em {corte_bip}!"
                )
                st.rerun()

    render_feedback_abaixo(f"bip_{chave_desossa}")

    # 4. Tabela Profissional de Cortes com Soma Automática
    df_grid = pd.DataFrame([
        {
            "codigo": l["codigo"],
            "corte": l["corte"],
            "pesagens": l["pesagens"],
            "qtd_pesos": l["qtd_pesagens"],
            "peso_kg": round(l["peso_kg"], 3),
            "part_pct": round(l["part_pct"] * 100, 2),
            "custo_kg": round(l["custo_kg"], 2),
            "preco_venda": round(l["preco_venda"], 2),
            "venda_total": round(l["venda_total"], 2),
        }
        for l in calc["linhas"]
    ])

    edited_df = st.data_editor(
        df_grid,
        key=f"editor_des_{chave_desossa}",
        use_container_width=True,
        hide_index=True,
        column_config={
            "codigo": st.column_config.NumberColumn("Código", disabled=True, width="small"),
            "corte": st.column_config.TextColumn("Descrição do Corte", disabled=True, width="medium"),
            "pesagens": st.column_config.TextColumn(
                "✍️ Registro de Pesagens (KG)",
                width="large",
                help="Insira ou edite os pesos separados por espaço ou + (ex: 9,785 + 11,435)."
            ),
            "qtd_pesos": st.column_config.NumberColumn("Lotes", disabled=True, width="small"),
            "peso_kg": st.column_config.NumberColumn("Peso Acumulado (KG)", disabled=True, format="%.3f"),
            "part_pct": st.column_config.NumberColumn("Participação (%)", disabled=True, format="%.2f%%"),
            "custo_kg": st.column_config.NumberColumn("Custo Apurado / KG", disabled=True, format="R$ %.2f"),
            "preco_venda": st.column_config.NumberColumn("✍️ Preço Venda / KG", format="%.2f", step=0.01),
            "venda_total": st.column_config.NumberColumn("Receita Total (R$)", disabled=True, format="R$ %.2f"),
        }
    )

    # Verifica se houve edição na tabela e salva automaticamente
    mudou_tabela = False
    for idx, row in edited_df.iterrows():
        corte_orig = dados_peca["cortes"][idx]
        nova_str_pesos = str(row["pesagens"]) if pd.notna(row["pesagens"]) else ""
        novo_pv = float(row["preco_venda"]) if pd.notna(row["preco_venda"]) else 0.0
        if nova_str_pesos != corte_orig.get("pesagens", "") or abs(novo_pv - float(corte_orig.get("preco_venda", 0.0))) > 1e-4:
            corte_orig["pesagens"] = nova_str_pesos
            corte_orig["preco_venda"] = novo_pv
            mudou_tabela = True

    if mudou_tabela:
        salvar_estado_rendimento()
        st.rerun()


# ==============================================================================
# MÓDULO 1: CENTRAL DE RENDIMENTO & DESOSSA
# ==============================================================================
if aba_selecionada == "🥩 Rendimento & Desossa":
    col_head_l, col_head_r = st.columns([7, 3])
    with col_head_l:
        st.markdown('<div class="app-badge">🥩 GESTÃO DE AÇOUGUE & PRODUÇÃO PRÓPRIA</div>', unsafe_allow_html=True)
        st.markdown('<div class="app-title">Rendimento de Desossa & Precificação</div>', unsafe_allow_html=True)
        st.markdown('<div class="app-subtitle">Apuração técnica de rendimento por carcaça, custo médio ponderado por corte, fichas de produção e controle de miúdos.</div>', unsafe_allow_html=True)
    with col_head_r:
        st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
        excel_rel_bytes = reng.exportar_relatorio_rendimento_excel(st.session_state.rend_state)
        st.download_button(
            label="📥 Exportar Relatório Gerencial (.xlsx)",
            data=excel_rel_bytes,
            file_name=f"Relatorio_Rendimento_Acougue_{ pd.Timestamp.now().strftime('%Y-%m-%d') }.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            use_container_width=True
        )

    # Navegação Principal dos 4 Fluxos de Rendimento
    fluxo_acougue = st.tabs([
        "🐄 1. Desossa Bovina & Consolidação",
        "🐖 2. Desossa Suína & Ovina",
        "🍲 3. Produção Própria & Receitas",
        "📝 4. Controle de Miúdos & Pesagens Extras"
    ])

    # --------------------------------------------------------------------------
    # FLUXO 1: BOVINO & MASTERBOI
    # --------------------------------------------------------------------------
    with fluxo_acougue[0]:
        sub_bov = st.radio(
            "Selecione a Operação Bovina:",
            [
                "📊 Visão Consolidada (Boi Casado + Lotes Extras)",
                "🔪 Dianteiro (Boi Casado)",
                "🔪 Traseiro (Boi Casado)",
                "🔪 Ponta de Agulha (Boi Casado)",
                "🏭 Dianteiro Masterboi",
                "🏭 Ponta de Agulha Masterboi",
            ],
            horizontal=True
        )

        if sub_bov.startswith("📊"):
            bov = reng.calcular_consolidado_bovino(st.session_state.rend_state)

            st.markdown("##### 📊 Indicadores Globais — Boi Casado (`Dianteiro + Traseiro + Ponta de Agulha`)")
            b1, b2, b3, b4, b5, b6 = st.columns(6)
            with b1:
                st.html(f"""
                <div class="kpi-box">
                    <div class="kpi-label">🐄 Peso Total Entrada</div>
                    <div class="kpi-val">{bov['peso_boi_casado']:,.3f} kg</div>
                    <div class="kpi-sub">D:{bov['res_dianteiro']['peso_peca']:g} | T:{bov['res_traseiro']['peso_peca']:g} | PA:{bov['res_pa']['peso_peca']:g}</div>
                </div>
                """)
            with b2:
                st.html(f"""
                <div class="kpi-box">
                    <div class="kpi-label">💵 Custo Total Entrada</div>
                    <div class="kpi-val">R$ {bov['custo_total_boi_casado']:,.2f}</div>
                    <div class="kpi-sub">Custo Médio: R$ {bov['custo_kg_boi_casado']:,.2f}/kg</div>
                </div>
                """)
            with b3:
                st.html(f"""
                <div class="kpi-box-accent">
                    <div class="kpi-label">🥩 Rendimento Líquido</div>
                    <div class="kpi-val" style="color:#34D399;">{bov['rendimento_total']:,.3f} kg</div>
                    <div class="kpi-sub">Aproveitamento: {bov['rendimento_pct']*100:.2f}%</div>
                </div>
                """)
            with b4:
                st.html(f"""
                <div class="kpi-box">
                    <div class="kpi-label">🦴 Quebra Total</div>
                    <div class="kpi-val" style="color:#FBBF24;">{bov['perda_apontada']:,.3f} kg</div>
                    <div class="kpi-sub">{bov['perda_apontada_pct']*100:.2f}% | Operac.: {bov['perda_verificada']:,.3f} kg ({bov['perda_verificada_pct']*100:.2f}%)</div>
                </div>
                """)
            with b5:
                st.html(f"""
                <div class="kpi-box">
                    <div class="kpi-label">💰 Receita Projetada</div>
                    <div class="kpi-val" style="color:#38BDF8;">R$ {bov['venda_total']:,.2f}</div>
                    <div class="kpi-sub">Faturamento Boi Casado</div>
                </div>
                """)
            with b6:
                st.html(f"""
                <div class="kpi-box-accent">
                    <div class="kpi-label">📈 Markup / Margem</div>
                    <div class="kpi-val">{bov['mkp_pct']*100:.2f}%</div>
                    <div class="kpi-sub">Margem Bruta: {bov['mkd_pct']*100:.2f}%</div>
                </div>
                """)

            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            col_bov_t, col_bov_z = st.columns([7, 3], vertical_alignment="center")
            with col_bov_t:
                st.markdown("##### 🎯 Matriz de Custos Ponderados por Corte (Boi Casado + Masterboi & Caixas)")
                st.caption("Consolida automaticamente a produção do Boi Casado com os lotes Masterboi. Nos cortes exclusivos de Traseiro, você pode informar compras adicionais em caixa para compor o **Preço Médio Final**.")
            with col_bov_z:
                if st.button("🧹 Limpar Compras Extras (Traseiro)", use_container_width=True, help="Redefine apenas os pesos de caixas extras informados manualmente nos cortes de Traseiro."):
                    for cod_k, ext_v in st.session_state.rend_state.get("bovino_extras_traseiro", {}).items():
                        ext_v["pesagens"] = ""
                        ext_v["peso"] = 0.0
                    salvar_estado_rendimento()
                    st.toast("Compras adicionais de Traseiro redefinidas!", icon="🧹")
                    st.rerun()

            df_bov_view = pd.DataFrame([
                {
                    "codigo": l["codigo"],
                    "corte": l["corte"],
                    "peso_bovino": round(l["peso_bovino"], 3),
                    "part_pct": round(l["part_pct"] * 100, 2),
                    "custo_bovino": round(l["custo_bovino"], 2),
                    "preco_venda": round(l["preco_venda"], 2),
                    "venda_total": round(l["venda_total"], 2),
                    "preco_medio_final": round(l["preco_medio_final"], 2),
                    "pesagens_col_o": l["pesagens_col_o"],
                    "peso_masterboi": round(l["peso_masterboi"], 3),
                    "custo_masterboi": round(l["custo_masterboi"], 2),
                    "origem_mb": l["origem_masterboi"],
                }
                for l in bov["linhas"]
            ])

            edited_bov = st.data_editor(
                df_bov_view,
                key="editor_bovino_consolidado",
                use_container_width=True,
                hide_index=True,
                height=680,
                column_config={
                    "codigo": st.column_config.NumberColumn("Código", disabled=True, width="small"),
                    "corte": st.column_config.TextColumn("Descrição do Corte", disabled=True, width="medium"),
                    "peso_bovino": st.column_config.NumberColumn("Peso Boi Casado (KG)", disabled=True, format="%.3f", help="Soma automática: Dianteiro + Traseiro + Ponta de Agulha"),
                    "part_pct": st.column_config.NumberColumn("Part. (%)", disabled=True, format="%.2f%%"),
                    "custo_bovino": st.column_config.NumberColumn("Custo Desossa (R$)", disabled=True, format="R$ %.2f"),
                    "preco_venda": st.column_config.NumberColumn("Preço Venda (R$)", disabled=True, format="R$ %.2f"),
                    "venda_total": st.column_config.NumberColumn("Receita Desossa (R$)", disabled=True, format="R$ %.2f"),
                    "preco_medio_final": st.column_config.NumberColumn("🎯 Custo Médio Final (R$)", disabled=True, format="R$ %.2f", help="Custo médio ponderado entre a Desossa do Boi Casado e os Lotes Adicionais (Masterboi / Caixas)"),
                    "pesagens_col_o": st.column_config.TextColumn("✍️ Lotes Adicionais (KG)", width="medium", help="Para cortes de Traseiro, informe o peso ou soma de caixas extras (ex: 200 + 150)"),
                    "peso_masterboi": st.column_config.NumberColumn("Peso Adicional Total (KG)", disabled=True, format="%.3f"),
                    "custo_masterboi": st.column_config.NumberColumn("✍️ Custo Adicional (R$)", format="%.2f", step=0.01),
                    "origem_mb": st.column_config.TextColumn("Fonte Lote Adicional", disabled=True, width="medium"),
                }
            )

            mudou_ext = False
            extras_dict = st.session_state.rend_state.setdefault("bovino_extras_traseiro", {})
            for idx, r in edited_bov.iterrows():
                cod_str = str(int(r["codigo"]))
                if cod_str in extras_dict:
                    nova_str_o = str(r["pesagens_col_o"]).strip() if pd.notna(r["pesagens_col_o"]) else ""
                    p_soma, _, _, _ = reng.parse_pesagens(nova_str_o)
                    c_novo = float(r["custo_masterboi"]) if pd.notna(r["custo_masterboi"]) else 0.0
                    ant_str_o = str(extras_dict[cod_str].get("pesagens", ""))
                    ant_c = float(extras_dict[cod_str].get("custo", 0.0))
                    if nova_str_o != ant_str_o or abs(c_novo - ant_c) > 1e-4:
                        extras_dict[cod_str] = {"pesagens": nova_str_o, "peso": p_soma, "custo": c_novo}
                        mudou_ext = True
            if mudou_ext:
                salvar_estado_rendimento()
                st.rerun()

            with st.container(border=True):
                c_nf1, c_nf2 = st.columns([7, 3], vertical_alignment="center")
                with c_nf1:
                    st.markdown("###### 💾 Exportar Cortes Consolidados para a Nota Fiscal")
                    st.caption("Transfere todos os cortes com volume apurado utilizando o **Custo Médio Final Ponderado**.")
                with c_nf2:
                    if st.button("💾 Registrar Cortes na Nota Fiscal", type="primary", use_container_width=True):
                        enviados = 0
                        for l in bov["linhas"]:
                            peso_tot = l["peso_bovino"] + l["peso_masterboi"]
                            pm_final = l["preco_medio_final"]
                            if peso_tot > 0 and pm_final > 0:
                                data_manager.add_item_nota(
                                    codigo=l["codigo"],
                                    descricao=l["corte"],
                                    quantidade=round(peso_tot, 3),
                                    valor_unitario=round(pm_final, 2),
                                    valor_total=round(peso_tot * pm_final, 2),
                                )
                                enviados += 1
                        st.toast(f"✅ {enviados} cortes registrados na Consolidação de Nota Fiscal!", icon="💾")

        elif "Dianteiro (Boi Casado)" in sub_bov:
            render_painel_desossa("DIANTEIRO", part_base="peca")
        elif "Traseiro (Boi Casado)" in sub_bov:
            render_painel_desossa("TRASEIRO", part_base="rendimento")
        elif "Ponta de Agulha (Boi Casado)" in sub_bov:
            render_painel_desossa("PONTA_AGULHA", part_base="rendimento")
        elif "Dianteiro Masterboi" in sub_bov:
            render_painel_desossa("DIANTEIRO_MASTERBOI", part_base="peca")
        elif "Ponta de Agulha Masterboi" in sub_bov:
            render_painel_desossa("PA_MASTERBOI", part_base="rendimento")

    # --------------------------------------------------------------------------
    # FLUXO 2: SUÍNO & CARNEIRO
    # --------------------------------------------------------------------------
    with fluxo_acougue[1]:
        sub_sc = st.radio(
            "Selecione a Linha de Desossa:",
            ["🐖 Desossa Suína (Carcaça)", "🐑 Desossa Ovina (Carneiro)"],
            horizontal=True
        )
        if sub_sc.startswith("🐖"):
            render_painel_desossa("SUINO", part_base="rendimento")
        else:
            render_painel_desossa("CARNEIRO", part_base="peca")

    # --------------------------------------------------------------------------
    # FLUXO 3: RECEITAS & PRODUÇÃO PRÓPRIA
    # --------------------------------------------------------------------------
    with fluxo_acougue[2]:
        col_rec_sel, col_rec_sync = st.columns([7, 3], vertical_alignment="bottom")
        with col_rec_sel:
            sub_rec = st.radio(
                "Selecione a Ficha Técnica de Produção:",
                [
                    "🍲 Kit Feijoada (Cód. 4457)",
                    "🥩 Carne de Sol Bovina (Cód. 3311)",
                    "🥓 Carne de Sol Suína (Cód. 30515)",
                    "🥘 Panelada Bovina (Cód. 6456)",
                ],
                horizontal=True
            )
        with col_rec_sync:
            if st.button("🔄 Sincronizar Custos c/ Desossa", use_container_width=True, help="Atualiza os custos unitários das matérias-primas com base nos custos apurados na Desossa"):
                mapa_custos = reng.obter_mapa_custos_atualizados(st.session_state.rend_state)
                atualizados = 0
                for ch_r, rec_obj in st.session_state.rend_state["receitas"].items():
                    for ing in rec_obj["ingredientes"]:
                        cod_i = int(ing["codigo"])
                        if cod_i in mapa_custos and mapa_custos[cod_i] > 0:
                            ing["custo_kg"] = mapa_custos[cod_i]
                            atualizados += 1
                salvar_estado_rendimento()
                st.toast(f"✅ {atualizados} insumos atualizados com os custos da Desossa!", icon="🔄")
                st.rerun()

        mapa_chave_rec = {
            "🍲 Kit Feijoada (Cód. 4457)": "KIT_FEIJOADA",
            "🥩 Carne de Sol Bovina (Cód. 3311)": "CARNE_SOL_BOVINA",
            "🥓 Carne de Sol Suína (Cód. 30515)": "CARNE_SOL_SUINA",
            "🥘 Panelada Bovina (Cód. 6456)": "PANELADA",
        }
        chave_rec_atual = mapa_chave_rec[sub_rec]
        dados_rec = st.session_state.rend_state["receitas"][chave_rec_atual]
        calc_r = reng.calcular_receita(dados_rec)

        with st.container(border=True):
            c_r1, c_r2, c_r3, c_r4 = st.columns([4, 2, 2, 2], vertical_alignment="bottom")
            with c_r1:
                novo_rend_str = st.text_input(
                    f"⚖️ Volume Final Produzido — {dados_rec['produto']} (KG):",
                    value=str(dados_rec.get("rendimento_str", "")),
                    key=f"rend_str_{chave_rec_atual}",
                    placeholder="Ex: 18,40 + 12,055",
                    help="Informe as pesagens do produto acabado separadas por espaço ou +"
                )
            with c_r2:
                pv_rec_atual = float(dados_rec.get("preco_venda", 0.0) or 0.0)
                novo_pv_rec_in = st.number_input(
                    "💵 Preço de Venda / KG (R$):",
                    min_value=0.0,
                    value=pv_rec_atual if pv_rec_atual > 0 else None,
                    step=0.01,
                    format="%.2f",
                    placeholder="Ex: 38,93",
                    key=f"pv_rec_{chave_rec_atual}"
                )
                novo_pv_rec = float(novo_pv_rec_in or 0.0)
            with c_r3:
                if st.button("💾 Enviar p/ Nota Fiscal", key=f"nf_rec_{chave_rec_atual}", type="primary", use_container_width=True):
                    if calc_r["rendimento_final"] > 0 and calc_r["custo_un_produzido"] > 0:
                        data_manager.add_item_nota(
                            codigo=dados_rec["codigo"],
                            descricao=dados_rec["produto"],
                            quantidade=round(calc_r["rendimento_final"], 3),
                            valor_unitario=round(calc_r["custo_un_produzido"], 2),
                            valor_total=round(calc_r["custo_total_insumos"], 2),
                        )
                        st.toast(f"✅ {dados_rec['produto']} registrado na Nota Fiscal!", icon="💾")
                    else:
                        st.warning("Informe o volume produzido e os insumos antes de registrar.")
            with c_r4:
                if st.button("🧹 Limpar Ficha", key=f"zerar_rec_{chave_rec_atual}", use_container_width=True):
                    dados_rec["rendimento_str"] = ""
                    for ing in dados_rec.get("ingredientes", []):
                        ing["pesagens"] = ""
                    salvar_estado_rendimento()
                    st.toast(f"Pesagens de {dados_rec['produto']} redefinidas!", icon="🧹")
                    st.rerun()

            if novo_rend_str != dados_rec.get("rendimento_str") or abs(novo_pv_rec - float(dados_rec.get("preco_venda", 0.0))) > 1e-4:
                dados_rec["rendimento_str"] = novo_rend_str
                dados_rec["preco_venda"] = novo_pv_rec
                salvar_estado_rendimento()
                st.rerun()

        # KPIs da Receita
        rk1, rk2, rk3, rk4, rk5 = st.columns(5)
        with rk1:
            st.html(f"""
            <div class="kpi-box">
                <div class="kpi-label">📥 Total de Insumos</div>
                <div class="kpi-val">{calc_r['peso_total_insumos']:,.3f} kg</div>
                <div class="kpi-sub">Custo Total: R$ {calc_r['custo_total_insumos']:,.2f}</div>
            </div>
            """)
        with rk2:
            st.html(f"""
            <div class="kpi-box-accent">
                <div class="kpi-label">📤 Produção Acabada</div>
                <div class="kpi-val" style="color:#34D399;">{calc_r['rendimento_final']:,.3f} kg</div>
                <div class="kpi-sub">{calc_r['qtd_pesos_rend']} lotes apontados</div>
            </div>
            """)
        with rk3:
            label_q = "📉 Quebra de Processo" if calc_r["quebra_kg"] >= 0 else "📈 Ganho de Rendimento"
            st.html(f"""
            <div class="kpi-box">
                <div class="kpi-label">{label_q}</div>
                <div class="kpi-val" style="color:#FBBF24;">{calc_r['quebra_kg']:,.3f} kg</div>
                <div class="kpi-sub">{calc_r['quebra_pct']*100:.2f}% sobre insumos</div>
            </div>
            """)
        with rk4:
            st.html(f"""
            <div class="kpi-box-accent">
                <div class="kpi-label">🎯 Custo Final / KG</div>
                <div class="kpi-val" style="color:#38BDF8;">R$ {calc_r['custo_un_produzido']:,.2f}</div>
                <div class="kpi-sub">Preço Venda: R$ {calc_r['preco_venda']:,.2f}/kg</div>
            </div>
            """)
        with rk5:
            st.html(f"""
            <div class="kpi-box">
                <div class="kpi-label">📈 Markup / Margem</div>
                <div class="kpi-val">{calc_r['mkp_pct']*100:.2f}%</div>
                <div class="kpi-sub">Margem Bruta: {calc_r['mkd_pct']*100:.2f}%</div>
            </div>
            """)

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        df_rec_grid = pd.DataFrame([
            {
                "codigo": l["codigo"],
                "ingrediente": l["ingrediente"],
                "pesagens": l["pesagens"],
                "qtd_pesos": l["qtd_pesagens"],
                "peso_kg": round(l["peso_kg"], 3),
                "custo_kg": round(l["custo_kg"], 2),
                "custo_total": round(l["custo_total"], 2),
                "part_pct": round(l["part_pct"] * 100, 2),
            }
            for l in calc_r["linhas"]
        ])

        edited_rec = st.data_editor(
            df_rec_grid,
            key=f"editor_rec_{chave_rec_atual}",
            use_container_width=True,
            hide_index=True,
            column_config={
                "codigo": st.column_config.NumberColumn("Código", disabled=True, width="small"),
                "ingrediente": st.column_config.TextColumn("Matéria-Prima / Ingrediente", disabled=True, width="medium"),
                "pesagens": st.column_config.TextColumn("✍️ Pesagens Utilizadas (KG)", width="large"),
                "qtd_pesos": st.column_config.NumberColumn("Lotes", disabled=True, width="small"),
                "peso_kg": st.column_config.NumberColumn("Peso Total (KG)", disabled=True, format="%.3f"),
                "custo_kg": st.column_config.NumberColumn("✍️ Custo Unitário (R$)", format="%.2f", step=0.01),
                "custo_total": st.column_config.NumberColumn("Custo Total (R$)", disabled=True, format="R$ %.2f"),
                "part_pct": st.column_config.NumberColumn("Participação (%)", disabled=True, format="%.2f%%"),
            }
        )

        mudou_rec = False
        for idx, r in edited_rec.iterrows():
            ing_orig = dados_rec["ingredientes"][idx]
            n_pes = str(r["pesagens"]) if pd.notna(r["pesagens"]) else ""
            n_ckg = float(r["custo_kg"]) if pd.notna(r["custo_kg"]) else 0.0
            if n_pes != ing_orig.get("pesagens", "") or abs(n_ckg - float(ing_orig.get("custo_kg", 0.0))) > 1e-4:
                ing_orig["pesagens"] = n_pes
                ing_orig["custo_kg"] = n_ckg
                mudou_rec = True
        if mudou_rec:
            salvar_estado_rendimento()
            st.rerun()

        if chave_rec_atual == "PANELADA":
            with st.container(border=True):
                st.markdown("###### 🧮 Dimensionamento de Batelada — Proporção Padrão (44% Tripa Fina | 40% Bucho | 16% Mocotó)")
                col_sim_p, col_sim_res = st.columns([2, 5])
                with col_sim_p:
                    lote_alvo = st.number_input(
                        "Meta de Produção (KG):",
                        min_value=1.0,
                        value=float(dados_rec.get("meta_simulacao_kg", 96.0)),
                        step=5.0
                    )
                    dados_rec["meta_simulacao_kg"] = lote_alvo
                with col_sim_res:
                    st.markdown(f"""
                    - **5710 - TRIPA FINA (Meta 44%)**: `{lote_alvo * 0.44:,.3f} kg` *(Participação real no lote: `{calc_r['linhas'][0]['part_pct']*100:.1f}%`)*
                    - **5709 - BUCHO BOVINO (Meta 40%)**: `{lote_alvo * 0.40:,.3f} kg` *(Participação real no lote: `{calc_r['linhas'][1]['part_pct']*100:.1f}%`)*
                    - **4342 - MOCOTÓ BOVINO (Meta 16%)**: `{lote_alvo * 0.16:,.3f} kg` *(Participação real no lote: `{calc_r['linhas'][2]['part_pct']*100:.1f}%`)*
                    """)

    # --------------------------------------------------------------------------
    # FLUXO 4: CONTROLE DE MIÚDOS & PESAGENS EXTRAS
    # --------------------------------------------------------------------------
    with fluxo_acougue[3]:
        lista_anot = st.session_state.rend_state.setdefault("anotacoes", [])
        linhas_anot, soma_geral_anot, total_tickets_anot = reng.calcular_anotacoes(lista_anot)

        col_t_anot, col_z_anot = st.columns([8, 2], vertical_alignment="center")
        with col_t_anot:
            st.markdown("##### 📝 Controle Consolidado de Miúdos, Subprodutos & Pesagens Operacionais")
            st.caption("Acompanhamento centralizado de **Fígado Bovino, Coração Bovino, Panelada, Picadinho, Carne Moída, Bife Amaciado, Sarrabulho, Pé Suíno, Orelha Suína, Buchada e Frissura**.")
        with col_z_anot:
            if st.button("🧹 Limpar Pesagens", use_container_width=True):
                for a in lista_anot:
                    a["pesagens"] = ""
                salvar_estado_rendimento()
                st.rerun()

        opcoes_anot = [f"{a['codigo']} - {a['item']} ({a['origem']})" for a in lista_anot]
        with st.form(key="form_bip_anotacoes", clear_on_submit=True, border=True):
            ca1, ca2, ca3 = st.columns([4, 4, 2], vertical_alignment="bottom")
            with ca1:
                sel_anot = st.selectbox("⚡ 1. Selecionar Item / Subproduto:", options=opcoes_anot, key="sel_bip_anot")
            with ca2:
                val_anot_str = st.text_input(
                    "⚖️ 2. Informar Peso(s) da Balança (KG) [Enter]:",
                    placeholder="Ex: 5,400  ou  5,40 6,10 4,85"
                )
            with ca3:
                sub_anot = st.form_submit_button("➕ Registrar Peso", type="primary", use_container_width=True)

            if sub_anot:
                texto_anot = str(val_anot_str or "").strip()
                soma_a, qtd_a, _, _ = reng.parse_pesagens(texto_anot)
                if not texto_anot or reng.tem_token_invalido_pesagem(texto_anot) or soma_a <= 0:
                    set_feedback_abaixo(
                        "bip_anot",
                        "error",
                        f"❌ Peso inválido ({texto_anot or 'vazio'}). Informe um peso válido maior que zero (ex: 5,400 ou ,874)."
                    )
                else:
                    cod_sel = int(sel_anot.split(" - ")[0])
                    for a in lista_anot:
                        if int(a["codigo"]) == cod_sel:
                            a["pesagens"] = reng.append_pesagem(a.get("pesagens", ""), texto_anot)
                            break
                    salvar_estado_rendimento()
                    set_feedback_abaixo(
                        "bip_anot",
                        "success",
                        f"✅ +{soma_a:.3f} kg ({qtd_a} pesagem/ns) registrado com sucesso em {sel_anot}!"
                    )
                    st.rerun()

        render_feedback_abaixo("bip_anot")

        ak1, ak2, ak3 = st.columns(3)
        with ak1:
            st.html(f"""
            <div class="kpi-box-accent">
                <div class="kpi-label">⚖️ Volume Total Apurado</div>
                <div class="kpi-val" style="color:#34D399;">{soma_geral_anot:,.3f} kg</div>
                <div class="kpi-sub">{len(linhas_anot)} itens em acompanhamento</div>
            </div>
            """)
        with ak2:
            st.html(f"""
            <div class="kpi-box">
                <div class="kpi-label">🏷️ Total de Pesagens Registradas</div>
                <div class="kpi-val">{total_tickets_anot} lotes</div>
                <div class="kpi-sub">Consolidação automática</div>
            </div>
            """)
        with ak3:
            peso_buchada = next((x["peso_total_kg"] for x in linhas_anot if x["codigo"] == 14338), 0.0)
            peso_frissura = next((x["peso_total_kg"] for x in linhas_anot if x["codigo"] == 27025), 0.0)
            st.html(f"""
            <div class="kpi-box">
                <div class="kpi-label">🐑 Volume Ovino (Buchada & Frissura)</div>
                <div class="kpi-val" style="color:#38BDF8;">{peso_buchada + peso_frissura:,.3f} kg</div>
                <div class="kpi-sub">Buchada: {peso_buchada:,.3f} kg | Frissura: {peso_frissura:,.3f} kg</div>
            </div>
            """)

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        df_anot_grid = pd.DataFrame([
            {
                "codigo": l["codigo"],
                "item": l["item"],
                "origem": l["origem"],
                "pesagens": l["pesagens"],
                "qtd_pesagens": l["qtd_pesagens"],
                "peso_total_kg": round(l["peso_total_kg"], 3),
                "observacao": l["observacao"],
            }
            for l in linhas_anot
        ])

        ed_anot = st.data_editor(
            df_anot_grid,
            key="editor_topico_anotacoes",
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic",
            column_config={
                "codigo": st.column_config.NumberColumn("Código", width="small", step=1),
                "item": st.column_config.TextColumn("Descrição do Item", width="medium"),
                "origem": st.column_config.SelectboxColumn("Categoria / Setor", options=["Bovino / Miúdos", "Bovino / Produção", "Bovino / Extra", "Suíno", "Carneiro", "Geral"], width="small"),
                "pesagens": st.column_config.TextColumn("✍️ Registro de Pesagens (KG)", width="large"),
                "qtd_pesagens": st.column_config.NumberColumn("Lotes", disabled=True, width="small"),
                "peso_total_kg": st.column_config.NumberColumn("Peso Acumulado (KG)", disabled=True, format="%.3f"),
                "observacao": st.column_config.TextColumn("Observações / Referência", width="small"),
            }
        )

        nova_lista_anot = []
        mudou_anot = False
        if len(ed_anot) != len(lista_anot):
            mudou_anot = True
        for idx, r in ed_anot.iterrows():
            cod_v = int(r["codigo"]) if pd.notna(r["codigo"]) else 0
            item_v = str(r["item"]).strip() if pd.notna(r["item"]) else "NOVO ITEM"
            orig_v = str(r["origem"]) if pd.notna(r["origem"]) else "Geral"
            pes_v = str(r["pesagens"]) if pd.notna(r["pesagens"]) else ""
            obs_v = str(r["observacao"]) if pd.notna(r["observacao"]) else ""
            nova_lista_anot.append({
                "codigo": cod_v,
                "item": item_v,
                "origem": orig_v,
                "pesagens": pes_v,
                "observacao": obs_v,
            })
            if idx < len(lista_anot):
                ant = lista_anot[idx]
                if (
                    cod_v != int(ant.get("codigo", 0))
                    or item_v != ant.get("item", "")
                    or orig_v != ant.get("origem", "")
                    or pes_v != ant.get("pesagens", "")
                    or obs_v != ant.get("observacao", "")
                ):
                    mudou_anot = True

        if mudou_anot:
            st.session_state.rend_state["anotacoes"] = nova_lista_anot
            salvar_estado_rendimento()
            st.rerun()


# ==============================================================================
# MÓDULO 2: GESTÃO DE CAIXARIA (REPROCESSAMENTO, CONVERSÃO & QUEBRAS)
# ==============================================================================
elif aba_selecionada == "📦 Gestão de Caixaria":
    dados_cx = st.session_state.rend_state["caixaria"]
    calc_cx = reng.calcular_caixaria(dados_cx)
    produtos_df_cx = data_manager.get_produtos()

    col_cx_head, col_cx_sync, col_cx_zerar = st.columns([5, 3, 2], vertical_alignment="center")
    with col_cx_head:
        st.markdown('<div class="app-badge">📦 CONTROLE OPERACIONAL DE CAIXARIA</div>', unsafe_allow_html=True)
        st.markdown('<div class="app-title">Gestão de Caixaria, Conversão & Perdas</div>', unsafe_allow_html=True)
        st.markdown('<div class="app-subtitle">Controle integrado de transformação entre cortes (Saída ➔ Entrada), apuração de custo médio de conversão e registro de descartes.</div>', unsafe_allow_html=True)
    with col_cx_sync:
        if st.button("🔄 Sincronizar Custos do Catálogo", type="primary", use_container_width=True, help="Atualiza os custos unitários da Caixaria com base no Custo Padrão cadastrado no Catálogo de Produtos"):
            mapa_cad = {int(r["codigo"]): float(r.get("custo_padrao", 0.0)) for _, r in produtos_df_cx.iterrows() if float(r.get("custo_padrao", 0.0)) > 0}
            cont_c = 0
            for item_p in dados_cx["perdas_custos"]:
                cod_p = int(item_p["codigo"])
                if cod_p in mapa_cad:
                    item_p["custo_kg"] = mapa_cad[cod_p]
                    cont_c += 1
            salvar_estado_rendimento()
            st.toast(f"✅ {cont_c} custos sincronizados a partir do Catálogo de Produtos!", icon="📋")
            st.rerun()
    with col_cx_zerar:
        if st.button("🧹 Limpar Movimentação", use_container_width=True):
            for p in dados_cx.get("perdas_custos", []):
                p["pesagens_perda"] = ""
            for s in dados_cx.get("saidas", []):
                s["pesagens_saida"] = ""
            for e in dados_cx.get("entradas", []):
                e["pesagens_entrada"] = ""
            salvar_estado_rendimento()
            st.toast("Movimentações da Caixaria redefinidas!", icon="🧹")
            st.rerun()

    # Barra expansível para incluir novo corte vindo do Catálogo
    with st.expander("➕ Adicionar Produto do Catálogo à Operação de Caixaria", expanded=False):
        if not produtos_df_cx.empty:
            c_inc1, c_inc2, c_inc3, c_inc4 = st.columns([4, 2, 2, 2], vertical_alignment="bottom")
            opcoes_cad_cx = [f"{int(r['codigo'])} - {r['descricao']}" for _, r in produtos_df_cx.iterrows()]
            with c_inc1:
                sel_novo_cx = st.selectbox("Produto do Catálogo:", options=opcoes_cad_cx, key="sel_add_prod_cx")
            with c_inc2:
                onde_inc = st.selectbox("Disponibilizar em:", options=["Todas as Listas (Saída, Entrada e Perda)", "Saídas e Perdas", "Somente Entradas"], key="onde_add_cx")
            with c_inc3:
                custo_inc_man_in = st.number_input("Custo Unitário (R$/KG):", min_value=0.0, value=None, step=0.01, format="%.2f", placeholder="Ex: 38,93", help="Deixe em branco para utilizar o custo já cadastrado no catálogo")
                custo_inc_man = float(custo_inc_man_in or 0.0)
            with c_inc4:
                if st.button("➕ Habilitar Produto", type="primary", use_container_width=True):
                    cod_inc = int(sel_novo_cx.split(" - ")[0])
                    row_prod = produtos_df_cx[produtos_df_cx["codigo"] == cod_inc].iloc[0]
                    nome_inc = str(row_prod["descricao"]).strip()
                    custo_final_inc = custo_inc_man if custo_inc_man > 0 else float(row_prod.get("custo_padrao", 0.0))

                    if not any(int(x["codigo"]) == cod_inc for x in dados_cx["perdas_custos"]):
                        dados_cx["perdas_custos"].append({"codigo": cod_inc, "corte": nome_inc, "pesagens_perda": "", "custo_kg": custo_final_inc})
                    if "Saída" in onde_inc and not any(int(x["codigo"]) == cod_inc for x in dados_cx["saidas"]):
                        dados_cx["saidas"].append({"codigo": cod_inc, "corte": nome_inc, "pesagens_saida": ""})
                    if ("Entrada" in onde_inc or "Todas" in onde_inc) and not any(int(x["codigo"]) == cod_inc for x in dados_cx["entradas"]):
                        dados_cx["entradas"].append({"codigo": cod_inc, "corte": nome_inc, "pesagens_entrada": ""})

                    if custo_final_inc > 0:
                        data_manager.update_custo_padrao_por_codigo(cod_inc, custo_final_inc)
                    salvar_estado_rendimento()
                    st.toast(f"✅ '{nome_inc}' habilitado na Caixaria!", icon="📦")
                    st.rerun()

    # KPIs Gerais da Caixaria
    ck1, ck2, ck3, ck4, ck5 = st.columns(5)
    with ck1:
        st.html(f"""
        <div class="kpi-box">
            <div class="kpi-label">🗑️ Total de Perdas / Descarte</div>
            <div class="kpi-val" style="color:#F87171;">R$ {calc_cx['total_valor_perda']:,.2f}</div>
            <div class="kpi-sub">Volume Descartado: {calc_cx['total_peso_perda']:,.3f} kg</div>
        </div>
        """)
    with ck2:
        st.html(f"""
        <div class="kpi-box-accent">
            <div class="kpi-label">📤 Volume Total de Saída</div>
            <div class="kpi-val">{calc_cx['total_peso_saida']:,.3f} kg</div>
            <div class="kpi-sub">Enviado p/ Transformação</div>
        </div>
        """)
    with ck3:
        st.html(f"""
        <div class="kpi-box-accent">
            <div class="kpi-label">💵 Custo Total de Saída</div>
            <div class="kpi-val" style="color:#38BDF8;">R$ {calc_cx['total_valor_saida']:,.2f}</div>
            <div class="kpi-sub">Valor Total em Reprocessamento</div>
        </div>
        """)
    with ck4:
        st.html(f"""
        <div class="kpi-box">
            <div class="kpi-label">⚖️ Custo Médio de Conversão</div>
            <div class="kpi-val" style="color:#FBBF24;">R$ {calc_cx['custo_medio_saida']:,.2f}/kg</div>
            <div class="kpi-sub">Custo Rateado por KG</div>
        </div>
        """)
    with ck5:
        cor_dif = "#34D399" if abs(calc_cx["diferenca_peso"]) < 0.005 else "#F87171"
        st.html(f"""
        <div class="kpi-box">
            <div class="kpi-label">📥 Volume Total de Entrada</div>
            <div class="kpi-val" style="color:{cor_dif};">{calc_cx['total_peso_entrada']:,.3f} kg</div>
            <div class="kpi-sub">Valor Rateado: R$ {calc_cx['total_nota_entrada']:,.2f}</div>
        </div>
        """)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    tab_cx_unif, tab_cx_perdas = st.tabs([
        f"1️⃣ Conversão Unificada: Saídas ➔ Entradas ({calc_cx['total_peso_saida']:,.3f} kg | R$ {calc_cx['custo_medio_saida']:,.2f}/kg)",
        f"2️⃣ Registro de Perdas & Descartes (R$ {calc_cx['total_valor_perda']:,.2f})"
    ])

    with tab_cx_unif:
        mapa_custo_atual = {int(x["codigo"]): float(x.get("custo_kg", 0.0)) for x in dados_cx["perdas_custos"]}
        opcoes_cx_s = [f"{item['codigo']} - {item['corte']}" for item in dados_cx["saidas"]]
        opcoes_cx_e = [f"{item['codigo']} - {item['corte']}" for item in dados_cx["entradas"]]
        idx_padrao_e = next((i for i, s in enumerate(opcoes_cx_e) if "6030" in s), 0)

        with st.form("form_bip_cx_unificado", clear_on_submit=True, border=True):
            st.markdown("###### ⚡ Registro Rápido de Conversão (Saída de Corte ➔ Entrada Reprocessada)")
            cu1, cu2, cu3, cu4, cu5 = st.columns([3, 3, 2, 2, 2], vertical_alignment="bottom")
            with cu1:
                sel_cx_s = st.selectbox("📤 1. Corte de Origem (Saída):", options=opcoes_cx_s, key="sel_unif_cx_s")
            with cu2:
                sel_cx_e = st.selectbox("📥 2. Produto Resultante (Entrada):", options=opcoes_cx_e, index=idx_padrao_e, key="sel_unif_cx_e")
            with cu3:
                val_cx_unif = st.text_input("⚖️ 3. Peso(s) (KG) [Enter]:", placeholder="Ex: 1,496 2,29")
            with cu4:
                custo_man_unif_in = st.number_input("💵 4. Custo Manual (Opcional):", min_value=0.0, value=None, step=0.01, format="%.2f", placeholder="Ex: 38,93", help="Deixe em branco para manter o custo cadastrado, ou informe um novo valor para atualizar o custo deste corte.")
                custo_man_unif = float(custo_man_unif_in or 0.0)
            with cu5:
                sub_cx_unif = st.form_submit_button("⚡ Registrar Conversão", type="primary", use_container_width=True)

            if sub_cx_unif:
                texto_peso_unif = str(val_cx_unif or "").strip()
                peso_invalido = reng.tem_token_invalido_pesagem(texto_peso_unif)
                soma_v, qtd_v, _, _ = reng.parse_pesagens(texto_peso_unif)
                cod_s = int(sel_cx_s.split(" - ")[0])
                cod_e = int(sel_cx_e.split(" - ")[0])

                if texto_peso_unif and (peso_invalido or soma_v <= 0):
                    set_feedback_abaixo(
                        "cx_unif",
                        "error",
                        f"❌ O peso informado ('{texto_peso_unif}') é inválido. Digite valores válidos maiores que zero (ex: 1,496 ou ,874). Nenhum peso ou custo foi alterado."
                    )
                elif soma_v > 0:
                    msg_custo_extra = ""
                    if custo_man_unif > 0:
                        for item_p in dados_cx["perdas_custos"]:
                            if int(item_p["codigo"]) == cod_s:
                                item_p["custo_kg"] = float(custo_man_unif)
                                break
                        data_manager.update_custo_padrao_por_codigo(cod_s, float(custo_man_unif))
                        msg_custo_extra = f" | 💵 Custo atualizado para R$ {custo_man_unif:.2f}/kg"

                    for item in dados_cx["saidas"]:
                        if int(item["codigo"]) == cod_s:
                            item["pesagens_saida"] = reng.append_pesagem(item.get("pesagens_saida", ""), texto_peso_unif)
                            break
                    for item in dados_cx["entradas"]:
                        if int(item["codigo"]) == cod_e:
                            item["pesagens_entrada"] = reng.append_pesagem(item.get("pesagens_entrada", ""), texto_peso_unif)
                            break
                    salvar_estado_rendimento()
                    set_feedback_abaixo(
                        "cx_unif",
                        "success",
                        f"✅ +{soma_v:.3f} kg ({qtd_v} pesagem/ns) registrado: {sel_cx_s} ➔ {sel_cx_e}{msg_custo_extra}!"
                    )
                    st.rerun()
                elif custo_man_unif > 0:
                    for item_p in dados_cx["perdas_custos"]:
                        if int(item_p["codigo"]) == cod_s:
                            item_p["custo_kg"] = float(custo_man_unif)
                            break
                    data_manager.update_custo_padrao_por_codigo(cod_s, float(custo_man_unif))
                    salvar_estado_rendimento()
                    set_feedback_abaixo(
                        "cx_unif",
                        "success",
                        f"✅ Custo unitário de {sel_cx_s} atualizado para R$ {custo_man_unif:.2f}/kg no catálogo! (Nenhum peso informado)"
                    )
                    st.rerun()
                else:
                    set_feedback_abaixo(
                        "cx_unif",
                        "warning",
                        "⚠️ Informe um peso válido (ex: 1,496 ou ,874) ou um custo manual maior que zero."
                    )

        render_feedback_abaixo("cx_unif")

        col_tab_s, col_tab_e = st.columns(2, gap="medium")

        with col_tab_s:
            st.markdown(f"###### 📤 Cortes de Saída (`Total: {calc_cx['total_peso_saida']:,.3f} kg` | `R$ {calc_cx['total_valor_saida']:,.2f}`)")
            df_s = pd.DataFrame(calc_cx["linhas_saidas"])
            ed_s = st.data_editor(
                df_s,
                key="ed_cx_saidas",
                use_container_width=True,
                hide_index=True,
                height=520,
                column_config={
                    "codigo": st.column_config.NumberColumn("Código", disabled=True, width="small"),
                    "corte": st.column_config.TextColumn("Corte de Origem", disabled=True, width="medium"),
                    "pesagens_saida": st.column_config.TextColumn("✍️ Pesagens de Saída", width="medium"),
                    "qtd_pesagens": st.column_config.NumberColumn("Lotes", disabled=True, width="small"),
                    "peso_kg": st.column_config.NumberColumn("Peso Total (KG)", disabled=True, format="%.3f"),
                    "custo_kg": st.column_config.NumberColumn("✍️ Custo Unit. (R$)", format="%.2f", step=0.01, help="Edite o custo manualmente se desejar; a alteração será sincronizada com o Catálogo."),
                    "total_rs": st.column_config.NumberColumn("Custo Total (R$)", disabled=True, format="R$ %.2f"),
                }
            )
            mudou_s = False
            for idx, r in ed_s.iterrows():
                orig = dados_cx["saidas"][idx]
                cod_row = int(orig["codigo"])
                ns_str = str(r["pesagens_saida"]) if pd.notna(r["pesagens_saida"]) else ""
                nc_val = float(r["custo_kg"]) if pd.notna(r["custo_kg"]) else 0.0
                custo_ant = mapa_custo_atual.get(cod_row, 0.0)
                if ns_str != orig.get("pesagens_saida", ""):
                    orig["pesagens_saida"] = ns_str
                    mudou_s = True
                if abs(nc_val - custo_ant) > 1e-4:
                    for item_p in dados_cx["perdas_custos"]:
                        if int(item_p["codigo"]) == cod_row:
                            item_p["custo_kg"] = nc_val
                            break
                    data_manager.update_custo_padrao_por_codigo(cod_row, nc_val)
                    mudou_s = True
            if mudou_s:
                salvar_estado_rendimento()
                st.rerun()

        with col_tab_e:
            st.markdown(f"###### 📥 Produtos de Entrada (`Total: {calc_cx['total_peso_entrada']:,.3f} kg` | `Custo Rateado: R$ {calc_cx['custo_medio_saida']:,.2f}/kg`)")
            df_e = pd.DataFrame(calc_cx["linhas_entradas"])
            ed_e = st.data_editor(
                df_e,
                key="ed_cx_entradas",
                use_container_width=True,
                hide_index=True,
                height=520,
                column_config={
                    "codigo": st.column_config.NumberColumn("Código", disabled=True, width="small"),
                    "corte": st.column_config.TextColumn("Produto Resultante", disabled=True, width="medium"),
                    "pesagens_entrada": st.column_config.TextColumn("✍️ Pesagens de Entrada", width="medium"),
                    "qtd_pesagens": st.column_config.NumberColumn("Lotes", disabled=True, width="small"),
                    "peso_kg": st.column_config.NumberColumn("Peso Total (KG)", disabled=True, format="%.3f"),
                    "t_nota_rs": st.column_config.NumberColumn("Valor Rateado (R$)", disabled=True, format="R$ %.2f"),
                    "custo_medio_rateado": st.column_config.NumberColumn("Custo Conversão / KG", disabled=True, format="R$ %.2f"),
                    "custo_tabela_ref": st.column_config.NumberColumn("Custo Catálogo / KG", disabled=True, format="R$ %.2f"),
                }
            )
            mudou_e = False
            for idx, r in ed_e.iterrows():
                orig = dados_cx["entradas"][idx]
                ne_str = str(r["pesagens_entrada"]) if pd.notna(r["pesagens_entrada"]) else ""
                if ne_str != orig.get("pesagens_entrada", ""):
                    orig["pesagens_entrada"] = ne_str
                    mudou_e = True
            if mudou_e:
                salvar_estado_rendimento()
                st.rerun()

    with tab_cx_perdas:
        opcoes_cx_p = [f"{item['codigo']} - {item['corte']}" for item in dados_cx["perdas_custos"]]
        with st.form("form_bip_cx_perdas", clear_on_submit=True, border=True):
            cp1, cp2, cp3, cp4 = st.columns([4, 3, 2, 2], vertical_alignment="bottom")
            with cp1:
                sel_cx_p = st.selectbox("⚡ 1. Selecionar Corte Descartado:", options=opcoes_cx_p, key="sel_bip_cx_p")
            with cp2:
                val_cx_p = st.text_input("⚖️ 2. Peso(s) de Perda (KG) [Enter]:", placeholder="Ex: 0,694 0,940")
            with cp3:
                custo_man_p_in = st.number_input("💵 3. Custo Manual (Opcional):", min_value=0.0, value=None, step=0.01, format="%.2f", placeholder="Ex: 38,93")
                custo_man_p = float(custo_man_p_in or 0.0)
            with cp4:
                sub_cx_p = st.form_submit_button("➕ Registrar Perda", type="primary", use_container_width=True)
            if sub_cx_p:
                texto_peso_p = str(val_cx_p or "").strip()
                peso_p_invalido = reng.tem_token_invalido_pesagem(texto_peso_p)
                soma_v, qtd_v, _, _ = reng.parse_pesagens(texto_peso_p)
                cod_alvo = int(sel_cx_p.split(" - ")[0])

                if texto_peso_p and (peso_p_invalido or soma_v <= 0):
                    set_feedback_abaixo(
                        "cx_perdas",
                        "error",
                        f"❌ O peso informado ('{texto_peso_p}') é inválido. Digite valores válidos maiores que zero (ex: 0,694 ou ,874). Nenhum lançamento foi realizado."
                    )
                elif soma_v > 0:
                    msg_custo_p = ""
                    if custo_man_p > 0:
                        for item in dados_cx["perdas_custos"]:
                            if int(item["codigo"]) == cod_alvo:
                                item["custo_kg"] = float(custo_man_p)
                                break
                        data_manager.update_custo_padrao_por_codigo(cod_alvo, float(custo_man_p))
                        msg_custo_p = f" | 💵 Custo atualizado para R$ {custo_man_p:.2f}/kg"

                    for item in dados_cx["perdas_custos"]:
                        if int(item["codigo"]) == cod_alvo:
                            item["pesagens_perda"] = reng.append_pesagem(item.get("pesagens_perda", ""), texto_peso_p)
                            break
                    salvar_estado_rendimento()
                    set_feedback_abaixo(
                        "cx_perdas",
                        "success",
                        f"✅ +{soma_v:.3f} kg ({qtd_v} pesagem/ns) registrado em Perdas ({sel_cx_p}){msg_custo_p}!"
                    )
                    st.rerun()
                elif custo_man_p > 0:
                    for item in dados_cx["perdas_custos"]:
                        if int(item["codigo"]) == cod_alvo:
                            item["custo_kg"] = float(custo_man_p)
                            break
                    data_manager.update_custo_padrao_por_codigo(cod_alvo, float(custo_man_p))
                    salvar_estado_rendimento()
                    set_feedback_abaixo(
                        "cx_perdas",
                        "success",
                        f"✅ Custo unitário de {sel_cx_p} atualizado para R$ {custo_man_p:.2f}/kg! (Nenhum peso informado)"
                    )
                    st.rerun()
                else:
                    set_feedback_abaixo(
                        "cx_perdas",
                        "warning",
                        "⚠️ Informe um peso válido (ex: 0,694 ou ,874) ou um custo manual maior que zero."
                    )

        render_feedback_abaixo("cx_perdas")

        df_p = pd.DataFrame(calc_cx["linhas_perdas"])
        ed_p = st.data_editor(
            df_p,
            key="ed_cx_perdas",
            use_container_width=True,
            hide_index=True,
            height=520,
            column_config={
                "codigo": st.column_config.NumberColumn("Código", disabled=True, width="small"),
                "corte": st.column_config.TextColumn("Descrição do Corte", disabled=True, width="medium"),
                "pesagens_perda": st.column_config.TextColumn("✍️ Registro de Pesagens Descartadas (KG)", width="large"),
                "qtd_pesagens": st.column_config.NumberColumn("Lotes", disabled=True, width="small"),
                "peso_kg": st.column_config.NumberColumn("Peso Descartado (KG)", disabled=True, format="%.3f"),
                "custo_kg": st.column_config.NumberColumn("✍️ Custo Unitário (R$)", format="%.2f", step=0.01),
                "total_rs": st.column_config.NumberColumn("Valor da Perda (R$)", disabled=True, format="R$ %.2f"),
            }
        )
        mudou_p = False
        for idx, r in ed_p.iterrows():
            orig = dados_cx["perdas_custos"][idx]
            np_str = str(r["pesagens_perda"]) if pd.notna(r["pesagens_perda"]) else ""
            nc_val = float(r["custo_kg"]) if pd.notna(r["custo_kg"]) else 0.0
            if np_str != orig.get("pesagens_perda", "") or abs(nc_val - float(orig.get("custo_kg", 0.0))) > 1e-4:
                orig["pesagens_perda"] = np_str
                if abs(nc_val - float(orig.get("custo_kg", 0.0))) > 1e-4:
                    orig["custo_kg"] = nc_val
                    data_manager.update_custo_padrao_por_codigo(int(orig["codigo"]), nc_val)
                mudou_p = True
        if mudou_p:
            salvar_estado_rendimento()
            st.rerun()


# ==============================================================================
# ABA 2: CALCULADORA DE PREÇO MÉDIO (DESIGN DE APLICATIVO SAAS / MODULAR)
# ==============================================================================
elif aba_selecionada == "🧮 Calculadora de Preço Médio":
    st.markdown('<div class="app-badge">⚡ MÓDULO OPERACIONAL</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-title">Calculadora de Preço Médio</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-subtitle">Adicione insumos ou compras, cada um com seu fator de conversão de rendimento. O sistema pondera os custos em tempo real.</div>', unsafe_allow_html=True)

    produtos_df = data_manager.get_produtos()

    if produtos_df.empty:
        st.warning("Nenhuma matéria-prima cadastrada. Acesse a aba 'Cadastro de Matérias-Primas' para cadastrar.")
    else:
        produtos_dict = {
            int(r['id']): {
                "codigo": int(r['codigo']),
                "descricao": str(r['descricao']),
                "unidade": str(r['unidade']),
                "fator": float(r['fator_conversao'])
            }
            for _, r in produtos_df.iterrows()
        }

        if "itens_calculo" not in st.session_state or len(st.session_state.itens_calculo) == 0:
            primeiro_id = list(produtos_dict.keys())[0]
            st.session_state.itens_calculo = [
                {
                    "uid": 1,
                    "produto_id": primeiro_id,
                    "quantidade": 0.0,
                    "custo_unitario": 0.0,
                    "fator": produtos_dict[primeiro_id]["fator"]
                }
            ]
            st.session_state.proximo_uid = 2

        col_itens, col_resumo = st.columns([7, 5], gap="large")

        with col_itens:
            st.markdown("##### 🛒 Itens / Lotes da Composição")
            st.caption("Adicione quantos itens ou compras desejar. Cada item puxa o seu fator de conversão automaticamente.")

            itens_processados = []
            itens_para_remover = []

            for idx, item in enumerate(st.session_state.itens_calculo):
                uid = item["uid"]
                with st.container(border=True):
                    c_num, c_remover = st.columns([5, 1])
                    with c_num:
                        st.markdown(f"<div class='item-number-badge'>📦 Item #{idx + 1}</div>", unsafe_allow_html=True)
                    with c_remover:
                        if len(st.session_state.itens_calculo) > 1:
                            if st.button("🗑️", key=f"del_{uid}", help="Remover este item"):
                                itens_para_remover.append(idx)

                    opcoes_idx = list(produtos_dict.keys())
                    current_idx = opcoes_idx.index(item["produto_id"]) if item["produto_id"] in opcoes_idx else 0

                    novo_prod_id = st.selectbox(
                        "Matéria-Prima:",
                        options=opcoes_idx,
                        format_func=lambda pid: f"{produtos_dict[pid]['descricao']}  [Cód: {produtos_dict[pid]['codigo']}]",
                        index=current_idx,
                        key=f"prod_sel_{uid}"
                    )

                    if novo_prod_id != item["produto_id"]:
                        item["produto_id"] = novo_prod_id
                        item["fator"] = produtos_dict[novo_prod_id]["fator"]
                        st.rerun()

                    col_qtd, col_custo, col_fator = st.columns([3, 3, 2], vertical_alignment="bottom")

                    unidade = produtos_dict[item["produto_id"]]["unidade"]
                    is_peso = unidade.upper() in ["KG", "G", "L"]
                    step_qtd = 0.005 if is_peso else 1.0
                    fmt_qtd = "%.3f" if is_peso else "%.2f"

                    with col_qtd:
                        qtd_atual = float(item.get("quantidade", 0.0) or 0.0)
                        qtd_in = st.number_input(
                            f"Quantidade ({unidade}):",
                            min_value=0.0,
                            value=qtd_atual if qtd_atual > 0 else None,
                            step=step_qtd,
                            format=fmt_qtd,
                            placeholder="Ex: 10,000" if is_peso else "Ex: 10,00",
                            key=f"qtd_{uid}"
                        )
                        item["quantidade"] = float(qtd_in or 0.0)

                    with col_custo:
                        custo_atual = float(item.get("custo_unitario", 0.0) or 0.0)
                        custo_in = st.number_input(
                            "Custo Unitário (R$):",
                            min_value=0.0,
                            value=custo_atual if custo_atual > 0 else None,
                            step=0.01,
                            format="%.2f",
                            placeholder="Ex: 38,93",
                            key=f"custo_{uid}"
                        )
                        item["custo_unitario"] = float(custo_in or 0.0)

                    with col_fator:
                        item["fator"] = st.number_input(
                            "Fator:",
                            min_value=0.0001,
                            value=float(item.get("fator", 1.0)),
                            step=0.05,
                            format="%.4f",
                            key=f"fator_{uid}",
                            help="Fator de conversão / rendimento deste insumo."
                        )

                    qtd_com_fator = item["quantidade"] * item["fator"]
                    valor_total_item = item["quantidade"] * item["custo_unitario"]

                    st.html(f"""
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 6px; padding-top: 8px; border-top: 1px dashed rgba(255, 255, 255, 0.08); font-size: 0.85rem;">
                        <span style="color: #94A3B8;">⚖️ Rendimento c/ Fator: <b style="color: #A5B4FC; font-family: 'JetBrains Mono';">{qtd_com_fator:,.3f}</b></span>
                        <span style="color: #94A3B8;">💵 Subtotal: <b style="color: #34D399; font-family: 'JetBrains Mono';">R$ {valor_total_item:,.2f}</b></span>
                    </div>
                    """)

                    itens_processados.append({
                        "produto_id": item["produto_id"],
                        "codigo": produtos_dict[item["produto_id"]]["codigo"],
                        "descricao": produtos_dict[item["produto_id"]]["descricao"],
                        "quantidade": item["quantidade"],
                        "custo_unitario": item["custo_unitario"],
                        "fator": item["fator"],
                        "qtd_com_fator": qtd_com_fator,
                        "valor_total": valor_total_item
                    })

            if itens_para_remover:
                for idx in reversed(itens_para_remover):
                    st.session_state.itens_calculo.pop(idx)
                st.rerun()

            col_add, col_reset = st.columns([2, 1])
            with col_add:
                if st.button("➕ Adicionar Outro Insumo / Lote", use_container_width=True):
                    primeiro_id = list(produtos_dict.keys())[0]
                    st.session_state.itens_calculo.append({
                        "uid": st.session_state.proximo_uid,
                        "produto_id": primeiro_id,
                        "quantidade": 0.0,
                        "custo_unitario": 0.0,
                        "fator": produtos_dict[primeiro_id]["fator"]
                    })
                    st.session_state.proximo_uid += 1
                    st.rerun()

            with col_reset:
                if st.button("🔄 Reiniciar", use_container_width=True, help="Limpa todos os itens e recomeça"):
                    primeiro_id = list(produtos_dict.keys())[0]
                    st.session_state.itens_calculo = [
                        {
                            "uid": st.session_state.proximo_uid,
                            "produto_id": primeiro_id,
                            "quantidade": 0.0,
                            "custo_unitario": 0.0,
                            "fator": produtos_dict[primeiro_id]["fator"]
                        }
                    ]
                    st.session_state.proximo_uid += 1
                    st.rerun()

        with col_resumo:
            st.markdown("##### 📊 Painel Executivo de Fechamento")
            st.caption("Consolidação automática ponderada com base no rendimento de cada insumo.")

            total_gasto = sum(it["valor_total"] for it in itens_processados)
            total_rendimento = sum(it["qtd_com_fator"] for it in itens_processados)
            total_volume_comprado = sum(it["quantidade"] for it in itens_processados)

            if total_rendimento > 0:
                preco_medio_ponderado = total_gasto / total_rendimento
            else:
                preco_medio_ponderado = 0.0

            st.html(f"""
            <div class="summary-card">
                <div class="summary-title">🎯 Preço Médio Ponderado Final</div>
                <div class="summary-highlight-val">R$ {preco_medio_ponderado:,.2f}</div>
                <div class="summary-unit-tag">Custo unitário por rendimento efetivo da composição</div>
                <div class="metric-row">
                    <span class="metric-row-label">💵 Custo Total Gasto:</span>
                    <span class="metric-row-val" style="color: #34D399;">R$ {total_gasto:,.2f}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-row-label">⚖️ Rendimento Efetivo Total:</span>
                    <span class="metric-row-val" style="color: #A5B4FC;">{total_rendimento:,.3f}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-row-label">📦 Quantidade Física Total:</span>
                    <span class="metric-row-val">{total_volume_comprado:,.3f}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-row-label">🔢 Total de Itens no Cálculo:</span>
                    <span class="metric-row-val">{len(itens_processados)}</span>
                </div>
            </div>
            """)

            st.markdown("<br>", unsafe_allow_html=True)

            with st.container(border=True):
                st.markdown("###### 💾 Registrar na Nota Fiscal")
                nomes_produtos = list(set(it["descricao"] for it in itens_processados))
                cod_sugerido = itens_processados[0]["codigo"] if len(itens_processados) > 0 else 0

                if len(nomes_produtos) == 1:
                    desc_sugerida = nomes_produtos[0]
                else:
                    desc_sugerida = f"MIX: {' + '.join([n.replace('MP ', '').replace('(LANCH)', '').strip() for n in nomes_produtos[:3]])}"

                nome_registro = st.text_input("Descrição do Item para a Nota Fiscal:", value=desc_sugerida)

                if st.button("💾 Salvar na Lista da Nota Fiscal", type="primary", use_container_width=True):
                    if total_rendimento <= 0 or total_gasto <= 0:
                        st.error("Preencha ao menos uma quantidade e custo unitário maiores que zero.")
                    else:
                        sucesso, msg = data_manager.add_item_nota(
                            codigo=cod_sugerido,
                            descricao=nome_registro.strip(),
                            quantidade=total_rendimento,
                            valor_unitario=preco_medio_ponderado,
                            valor_total=total_gasto
                        )
                        if sucesso:
                            st.toast(f"✅ '{nome_registro}' registrado com sucesso na Nota Fiscal!", icon="💾")
                            st.success(f"**Sucesso:** Registrado com Preço Médio de `R$ {preco_medio_ponderado:,.2f}` e Total de `R$ {total_gasto:,.2f}`.")
                        else:
                            st.error(msg)

# ==============================================================================
# MÓDULO 4: CATÁLOGO DE PRODUTOS, FATORES & CUSTOS PADRÃO
# ==============================================================================
elif aba_selecionada == "📋 Catálogo de Produtos & Custos":
    st.markdown('<div class="app-badge">📋 GESTÃO DE CADASTROS & PRECIFICAÇÃO</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-title">Catálogo de Produtos, Custos & Fatores</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-subtitle">Gerencie o cadastro central de matérias-primas e cortes, atualize o Custo Padrão de referência e configure fatores de rendimento.</div>', unsafe_allow_html=True)

    tab_lista, tab_novo = st.tabs(["📋 Catálogo Geral de Produtos", "➕ Cadastrar Novo Produto / Corte"])

    with tab_lista:
        produtos_df = data_manager.get_produtos()

        col_pesq, col_kpi_total = st.columns([3, 2], vertical_alignment="bottom")
        with col_pesq:
            termo_pesquisa = st.text_input("🔍 Pesquisar no Catálogo:", "", placeholder="Digite a descrição ou código do produto...")

        with col_kpi_total:
            st.markdown(f"""
            <div style="background: #131B2A; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 10px; height: 42px; padding: 0 18px; display: flex; align-items: center; justify-content: flex-end;">
                <span style="font-size: 0.8rem; font-weight: 700; color: #94A3B8; text-transform: uppercase;">Itens Cadastrados:</span>
                <span style="font-family: 'Outfit', sans-serif; font-size: 1.25rem; font-weight: 800; color: #38BDF8; margin-left: 8px;">{len(produtos_df)} registros</span>
            </div>
            """, unsafe_allow_html=True)

        df_filtrado = produtos_df.copy()
        if termo_pesquisa.strip():
            termo = termo_pesquisa.strip().lower()
            df_filtrado = df_filtrado[
                df_filtrado["descricao"].str.lower().str.contains(termo, na=False) |
                df_filtrado["codigo"].astype(str).str.contains(termo, na=False)
            ]

        edited_produtos = st.data_editor(
            df_filtrado,
            key="editor_produtos",
            use_container_width=True,
            column_config={
                "id": st.column_config.NumberColumn("ID", disabled=True, width="small"),
                "codigo": st.column_config.NumberColumn("Código", step=1, format="%d", width="small"),
                "descricao": st.column_config.TextColumn("Descrição do Produto / Corte", width="large"),
                "unidade": st.column_config.SelectboxColumn("Unidade", options=["UN", "KG", "L", "CX", "PCT", "G"], width="small"),
                "fator_conversao": st.column_config.NumberColumn("Fator de Rendimento", step=0.005, format="%.4f"),
                "custo_padrao": st.column_config.NumberColumn("✍️ Custo Unitário Padrão (R$)", step=0.01, format="R$ %.2f", help="Custo unitário de referência utilizado na Gestão de Caixaria"),
            },
            hide_index=True
        )

        col_salvar_edicao, _ = st.columns([2, 3])
        with col_salvar_edicao:
            if st.button("💾 Salvar Alterações no Catálogo", type="primary", use_container_width=True):
                alteracoes_salvas = 0
                for _, row in edited_produtos.iterrows():
                    sucesso, _ = data_manager.update_produto(
                        id_prod=int(row['id']),
                        codigo=int(row['codigo']),
                        descricao=str(row['descricao']),
                        unidade=str(row['unidade']),
                        fator_conversao=float(row['fator_conversao']),
                        custo_padrao=float(row.get('custo_padrao', 0.0)),
                    )
                    if sucesso:
                        alteracoes_salvas += 1
                st.toast(f"✅ {alteracoes_salvas} registro(s) atualizado(s) com sucesso!", icon="💾")
                st.rerun()

        st.divider()
        st.markdown("##### 🗑️ Remover Produto do Catálogo")
        col_sel_del, col_btn_del = st.columns([4, 1], vertical_alignment="bottom")
        with col_sel_del:
            prod_para_excluir = st.selectbox(
                "Selecione o registro para exclusão:",
                options=produtos_df["descricao"].tolist(),
                key="select_del_prod"
            )
        with col_btn_del:
            if st.button("🗑️ Excluir", type="secondary", use_container_width=True):
                id_excluir = int(produtos_df[produtos_df["descricao"] == prod_para_excluir]["id"].values[0])
                sucesso, msg = data_manager.delete_produto(id_excluir)
                if sucesso:
                    st.toast(msg, icon="🗑️")
                    st.rerun()
                else:
                    st.error(msg)

    with tab_novo:
        st.markdown("##### Novo Registro de Produto, Matéria-Prima ou Corte")
        with st.form("form_novo_produto", clear_on_submit=True):
            col_cod_n, col_desc_n = st.columns([1, 3], vertical_alignment="bottom")
            with col_cod_n:
                novo_cod = st.number_input("Código Interno / ERP:", min_value=1, step=1, value=10001)
            with col_desc_n:
                novo_desc = st.text_input("Descrição do Produto:", placeholder="Ex: ALCATRA BOVINA KG ou MP LEITE CONDENSADO")

            col_unid_n, col_fator_n, col_custo_n = st.columns([1, 1, 1], vertical_alignment="bottom")
            with col_unid_n:
                novo_unid = st.selectbox("Unidade de Medida:", options=["KG", "UN", "L", "CX", "PCT", "G"])
            with col_fator_n:
                novo_fator = st.number_input(
                    "Fator de Conversão Padrão:",
                    min_value=0.0001,
                    value=1.0,
                    step=0.05,
                    format="%.4f",
                    help="Multiplicador técnico de rendimento (utilize 1.0000 quando não houver fator específico)"
                )
            with col_custo_n:
                novo_custo_pad_in = st.number_input(
                    "Custo Unitário Padrão (R$):",
                    min_value=0.0,
                    value=None,
                    step=0.01,
                    format="%.2f",
                    placeholder="Ex: 38,93",
                    help="Custo unitário de referência utilizado nas operações de Caixaria"
                )
                novo_custo_pad = float(novo_custo_pad_in or 0.0)

            btn_cadastrar = st.form_submit_button("Cadastrar no Catálogo", type="primary")

            if btn_cadastrar:
                if not novo_desc.strip():
                    st.error("A descrição do produto é obrigatória.")
                else:
                    sucesso, msg = data_manager.add_produto(
                        codigo=novo_cod,
                        descricao=novo_desc,
                        unidade=novo_unid,
                        fator_conversao=novo_fator,
                        custo_padrao=novo_custo_pad,
                    )
                    if sucesso:
                        st.toast(f"✅ Produto '{novo_desc}' cadastrado com sucesso!", icon="✨")
                        st.success(f"**Sucesso:** `{novo_desc}` registrado no catálogo.")
                    else:
                        st.error(msg)

# ==============================================================================
# MÓDULO 5: CONSOLIDAÇÃO DE NOTA FISCAL
# ==============================================================================
elif aba_selecionada == "📑 Consolidação de Nota Fiscal":
    st.markdown('<div class="app-badge">📑 FECHAMENTO & CONSOLIDAÇÃO FINANCEIRA</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-title">Consolidação de Itens para Nota Fiscal</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-subtitle">Conferência de volumes, custos médios unitários e exportação gerencial em Excel (.xlsx) ou CSV.</div>', unsafe_allow_html=True)

    df_nota = data_manager.get_nota_fiscal()

    if df_nota.empty:
        st.info("Nenhum lançamento consolidado até o momento. Utilize a 'Calculadora de Preço Médio' ou 'Rendimento & Desossa' para registrar itens.")
    else:
        total_itens = len(df_nota)
        valor_total_nota = float(df_nota["valor_total"].sum())
        quantidade_total = float(df_nota["quantidade"].sum())

        m1, m2, m3 = st.columns(3)
        with m1:
            with st.container(border=True):
                st.metric("Total de Lançamentos", total_itens)

        with m2:
            with st.container(border=True):
                st.metric("Volume Total Consolidado", f"{quantidade_total:,.3f}")

        with m3:
            with st.container(border=True):
                st.metric("💰 Valor Total Consolidado", f"R$ {valor_total_nota:,.2f}")

        st.markdown("<br>", unsafe_allow_html=True)

        df_exibicao = df_nota.copy()
        df_exibicao["valor_unitario"] = df_exibicao["valor_unitario"].apply(lambda v: f"R$ {v:,.2f}")
        df_exibicao["valor_total"] = df_exibicao["valor_total"].apply(lambda v: f"R$ {v:,.2f}")
        df_exibicao["quantidade"] = df_exibicao["quantidade"].apply(lambda v: f"{v:,.3f}")

        st.dataframe(
            df_exibicao[["id", "codigo", "descricao", "quantidade", "valor_unitario", "valor_total", "data_registro"]],
            use_container_width=True,
            column_config={
                "id": st.column_config.NumberColumn("Nº", width="small"),
                "codigo": st.column_config.NumberColumn("Código", width="small"),
                "descricao": st.column_config.TextColumn("Descrição do Produto"),
                "quantidade": st.column_config.TextColumn("Volume Apurado"),
                "valor_unitario": st.column_config.TextColumn("Custo Médio Unit."),
                "valor_total": st.column_config.TextColumn("Valor Total (R$)"),
                "data_registro": st.column_config.TextColumn("Data / Hora")
            },
            hide_index=True
        )

        st.divider()

        col_down_excel, col_down_csv, col_limpar = st.columns([2, 2, 2])

        with col_down_excel:
            excel_bytes = data_manager.export_all_to_excel()
            st.download_button(
                label="📥 Exportar Relatório Excel (.xlsx)",
                data=excel_bytes,
                file_name="Consolidacao_Nota_Fiscal.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
                use_container_width=True
            )

        with col_down_csv:
            csv_bytes = df_nota.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Exportar Arquivo CSV",
                data=csv_bytes,
                file_name="Consolidacao_Nota_Fiscal.csv",
                mime="text/csv",
                use_container_width=True
            )

        with col_limpar:
            if st.button("🗑️ Limpar Consolidação", type="secondary", use_container_width=True):
                sucesso, msg = data_manager.clear_nota_fiscal()
                if sucesso:
                    st.toast(msg, icon="🗑️")
                    st.rerun()
                else:
                    st.error(msg)

# ==============================================================================
# MÓDULO 6: BACKUP & SINCRONIZAÇÃO
# ==============================================================================
elif aba_selecionada == "☁️ Backup & Sincronização":
    st.markdown('<div class="app-badge">☁️ SEGURANÇA DE DADOS & SINCRONIZAÇÃO</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-title">Backup Gerencial & Sincronização em Nuvem</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-subtitle">Exporte cópias completas do catálogo e movimentações ou sincronize planilhas em lote com o banco de dados.</div>', unsafe_allow_html=True)

    col_bkp_down, col_bkp_up = st.columns(2)

    with col_bkp_down:
        with st.container(border=True):
            st.markdown("#### 📤 Exportar Backup Completo")
            st.caption("Gera um arquivo Excel (.xlsx) contendo todo o catálogo de produtos, custos, fatores e a consolidação atual.")
            dados_excel = data_manager.export_all_to_excel()
            st.download_button(
                label="Baixar Backup Completo (.xlsx)",
                data=dados_excel,
                file_name="Backup_Gerencial_Supermercado_Jean.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
                use_container_width=True
            )

    with col_bkp_up:
        with st.container(border=True):
            st.markdown("#### 📥 Importar / Sincronizar Catálogo")
            st.caption("Carregue uma planilha Excel (.xlsx) para atualizar produtos, custos padrão ou fatores de conversão em lote.")
            arquivo_up = st.file_uploader("Selecione o arquivo .xlsx:", type=["xlsx"])
            if arquivo_up is not None:
                if st.button("Importar e Sincronizar", use_container_width=True):
                    sucesso, msg = data_manager.import_backup_excel(arquivo_up.read())
                    if sucesso:
                        st.toast(msg, icon="✅")
                        st.success(f"**Sucesso:** {msg}")
                        st.rerun()
                    else:
                        st.error(msg)
