import streamlit as st
import pandas as pd
import feedparser
import seaborn as sns
import matplotlib.pyplot as plt

# Configuração da página
st.set_page_config(page_title="Dashboard Financeiro", layout="wide")

# --- CARREGAR DADOS ---
@st.cache_data
def carregar_dados():
    try:
        # Tenta ler xlsx, se falhar tenta xls
        try:
            return pd.read_excel("analises_wacc_Final_Teste_Final_Norm.xlsx")
        except:
            return pd.read_excel("analises_wacc_Final_Teste_Final_Norm.xls")
    except Exception as e:
        st.error(f"Erro ao ler o Excel. Verifique se o arquivo está no GitHub. Erro: {e}")
        return pd.DataFrame()

df = carregar_dados()

if df.empty:
    st.stop()

# --- BARRA LATERAL (CONFIGURAÇÕES) ---
st.sidebar.title("Painel de Controle")

# Criando lista de empresas (baseado no ID ou Nome se tiver coluna Nome)
# Como seu código original usava um mapa manual, vou recriar os principais para exemplo
# O ideal é ter uma coluna 'Nome' no Excel, mas vamos usar a lógica do seu código:
mapa_empresas = {
    "Ambev S/A": 5, "Bradesco": 12, "Petrobras": 65, "Vale": 88, 
    "Weg": 91, "Magaz Luiza": 53, "Itauunibanco": 45
    # Adicione as outras aqui se necessário, ou use df['nome'].unique() se existir a coluna
}
lista_empresas = sorted(list(mapa_empresas.keys()))

empresa_selecionada = st.sidebar.selectbox("Empresa Principal", lista_empresas)
empresa_comparacao = st.sidebar.selectbox("Comparar com", ["Nenhum"] + lista_empresas)

metricas_disponiveis = ['mtb', 'wacc', 'ccp', 'beta', 'lev', 'roa']
metricas_selecionadas = st.sidebar.multiselect("Métricas no Gráfico", metricas_disponiveis, default=['roa', 'wacc'])

# --- FILTRAR DADOS ---
id_principal = mapa_empresas[empresa_selecionada]
df_principal = df[df['id'] == id_principal].sort_values(by='ano')
dados_recentes = df_principal.iloc[-1]

df_comp = None
if empresa_comparacao != "Nenhum":
    id_comp = mapa_empresas[empresa_comparacao]
    df_comp = df[df['id'] == id_comp].sort_values(by='ano')

# --- INTERFACE PRINCIPAL ---
st.title(f"Análise: {empresa_selecionada}")

# Cards de Métricas (KPIs)
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Ano Ref.", int(dados_recentes['ano']))
col2.metric("WACC", f"{dados_recentes.get('wacc',0):.4f}")
col3.metric("ROA", f"{dados_recentes.get('roa',0)*100:.2f}%")
col4.metric("Beta", f"{dados_recentes.get('beta',0):.3f}")
col5.metric("Mkt to Book", f"{dados_recentes.get('mtb',0):.2f}")

# Abas
tab1, tab2, tab3 = st.tabs(["Gráfico Histórico", "Estatísticas", "Notícias"])

with tab1:
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Linhas da Empresa Principal
    for metrica in metricas_selecionadas:
        if metrica in df_principal.columns:
            # Ajuste de escala para ROA (que é %)
            y_data = df_principal[metrica] * 100 if metrica == 'roa' else df_principal[metrica]
            ax.plot(df_principal['ano'], y_data, marker='o', linewidth=2, label=f"{metrica.upper()} - {empresa_selecionada}")

    # Linhas da Comparação
    if df_comp is not None:
        for metrica in metricas_selecionadas:
            if metrica in df_comp.columns:
                y_data = df_comp[metrica] * 100 if metrica == 'roa' else df_comp[metrica]
                ax.plot(df_comp['ano'], y_data, marker='x', linestyle='--', alpha=0.7, label=f"{metrica.upper()} - {empresa_comparacao}")

    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_title("Evolução dos Indicadores")
    st.pyplot(fig)

with tab2:
    st.subheader("Resumo Estatístico")
    st.dataframe(df_principal[metricas_disponiveis].describe())

with tab3:
    st.subheader("Manchetes InfoMoney")
    try:
        feed = feedparser.parse('https://www.infomoney.com.br/feed/')
        for entry in feed.entries[:5]:
            st.write(f"• [{entry.title}]({entry.link})")
    except:
        st.warning("Não foi possível carregar as notícias.")