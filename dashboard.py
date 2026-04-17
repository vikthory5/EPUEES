import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Dashboard Escuela de Posgrados",
    page_icon="🎓",
    layout="wide"
)

# --- CONSTANTES ---
# Asegúrate de que este nombre coincida exactamente con tu archivo en la carpeta
FILE_NAME = 'cleaned_indicadores.csv'

ORDEN_CRONOLOGICO = [
    'Ciclo 1-2024', 'Ciclo 2-2024', 
    'Ciclo 1-2025', 'Ciclo 2-2025', 
    'Ciclo 1-2026'
]

# --- CARGA DE DATOS ---
@st.cache_data
def load_clean_data(file_path):
    try:
        df = pd.read_csv(file_path)
        
        # Convertir Ciclo a categórico para mantener el orden cronológico
        df['Ciclo'] = pd.Categorical(
            df['Ciclo'], 
            categories=[c for c in ORDEN_CRONOLOGICO if c in df['Ciclo'].unique()], 
            ordered=True
        )
        return df
    except FileNotFoundError:
        st.error(f"No se encontró el archivo: {file_path}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")
        return pd.DataFrame()

df = load_clean_data(FILE_NAME)

if not df.empty:
    # --- BARRA LATERAL (FILTROS) ---
    st.sidebar.header("🎯 Filtros de Análisis")
    
    # 1. Filtro de Indicador
    indicadores_disponibles = df['Indicador'].unique()
    indicador_selected = st.sidebar.radio("Seleccione el Indicador:", indicadores_disponibles)
    
    # 2. Filtro de Programas
    programas_all = sorted(df['Programa'].unique().tolist())
    programas_selected = st.sidebar.multiselect(
        "Seleccione Programas:", 
        programas_all, 
        default=programas_all[:3] # Selecciona los 3 primeros por defecto
    )
    
    # 3. Filtro de Períodos
    ciclos_disponibles = sorted(df['Ciclo'].unique().tolist())
    ciclos_selected = st.sidebar.multiselect(
        "Seleccione Períodos:", 
        ciclos_disponibles, 
        default=ciclos_disponibles
    )

    # Filtrado dinámico
    mask = (
        (df['Indicador'] == indicador_selected) & 
        (df['Programa'].isin(programas_selected)) &
        (df['Ciclo'].isin(ciclos_selected))
    )
    df_filtered = df[mask].sort_values('Ciclo')

    # --- CUERPO PRINCIPAL ---
    st.title("📊 Dashboard de Indicadores - Posgrados")
    
    if not df_filtered.empty:
        # Métricas principales
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric(f"Total {indicador_selected}", int(df_filtered['Valor'].sum()))
        with m2:
            avg = df_filtered.groupby('Ciclo', observed=True)['Valor'].sum().mean()
            st.metric("Promedio por Ciclo", f"{avg:.1f}")
        with m3:
            st.metric("Programas en Vista", len(programas_selected))

        st.divider()

        # Gráficos
        tab1, tab2, tab3 = st.tabs(["📈 Tendencia", "📊 Comparativa", "📋 Tabla"])

        with tab1:
            fig_line = px.line(
                df_filtered, x='Ciclo', y='Valor', color='Programa',
                markers=True, template="plotly_white",
                title=f"Evolución Temporal: {indicador_selected}"
            )
            st.plotly_chart(fig_line, use_container_width=True)

        with tab2:
            fig_bar = px.bar(
                df_filtered, x='Ciclo', y='Valor', color='Programa',
                barmode='group', text_auto=True, template="plotly_white",
                title=f"Comparativo por Programa"
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        with tab3:
            st.subheader("Detalle de Registros")
            pivot_df = df_filtered.pivot_table(
                index='Programa', columns='Ciclo', values='Valor', 
                aggfunc='sum', observed=True
            ).fillna(0)
            st.dataframe(pivot_df, use_container_width=True)
    else:
        st.info("Ajusta los filtros para visualizar la información.")

else:
    st.warning("El archivo de datos está vacío o no se pudo procesar.")