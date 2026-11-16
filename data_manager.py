import sqlite3
import os
import io
import pandas as pd
import openpyxl
import requests

DB_FILE = "database.db"
EXCEL_ORIGINAL = "Preço_Médio.xlsm"

FATORES_PADRAO_MAP = {
    "MARACUJA": 0.875,
    "MANGA": 0.875,
    "GOIABA": 2.5,
    "ABACAXI": 0.5,
    "MORANGO": 0.25,
    "CAFE": 5.0,
    "CAFÉ": 5.0,
    "ESCURETO": 20.0,
    "BIS": 16.0,
    "POLPA": 0.8,
    "PAO FORMA": 20.0,
    "PÃO FORMA": 20.0,
}

ITENS_ADICIONAIS = [
    (4416, 'ALCATRA KG', 'KG', 1.0),
    (3377, 'ARANHA KG', 'KG', 1.0),
    (5670, 'BIFE DE 1', 'KG', 1.0),
    (5709, 'BUCHO BOVINO KG', 'KG', 1.0),
    (6030, 'CARNE MOIDA', 'KG', 1.0),
    (9960, 'CONTRA FILÉ BIFE DE CHORIZO KG', 'KG', 1.0),
    (3379, 'CONTRA FILE KG', 'KG', 1.0),
    (3366, 'COSTELA PONTA DE AGULHA KG', 'KG', 1.0),
    (3376, 'COXAO DURO KG', 'KG', 1.0),
    (2699, 'COXAO MOLE KG', 'KG', 1.0),
    (4326, 'DIANTEIRO', 'KG', 1.0),
    (2669, 'FIGADO BOVINO KG', 'KG', 1.0),
    (3361, 'FRALDINHA KG', 'KG', 1.0),
    (3329, 'LAGARTO KG', 'KG', 1.0),
    (5716, 'MAMINHA MASTERBOI KG', 'KG', 1.0),
    (6028, 'MAO DE VACA', 'KG', 1.0),
    (4342, 'MOCOTO BOVINO KG', 'KG', 1.0),
    (6051, 'OSSADA', 'KG', 1.0),
    (3373, 'PATINHO KG', 'KG', 1.0),
    (6032, 'PICADINHO KG', 'KG', 1.0),
    (4624, 'PICANHA BOVINA KG', 'KG', 1.0),
    (4327, 'TRASEIRO', 'KG', 1.0),
]


def get_supabase_credentials() -> tuple[str, str]:
    """Busca SUPABASE_URL e SUPABASE_KEY nas variáveis de ambiente ou no st.secrets."""
    url = os.environ.get("SUPABASE_URL", "").strip()
    key = os.environ.get("SUPABASE_KEY", "").strip()
    if url and key:
        return url.rstrip("/"), key
    try:
        import streamlit as st
        url = str(st.secrets.get("SUPABASE_URL", "")).strip()
        key = str(st.secrets.get("SUPABASE_KEY", "")).strip()
        if url and key:
            return url.rstrip("/"), key
    except Exception:
        pass
    return "", ""


def is_supabase_rest() -> bool:
    url, key = get_supabase_credentials()
    return bool(url and key)


def is_supabase_configured() -> bool:
    return is_supabase_rest()


def _rest_headers(prefer: str = "") -> dict:
    _, key = get_supabase_credentials()
    h = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    if prefer:
        h["Prefer"] = prefer
    return h


def get_connection():
    """Retorna conexão com SQLite local (fallback quando Supabase não está configurado)."""
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Inicializa as tabelas locais (e sincroniza caso Supabase REST esteja ativo)."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo INTEGER NOT NULL,
            descricao TEXT NOT NULL UNIQUE,
            unidade TEXT NOT NULL,
            fator_conversao REAL NOT NULL DEFAULT 1.0,
            custo_padrao REAL NOT NULL DEFAULT 0.0
        )
    """)
    try:
        cursor.execute("ALTER TABLE produtos ADD COLUMN custo_padrao REAL NOT NULL DEFAULT 0.0")
    except Exception:
        pass
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS nota_fiscal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo INTEGER,
            descricao TEXT NOT NULL,
            quantidade REAL NOT NULL,
            valor_unitario REAL NOT NULL,
            valor_total REAL NOT NULL,
            data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM produtos")
    count_prod = cursor.fetchone()[0]

    if count_prod == 0 and os.path.exists(EXCEL_ORIGINAL):
        migrar_dados_excel(conn)

    conn.close()


def identificar_fator_padrao(descricao: str) -> float:
    desc_upper = descricao.upper()
    for chave, fator in FATORES_PADRAO_MAP.items():
        if chave in desc_upper:
            return float(fator)
    return 1.0


def migrar_dados_excel(conn):
    """Importa os 144 produtos e os itens já registrados na planilha original."""
    try:
        wb = openpyxl.load_workbook(EXCEL_ORIGINAL, data_only=True)
        cursor = conn.cursor()

        if "Produtos" in wb.sheetnames:
            ws_prod = wb["Produtos"]
            produtos_para_inserir = []
            for r in range(2, ws_prod.max_row + 1):
                desc = ws_prod.cell(r, 1).value
                emb = ws_prod.cell(r, 2).value
                cod = ws_prod.cell(r, 3).value
                if desc and cod is not None:
                    desc_str = str(desc).strip()
                    emb_str = str(emb).strip() if emb else "UN"
                    cod_int = int(cod)
                    fator = identificar_fator_padrao(desc_str)
                    produtos_para_inserir.append((cod_int, desc_str, emb_str, fator))

            todos_produtos = produtos_para_inserir + list(ITENS_ADICIONAIS)
            cursor.executemany("""
                INSERT OR IGNORE INTO produtos (codigo, descricao, unidade, fator_conversao)
                VALUES (?, ?, ?, ?)
            """, todos_produtos)

        if "Calculadora" in wb.sheetnames:
            ws_calc = wb["Calculadora"]
            itens_nota = []
            for r in range(7, 45):
                cod = ws_calc.cell(r, 11).value
                desc = ws_calc.cell(r, 12).value
                qtd = ws_calc.cell(r, 13).value
                v_unid = ws_calc.cell(r, 14).value
                v_total = ws_calc.cell(r, 15).value

                if desc and str(desc).strip() != "":
                    try:
                        cod_val = int(cod) if cod is not None else None
                        qtd_val = float(qtd) if qtd is not None else 0.0
                        v_unid_val = float(v_unid) if v_unid is not None else 0.0
                        v_total_val = float(v_total) if v_total is not None else (qtd_val * v_unid_val)
                        itens_nota.append((cod_val, str(desc).strip(), qtd_val, v_unid_val, v_total_val))
                    except (ValueError, TypeError):
                        pass

            if itens_nota:
                cursor.executemany("""
                    INSERT INTO nota_fiscal (codigo, descricao, quantidade, valor_unitario, valor_total)
                    VALUES (?, ?, ?, ?, ?)
                """, itens_nota)

        conn.commit()
    except Exception as e:
        print(f"Erro ao migrar dados: {e}")


# ==============================================================================
# OPERAÇÕES DE PRODUTOS (DIRETO NO TABLE EDITOR DO SUPABASE QUANDO CONFIGURADO)
# ==============================================================================

def get_produtos() -> pd.DataFrame:
    if is_supabase_rest():
        url, _ = get_supabase_credentials()
        try:
            r = requests.get(
                f"{url}/rest/v1/produtos?select=id,codigo,descricao,unidade,fator_conversao,custo_padrao&order=descricao.asc",
                headers=_rest_headers(),
                timeout=8,
            )
            if r.status_code == 200:
                rows = r.json()
                if rows:
                    df = pd.DataFrame(rows)
                    if "custo_padrao" not in df.columns:
                        df["custo_padrao"] = 0.0
                    return df
                return pd.DataFrame(columns=["id", "codigo", "descricao", "unidade", "fator_conversao", "custo_padrao"])
        except Exception as e:
            print(f"Aviso Supabase get_produtos: {e}")

    conn = get_connection()
    df = pd.read_sql_query("SELECT id, codigo, descricao, unidade, fator_conversao, COALESCE(custo_padrao, 0.0) AS custo_padrao FROM produtos ORDER BY descricao ASC", conn)
    conn.close()
    return df


def add_produto(codigo: int, descricao: str, unidade: str, fator_conversao: float, custo_padrao: float = 0.0) -> tuple[bool, str]:
    payload = {
        "codigo": int(codigo),
        "descricao": descricao.strip(),
        "unidade": unidade.strip().upper(),
        "fator_conversao": float(fator_conversao),
        "custo_padrao": float(custo_padrao),
    }
    if is_supabase_rest():
        url, _ = get_supabase_credentials()
        try:
            r = requests.post(
                f"{url}/rest/v1/produtos",
                headers=_rest_headers("return=representation"),
                json=payload,
                timeout=8,
            )
            if r.status_code in (200, 201):
                return True, "Produto cadastrado no Supabase Table Editor com sucesso!"
            if r.status_code == 409 or "duplicate" in r.text.lower():
                return False, "Já existe um produto com esta descrição."
            return False, f"Erro ao cadastrar no Supabase: {r.text}"
        except Exception as e:
            return False, f"Erro de conexão com Supabase: {e}"

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO produtos (codigo, descricao, unidade, fator_conversao, custo_padrao)
            VALUES (?, ?, ?, ?, ?)
        """, (payload["codigo"], payload["descricao"], payload["unidade"], payload["fator_conversao"], payload["custo_padrao"]))
        conn.commit()
        return True, "Produto cadastrado com sucesso!"
    except Exception as e:
        return False, f"Erro ao cadastrar produto: {e}"
    finally:
        conn.close()


def update_produto(id_prod: int, codigo: int, descricao: str, unidade: str, fator_conversao: float, custo_padrao: float = 0.0) -> tuple[bool, str]:
    payload = {
        "codigo": int(codigo),
        "descricao": descricao.strip(),
        "unidade": unidade.strip().upper(),
        "fator_conversao": float(fator_conversao),
        "custo_padrao": float(custo_padrao),
    }
    if is_supabase_rest():
        url, _ = get_supabase_credentials()
        try:
            r = requests.patch(
                f"{url}/rest/v1/produtos?id=eq.{int(id_prod)}",
                headers=_rest_headers(),
                json=payload,
                timeout=8,
            )
            if r.status_code in (200, 204):
                return True, "Produto atualizado com sucesso!"
            return False, f"Erro ao atualizar no Supabase: {r.text}"
        except Exception as e:
            return False, f"Erro de conexão com Supabase: {e}"

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE produtos
            SET codigo = ?, descricao = ?, unidade = ?, fator_conversao = ?, custo_padrao = ?
            WHERE id = ?
        """, (payload["codigo"], payload["descricao"], payload["unidade"], payload["fator_conversao"], payload["custo_padrao"], int(id_prod)))
        conn.commit()
        return True, "Produto atualizado com sucesso!"
    except Exception as e:
        return False, f"Erro ao atualizar produto: {e}"
    finally:
        conn.close()


def update_custo_padrao_por_codigo(codigo: int, custo_padrao: float):
    """Atualiza o custo_padrao de um produto no catálogo pelo seu código."""
    if is_supabase_rest():
        url, _ = get_supabase_credentials()
        try:
            requests.patch(
                f"{url}/rest/v1/produtos?codigo=eq.{int(codigo)}",
                headers=_rest_headers(),
                json={"custo_padrao": float(custo_padrao)},
                timeout=6,
            )
        except Exception:
            pass
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE produtos SET custo_padrao = ? WHERE codigo = ?", (float(custo_padrao), int(codigo)))
        conn.commit()
    except Exception:
        pass
    finally:
        conn.close()


def delete_produto(id_prod: int) -> tuple[bool, str]:
    if is_supabase_rest():
        url, _ = get_supabase_credentials()
        try:
            r = requests.delete(
                f"{url}/rest/v1/produtos?id=eq.{int(id_prod)}",
                headers=_rest_headers(),
                timeout=8,
            )
            if r.status_code in (200, 204):
                return True, "Produto excluído com sucesso!"
            return False, f"Erro ao excluir no Supabase: {r.text}"
        except Exception as e:
            return False, f"Erro de conexão com Supabase: {e}"

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM produtos WHERE id = ?", (int(id_prod),))
        conn.commit()
        return True, "Produto excluído com sucesso!"
    except Exception as e:
        return False, f"Erro ao excluir produto: {e}"
    finally:
        conn.close()


# ==============================================================================
# OPERAÇÕES DE NOTA FISCAL (DIRETO NO TABLE EDITOR DO SUPABASE)
# ==============================================================================

def get_nota_fiscal() -> pd.DataFrame:
    if is_supabase_rest():
        url, _ = get_supabase_credentials()
        try:
            r = requests.get(
                f"{url}/rest/v1/nota_fiscal?select=id,codigo,descricao,quantidade,valor_unitario,valor_total,data_registro&order=id.asc",
                headers=_rest_headers(),
                timeout=8,
            )
            if r.status_code == 200:
                rows = r.json()
                if rows:
                    return pd.DataFrame(rows)
                return pd.DataFrame(columns=["id", "codigo", "descricao", "quantidade", "valor_unitario", "valor_total", "data_registro"])
        except Exception as e:
            print(f"Aviso Supabase get_nota_fiscal: {e}")

    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT id, codigo, descricao, quantidade, valor_unitario, valor_total, data_registro
        FROM nota_fiscal
        ORDER BY id ASC
    """, conn)
    conn.close()
    return df


def add_item_nota(codigo: int, descricao: str, quantidade: float, valor_unitario: float, valor_total: float) -> tuple[bool, str]:
    payload = {
        "codigo": int(codigo) if codigo is not None else None,
        "descricao": descricao.strip(),
        "quantidade": float(quantidade),
        "valor_unitario": float(valor_unitario),
        "valor_total": float(valor_total),
    }
    if is_supabase_rest():
        url, _ = get_supabase_credentials()
        try:
            r = requests.post(
                f"{url}/rest/v1/nota_fiscal",
                headers=_rest_headers(),
                json=payload,
                timeout=8,
            )
            if r.status_code in (200, 201):
                return True, "Item salvo na nota fiscal (Supabase) com sucesso!"
            return False, f"Erro ao salvar no Supabase: {r.text}"
        except Exception as e:
            return False, f"Erro de conexão com Supabase: {e}"

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO nota_fiscal (codigo, descricao, quantidade, valor_unitario, valor_total)
            VALUES (?, ?, ?, ?, ?)
        """, (payload["codigo"], payload["descricao"], payload["quantidade"], payload["valor_unitario"], payload["valor_total"]))
        conn.commit()
        return True, "Item salvo na nota fiscal com sucesso!"
    except Exception as e:
        return False, f"Erro ao salvar item: {e}"
    finally:
        conn.close()


def delete_item_nota(id_item: int) -> tuple[bool, str]:
    if is_supabase_rest():
        url, _ = get_supabase_credentials()
        try:
            r = requests.delete(
                f"{url}/rest/v1/nota_fiscal?id=eq.{int(id_item)}",
                headers=_rest_headers(),
                timeout=8,
            )
            if r.status_code in (200, 204):
                return True, "Item removido com sucesso!"
            return False, f"Erro ao remover no Supabase: {r.text}"
        except Exception as e:
            return False, f"Erro de conexão com Supabase: {e}"

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM nota_fiscal WHERE id = ?", (int(id_item),))
        conn.commit()
        return True, "Item removido com sucesso!"
    except Exception as e:
        return False, f"Erro ao remover item: {e}"
    finally:
        conn.close()


def clear_nota_fiscal() -> tuple[bool, str]:
    if is_supabase_rest():
        url, _ = get_supabase_credentials()
        try:
            # PostgREST requires a filter on DELETE
            r = requests.delete(
                f"{url}/rest/v1/nota_fiscal?id=gt.0",
                headers=_rest_headers(),
                timeout=8,
            )
            if r.status_code in (200, 204):
                return True, "Nota fiscal limpa com sucesso!"
            return False, f"Erro ao limpar no Supabase: {r.text}"
        except Exception as e:
            return False, f"Erro de conexão com Supabase: {e}"

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM nota_fiscal")
        conn.commit()
        return True, "Nota fiscal limpa com sucesso!"
    except Exception as e:
        return False, f"Erro ao limpar nota fiscal: {e}"
    finally:
        conn.close()


# --- Backup e Exportação / Importação ---

def export_all_to_excel() -> bytes:
    df_prod = get_produtos()
    df_nota = get_nota_fiscal()

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_prod.to_excel(writer, sheet_name='Produtos_Fatores', index=False)
        df_nota.to_excel(writer, sheet_name='Nota_Fiscal', index=False)

    return output.getvalue()


def import_backup_excel(file_bytes: bytes) -> tuple[bool, str]:
    try:
        excel_file = io.BytesIO(file_bytes)
        xls = pd.ExcelFile(excel_file)

        if 'Produtos_Fatores' in xls.sheet_names:
            df = pd.read_excel(xls, 'Produtos_Fatores')
            lote = []
            for _, row in df.iterrows():
                cod = int(row.get('codigo', 0))
                desc = str(row.get('descricao', '')).strip()
                unid = str(row.get('unidade', 'UN')).strip().upper()
                fator = float(row.get('fator_conversao', 1.0))
                if desc:
                    lote.append({
                        "codigo": cod,
                        "descricao": desc,
                        "unidade": unid,
                        "fator_conversao": fator,
                    })

            if is_supabase_rest() and lote:
                url, _ = get_supabase_credentials()
                requests.post(
                    f"{url}/rest/v1/produtos?on_conflict=descricao",
                    headers=_rest_headers("resolution=merge-duplicates"),
                    json=lote,
                    timeout=10,
                )
            elif lote:
                conn = get_connection()
                cursor = conn.cursor()
                for item in lote:
                    cursor.execute("""
                        INSERT INTO produtos (codigo, descricao, unidade, fator_conversao)
                        VALUES (?, ?, ?, ?)
                        ON CONFLICT(descricao) DO UPDATE SET
                            codigo = excluded.codigo,
                            unidade = excluded.unidade,
                            fator_conversao = excluded.fator_conversao
                    """, (item["codigo"], item["descricao"], item["unidade"], item["fator_conversao"]))
                conn.commit()
                conn.close()

        return True, "Backup importado e sincronizado com sucesso!"
    except Exception as e:
        return False, f"Erro ao importar backup: {e}"
