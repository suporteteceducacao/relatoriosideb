import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

# Configuração da página Streamlit
st.set_page_config(
    page_title="Dashboard de Análise",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Adicionando o logotipo na barra lateral
logo_url = 'relatoriosideb/img/Logomarca da Secretaria de Educação 2021.png'
st.sidebar.image(logo_url, width=270)

# Título principal do aplicativo
st.title("📊 Dashboard de Análise de Desempenho por Escola - SAEB/IDEB (2005 - 2023)")
st.markdown("Bem-vindo ao sistema de acesso aos resultados do IDEB e SAEB.")

# Função para carregar os dados
@st.cache_data
def load_data(file_path):
    df = pd.read_excel(file_path)
    # Remove colunas Unnamed se existirem
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    return df

# Carregamento dos dados
try:
    df_ideb = load_data('ideb/xls/ideb.xlsx')
    df_saeb = load_data('ideb/xls/saeb.xlsx')

    # Processamento dos dados
    df_ideb.columns = df_ideb.columns.str.strip()
    df_saeb.columns = df_saeb.columns.str.strip()

    # Converter colunas numéricas
    df_ideb['INEP'] = pd.to_numeric(df_ideb['INEP'], errors='coerce').fillna(0).astype(int).astype(str)
    df_saeb['INEP'] = pd.to_numeric(df_saeb['INEP'], errors='coerce').fillna(0).astype(int).astype(str)

    df_ideb['EDIÇÃO'] = pd.to_numeric(df_ideb['EDIÇÃO'], errors='coerce').fillna(0).astype(int).astype(str)
    df_saeb['EDIÇÃO'] = pd.to_numeric(df_saeb['EDIÇÃO'], errors='coerce').fillna(0).astype(int).astype(str)

    df_ideb['IDEB'] = pd.to_numeric(df_ideb['IDEB'], errors='coerce')
    df_saeb['PROFICIENCIA_MEDIA'] = pd.to_numeric(df_saeb['PROFICIENCIA_MEDIA'], errors='coerce')

except FileNotFoundError as e:
    st.error(f"Erro: Arquivo não encontrado: {e.filename}. Verifique os arquivos.")
    st.stop()

# Função para formatar a variação
def formatar_variacao(valor):
    if valor > 0:
        sinal = "▲"
        cor = "green"
    elif valor < 0:
        sinal = "▼"
        cor = "red"
    else:
        sinal = ""
        cor = "blue"
    return f'<p style="color:{cor};">{sinal} {valor:.2f}</p>'

# Função para criar e exibir gráficos
def criar_grafico(df, escola_nome, variavel, titulo_variavel, etapa=None, componente=None):
    if df.empty:
        return None
    
    # Ordenar edições em ordem crescente
    edicoes_ordenadas = sorted(df['EDIÇÃO'].unique(), key=lambda x: int(x))
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df['EDIÇÃO'], df[variavel], marker='o', linestyle='-', linewidth=2, markersize=8)
    
    # Adicionar rótulos de valores
    for edicao, valor in zip(df['EDIÇÃO'], df[variavel]):
        ax.text(edicao, valor + 0.05, f'{valor:.1f}', ha='center', va='bottom', color='black', fontsize=10)
    
    # Configurar título com informações relevantes
    titulo = f"{titulo_variavel} - {escola_nome}"
    if etapa:
        titulo += f" - {etapa}"
    if componente:
        titulo += f" - {componente}"
    
    ax.set_xlabel('Edição', fontsize=12)
    ax.set_ylabel(titulo_variavel, fontsize=12)
    ax.set_title(titulo)
    ax.set_xticks(edicoes_ordenadas)
    ax.set_xticklabels(edicoes_ordenadas, rotation=45)
    ax.grid(True, linestyle='--', alpha=0.7)
    
    return fig

# Função para download do gráfico
def download_grafico(fig, nome_arquivo):
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=300, bbox_inches='tight')
    buf.seek(0)
    st.download_button(
        label="Download do Gráfico",
        data=buf,
        file_name=nome_arquivo,
        mime="image/png"
    )

# Criar abas para IDEB e SAEB
tab1, tab2, tab3 = st.tabs(["📈 IDEB", "📊 SAEB","🗺️ REGIÕES"])

with tab1:
    # Seletores para IDEB
    col1, col2 = st.columns(2)
    with col1:
        escolas_ideb = df_ideb['ESCOLA'].unique().tolist()
        escolas_ideb.insert(0, 'TODAS')
        escola_selecionada_ideb = st.selectbox("Selecione a ESCOLA (IDEB)", escolas_ideb)
    with col2:
        etapas_ideb = df_ideb['ETAPA'].unique().tolist()
        etapa_selecionada_ideb = st.selectbox("Selecione a ETAPA (IDEB)", etapas_ideb)
    
    # Filtrar dados conforme seletores
    if escola_selecionada_ideb == 'TODAS':
        df_filtrado_ideb = df_ideb.copy()
    else:
        df_filtrado_ideb = df_ideb[df_ideb['ESCOLA'] == escola_selecionada_ideb].copy()
    
    df_filtrado_ideb = df_filtrado_ideb[df_filtrado_ideb['ETAPA'] == etapa_selecionada_ideb].copy()
    
    if df_filtrado_ideb.empty:
        st.warning("Não há dados disponíveis para esta combinação de filtros no IDEB.")
    else:
        # Ordena os dados pela coluna 'EDIÇÃO' em ordem crescente
        df_filtrado_ideb = df_filtrado_ideb.sort_values(by='EDIÇÃO')

        # Título com informações completas
        st.subheader(f"Resultados do IDEB - {escola_selecionada_ideb} - {etapa_selecionada_ideb}")

        # Tabela de resultados do IDEB
        st.dataframe(
            df_filtrado_ideb,
            use_container_width=True,
            column_config={
                "INEP": "INEP",
                "ESCOLA": "ESCOLA",
                "REGIÃO": "REGIÃO",
                "EDIÇÃO": "EDIÇÃO",
                "IDEB": st.column_config.NumberColumn("IDEB", format="%.1f"),
                "ETAPA": "ETAPA",
            },
            hide_index=True,
        )

        # Tabela de diferença entre edições
        st.subheader(f"Variação do IDEB - {etapa_selecionada_ideb}")
        variacao_data = []
        for i in range(1, len(df_filtrado_ideb)):
            edicao_atual = df_filtrado_ideb.iloc[i]['EDIÇÃO']
            edicao_anterior = df_filtrado_ideb.iloc[i - 1]['EDIÇÃO']
            ideb_atual = df_filtrado_ideb.iloc[i]['IDEB']
            ideb_anterior = df_filtrado_ideb.iloc[i - 1]['IDEB']
            diferenca = ideb_atual - ideb_anterior

            variacao_data.append({
                'Comparação': f"{edicao_atual} - {edicao_anterior}",
                'Edição Atual': edicao_atual,
                'IDEB Atual': ideb_atual,
                'Edição Anterior': edicao_anterior,
                'IDEB Anterior': ideb_anterior,
                'Variação': diferenca
            })

        if variacao_data:
            variacao_df = pd.DataFrame(variacao_data)
            # Adiciona colunas de ESCOLA e ETAPA
            variacao_df['ESCOLA'] = escola_selecionada_ideb
            variacao_df['ETAPA'] = etapa_selecionada_ideb
            # Reordena as colunas
            variacao_df = variacao_df[['ESCOLA', 'ETAPA', 'Comparação', 'Edição Atual', 'IDEB Atual', 
                                    'Edição Anterior', 'IDEB Anterior', 'Variação']]
            variacao_df['Variação'] = variacao_df['Variação'].apply(formatar_variacao)
            st.write(variacao_df.to_html(escape=False, index=False), unsafe_allow_html=True)

        # Gráficos
        if not df_filtrado_ideb.empty:
            st.subheader(f"Gráfico do IDEB - {etapa_selecionada_ideb}")
            fig = criar_grafico(df_filtrado_ideb, 
                              escola_selecionada_ideb, 
                              'IDEB', 
                              'IDEB', 
                              etapa_selecionada_ideb)
            if fig:
                st.pyplot(fig)
                download_grafico(fig, f"IDEB_{escola_selecionada_ideb}_{etapa_selecionada_ideb}.png")

with tab2:
    # Seletores para SAEB
    col1, col2, col3 = st.columns(3)
    with col1:
        escolas_saeb = df_saeb['ESCOLA'].unique().tolist()
        escolas_saeb.insert(0, 'TODAS')
        escola_selecionada_saeb = st.selectbox("Selecione a ESCOLA (SAEB)", escolas_saeb)
    with col2:
        etapas_saeb = df_saeb['ETAPA'].unique().tolist()
        etapa_selecionada_saeb = st.selectbox("Selecione a ETAPA (SAEB)", etapas_saeb)
    with col3:
        componentes = df_saeb['COMP_CURRICULAR'].unique().tolist()
        componente_selecionado = st.selectbox("Selecione o COMPONENTE CURRICULAR", componentes)
    
    # Filtrar dados conforme seletores
    if escola_selecionada_saeb == 'TODAS':
        df_filtrado_saeb = df_saeb.copy()
    else:
        df_filtrado_saeb = df_saeb[df_saeb['ESCOLA'] == escola_selecionada_saeb].copy()
    
    df_filtrado_saeb = df_filtrado_saeb[(df_filtrado_saeb['ETAPA'] == etapa_selecionada_saeb) & 
                                      (df_filtrado_saeb['COMP_CURRICULAR'] == componente_selecionado)].copy()
    
    if df_filtrado_saeb.empty:
        st.warning("Não há dados disponíveis para esta combinação de filtros no SAEB.")
    else:
        # Ordena os dados pela coluna 'EDIÇÃO' em ordem crescente
        df_filtrado_saeb = df_filtrado_saeb.sort_values(by='EDIÇÃO')

        # Título com informações completas
        st.subheader(f"Resultados do SAEB - {escola_selecionada_saeb} - {etapa_selecionada_saeb} - {componente_selecionado}")

        # Tabela de resultados do SAEB
        st.dataframe(
            df_filtrado_saeb,
            use_container_width=True,
            column_config={
                "INEP": "INEP",
                "ESCOLA": "ESCOLA",
                "REGIÃO": "REGIÃO",
                "EDIÇÃO": "EDIÇÃO",
                "PROFICIENCIA_MEDIA": st.column_config.NumberColumn("PROFICIÊNCIA MÉDIA", format="%.1f"),
                "COMP_CURRICULAR": "COMPONENTE CURRICULAR",
                "ETAPA": "ETAPA",
            },
            hide_index=True,
        )

        # Tabela de diferença entre edições
        st.subheader(f"Variação da Proficiência Média - {componente_selecionado}")
        variacao_data_saeb = []
        for i in range(1, len(df_filtrado_saeb)):
            edicao_atual = df_filtrado_saeb.iloc[i]['EDIÇÃO']
            edicao_anterior = df_filtrado_saeb.iloc[i - 1]['EDIÇÃO']
            proficiencia_atual = df_filtrado_saeb.iloc[i]['PROFICIENCIA_MEDIA']
            proficiencia_anterior = df_filtrado_saeb.iloc[i - 1]['PROFICIENCIA_MEDIA']
            diferenca = proficiencia_atual - proficiencia_anterior

            variacao_data_saeb.append({
                'Comparação': f"{edicao_atual} - {edicao_anterior}",
                'Edição Atual': edicao_atual,
                'Proficiência Atual': proficiencia_atual,
                'Edição Anterior': edicao_anterior,
                'Proficiência Anterior': proficiencia_anterior,
                'Variação': diferenca
            })

        if variacao_data_saeb:
            variacao_df_saeb = pd.DataFrame(variacao_data_saeb)
            # Adiciona colunas de ESCOLA, ETAPA e COMPONENTE
            variacao_df_saeb['ESCOLA'] = escola_selecionada_saeb
            variacao_df_saeb['ETAPA'] = etapa_selecionada_saeb
            variacao_df_saeb['COMPONENTE'] = componente_selecionado
            # Reordena as colunas
            variacao_df_saeb = variacao_df_saeb[['ESCOLA', 'ETAPA', 'COMPONENTE', 'Comparação', 'Edição Atual', 
                                                'Proficiência Atual', 'Edição Anterior', 'Proficiência Anterior', 'Variação']]
            variacao_df_saeb['Variação'] = variacao_df_saeb['Variação'].apply(formatar_variacao)
            st.write(variacao_df_saeb.to_html(escape=False, index=False), unsafe_allow_html=True)

        # Gráficos
        if not df_filtrado_saeb.empty:
            st.subheader(f"Gráfico de Proficiência Média - {componente_selecionado}")
            fig_saeb = criar_grafico(df_filtrado_saeb, 
                                   escola_selecionada_saeb, 
                                   'PROFICIENCIA_MEDIA', 
                                   f'Proficiência Média ({componente_selecionado})', 
                                   etapa_selecionada_saeb,
                                   componente_selecionado)
            if fig_saeb:
                st.pyplot(fig_saeb)
                download_grafico(fig_saeb, f"SAEB_{escola_selecionada_saeb}_{etapa_selecionada_saeb}_{componente_selecionado}.png")

with tab3:
    st.header("📊 Análise por Região")
    
    # 1. Padronização dos dados de REGIÃO
    def padronizar_regioes(df):
        if 'REGIÃO' in df.columns:
            df['REGIÃO'] = df['REGIÃO'].astype(str).str.strip().str.upper()
            df = df[~df['REGIÃO'].isin(['NAN', '', 'NaN'])]
            return df
        return df
    
    df_ideb = padronizar_regioes(df_ideb)
    df_saeb = padronizar_regioes(df_saeb)
    
    if 'REGIÃO' not in df_ideb.columns or 'REGIÃO' not in df_saeb.columns:
        st.error("Erro: A coluna 'REGIÃO' não foi encontrada nos dados.")
        st.stop()

    # 2. Seletores
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        regioes = sorted(list(set(df_ideb['REGIÃO'].unique().tolist() + df_saeb['REGIÃO'].unique().tolist())))
        regioes.insert(0, 'TODAS')  # Adiciona opção TODAS
        regiao_selecionada = st.selectbox("Selecione a REGIÃO", regioes)
    
    # Seletor de Edição (aparece apenas quando selecionar TODAS as regiões)
    edicoes_disponiveis = []
    if regiao_selecionada == 'TODAS':
        edicoes_ideb = df_ideb['EDIÇÃO'].unique().tolist()
        edicoes_saeb = df_saeb['EDIÇÃO'].unique().tolist()
        edicoes_disponiveis = sorted(list(set(edicoes_ideb + edicoes_saeb)))
        edicao_selecionada = st.selectbox("Selecione a EDIÇÃO para comparar regiões", edicoes_disponiveis)
    
    with col2:
        tipo_indicador = st.selectbox("Selecione o Indicador", ['IDEB', 'SAEB'])
    
    with col3:
        etapas = df_ideb['ETAPA'].unique().tolist() if tipo_indicador == 'IDEB' else df_saeb['ETAPA'].unique().tolist()
        etapa_selecionada = st.selectbox("Selecione a ETAPA", etapas)
    
    with col4:
        componentes = ['-'] if tipo_indicador == 'IDEB' else df_saeb['COMP_CURRICULAR'].unique().tolist()
        componente_selecionado = st.selectbox("Selecione o COMPONENTE", componentes)

    # 3. Processamento dos dados
    try:
        if regiao_selecionada == 'TODAS':
            # Modo comparativo entre regiões para uma edição específica
            if tipo_indicador == 'IDEB':
                df_filtrado = df_ideb[(df_ideb['EDIÇÃO'] == edicao_selecionada) & 
                                    (df_ideb['ETAPA'] == etapa_selecionada)]
                coluna_metric = 'IDEB'
                titulo_metric = 'IDEB'
            else:
                df_filtrado = df_saeb[(df_saeb['EDIÇÃO'] == edicao_selecionada) & 
                                    (df_saeb['ETAPA'] == etapa_selecionada) & 
                                    (df_saeb['COMP_CURRICULAR'] == componente_selecionado)]
                coluna_metric = 'PROFICIENCIA_MEDIA'
                titulo_metric = f'Proficiência em {componente_selecionado}'
            
            if df_filtrado.empty:
                st.warning(f"Não há dados disponíveis para os filtros selecionados.")
            else:
                # Calcula médias por região
                df_medias = df_filtrado.groupby('REGIÃO', as_index=False).agg({
                    coluna_metric: 'mean',
                    'ESCOLA': pd.Series.nunique
                }).rename(columns={coluna_metric: 'MEDIA', 'ESCOLA': 'QTD_ESCOLAS'})
                
                df_medias['MEDIA'] = df_medias['MEDIA'].round(2)
                
                # Gráfico de barras comparativo entre regiões
                st.subheader(f"Comparativo de {titulo_metric} entre Regiões - Edição {edicao_selecionada}")
                
                fig, ax = plt.subplots(figsize=(12, 6))
                bars = ax.bar(df_medias['REGIÃO'], df_medias['MEDIA'], color='skyblue')
                
                # Adiciona rótulos
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                            f'{height:.1f}',
                            ha='center', va='bottom', color='blue', fontsize=10)
                
                ax.set_title(f"Comparativo de {titulo_metric} entre Regiões - Edição {edicao_selecionada}")
                ax.set_xlabel('Região')
                ax.set_ylabel(f'Média {titulo_metric}')
                ax.grid(axis='y', linestyle='--', alpha=0.7)
                
                st.pyplot(fig)
                
                # Botão de download
                buf = BytesIO()
                fig.savefig(buf, format="png", dpi=120, bbox_inches='tight')
                buf.seek(0)
                
                nome_arquivo = f"COMPARATIVO_{tipo_indicador}_EDICAO_{edicao_selecionada}"
                st.download_button(
                    label="⬇️ Download do Gráfico (PNG)",
                    data=buf,
                    file_name=f"{nome_arquivo}.png",
                    mime="image/png"
                )
                
                # Tabela de dados
                st.subheader("📋 Dados por Região")
                st.dataframe(df_medias.sort_values('MEDIA', ascending=False), hide_index=True, use_container_width=True)
        
        else:
            # Modo original (análise de uma região específica)
            if tipo_indicador == 'IDEB':
                df_filtrado = df_ideb[(df_ideb['REGIÃO'] == regiao_selecionada) & 
                                    (df_ideb['ETAPA'] == etapa_selecionada)]
                coluna_metric = 'IDEB'
                titulo_metric = 'IDEB'
            else:
                df_filtrado = df_saeb[(df_saeb['REGIÃO'] == regiao_selecionada) & 
                                    (df_saeb['ETAPA'] == etapa_selecionada) & 
                                    (df_saeb['COMP_CURRICULAR'] == componente_selecionado)]
                coluna_metric = 'PROFICIENCIA_MEDIA'
                titulo_metric = f'Proficiência em {componente_selecionado}'
            
            if df_filtrado.empty:
                st.warning(f"Não há dados disponíveis para os filtros selecionados.")
            else:
                # Cálculo das médias por edição
                df_medias = df_filtrado.groupby('EDIÇÃO', as_index=False).agg({
                    coluna_metric: 'mean',
                    'ESCOLA': pd.Series.nunique
                }).rename(columns={'ESCOLA': 'QTD_ESCOLAS', coluna_metric: 'MEDIA'})
                
                df_medias['MEDIA'] = df_medias['MEDIA'].round(2)
                
                # Gráfico de barras (versão simplificada)
                st.subheader(f"Médias de {titulo_metric} - Região {regiao_selecionada}")
                
                fig, ax = plt.subplots(figsize=(12, 6))
                bars = ax.bar(df_medias['EDIÇÃO'], df_medias['MEDIA'], color='skyblue')
                
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                            f'{height:.1f}',
                            ha='center', va='bottom', color='blue', fontsize=10)
                
                ax.set_title(f"Média de {titulo_metric} - Região {regiao_selecionada}")
                ax.set_xlabel('Edição')
                ax.set_ylabel(f'Média {titulo_metric}')
                ax.grid(axis='y', linestyle='--', alpha=0.7)
                
                st.pyplot(fig)
                
                # Botão de download
                buf = BytesIO()
                fig.savefig(buf, format="png", dpi=120, bbox_inches='tight')
                buf.seek(0)
                
                nome_arquivo = f"{tipo_indicador}_{regiao_selecionada}_{etapa_selecionada}"
                if tipo_indicador == 'SAEB':
                    nome_arquivo += f"_{componente_selecionado}"
                
                st.download_button(
                    label="⬇️ Download do Gráfico (PNG)",
                    data=buf,
                    file_name=f"{nome_arquivo}.png",
                    mime="image/png"
                )
                
                # Resumo estatístico
                st.subheader("📊 Resumo Estatístico")
                
                if tipo_indicador == 'IDEB':
                    df_resumo = df_filtrado.groupby(['EDIÇÃO', 'ETAPA']).agg({
                        'ESCOLA': 'count',
                        'IDEB': ['mean', 'min', 'max', 'std']
                    }).round(1)
                    df_resumo.columns = ['Qtd Escolas', 'Média', 'Mínimo', 'Máximo', 'Desvio Padrão']
                else:
                    df_resumo = df_filtrado.groupby(['EDIÇÃO', 'ETAPA', 'COMP_CURRICULAR']).agg({
                        'ESCOLA': 'count',
                        'PROFICIENCIA_MEDIA': ['mean', 'min', 'max', 'std']
                    }).round(2)
                    df_resumo.columns = ['Qtd Escolas', 'Média', 'Mínimo', 'Máximo', 'Desvio Padrão']
                
                st.dataframe(df_resumo, use_container_width=True)
    
    except Exception as e:
        st.error(f"Erro ao processar os dados: {str(e)}")
