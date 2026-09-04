import streamlit as st
import pandas as pd
from datetime import date
import os
import plotly.express as px

st.set_page_config(page_title="Cadê meu Dinheiro?", layout="centered")

ARQUIVO_DADOS = 'minhas_financas.csv'

def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        df = pd.read_csv(ARQUIVO_DADOS)
        # Garante que a coluna de data seja lida corretamente
        df['Data'] = pd.to_datetime(df['Data']).dt.date
        return df
    else:
        return pd.DataFrame(columns=['Data', 'Tipo', 'Categoria', 'Valor'])

df = carregar_dados()

st.title("Cadê meu Dinheiro? 💸")

# --- FILTRO POR PERÍODO ---
st.subheader("Filtrar Período")
filtro_modo = st.selectbox("Visualizar por:", ["Todos os Registros", "Mês Atual", "Personalizado"])

df_filtrado = df.copy()

if filtro_modo == "Mês Atual":
    hoje = date.today()
    df_filtrado = df[(pd.to_datetime(df['Data']).dt.month == hoje.month) & (pd.to_datetime(df['Data']).dt.year == hoje.year)]
elif filtro_modo == "Personalizado":
    if not df.empty:
        min_data = pd.to_datetime(df['Data']).min()
        max_data = pd.to_datetime(df['Data']).max()
    else:
        min_data = date.today()
        max_data = date.today()
    
    col_d1, col_d2 = st.columns(2)
    data_inicio = col_d1.date_input("Data Inicial", min_data)
    data_fim = col_d2.date_input("Data Final", max_data)
    
    df_filtrado = df[(df['Data'] >= data_inicio) & (df['Data'] <= data_fim)]

st.divider()

# Os cálculos agora respeitam o período filtrado na tela
entradas = df_filtrado[df_filtrado['Tipo'] == 'Entrada']['Valor'].sum()
saidas = df_filtrado[df_filtrado['Tipo'] == 'Saída']['Valor'].sum()
saldo = entradas - saidas

col1, col2, col3 = st.columns(3)
col1.metric("Saldo do Período", f"R$ {saldo:.2f}")
col2.metric("Entradas", f"R$ {entradas:.2f}")
col3.metric("Saídas", f"R$ {saidas:.2f}")

st.divider()

st.subheader("Adicionar Lançamento")
with st.form("form_lancamento", clear_on_submit=True):
    col_tipo, col_data = st.columns(2)
    tipo = col_tipo.selectbox("Tipo", ["Saída", "Entrada"])
    data_lanc = col_data.date_input("Data", date.today())
    
    categorias = [
        "Mercado", 
        "Bebidas", 
        "Jogos", 
        "Lanches", 
        "Contas fixas", 
        "Outros gastos",
        "Renda / Salário"
    ]
    categoria = st.selectbox("Categoria", categorias)
    valor = st.number_input("Valor (R$)", min_value=0.01, format="%.2f")
    
    salvar = st.form_submit_button("Salvar Lançamento", use_container_width=True)
    
    if salvar:
        novo_dado = pd.DataFrame({
            'Data': [data_lanc],
            'Tipo': [tipo],
            'Categoria': [categoria],
            'Valor': [valor]
        })
        df = pd.concat([df, novo_dado], ignore_index=True)
        df.to_csv(ARQUIVO_DADOS, index=False)
        st.success("Lançamento salvo com sucesso.")
        st.rerun()

st.divider()

st.subheader("Resumo de Gastos do Período")
df_saidas = df_filtrado[df_filtrado['Tipo'] == 'Saída']
if not df_saidas.empty:
    fig = px.pie(df_saidas, values='Valor', names='Categoria', hole=0.4)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Nenhuma despesa registrada neste período.")

st.divider()

st.subheader("Histórico e Gerenciamento")
if not df_filtrado.empty:
    st.dataframe(df_filtrado.sort_values(by='Data', ascending=False), use_container_width=True, hide_index=True)
    
    st.markdown("### Excluir Registro")
    opcoes_exclusao = []
    for index, row in df.iterrows(): # Mantém a busca no arquivo geral para segurança do ID
        opcoes_exclusao.append(f"ID {index} | {row['Data']} | {row['Categoria']} | R$ {row['Valor']}")
    
    item_para_excluir = st.selectbox("Selecione o lançamento incorreto:", opcoes_exclusao)
    
    if st.button("Excluir Lançamento Selecionado"):
        indice_real = int(item_para_excluir.split(" | ")[0].replace("ID ", ""))
        df = df.drop(indice_real)
        df.to_csv(ARQUIVO_DADOS, index=False)
        st.success("Registro removido do sistema.")
        st.rerun()
        
else:
    st.info("Nenhum histórico disponível para este filtro.")