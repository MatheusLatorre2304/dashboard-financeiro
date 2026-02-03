import streamlit as st
import pandas as pd
import feedparser
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

# Configuração da página para usar tela cheia
st.set_page_config(page_title="Dashboard Profissional", layout="wide")

# Estilo Dark
plt.style.use('dark_background')

# --- FUNÇÃO DE CARREGAMENTO (COM CACHE) ---
@st.cache_data
def carregar_dados():
    try:
        try:
            return pd.read_excel("analises_wacc_Final_Teste_Final_Norm.xlsx")
        except:
            return pd.read_excel("analises_wacc_Final_Teste_Final_Norm.xls")
    except Exception as e:
        st.error(f"Erro ao ler o Excel: {e}")
        return pd.DataFrame()

df = carregar_dados()

if df.empty:
    st.stop()

# --- BARRA LATERAL (CONTROLES) ---
st.sidebar.title("Painel de Análise")

# 1. Seleção de Empresas
mapa_empresas = {
    "Abc Brasil": 1, "Alianscsonae": 2, "Alpargatas": 3, "Alupar": 4, "Ambev S/A": 5,
    "Anima": 6, "Banrisul": 7, "Bbseguridade": 8, "B3": 9, "Americanas": 10,
    "Br Malls Par": 11, "Bradesco": 12, "Bradespar": 13, "Brasil": 14, "Braskem": 15,
    "Brf Sa": 16, "Ccr Sa": 17, "Cemig": 18, "Cesp": 19, "Cielo": 20,
    "Copasa": 21, "Copel": 22, "Cosan": 23, "Cpfl Energia": 24, "Cvc Brasil": 25,
    "Cyrela Realt": 26, "Direcional": 27, "Dexco": 28, "Ecorodovias": 29, "Eletrobras": 30,
    "Embraer": 31, "Energias Br": 32, "Equatorial": 33, "Even": 34, "Eztec": 35,
    "Fleury": 36, "Gafisa": 37, "Gerdau": 38, "Gol": 39, "Grendene": 40,
    "Helbor": 41, "Hypera": 42, "Iguatemi": 43, "Iochp-Maxion": 44, "Itauunibanco": 45,
    "Jbs": 46, "Klabin S/A": 47, "Cogna On": 48, "Light S/A": 49, "Localiza": 50,
    "Lojas Renner": 51, "M.Diasbranco": 52, "Magaz Luiza": 53, "Marcopolo": 54, "Marfrig": 55,
    "Metal Leve": 56, "Mills": 57, "Minerva": 58, "Mrv": 59, "Multiplan": 60,
    "Natura": 61, "Odontoprev": 62, "P.Acucar-Cbd": 63, "Pdg Realt": 64, "Petrobras": 65,
    "Porto Seguro": 66, "Qualicorp": 67, "Raiadrogasil": 68, "Randon Part": 69, "Rumo S.A.": 70,
    "Sabesp": 71, "Sao Martinho": 72, "Santander Br": 73, "Ser Educa": 74, "Sid Nacional": 75,
    "Slc Agricola": 76, "Sul America": 77, "Suzano S.A.": 78, "Taesa": 79, "Tecnisa": 80,
    "Telef Brasil": 81, "Tim": 82, "Totvs": 83, "Tran Paulist": 84, "Tupy": 85,
    "Ultrapar": 86, "Usiminas": 87, "Vale": 88, "Valid": 89, "Via": 90, "Weg": 91
}
lista_empresas = sorted(list(mapa_empresas.keys()))

empresa_principal = st.sidebar.selectbox("Empresa Principal", lista_empresas)
empresa_comparacao = st.sidebar.selectbox("Comparar com", ["Nenhum"] + lista_empresas)

# 2. Seleção de Métricas
metricas_padrao = ['mtb', 'wacc', 'ccp', 'beta', 'lev', 'roa']
metricas_grafico = st.sidebar.multiselect("Métricas (Histórico)", metricas_padrao, default=['roa', 'wacc'])

# --- PROCESSAMENTO ---
id_principal = mapa_empresas[empresa_principal]
df_principal = df[df['id'] == id_principal].sort_values(by='ano')
dados_recentes = df_principal.iloc[-1] if not df_principal.empty else None

df_comp = None
dados_recentes_comp = None
if empresa_comparacao != "Nenhum" and empresa_comparacao in mapa_empresas:
    id_comp = mapa_empresas[empresa_comparacao]
    if id_comp != id_principal:
        df_comp = df[df['id'] == id_comp].sort_values(by='ano')
        dados_recentes_comp = df_comp.iloc[-1] if not df_comp.empty else None

# --- INFO IQ (LATERAL) ---
st.sidebar.markdown("---")
st.sidebar.subheader("Info & Métricas IQ")
st.sidebar.info(f"**{empresa_principal}**")
if dados_recentes is not None:
    st.sidebar.write(f"ROA Recente: **{dados_recentes.get('roa', 0)*100:.2f}%**")
    st.sidebar.progress(min(max(dados_recentes.get('roa', 0), 0.0), 1.0))
    c1, c2 = st.sidebar.columns(2)
    c1.metric("IQG", f"{dados_recentes.get('iqg', 0):.4f}")
    c1.metric("IQ1", f"{dados_recentes.get('iq1', 0):.4f}")
    c2.metric("IQ2", f"{dados_recentes.get('iq2', 0):.4f}")
    c2.metric("QuantMN", f"{dados_recentes.get('quantmn', 0):.4f}")

if dados_recentes_comp is not None:
    st.sidebar.markdown("---")
    st.sidebar.warning(f"**{empresa_comparacao}** (Comp.)")
    st.sidebar.write(f"ROA Recente: **{dados_recentes_comp.get('roa', 0)*100:.2f}%**")
    st.sidebar.progress(min(max(dados_recentes_comp.get('roa', 0), 0.0), 1.0))

# --- NOTÍCIAS (LATERAL) ---
st.sidebar.markdown("---")
st.sidebar.subheader("🗞️ InfoMoney")
try:
    feed = feedparser.parse('https://www.infomoney.com.br/feed/')
    if feed.entries:
        for entry in feed.entries[:5]:
            st.sidebar.markdown(f"• [{entry.title}]({entry.link})")
    else:
        st.sidebar.warning("Sem notícias.")
except Exception as e:
    st.sidebar.error("Erro no feed.")

if st.sidebar.button("Atualizar Feed"):
    st.cache_data.clear()

# --- DASHBOARD PRINCIPAL ---
st.title(f"Dashboard: {empresa_principal}")

# Cards
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Ano", int(dados_recentes['ano']))
col2.metric("Market-to-Book", f"{dados_recentes.get('mtb', 0):.2f}")
col3.metric("WACC", f"{dados_recentes.get('wacc', 0):.4f}")
col4.metric("CCP", f"{dados_recentes.get('ccp', 0):.3f}")
col5.metric("Beta", f"{dados_recentes.get('beta', 0):.3f}")

# Abas (Sem aba de notícias, pois já está na lateral)
abas = st.tabs([
    "Gráfico Histórico", "Métricas IQ", "Volatilidade (Box Plot)", 
    "Scatter (X-Y)", "Correlação", "Resumo", "Dados"
])

with abas[0]: # Histórico
    fig, ax = plt.subplots(figsize=(10, 4))
    for metrica in metricas_grafico:
        if metrica in df_principal.columns:
            y_data = df_principal[metrica] * 100 if metrica == 'roa' else df_principal[metrica]
            label = f"{metrica.upper()} (%)" if metrica == 'roa' else metrica.upper()
            ax.plot(df_principal['ano'], y_data, marker='o', linewidth=2, label=f"{label} - {empresa_principal}")
    if df_comp is not None:
        for metrica in metricas_grafico:
            if metrica in df_comp.columns:
                y_data = df_comp[metrica] * 100 if metrica == 'roa' else df_comp[metrica]
                label = f"{metrica.upper()} (%)" if metrica == 'roa' else metrica.upper()
                ax.plot(df_comp['ano'], y_data, marker='x', linestyle='--', alpha=0.8, label=f"{label} - {empresa_comparacao}")
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.legend(); ax.grid(True, linestyle='--', alpha=0.3); st.pyplot(fig)

with abas[1]: # IQ
    st.subheader("Métricas IQ Recentes")
    metricas_iq = ['iqg', 'iq1', 'iq2', 'quantmn']
    valores_iq = [dados_recentes.get(m, 0) for m in metricas_iq]
    fig_iq, ax_iq = plt.subplots(figsize=(8, 4))
    bars = ax_iq.bar(metricas_iq, valores_iq, color=['#007bff', '#17a2b8', '#28a745', '#ffc107'])
    ax_iq.bar_label(bars, fmt='%.4f'); st.pyplot(fig_iq)

with abas[2]: # BoxPlot
    st.subheader("Distribuição e Volatilidade")
    df_plot = df_principal[metricas_padrao].copy()
    if 'roa' in df_plot.columns: df_plot['roa'] = df_plot['roa'] * 100
    fig_box, ax_box = plt.subplots(figsize=(10, 5))
    sns.boxplot(x='Métrica', y='Valor', data=df_plot.melt(var_name='Métrica', value_name='Valor'), ax=ax_box, palette="coolwarm")
    st.pyplot(fig_box)

with abas[3]: # Scatter
    st.subheader("Análise de Dispersão (X vs Y)")
    col_x, col_y = st.columns(2)
    eixo_x = col_x.selectbox("Eixo X", metricas_padrao, index=4)
    eixo_y = col_y.selectbox("Eixo Y", metricas_padrao, index=5)
    fig_sc, ax_sc = plt.subplots(figsize=(10, 5))
    x_val = df_principal[eixo_x] * 100 if eixo_x == 'roa' else df_principal[eixo_x]
    y_val = df_principal[eixo_y] * 100 if eixo_y == 'roa' else df_principal[eixo_y]
    ax_sc.scatter(x_val, y_val, color='cyan', s=100, alpha=0.8)
    for i, txt in enumerate(df_principal['ano']): ax_sc.annotate(int(txt), (x_val.iloc[i], y_val.iloc[i]), fontsize=9)
    ax_sc.set_xlabel(eixo_x.upper()); ax_sc.set_ylabel(eixo_y.upper()); ax_sc.grid(True, linestyle='--', alpha=0.3)
    st.pyplot(fig_sc)

with abas[4]: # Correlação
    st.subheader("Matriz de Correlação")
    fig_corr, ax_corr = plt.subplots(figsize=(8, 6))
    sns.heatmap(df_principal[metricas_padrao].corr(), annot=True, fmt=".2f", cmap="vlag", ax=ax_corr)
    st.pyplot(fig_corr)

with abas[5]: # Resumo
    st.subheader("Resumo Estatístico")
    st.dataframe(df_principal[metricas_padrao].describe())

with abas[6]: # Dados
    st.subheader("Base de Dados Completa")
    st.dataframe(df_principal[['ano'] + metricas_padrao].style.format("{:.4f}"))
