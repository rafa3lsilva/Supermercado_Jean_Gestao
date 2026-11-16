import sqlite3
import json
import re
import io
from datetime import datetime
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
import data_manager

DB_FILE = "database.db"


def get_connection():
    return data_manager.get_connection()


def parse_pesagens(texto) -> tuple[float, int, list[float], str]:
    """
    Converte uma string de pesagens (ex: '=12.67+6.305+10,95' ou '12,67 6,305 10,95')
    em: (soma_total, qtd_pesagens, lista_de_pesos, string_normalizada).
    """
    if texto is None:
        return 0.0, 0, [], ""
    if isinstance(texto, (int, float)):
        val = float(texto)
        if val == 0:
            return 0.0, 0, [], ""
        return round(val, 3), 1, [round(val, 3)], f"{val:.3f}".rstrip("0").rstrip(".")

    s = str(texto).strip()
    if not s:
        return 0.0, 0, [], ""

    if s.startswith("="):
        s = s[1:].strip()

    # Substitui vírgula decimal por ponto quando estiver entre dígitos
    s_clean = re.sub(r"(\d),(\d)", r"\1.\2", s)
    # Divide por +, espaço, ponto-e-vírgula, barra ou quebra de linha
    tokens = re.split(r"[+\s;/\n\r\t]+", s_clean)
    pesos = []
    for tok in tokens:
        tok = tok.strip()
        if not tok:
            continue
        try:
            v = float(tok)
            if v != 0:
                pesos.append(round(v, 3))
        except ValueError:
            pass

    total = round(sum(pesos), 3)
    norm_str = " + ".join(f"{p:g}" for p in pesos)
    return total, len(pesos), pesos, norm_str


def append_pesagem(texto_atual: str, novo_peso) -> str:
    """Adiciona uma ou mais novas pesagens (float ou string) à string existente."""
    _, _, pesos_atuais, _ = parse_pesagens(texto_atual)
    _, _, novos_pesos, _ = parse_pesagens(novo_peso)
    pesos_atuais.extend(novos_pesos)
    return " + ".join(f"{p:g}" for p in pesos_atuais)


def zerar_todos_os_pesos(state: dict) -> dict:
    """
    Zera todas as pesagens, pesos de entrada e perdas de todas as abas para iniciar
    um novo fechamento do zero, preservando os cortes cadastrados e os Preços de Venda (R$ VENDA).
    """
    for _, peca in state.get("desossas", {}).items():
        peca["peso_peca_str"] = ""
        peca["perda_apontada_str"] = ""
        peca["notas"] = ""
        for c in peca.get("cortes", []):
            c["pesagens"] = ""

    for cod_k, ext in state.get("bovino_extras_traseiro", {}).items():
        ext["peso"] = 0.0

    for _, rec in state.get("receitas", {}).items():
        rec["rendimento_str"] = ""
        for ing in rec.get("ingredientes", []):
            ing["pesagens"] = ""

    cx = state.get("caixaria", {})
    for p in cx.get("perdas_custos", []):
        p["pesagens_perda"] = ""
    for s in cx.get("saidas", []):
        s["pesagens_saida"] = ""
    for e in cx.get("entradas", []):
        e["pesagens_entrada"] = ""

    for a in state.get("anotacoes", []):
        a["pesagens"] = ""

    save_state(state)
    return state


# ==============================================================================
# ESTADO INICIAL EXTRAÍDO FIELMENTE DE RENDIMENTO_ATUAL.xlsm
# ==============================================================================

def get_default_state() -> dict:
    return {
        "desossas": {
            "DIANTEIRO": {
                "titulo": "DIANTEIRO (Boi Casado)",
                "peca_nome": "DIANTEIRO",
                "codigo_peca": 4326,
                "peso_peca_str": "211.1",
                "custo_kg": 24.12,
                "notas": "16774",
                "perda_apontada_str": "6.455 + 9.045 + 0.646 + 12.8",
                "cortes": [
                    {"codigo": 6025, "corte": "PEITO BOVINO", "pesagens": "9.785 + 11.435", "preco_venda": 35.90},
                    {"codigo": 6022, "corte": "LOMBO BOVINO", "pesagens": "8.92 + 17.8", "preco_venda": 35.80},
                    {"codigo": 6029, "corte": "CARRE PAULISTA", "pesagens": "8.175 + 7.275 + 7.294", "preco_venda": 33.90},
                    {"codigo": 3375, "corte": "CUPIM", "pesagens": "2.786", "preco_venda": 48.50},
                    {"codigo": 34654, "corte": "MIOLO ACEM S/OSSO", "pesagens": "2.878 + 6.72", "preco_venda": 38.90},
                    {"codigo": 34656, "corte": "PONTA DO PEITO S/OSSO", "pesagens": "3.54", "preco_venda": 38.90},
                    {"codigo": 6032, "corte": "PICADINHO", "pesagens": "9.05 + 2.362 + 4.84 + 4.412", "preco_venda": 44.50},
                    {"codigo": 6030, "corte": "CARNE MOIDA", "pesagens": "6.16 + 1.3 + 6.82", "preco_venda": 31.50},
                    {"codigo": 6028, "corte": "MAO DE VACA", "pesagens": "6.905 + 13.375", "preco_venda": 33.90},
                    {"codigo": 5670, "corte": "BIFE DE 1", "pesagens": "7.05 + 5.388 + 1.648 + 5.688", "preco_venda": 45.50},
                    {"codigo": 6051, "corte": "OSSADA", "pesagens": "2.982 + 3.792 + 7.53", "preco_venda": 11.80},
                ],
            },
            "TRASEIRO": {
                "titulo": "TRASEIRO (Boi Casado)",
                "peca_nome": "TRASEIRO",
                "codigo_peca": 4327,
                "peso_peca_str": "304.6",
                "custo_kg": 26.43,
                "notas": "16774",
                "perda_apontada_str": "8.595 + 25.36 + 27.62",
                "cortes": [
                    {"codigo": 6032, "corte": "PICADINHO", "pesagens": "5.04 + 6.385", "preco_venda": 44.50},
                    {"codigo": 6030, "corte": "CARNE MOIDA", "pesagens": "6.39 + 3.676 + 10.38", "preco_venda": 31.50},
                    {"codigo": 6028, "corte": "MAO DE VACA", "pesagens": "4.492 + 8.915", "preco_venda": 33.90},
                    {"codigo": 5670, "corte": "BIFE DE 1", "pesagens": "1.982", "preco_venda": 45.50},
                    {"codigo": 6051, "corte": "OSSADA", "pesagens": "10.725 + 9.815", "preco_venda": 11.80},
                    {"codigo": 3376, "corte": "COXAO DURO", "pesagens": "7.756 + 3.09 + 10.11 + 6.875", "preco_venda": 45.50},
                    {"codigo": 4416, "corte": "ALCATRA", "pesagens": "5.08 + 9.89", "preco_venda": 55.50},
                    {"codigo": 3379, "corte": "CONTRA FILE", "pesagens": "3.926 + 6.25 + 11.315 + 5.942", "preco_venda": 56.90},
                    {"codigo": 3381, "corte": "FILE MIGNON", "pesagens": "2.704 + 5.23", "preco_venda": 64.90},
                    {"codigo": 4624, "corte": "PICANHA", "pesagens": "2.688 + 4.674", "preco_venda": 75.90},
                    {"codigo": 3378, "corte": "MAMINHA", "pesagens": "2.19 + 3.75", "preco_venda": 59.90},
                    {"codigo": 2699, "corte": "COXAO MOLE", "pesagens": "13.405 + 12.22", "preco_venda": 49.50},
                    {"codigo": 3373, "corte": "PATINHO", "pesagens": "7.295 + 7.465 + 5.814", "preco_venda": 49.50},
                    {"codigo": 3329, "corte": "LAGARTO", "pesagens": "3.565 + 5.508", "preco_venda": 46.50},
                    {"codigo": 3361, "corte": "FRALDINHA", "pesagens": "3.16 + 5.958", "preco_venda": 47.50},
                    {"codigo": 3944, "corte": "RABADA", "pesagens": "0.97 + 1.866", "preco_venda": 31.90},
                ],
            },
            "PONTA_AGULHA": {
                "titulo": "PONTA DE AGULHA (Boi Casado)",
                "peca_nome": "PA",
                "codigo_peca": 3366,
                "peso_peca_str": "67",
                "custo_kg": 20.98,
                "notas": "16774",
                "perda_apontada_str": "1.15 + 1.482 + 2.372",
                "cortes": [
                    {"codigo": 6032, "corte": "PICADINHO", "pesagens": "", "preco_venda": 44.50},
                    {"codigo": 6030, "corte": "CARNE MOIDA", "pesagens": "0.96 + 1.038 + 1.162", "preco_venda": 31.50},
                    {"codigo": 3366, "corte": "PONTA DE AGULHA", "pesagens": "18.3 + 18.28 + 20.56", "preco_venda": 28.60},
                ],
            },
            "DIANTEIRO_MASTERBOI": {
                "titulo": "DIANTEIRO MASTERBOI",
                "peca_nome": "DIANTEIRO MASTERBOI",
                "codigo_peca": 4326,
                "peso_peca_str": "527.4 + 478",
                "custo_kg": 24.12,
                "notas": "137073, 137766",
                "perda_apontada_str": "13.64 + 2.592 + 7.49 + 11.135 + 8.82 + 5.438 + 4.73 + 3.916 + 9.09 + 11.6 + 0.068 + 9.605 + 5.332 + 3.02 + 5.412 + 0.612 + 6.12 + 2.024 + 1.948 + 0.684",
                "cortes": [
                    {"codigo": 6025, "corte": "PEITO BOVINO", "pesagens": "15.64 + 17.69 + 14.97 + 16.65 + 15.02 + 6.785 + 7.1 + 18.43", "preco_venda": 35.90},
                    {"codigo": 6022, "corte": "LOMBO BOVINO", "pesagens": "15.28 + 16.98 + 19.05 + 15.78 + 15.25 + 9.215 + 14.545 + 13.295 + 15.84", "preco_venda": 35.80},
                    {"codigo": 6029, "corte": "CARRE PAULISTA", "pesagens": "9.965 + 4.698 + 10.015 + 10.53 + 6.505 + 15.97 + 4.426 + 4.828 + 3.93 + 11.62", "preco_venda": 33.90},
                    {"codigo": 3375, "corte": "CUPIM", "pesagens": "5.096 + 6.37 + 6.705 + 10.07 + 9.775 + 10.45", "preco_venda": 48.50},
                    {"codigo": 34654, "corte": "MIOLO ACEM S/OSSO", "pesagens": "4.244", "preco_venda": 38.90},
                    {"codigo": 34656, "corte": "PONTA DO PEITO S/OSSO", "pesagens": "", "preco_venda": 38.90},
                    {"codigo": 6032, "corte": "PICADINHO", "pesagens": "12.67 + 6.305 + 10.95 + 13.75 + 1.142 + 1.426 + 17.41 + 5.444 + 3.434 + 3.692 + 12.415 + 4.322 + 3.878 + 2.856 + 1.034 + 6.445 + 9.19 + 1.762 + 12.125 + 4.244 + 1.362", "preco_venda": 44.50},
                    {"codigo": 6030, "corte": "CARNE MOIDA", "pesagens": "6.47 + 6.41 + 9.055 + 6.05 + 1.53 + 0.57 + 6.995 + 5.446 + 3.384 + 1.822 + 1.314 + 6.605 + 1.984 + 10.815 + 7.065 + 3.78 + 2.852 + 3.154 + 6.825 + 1.83 + 7.635 + 1.26 + 1.06 + 5.246 + 0.86 + 0.882 + 5.978 + 1.684", "preco_venda": 31.50},
                    {"codigo": 6028, "corte": "MAO DE VACA", "pesagens": "11.105 + 11.375 + 24.17 + 10.925 + 5.904 + 4.908 + 5.044 + 5.25 + 11.895", "preco_venda": 33.90},
                    {"codigo": 5670, "corte": "BIFE DE 1", "pesagens": "11.63 + 4.764 + 12.195 + 9.965 + 11.755 + 2.356 + 15.21 + 1.382 + 6.24 + 5.308 + 9.595 + 9.94", "preco_venda": 45.50},
                    {"codigo": 6051, "corte": "OSSADA", "pesagens": "12.215 + 2.396 + 5.922 + 3.302", "preco_venda": 11.80},
                ],
            },
            "PA_MASTERBOI": {
                "titulo": "P. A. MASTERBOI",
                "peca_nome": "PA MASTERBOI",
                "codigo_peca": 3366,
                "peso_peca_str": "211.02 + 231.397 + 348.158 + 406.86",
                "custo_kg": 20.98,
                "notas": "135572, 135879, 137073, 137766",
                "perda_apontada_str": "1.018 + 1.875 + 3.694 + 4.04 + 2.695 + 3.292 + 2.976 + 5.606 + 2.23 + 6.565 + 20.3 + 1.704 + 0.998 + 2.79 + 1.53 + 2.482 + 2.576 + 6.405 + 3.258 + 1.504 + 1.892 + 2.114 + 1.166 + 1.3 + 1.632 + 4.594 + 3.924 + 3.406",
                "cortes": [
                    {"codigo": 6032, "corte": "PICADINHO", "pesagens": "2.63 + 1.21 + 2.298 + 3.044", "preco_venda": 44.50},
                    {"codigo": 6030, "corte": "CARNE MOIDA", "pesagens": "2.584 + 3.18 + 2.082 + 3.098 + 4.164 + 4.356 + 4.284 + 2.236 + 6.66 + 2.092 + 5.238 + 2.902 + 5.026 + 3.426 + 1.34 + 0.824 + 3.686 + 5.746 + 4.596 + 7.425 + 4.09 + 3.538 + 2.778 + 2.164 + 0.712 + 5.3 + 4.376 + 7.225", "preco_venda": 31.50},
                    {"codigo": 3366, "corte": "PONTA DE AGULHA", "pesagens": "22.18 + 11.16 + 14.48 + 24.98 + 20.97 + 12.83 + 22.36 + 11.44 + 10.86 + 17.82 + 21.24 + 11.625 + 24.48 + 10.775 + 25.38 + 20.53 + 1.666 + 11.405 + 19.95 + 19.86 + 20.68 + 9.055 + 21.2 + 24.14 + 10.825 + 27.82 + 20.11 + 13 + 23.48 + 22.72 + 25.02 + 11.33 + 23.55 + 24.33 + 9.9 + 17.2 + 16.1 + 10.06 + 21.87 + 21.01 + 22.91 + 25.6 + 23.61 + 24.12 + 12.265 + 27.21 + 20.53 + 20.34 + 8.685 + 23.25 + 22.27 + 11.72", "preco_venda": 28.60},
                ],
            },
            "SUINO": {
                "titulo": "SUÍNO (Carcaça)",
                "peca_nome": "PORCO",
                "codigo_peca": 5963,
                "peso_peca_str": "1457 + 951.55 + 806.8 + 1475.7",
                "custo_kg": 12.78,
                "notas": "12052, 765879, 766498, 308688",
                "perda_apontada_str": "41.108 + 12.428 + 5.016 + 1.076",
                "cortes": [
                    {"codigo": 5963, "corte": "PERNIL SUINO", "pesagens": "312.405 + 243.69 + 204 + 349.84", "preco_venda": 21.90},
                    {"codigo": 10543, "corte": "BISTECA SUINA", "pesagens": "24.738 + 64.7", "preco_venda": 19.90},
                    {"codigo": 3959, "corte": "PALETA SUINA", "pesagens": "188.235 + 121.36 + 100.9 + 180.219", "preco_venda": 16.90},
                    {"codigo": 3369, "corte": "COSTELA SUINA", "pesagens": "136.936 + 92.45 + 85.185 + 162.112", "preco_venda": 22.90},
                    {"codigo": 3453, "corte": "TOUCINHO", "pesagens": "198.416 + 117.523 + 130.727 + 190.237", "preco_venda": 9.50},
                    {"codigo": 3960, "corte": "COPA LOMBO", "pesagens": "196.878 + 119.892 + 117.238 + 186.414", "preco_venda": 21.90},
                    {"codigo": 6243, "corte": "REJEITO", "pesagens": "75.555 + 47.106 + 38.45 + 81.063", "preco_venda": 12.50},
                    {"codigo": 3504, "corte": "PANCETA", "pesagens": "122.116 + 84.828 + 77.711 + 117.876", "preco_venda": 16.90},
                    {"codigo": 4448, "corte": "COSTELA SALG", "pesagens": "78.285 + 54.1 + 44.95 + 83.507", "preco_venda": 10.90},
                    {"codigo": 29183, "corte": "COSTELA C/TOUCINHO", "pesagens": "", "preco_venda": 18.60},
                    {"codigo": 31611, "corte": "PALETA SUINA PURURUCA", "pesagens": "", "preco_venda": 13.90},
                    {"codigo": 29184, "corte": "PERNIL C/TOUCINHO", "pesagens": "56.605 + 29.464", "preco_venda": 16.50},
                ],
            },
            "CARNEIRO": {
                "titulo": "CARNEIRO",
                "peca_nome": "CARNEIRO",
                "codigo_peca": 6505,
                "peso_peca_str": "25.06",
                "custo_kg": 26.50,
                "notas": "16904",
                "perda_apontada_str": "",
                "cortes": [
                    {"codigo": 6505, "corte": "DIANTEIRO CARNEIRO", "pesagens": "4.306 + 9.44", "preco_venda": 36.00},
                    {"codigo": 6506, "corte": "TRASEIRO CARNEIRO", "pesagens": "3.276 + 7.16", "preco_venda": 38.00},
                ],
            },
        },
        # Pesos e custos extras de cortes traseiros na aba BOVINO (Colunas O e P linhas 18 a 28)
        "bovino_extras_traseiro": {
            "3376": {"pesagens": "615.841", "peso": 615.841, "custo": 35.52},
            "4416": {"pesagens": "470.392", "peso": 470.392, "custo": 45.15},
            "3379": {"pesagens": "170.37", "peso": 170.370, "custo": 46.83},
            "3381": {"pesagens": "", "peso": 0.0, "custo": 0.0},
            "4624": {"pesagens": "63.973", "peso": 63.973, "custo": 63.13},
            "3378": {"pesagens": "85.738", "peso": 85.738, "custo": 47.44},
            "2699": {"pesagens": "438.521", "peso": 438.521, "custo": 38.90},
            "3373": {"pesagens": "359.124", "peso": 359.124, "custo": 38.56},
            "3329": {"pesagens": "654.077", "peso": 654.077, "custo": 36.48},
            "3361": {"pesagens": "75.351", "peso": 75.351, "custo": 39.90},
            "3944": {"pesagens": "10.341", "peso": 10.341, "custo": 25.40},
        },
        # Receitas / Produção Própria
        "receitas": {
            "KIT_FEIJOADA": {
                "codigo": 4457,
                "produto": "KIT FEIJOADA SJ KG",
                "rendimento_str": "18.4 + 12.055",
                "preco_venda": 15.60,
                "ingredientes": [
                    {"codigo": 3686, "ingrediente": "LINGUICA SEARA CALABRESA KG", "pesagens": "", "custo_kg": 0.0},
                    {"codigo": 4448, "ingrediente": "COSTELA SUINA SALGADA KG", "pesagens": "", "custo_kg": 8.10},
                    {"codigo": 6243, "ingrediente": "REJEITO SUINO KG", "pesagens": "", "custo_kg": 9.28},
                    {"codigo": 3453, "ingrediente": "TOUCINHO KG", "pesagens": "8.44", "custo_kg": 6.61},
                    {"codigo": 3504, "ingrediente": "PANCETA KG", "pesagens": "", "custo_kg": 12.55},
                    {"codigo": 3959, "ingrediente": "PALETA SUINA KG", "pesagens": "", "custo_kg": 12.55},
                    {"codigo": 31611, "ingrediente": "PALETA SUINA PURURUCA CONG KG", "pesagens": "", "custo_kg": 10.32},
                    {"codigo": 3366, "ingrediente": "COSTELA PONTA DE AGULHA KG", "pesagens": "", "custo_kg": 23.19},
                    {"codigo": 219, "ingrediente": "PE SUINO KG", "pesagens": "", "custo_kg": 0.0},
                    {"codigo": 5963, "ingrediente": "PERNIL SUINO KG", "pesagens": "21.27", "custo_kg": 15.23},
                    {"codigo": 3944, "ingrediente": "RABADA KG", "pesagens": "", "custo_kg": 25.41},
                    {"codigo": 21191, "ingrediente": "LINGUICA SADIA RETA CALABRESA KG", "pesagens": "", "custo_kg": 0.0},
                    {"codigo": 3982, "ingrediente": "LINGUICA SADIA CALABRESA KG", "pesagens": "0.842 + 0.248", "custo_kg": 17.37},
                    {"codigo": 6025, "ingrediente": "PEITO BOVINO C/OSSO KG", "pesagens": "", "custo_kg": 27.51},
                ],
            },
            "CARNE_SOL_BOVINA": {
                "codigo": 3311,
                "produto": "CARNE DE SOL KG",
                "rendimento_str": "15.88 + 5.052 + 1.002 + 14.63 + 8.77 + 18.02 + 24.37 + 10.735 + 0.624 + 1.078 + 5 + 0.538 + 2.738 + 13.315",
                "preco_venda": 50.90,
                "ingredientes": [
                    {"codigo": 3329, "ingrediente": "LAGARTO KG", "pesagens": "21.84", "custo_kg": 34.81},
                    {"codigo": 3376, "ingrediente": "COXAO DURO KG", "pesagens": "15.73", "custo_kg": 32.89},
                    {"codigo": 2699, "ingrediente": "COXAO MOLE KG", "pesagens": "3.938", "custo_kg": 37.52},
                    {"codigo": 3361, "ingrediente": "FRALDINHA KG", "pesagens": "", "custo_kg": 39.68},
                    {"codigo": 3379, "ingrediente": "CONTRA FILE KG", "pesagens": "7.82 + 16.04 + 15.42 + 12.87", "custo_kg": 42.89},
                    {"codigo": 6025, "ingrediente": "PEITO BOVINO C/OSSO KG", "pesagens": "", "custo_kg": 27.51},
                    {"codigo": 6022, "ingrediente": "LOMBO BOVINO C/OSSO KG", "pesagens": "22.75 + 8.625", "custo_kg": 24.93},
                    {"codigo": 3373, "ingrediente": "PATINHO KG", "pesagens": "", "custo_kg": 38.61},
                    {"codigo": 4416, "ingrediente": "ALCATRA KG", "pesagens": "", "custo_kg": 45.12},
                    {"codigo": 3497, "ingrediente": "BIFE AMACIADO KG", "pesagens": "", "custo_kg": 36.68},
                    {"codigo": 4624, "ingrediente": "PICANHA BOVINA KG", "pesagens": "", "custo_kg": 62.86},
                    {"codigo": 31888, "ingrediente": "PICANHA PUL SELECAO KG", "pesagens": "", "custo_kg": 0.0},
                    {"codigo": 9960, "ingrediente": "CONTRA FILE BIFE DE CHORIZO KG", "pesagens": "", "custo_kg": 0.0},
                ],
            },
            "CARNE_SOL_SUINA": {
                "codigo": 30515,
                "produto": "CARNE DE SOL SUINA KG",
                "rendimento_str": "",
                "preco_venda": 0.0,
                "ingredientes": [
                    {"codigo": 5963, "ingrediente": "PERNIL SUINO KG", "pesagens": "", "custo_kg": 16.27},
                ],
            },
            "PANELADA": {
                "codigo": 6456,
                "produto": "PANELADA KG",
                "rendimento_str": "27.29 + 27 + 5.438 + 24.61 + 1.242 + 1.624 + 15 + 20.9 + 2.042 + 96",
                "preco_venda": 16.90,
                "meta_simulacao_kg": 96.0,
                "ingredientes": [
                    {"codigo": 5710, "ingrediente": "TRIPA FINA KG", "pesagens": "22.11 + 12.36 + 0.44 + 0.682 + 9.99 + 4.082 + 0.856 + 32.378", "custo_kg": 17.50, "prop_padrao": 44.0},
                    {"codigo": 5709, "ingrediente": "BUCHO BOVINO KG", "pesagens": "23.33 + 8.025 + 0.438 + 0.472 + 9.47 + 3.39 + 0.762 + 27.708", "custo_kg": 15.35, "prop_padrao": 40.0},
                    {"codigo": 4342, "ingrediente": "MOCOTO BOVINO KG", "pesagens": "12.5 + 4.226 + 0.374 + 0.5 + 0.436 + 12.258", "custo_kg": 11.12, "prop_padrao": 16.0},
                ],
            },
        },
        # Caixaria (Perdas, Saídas e Entradas)
        "caixaria": {
            "perdas_custos": [
                {"codigo": 4416, "corte": "ALCATRA", "pesagens_perda": "0.694 + 0.94 + 0.558", "custo_kg": 45.12},
                {"codigo": 3377, "corte": "ARANHA", "pesagens_perda": "", "custo_kg": 31.63},
                {"codigo": 5670, "corte": "BIFE DE 1", "pesagens_perda": "", "custo_kg": 34.90},
                {"codigo": 3497, "corte": "BIFE AMACIADO KG", "pesagens_perda": "", "custo_kg": 36.68},
                {"codigo": 10543, "corte": "BISTECA SUINA KG", "pesagens_perda": "", "custo_kg": 14.78},
                {"codigo": 6030, "corte": "CARNE MOIDA", "pesagens_perda": "", "custo_kg": 24.77},
                {"codigo": 6029, "corte": "CARRE P BOVINO KG", "pesagens_perda": "", "custo_kg": 26.05},
                {"codigo": 3379, "corte": "CONTRA FILE", "pesagens_perda": "0.16 + 0.132 + 0.04 + 0.218 + 0.054 + 0.064 + 0.094 + 0.168 + 0.092 + 0.156 + 0.352 + 0.16 + 0.08 + 0.126", "custo_kg": 46.62},
                {"codigo": 3960, "corte": "COPA LOMBO SUINO", "pesagens_perda": "", "custo_kg": 16.27},
                {"codigo": 3376, "corte": "COXAO DURO", "pesagens_perda": "1.208", "custo_kg": 35.55},
                {"codigo": 2699, "corte": "COXAO MOLE", "pesagens_perda": "", "custo_kg": 38.93},
                {"codigo": 3375, "corte": "CUPIM KG", "pesagens_perda": "", "custo_kg": 36.99},
                {"codigo": 3381, "corte": "FILE MIGNON", "pesagens_perda": "", "custo_kg": 51.72},
                {"codigo": 3503, "corte": "FILE DE PERNIL", "pesagens_perda": "", "custo_kg": 17.90},
                {"codigo": 3361, "corte": "FRALDINHA KG", "pesagens_perda": "", "custo_kg": 39.68},
                {"codigo": 3329, "corte": "LAGARTO", "pesagens_perda": "0.82", "custo_kg": 36.49},
                {"codigo": 6022, "corte": "LOMB BOV C/OSSO", "pesagens_perda": "", "custo_kg": 27.45},
                {"codigo": 5716, "corte": "MAMINHA MASTER KG", "pesagens_perda": "", "custo_kg": 41.89},
                {"codigo": 6028, "corte": "MAO DE VACA", "pesagens_perda": "", "custo_kg": 26.12},
                {"codigo": 3373, "corte": "PATINHO", "pesagens_perda": "0.496 + 0.676 + 0.384 + 0.136 + 1.076 + 1.042 + 0.842 + 1.436 + 0.604", "custo_kg": 38.61},
                {"codigo": 6025, "corte": "PEITO BOVINO C/OSSO", "pesagens_perda": "", "custo_kg": 27.51},
                {"codigo": 5963, "corte": "PERNIL SUINO", "pesagens_perda": "", "custo_kg": 16.27},
                {"codigo": 6032, "corte": "PICADINHO", "pesagens_perda": "", "custo_kg": 34.26},
                {"codigo": 3366, "corte": "PONTA DE AGULHA KG", "pesagens_perda": "", "custo_kg": 23.19},
                {"codigo": 6051, "corte": "OSSADA", "pesagens_perda": "", "custo_kg": 9.23},
            ],
            "saidas": [
                {"codigo": 4416, "corte": "ALCATRA", "pesagens_saida": "1.496 + 2.29 + 1.026"},
                {"codigo": 3377, "corte": "ARANHA", "pesagens_saida": ""},
                {"codigo": 5670, "corte": "BIFE DE 1", "pesagens_saida": ""},
                {"codigo": 3497, "corte": "BIFE AMACIADO KG", "pesagens_saida": ""},
                {"codigo": 10543, "corte": "BISTECA SUINA KG", "pesagens_saida": ""},
                {"codigo": 6029, "corte": "CARRE P BOVINO KG", "pesagens_saida": ""},
                {"codigo": 3379, "corte": "CONTRA FILE", "pesagens_saida": ""},
                {"codigo": 3960, "corte": "COPA LOMBO SUINO", "pesagens_saida": "15.48"},
                {"codigo": 3376, "corte": "COXAO DURO", "pesagens_saida": "14.57 + 8.185 + 1.955"},
                {"codigo": 2699, "corte": "COXAO MOLE", "pesagens_saida": "1.948"},
                {"codigo": 3375, "corte": "CUPIM KG", "pesagens_saida": ""},
                {"codigo": 3381, "corte": "FILE MIGNON", "pesagens_saida": ""},
                {"codigo": 3503, "corte": "FILE DE PERNIL", "pesagens_saida": ""},
                {"codigo": 3361, "corte": "FRALDINHA KG", "pesagens_saida": ""},
                {"codigo": 3329, "corte": "LAGARTO", "pesagens_saida": "8.63"},
                {"codigo": 6022, "corte": "LOMBO BOV C/OSSO", "pesagens_saida": ""},
                {"codigo": 5716, "corte": "MAMINHA MASTER KG", "pesagens_saida": ""},
                {"codigo": 6028, "corte": "MAO DE VACA", "pesagens_saida": ""},
                {"codigo": 3373, "corte": "PATINHO", "pesagens_saida": "0.34 + 0.632 + 0.542 + 0.902"},
                {"codigo": 6025, "corte": "PEITO BOVINO C/OSSO", "pesagens_saida": ""},
                {"codigo": 5963, "corte": "PERNIL SUINO", "pesagens_saida": ""},
                {"codigo": 6032, "corte": "PICADINHO", "pesagens_saida": ""},
                {"codigo": 3366, "corte": "PONTA DE AGULHA KG", "pesagens_saida": ""},
            ],
            "entradas": [
                {"codigo": 4416, "corte": "ALCATRA", "pesagens_entrada": ""},
                {"codigo": 5670, "corte": "BIFE DE 1", "pesagens_entrada": "14.57 + 8.63"},
                {"codigo": 3497, "corte": "BIFE AMACIADO KG", "pesagens_entrada": "1.948 + 0.542 + 8.185"},
                {"codigo": 6030, "corte": "CARNE MOIDA", "pesagens_entrada": "1.496 + 2.29 + 0.34 + 0.632 + 0.902 + 1.026 + 1.955"},
                {"codigo": 6029, "corte": "CARRE P BOVINO KG", "pesagens_entrada": ""},
                {"codigo": 3379, "corte": "CONTRA FILE", "pesagens_entrada": ""},
                {"codigo": 3960, "corte": "COPA LOMBO SUINO", "pesagens_entrada": ""},
                {"codigo": 3369, "corte": "COSTELA SUINA", "pesagens_entrada": ""},
                {"codigo": 4448, "corte": "COST SUINA SALG", "pesagens_entrada": ""},
                {"codigo": 3376, "corte": "COXAO DURO", "pesagens_entrada": ""},
                {"codigo": 2699, "corte": "COXAO MOLE", "pesagens_entrada": ""},
                {"codigo": 3503, "corte": "FILE DE PERNIL", "pesagens_entrada": "15.48"},
                {"codigo": 3329, "corte": "LAGARTO", "pesagens_entrada": ""},
                {"codigo": 6022, "corte": "LOMBO BOV C/OSSO", "pesagens_entrada": ""},
                {"codigo": 6051, "corte": "OSSADA", "pesagens_entrada": ""},
                {"codigo": 3373, "corte": "PATINHO", "pesagens_entrada": ""},
                {"codigo": 6032, "corte": "PICADINHO", "pesagens_entrada": ""},
                {"codigo": 3366, "corte": "PONTA DE AGULHA KG", "pesagens_entrada": ""},
                {"codigo": 6243, "corte": "REJEITO SUINO", "pesagens_entrada": ""},
            ],
        },
        # Tópico Unificado de Anotações (Miúdos, Subprodutos e Pesagens Extras)
        "anotacoes": [
            {
                "codigo": 2669,
                "item": "FIGADO BOVINO KG",
                "origem": "Bovino / Miúdos",
                "pesagens": "13.72 + 17.43 + 9.76 + 5.56 + 5.326 + 10.8 + 6.39 + 14.975 + 20.38 + 23.5 + 1.804 + 11.865 + 4.152 + 10.31 + 3.086",
                "observacao": "",
            },
            {
                "codigo": 3941,
                "item": "CORAÇÃO BOVINO KG",
                "origem": "Bovino / Miúdos",
                "pesagens": "2.356 + 7.795 + 6.065 + 6.51 + 4.7 + 1.594 + 5.898 + 5.428 + 6.41 + 2.424 + 1.944",
                "observacao": "",
            },
            {
                "codigo": 6456,
                "item": "PANELADA KG",
                "origem": "Bovino / Produção",
                "pesagens": "23.4 + 18.22 + 26.9 + 12.765 + 5 + 2.084 + 13.28 + 20.18 + 2.37 + 19.41 + 23.56 + 3.04 + 27.7 + 9.54 + 11.845 + 13.585 + 13.79 + 20.49 + 18.79 + 9.34 + 1.284 + 2.2 + 2.072 + 13.45 + 11.245 + 19.15 + 23.49 + 22.15",
                "observacao": "",
            },
            {
                "codigo": 6032,
                "item": "PICADINHO",
                "origem": "Bovino / Extra",
                "pesagens": "",
                "observacao": "",
            },
            {
                "codigo": 6030,
                "item": "CARNE MOIDA",
                "origem": "Bovino / Extra",
                "pesagens": "3.194 + 1.262 + 1.61 + 2.718 + 2.304 + 2.458 + 2.75 + 1.16",
                "observacao": "",
            },
            {
                "codigo": 3497,
                "item": "BIFE AMACIADO KG",
                "origem": "Bovino / Extra",
                "pesagens": "4.66 + 6.81",
                "observacao": "",
            },
            {
                "codigo": 7222,
                "item": "SARRABULHO",
                "origem": "Suíno",
                "pesagens": "4.814 + 5.126 + 6.705 + 1.454 + 27.7 + 1.04",
                "observacao": "",
            },
            {
                "codigo": 219,
                "item": "PE SUINO",
                "origem": "Suíno",
                "pesagens": "16.37 + 1.07 + 1.128 + 2.378 + 4.15 + 3.97",
                "observacao": "",
            },
            {
                "codigo": 19978,
                "item": "ORELHA SUINA",
                "origem": "Suíno",
                "pesagens": "",
                "observacao": "Ref: 3750",
            },
            {
                "codigo": 14338,
                "item": "BUCHADA",
                "origem": "Carneiro",
                "pesagens": "5.072 + 5.488 + 5.202 + 5.878 + 5.606 + 5.248 + 5.178 + 5.188 + 5.628 + 5.054 + 4.968 + 5.624 + 5.69 + 6.135 + 5.01 + 5.2 + 4.95 + 4.134 + 5.268 + 4.716",
                "observacao": "",
            },
            {
                "codigo": 27025,
                "item": "FRISSURA",
                "origem": "Carneiro",
                "pesagens": "6.235 + 6.5 + 1.116 + 7.86 + 5.288 + 5.322 + 3.632 + 6.525 + 7.315 + 5.74 + 5.756 + 7.345 + 5.984 + 4.924 + 6.715 + 5.1 + 4.458 + 4.9",
                "observacao": "",
            },
        ],
    }


# ==============================================================================
# PERSISTÊNCIA NO BANCO DE DADOS (TABLE EDITOR DO SUPABASE OU SQLITE LOCAL)
# ==============================================================================

def init_rendimento_tables():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rendimento_estado (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            dados_json TEXT NOT NULL,
            atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rendimento_historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo_fechamento TEXT NOT NULL,
            notas_fiscais TEXT,
            resumo_json TEXT NOT NULL,
            dados_json TEXT NOT NULL,
            data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

    cursor.execute("SELECT COUNT(*) AS total FROM rendimento_estado WHERE id = 1")
    row = cursor.fetchone()
    count_est = row["total"] if isinstance(row, dict) else row[0]
    if count_est == 0:
        default_json = json.dumps(get_default_state(), ensure_ascii=False)
        cursor.execute(
            "INSERT INTO rendimento_estado (id, dados_json) VALUES (1, ?)",
            (default_json,),
        )
        conn.commit()
    conn.close()


def load_state() -> dict:
    if data_manager.is_supabase_rest():
        url, _ = data_manager.get_supabase_credentials()
        try:
            import requests
            r = requests.get(
                f"{url}/rest/v1/rendimento_estado?id=eq.1&select=dados_json",
                headers=data_manager._rest_headers(),
                timeout=8,
            )
            if r.status_code == 200:
                rows = r.json()
                if rows and rows[0].get("dados_json"):
                    val = rows[0]["dados_json"]
                    return json.loads(val) if isinstance(val, str) else val
        except Exception as e:
            print(f"Aviso Supabase load_state: {e}")

    init_rendimento_tables()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT dados_json FROM rendimento_estado WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        try:
            val = row["dados_json"] if isinstance(row, dict) else row[0]
            return json.loads(val)
        except Exception:
            pass
    return get_default_state()


def save_state(state: dict):
    dados_json = json.dumps(state, ensure_ascii=False)
    if data_manager.is_supabase_rest():
        url, _ = data_manager.get_supabase_credentials()
        try:
            import requests
            requests.post(
                f"{url}/rest/v1/rendimento_estado?on_conflict=id",
                headers=data_manager._rest_headers("resolution=merge-duplicates"),
                json={"id": 1, "dados_json": dados_json},
                timeout=8,
            )
        except Exception as e:
            print(f"Aviso Supabase save_state: {e}")

    init_rendimento_tables()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO rendimento_estado (id, dados_json, atualizado_em)
        VALUES (1, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(id) DO UPDATE SET
            dados_json = excluded.dados_json,
            atualizado_em = CURRENT_TIMESTAMP
    """, (dados_json,))
    conn.commit()
    conn.close()


def reset_to_excel_defaults() -> dict:
    state = get_default_state()
    save_state(state)
    return state


def salvar_historico_fechamento(titulo: str, notas: str, resumo: dict, state: dict) -> tuple[bool, str]:
    payload = {
        "titulo_fechamento": titulo.strip() or f"Fechamento {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        "notas_fiscais": notas.strip(),
        "resumo_json": json.dumps(resumo, ensure_ascii=False),
        "dados_json": json.dumps(state, ensure_ascii=False),
    }
    if data_manager.is_supabase_rest():
        url, _ = data_manager.get_supabase_credentials()
        try:
            import requests
            r = requests.post(
                f"{url}/rest/v1/rendimento_historico",
                headers=data_manager._rest_headers(),
                json=payload,
                timeout=8,
            )
            if r.status_code in (200, 201):
                return True, "Fechamento salvo no histórico do Supabase com sucesso!"
        except Exception as e:
            return False, f"Erro ao salvar no Supabase: {e}"

    init_rendimento_tables()
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO rendimento_historico (titulo_fechamento, notas_fiscais, resumo_json, dados_json)
            VALUES (?, ?, ?, ?)
        """, (payload["titulo_fechamento"], payload["notas_fiscais"], payload["resumo_json"], payload["dados_json"]))
        conn.commit()
        return True, "Fechamento salvo no histórico com sucesso!"
    except Exception as e:
        return False, f"Erro ao salvar histórico: {e}"
    finally:
        conn.close()


def listar_historico() -> pd.DataFrame:
    if data_manager.is_supabase_rest():
        url, _ = data_manager.get_supabase_credentials()
        try:
            import requests
            r = requests.get(
                f"{url}/rest/v1/rendimento_historico?select=id,titulo_fechamento,notas_fiscais,resumo_json,dados_json,data_registro&order=id.desc",
                headers=data_manager._rest_headers(),
                timeout=8,
            )
            if r.status_code == 200:
                rows = r.json()
                if rows:
                    return pd.DataFrame(rows)
                return pd.DataFrame(columns=["id", "titulo_fechamento", "notas_fiscais", "resumo_json", "dados_json", "data_registro"])
        except Exception as e:
            print(f"Aviso Supabase listar_historico: {e}")

    init_rendimento_tables()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, titulo_fechamento, notas_fiscais, resumo_json, dados_json, data_registro
        FROM rendimento_historico
        ORDER BY id DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        return pd.DataFrame(columns=["id", "titulo_fechamento", "notas_fiscais", "resumo_json", "dados_json", "data_registro"])
    return pd.DataFrame([dict(r) for r in rows])


# ==============================================================================
# MOTORES DE CÁLCULO (100% FIÉIS ÀS FÓRMULAS DE RENDIMENTO_ATUAL.xlsm)
# ==============================================================================

def calcular_desossa(dados_peca: dict, part_base: str = "rendimento") -> dict:
    """
    Calcula todos os indicadores de uma guia de desossa:
    - DIANTEIRO e DIANTEIRO_MASTERBOI e CARNEIRO dividem % PART KG por G3 (peso_peca),
      enquanto TRASEIRO, PONTA_AGULHA, PA_MASTERBOI, SUINO e BOVINO dividem por Rendimento Total.
      (Ambos estão disponíveis nos resultados de cada linha).
    """
    peso_peca, qtd_lotes_peca, _, _ = parse_pesagens(dados_peca.get("peso_peca_str", ""))
    custo_kg_entrada = float(dados_peca.get("custo_kg", 0.0))
    custo_total_entrada = peso_peca * custo_kg_entrada

    perda_apontada, qtd_pesagens_perda, _, _ = parse_pesagens(dados_peca.get("perda_apontada_str", ""))

    linhas = []
    rendimento_total = 0.0
    venda_total = 0.0

    for item in dados_peca.get("cortes", []):
        peso_corte, n_pesos, _, norm_pesos = parse_pesagens(item.get("pesagens", ""))
        preco_venda = float(item.get("preco_venda", 0.0))
        venda_item = peso_corte * preco_venda
        rendimento_total += peso_corte
        venda_total += venda_item
        linhas.append({
            "codigo": int(item["codigo"]),
            "corte": item["corte"],
            "pesagens": item.get("pesagens", ""),
            "pesagens_norm": norm_pesos,
            "qtd_pesagens": n_pesos,
            "peso_kg": peso_corte,
            "preco_venda": preco_venda,
            "venda_total": venda_item,
        })

    perda_verificada = peso_peca - rendimento_total - perda_apontada

    rendimento_pct = (rendimento_total / peso_peca) if peso_peca > 0 else 0.0
    perda_apontada_pct = (perda_apontada / peso_peca) if peso_peca > 0 else 0.0
    perda_verificada_pct = (perda_verificada / peso_peca) if peso_peca > 0 else 0.0

    mkp_pct = ((venda_total - custo_total_entrada) / custo_total_entrada) if custo_total_entrada > 0 else 0.0
    mkd_pct = ((venda_total - custo_total_entrada) / venda_total) if venda_total > 0 else 0.0

    base_part = peso_peca if part_base == "peca" else rendimento_total

    for l in linhas:
        l["part_pct"] = (l["peso_kg"] / base_part) if base_part > 0 else 0.0
        # Fórmula exata da planilha: K = L - (L * MKD)
        l["custo_kg"] = l["preco_venda"] - (l["preco_venda"] * mkd_pct)

    return {
        "peso_peca": peso_peca,
        "qtd_lotes_peca": qtd_lotes_peca,
        "custo_kg_entrada": custo_kg_entrada,
        "custo_total_entrada": custo_total_entrada,
        "rendimento_total": rendimento_total,
        "rendimento_pct": rendimento_pct,
        "perda_apontada": perda_apontada,
        "qtd_pesagens_perda": qtd_pesagens_perda,
        "perda_apontada_pct": perda_apontada_pct,
        "perda_verificada": perda_verificada,
        "perda_verificada_pct": perda_verificada_pct,
        "venda_total": venda_total,
        "mkp_pct": mkp_pct,
        "mkd_pct": mkd_pct,
        "linhas": linhas,
    }


def calcular_consolidado_bovino(state: dict) -> dict:
    """
    Reproduz fielmente a Guia BOVINO:
    1ª Parte: Soma automática de DIANTEIRO + TRASEIRO + PONTA_AGULHA (Boi Casado).
    2ª Parte: Preço Médio Ponderado somando o BOVINO (1ª parte) com DIANTEIRO MASTERBOI e P. A. MASTERBOI
              (e lotes extras de traseiro se informados).
    """
    des = state["desossas"]
    res_diant = calcular_desossa(des["DIANTEIRO"], part_base="peca")
    res_tras = calcular_desossa(des["TRASEIRO"], part_base="rendimento")
    res_pa = calcular_desossa(des["PONTA_AGULHA"], part_base="rendimento")
    res_dm = calcular_desossa(des["DIANTEIRO_MASTERBOI"], part_base="peca")
    res_pam = calcular_desossa(des["PA_MASTERBOI"], part_base="rendimento")

    # Mapas por código de cada desossa
    map_diant = {r["codigo"]: r for r in res_diant["linhas"]}
    map_tras = {r["codigo"]: r for r in res_tras["linhas"]}
    map_pa = {r["codigo"]: r for r in res_pa["linhas"]}
    map_dm = {r["codigo"]: r for r in res_dm["linhas"]}
    map_pam = {r["codigo"]: r for r in res_pam["linhas"]}

    # Totais de Entrada do Boi Casado (T3:V6 na planilha BOVINO)
    peso_boi_casado = res_diant["peso_peca"] + res_tras["peso_peca"] + res_pa["peso_peca"]
    custo_total_boi_casado = (
        res_diant["custo_total_entrada"]
        + res_tras["custo_total_entrada"]
        + res_pa["custo_total_entrada"]
    )
    custo_kg_boi_casado = (custo_total_boi_casado / peso_boi_casado) if peso_boi_casado > 0 else 0.0

    # Ordem exata dos 23 cortes na guia BOVINO (B6:C28)
    ordem_cortes_bovino = [
        (6025, "PEITO BOVINO"),
        (6022, "LOMBO BOVINO"),
        (6029, "CARRE PAULISTA"),
        (3375, "CUPIM"),
        (34654, "MIOLO ACEM S/OSSO"),
        (34656, "PONTA DO PEITO S/OSSO"),
        (6032, "PICADINHO"),
        (6030, "CARNE MOIDA"),
        (6028, "MAO DE VACA"),
        (5670, "BIFE DE 1"),
        (6051, "OSSADA"),
        (3366, "PONTA DE AGULHA"),
        (3376, "COXAO DURO"),
        (4416, "ALCATRA"),
        (3379, "CONTRA FILE"),
        (3381, "FILE MIGNON"),
        (4624, "PICANHA"),
        (3378, "MAMINHA"),
        (2699, "COXAO MOLE"),
        (3373, "PATINHO"),
        (3329, "LAGARTO"),
        (3361, "FRALDINHA"),
        (3944, "RABADA"),
    ]

    linhas_bovino = []
    rendimento_total = 0.0
    venda_total = 0.0

    for cod, nome in ordem_cortes_bovino:
        p_d = map_diant.get(cod, {}).get("peso_kg", 0.0)
        p_t = map_tras.get(cod, {}).get("peso_kg", 0.0)
        p_pa = map_pa.get(cod, {}).get("peso_kg", 0.0)
        peso_bovino = p_d + p_t + p_pa

        # Preço de venda vem da peça correspondente
        preco_venda = (
            map_diant.get(cod, {}).get("preco_venda")
            or map_tras.get(cod, {}).get("preco_venda")
            or map_pa.get(cod, {}).get("preco_venda")
            or 0.0
        )

        venda_item = peso_bovino * preco_venda
        rendimento_total += peso_bovino
        venda_total += venda_item

        linhas_bovino.append({
            "codigo": cod,
            "corte": nome,
            "peso_dianteiro": p_d,
            "peso_traseiro": p_t,
            "peso_pa": p_pa,
            "peso_bovino": peso_bovino,
            "preco_venda": preco_venda,
            "venda_total": venda_item,
        })

    perda_apontada = res_diant["perda_apontada"] + res_tras["perda_apontada"] + res_pa["perda_apontada"]
    perda_verificada = peso_boi_casado - rendimento_total - perda_apontada

    rendimento_pct = (rendimento_total / peso_boi_casado) if peso_boi_casado > 0 else 0.0
    perda_apontada_pct = (perda_apontada / peso_boi_casado) if peso_boi_casado > 0 else 0.0
    perda_verificada_pct = (perda_verificada / peso_boi_casado) if peso_boi_casado > 0 else 0.0

    mkp_pct = ((venda_total - custo_total_boi_casado) / custo_total_boi_casado) if custo_total_boi_casado > 0 else 0.0
    mkd_pct = ((venda_total - custo_total_boi_casado) / venda_total) if venda_total > 0 else 0.0

    extras_tras = state.get("bovino_extras_traseiro", {})

    # 2ª Parte: Custo Bovino (Coluna K) e Preço Médio Ponderado com Masterboi / Extras (Colunas O, P e N)
    for l in linhas_bovino:
        cod = l["codigo"]
        l["part_pct"] = (l["peso_bovino"] / rendimento_total) if rendimento_total > 0 else 0.0
        l["custo_bovino"] = l["preco_venda"] - (l["preco_venda"] * mkd_pct)

        # Determina Peso Masterboi/Extra (Coluna O) e Custo Masterboi/Extra (Coluna P)
        if cod in (6032, 6030):
            # Picadinho e Carne Moída somam Dianteiro Masterboi + PA Masterboi
            p_dm = map_dm.get(cod, {}).get("peso_kg", 0.0)
            c_dm = map_dm.get(cod, {}).get("custo_kg", 0.0)
            p_pam = map_pam.get(cod, {}).get("peso_kg", 0.0)
            c_pam = map_pam.get(cod, {}).get("custo_kg", 0.0)
            peso_mb = p_dm + p_pam
            custo_mb = ((p_dm * c_dm) + (p_pam * c_pam)) / peso_mb if peso_mb > 0 else 0.0
            pesagens_o_str = f"{peso_mb:g}" if peso_mb > 0 else ""
            origem_mb = "Desossa Masterboi (Diant. + PA)"
            editavel_op = False
        elif cod == 3366:
            # Ponta de Agulha vem de P. A. Masterboi
            peso_mb = map_pam.get(cod, {}).get("peso_kg", 0.0)
            custo_mb = map_pam.get(cod, {}).get("custo_kg", 0.0)
            pesagens_o_str = f"{peso_mb:g}" if peso_mb > 0 else ""
            origem_mb = "Desossa PA Masterboi"
            editavel_op = False
        elif cod in map_dm:
            # Demais cortes do Dianteiro vêm de Dianteiro Masterboi
            peso_mb = map_dm.get(cod, {}).get("peso_kg", 0.0)
            custo_mb = map_dm.get(cod, {}).get("custo_kg", 0.0)
            pesagens_o_str = f"{peso_mb:g}" if peso_mb > 0 else ""
            origem_mb = "Desossa Dianteiro Masterboi"
            editavel_op = False
        else:
            # Cortes exclusivos de Traseiro (linhas 18 a 28: digitados manualmente em O e P, aceitando soma ex: '200+150')
            ext = extras_tras.get(str(cod), {"pesagens": "", "peso": 0.0, "custo": 0.0})
            raw_str = ext.get("pesagens")
            if raw_str is None:
                p_val = float(ext.get("peso", 0.0))
                raw_str = f"{p_val:g}" if p_val > 0 else ""
            peso_mb, _, _, _ = parse_pesagens(raw_str)
            custo_mb = float(ext.get("custo", 0.0))
            pesagens_o_str = str(raw_str)
            origem_mb = "Compra Adicional / Caixa"
            editavel_op = True

        l["pesagens_col_o"] = pesagens_o_str
        l["peso_masterboi"] = peso_mb
        l["custo_masterboi"] = custo_mb
        l["origem_masterboi"] = origem_mb
        l["editavel_op"] = editavel_op
        l["peso_total_geral"] = l["peso_bovino"] + peso_mb

        # Preço Médio Ponderado (Coluna N = ((P*O)+(H*K))/(O+H)) em todas as linhas (incluindo L17 Ponta de Agulha)
        if (l["peso_bovino"] + peso_mb) > 0:
            l["preco_medio_final"] = (
                (l["peso_bovino"] * l["custo_bovino"]) + (peso_mb * custo_mb)
            ) / (l["peso_bovino"] + peso_mb)
        else:
            l["preco_medio_final"] = l["custo_bovino"]

    return {
        "res_dianteiro": res_diant,
        "res_traseiro": res_tras,
        "res_pa": res_pa,
        "res_dm": res_dm,
        "res_pam": res_pam,
        "peso_boi_casado": peso_boi_casado,
        "custo_kg_boi_casado": custo_kg_boi_casado,
        "custo_total_boi_casado": custo_total_boi_casado,
        "rendimento_total": rendimento_total,
        "rendimento_pct": rendimento_pct,
        "perda_apontada": perda_apontada,
        "perda_apontada_pct": perda_apontada_pct,
        "perda_verificada": perda_verificada,
        "perda_verificada_pct": perda_verificada_pct,
        "venda_total": venda_total,
        "mkp_pct": mkp_pct,
        "mkd_pct": mkd_pct,
        "linhas": linhas_bovino,
    }


def obter_mapa_custos_atualizados(state: dict) -> dict[int, float]:
    """
    Retorna um dicionário {codigo_corte: preco_medio_final} consolidando:
    - Cortes Bovinos (Preço Médio Final de BOVINO + MASTERBOI)
    - Cortes Suínos (Custo/KG apurado na guia SUINO)
    - Cortes Carneiro (Custo/KG apurado na guia CARNEIRO)
    """
    mapa = {}
    bov = calcular_consolidado_bovino(state)
    for l in bov["linhas"]:
        mapa[int(l["codigo"])] = round(float(l["preco_medio_final"]), 2)

    suino = calcular_desossa(state["desossas"]["SUINO"], part_base="rendimento")
    for l in suino["linhas"]:
        mapa[int(l["codigo"])] = round(float(l["custo_kg"]), 2)

    carneiro = calcular_desossa(state["desossas"]["CARNEIRO"], part_base="peca")
    for l in carneiro["linhas"]:
        mapa[int(l["codigo"])] = round(float(l["custo_kg"]), 2)

    return mapa


def calcular_receita(dados_rec: dict) -> dict:
    """
    Calcula os indicadores de uma Receita / Produção Própria
    (KIT FEIJOADA, CARNE DE SOL BOVINA/SUINA, PANELADA).
    """
    rendimento_final, qtd_pesos_rend, _, _ = parse_pesagens(dados_rec.get("rendimento_str", ""))
    preco_venda = float(dados_rec.get("preco_venda", 0.0))

    linhas = []
    peso_total_insumos = 0.0
    custo_total_insumos = 0.0

    for ing in dados_rec.get("ingredientes", []):
        peso_ing, n_pesos, _, norm_pesos = parse_pesagens(ing.get("pesagens", ""))
        custo_kg = float(ing.get("custo_kg", 0.0))
        custo_tot = peso_ing * custo_kg
        peso_total_insumos += peso_ing
        custo_total_insumos += custo_tot
        linhas.append({
            "codigo": int(ing["codigo"]),
            "ingrediente": ing["ingrediente"],
            "pesagens": ing.get("pesagens", ""),
            "pesagens_norm": norm_pesos,
            "qtd_pesagens": n_pesos,
            "peso_kg": peso_ing,
            "custo_kg": custo_kg,
            "custo_total": custo_tot,
            "prop_padrao": float(ing.get("prop_padrao", 0.0)),
        })

    for l in linhas:
        l["part_pct"] = (l["peso_kg"] / peso_total_insumos) if peso_total_insumos > 0 else 0.0

    custo_un_produzido = (custo_total_insumos / rendimento_final) if rendimento_final > 0 else 0.0
    quebra_kg = peso_total_insumos - rendimento_final
    quebra_pct = (quebra_kg / peso_total_insumos) if peso_total_insumos > 0 else 0.0

    mkp_pct = ((preco_venda - custo_un_produzido) / custo_un_produzido) if custo_un_produzido > 0 else 0.0
    mkd_pct = ((preco_venda - custo_un_produzido) / preco_venda) if preco_venda > 0 else 0.0
    venda_total_estimada = rendimento_final * preco_venda

    return {
        "codigo": dados_rec.get("codigo"),
        "produto": dados_rec.get("produto"),
        "rendimento_final": rendimento_final,
        "qtd_pesos_rend": qtd_pesos_rend,
        "preco_venda": preco_venda,
        "peso_total_insumos": peso_total_insumos,
        "custo_total_insumos": custo_total_insumos,
        "custo_un_produzido": custo_un_produzido,
        "quebra_kg": quebra_kg,
        "quebra_pct": quebra_pct,
        "mkp_pct": mkp_pct,
        "mkd_pct": mkd_pct,
        "venda_total_estimada": venda_total_estimada,
        "linhas": linhas,
    }


def calcular_caixaria(dados_cx: dict) -> dict:
    """
    Calcula as 3 tabelas da guia CAIXARIA:
    1. PERDAS: Peso * Custo -> Total da Perca (=SOMA(F4:F28))
    2. SAÍDAS: Peso (=SOMA(K4:K26)) e Total em R$ (=SOMA(M4:M26))
    3. ENTRADAS: Peso Total Entrada (=SOMA(R4:R22)), Custo Médio Saída (M27/L27) e Total Nota (R * S23).
    """
    mapa_custo_cx = {}
    linhas_perdas = []
    total_peso_perda = 0.0
    total_valor_perda = 0.0

    for item in dados_cx.get("perdas_custos", []):
        cod = int(item["codigo"])
        custo = float(item.get("custo_kg", 0.0))
        mapa_custo_cx[cod] = custo
        peso, n_pesos, _, norm_p = parse_pesagens(item.get("pesagens_perda", ""))
        tot = peso * custo
        total_peso_perda += peso
        total_valor_perda += tot
        linhas_perdas.append({
            "codigo": cod,
            "corte": item["corte"],
            "pesagens_perda": item.get("pesagens_perda", ""),
            "qtd_pesagens": n_pesos,
            "peso_kg": peso,
            "custo_kg": custo,
            "total_rs": tot,
        })

    linhas_saidas = []
    total_peso_saida = 0.0   # =SOMA(K4:K26)
    total_valor_saida = 0.0  # =SOMA(M4:M26)

    for item in dados_cx.get("saidas", []):
        cod = int(item["codigo"])
        peso, n_pesos, _, _ = parse_pesagens(item.get("pesagens_saida", ""))
        custo = mapa_custo_cx.get(cod, 0.0)
        tot = peso * custo
        total_peso_saida += peso
        total_valor_saida += tot
        linhas_saidas.append({
            "codigo": cod,
            "corte": item["corte"],
            "pesagens_saida": item.get("pesagens_saida", ""),
            "qtd_pesagens": n_pesos,
            "peso_kg": peso,
            "custo_kg": custo,
            "total_rs": tot,
        })

    # S23 = IFERROR(M27 / L27, 0)
    custo_medio_saida = (total_valor_saida / total_peso_saida) if total_peso_saida > 0 else 0.0

    linhas_entradas = []
    total_peso_entrada = 0.0  # =SOMA(R4:R22)
    total_nota_entrada = 0.0  # =SOMA(S4:S22)

    for item in dados_cx.get("entradas", []):
        cod = int(item["codigo"])
        peso, n_pesos, _, _ = parse_pesagens(item.get("pesagens_entrada", ""))
        t_nota = peso * custo_medio_saida
        custo_ref = mapa_custo_cx.get(cod, 0.0) if peso > 0 else 0.0
        total_peso_entrada += peso
        total_nota_entrada += t_nota
        linhas_entradas.append({
            "codigo": cod,
            "corte": item["corte"],
            "pesagens_entrada": item.get("pesagens_entrada", ""),
            "qtd_pesagens": n_pesos,
            "peso_kg": peso,
            "t_nota_rs": t_nota,
            "custo_medio_rateado": custo_medio_saida if peso > 0 else 0.0,
            "custo_tabela_ref": custo_ref,
        })

    return {
        "linhas_perdas": linhas_perdas,
        "total_peso_perda": total_peso_perda,
        "total_valor_perda": total_valor_perda,
        "linhas_saidas": linhas_saidas,
        "total_peso_saida": total_peso_saida,
        "total_valor_saida": total_valor_saida,
        "custo_medio_saida": custo_medio_saida,
        "linhas_entradas": linhas_entradas,
        "total_peso_entrada": total_peso_entrada,
        "total_nota_entrada": total_nota_entrada,
        "diferenca_peso": total_peso_entrada - total_peso_saida,
    }


def calcular_anotacoes(lista_anot: list) -> tuple[list[dict], float, int]:
    """Calcula a soma de pesagens de todos os itens do Tópico Unificado de Anotações."""
    linhas = []
    soma_geral_kg = 0.0
    total_tickets = 0
    for item in lista_anot:
        peso, n_pesos, _, norm_str = parse_pesagens(item.get("pesagens", ""))
        soma_geral_kg += peso
        total_tickets += n_pesos
        linhas.append({
            "codigo": int(item.get("codigo", 0)),
            "item": item.get("item", ""),
            "origem": item.get("origem", "Geral"),
            "pesagens": item.get("pesagens", ""),
            "pesagens_norm": norm_str,
            "qtd_pesagens": n_pesos,
            "peso_total_kg": peso,
            "observacao": item.get("observacao", ""),
        })
    return linhas, soma_geral_kg, total_tickets


# ==============================================================================
# EXPORTAÇÃO PROFISSIONAL MULTI-ABAS EM EXCEL (.XLSX)
# ==============================================================================

def exportar_relatorio_rendimento_excel(state: dict) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        # 1. Aba BOVINO CONSOLIDADO (+ Preço Médio com Masterboi)
        bov = calcular_consolidado_bovino(state)
        df_bov = pd.DataFrame([
            {
                "Código": l["codigo"],
                "Corte": l["corte"],
                "Peso Diant. (KG)": round(l["peso_dianteiro"], 3),
                "Peso Tras. (KG)": round(l["peso_traseiro"], 3),
                "Peso PA (KG)": round(l["peso_pa"], 3),
                "Peso Boi Casado (KG)": round(l["peso_bovino"], 3),
                "(%) Part. KG": round(l["part_pct"] * 100, 2),
                "R$ Custo Bovino": round(l["custo_bovino"], 2),
                "R$ Venda": round(l["preco_venda"], 2),
                "Venda Total (R$)": round(l["venda_total"], 2),
                "Peso Masterboi/Extra (KG)": round(l["peso_masterboi"], 3),
                "Custo Masterboi/Extra (R$)": round(l["custo_masterboi"], 2),
                "PREÇO MÉDIO FINAL (R$)": round(l["preco_medio_final"], 2),
            }
            for l in bov["linhas"]
        ])
        df_bov.to_excel(writer, sheet_name="BOVINO_CONSOLIDADO", index=False)

        # 2. Abas de Desossa Individuais
        for chave, nome_aba in [
            ("DIANTEIRO", "DIANTEIRO"),
            ("TRASEIRO", "TRASEIRO"),
            ("PONTA_AGULHA", "PONTA_AGULHA"),
            ("DIANTEIRO_MASTERBOI", "DIANT_MASTERBOI"),
            ("PA_MASTERBOI", "PA_MASTERBOI"),
            ("SUINO", "SUINO"),
            ("CARNEIRO", "CARNEIRO"),
        ]:
            part_base = "peca" if chave in ("DIANTEIRO", "DIANTEIRO_MASTERBOI", "CARNEIRO") else "rendimento"
            res = calcular_desossa(state["desossas"][chave], part_base=part_base)
            df_des = pd.DataFrame([
                {
                    "Código": l["codigo"],
                    "Corte": l["corte"],
                    "Pesagens": l["pesagens"],
                    "Qtd Pesagens": l["qtd_pesagens"],
                    "Peso Total (KG)": round(l["peso_kg"], 3),
                    "(%) Part. KG": round(l["part_pct"] * 100, 2),
                    "R$ Custo": round(l["custo_kg"], 2),
                    "R$ Venda": round(l["preco_venda"], 2),
                    "Venda Total (R$)": round(l["venda_total"], 2),
                }
                for l in res["linhas"]
            ])
            df_des.to_excel(writer, sheet_name=nome_aba, index=False)

        # 3. Abas de Receitas
        for chave_rec, nome_aba in [
            ("KIT_FEIJOADA", "KIT_FEIJOADA"),
            ("CARNE_SOL_BOVINA", "CARNE_DE_SOL"),
            ("PANELADA", "PANELADA"),
        ]:
            res_r = calcular_receita(state["receitas"][chave_rec])
            df_r = pd.DataFrame([
                {
                    "Código": l["codigo"],
                    "Ingrediente": l["ingrediente"],
                    "Pesagens": l["pesagens"],
                    "Peso (KG)": round(l["peso_kg"], 3),
                    "R$ Custo/KG": round(l["custo_kg"], 2),
                    "R$ Custo Total": round(l["custo_total"], 2),
                    "(%) Participação": round(l["part_pct"] * 100, 2),
                }
                for l in res_r["linhas"]
            ])
            df_r.to_excel(writer, sheet_name=nome_aba, index=False)

        # 4. Aba CAIXARIA
        res_cx = calcular_caixaria(state["caixaria"])
        df_cx_perdas = pd.DataFrame(res_cx["linhas_perdas"])
        df_cx_saidas = pd.DataFrame(res_cx["linhas_saidas"])
        df_cx_entradas = pd.DataFrame(res_cx["linhas_entradas"])
        df_cx_perdas.to_excel(writer, sheet_name="CAIXARIA_PERDAS", index=False)
        df_cx_saidas.to_excel(writer, sheet_name="CAIXARIA_SAIDAS", index=False)
        df_cx_entradas.to_excel(writer, sheet_name="CAIXARIA_ENTRADAS", index=False)

        # 5. Aba ANOTAÇÕES (Miúdos & Extras)
        linhas_anot, _, _ = calcular_anotacoes(state.get("anotacoes", []))
        df_anot = pd.DataFrame([
            {
                "Código": l["codigo"],
                "Item / Corte": l["item"],
                "Grupo": l["origem"],
                "Pesagens": l["pesagens"],
                "Qtd Pesagens": l["qtd_pesagens"],
                "Peso Total (KG)": round(l["peso_total_kg"], 3),
                "Observação": l["observacao"],
            }
            for l in linhas_anot
        ])
        df_anot.to_excel(writer, sheet_name="ANOTACOES_MIUDOS", index=False)

    return output.getvalue()

