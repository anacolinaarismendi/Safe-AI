"""
Safe AI — Asistente Clínico Inteligente de Prescripción Segura
================================================================================
Aplicación interactiva Streamlit diseñada para médicos y directores clínicos
del Grupo Hospitalario FritzeFriends.

Incluye soporte multilingüe completo con barra de idiomas (Español, Inglés y Alemán).
"""

from datetime import datetime
from pathlib import Path
import sqlite3
import sys

import altair as alt
import joblib
import pandas as pd
import streamlit as st

# Soporte de importación flexible para traducciones
try:
    from prototype.translations import TRANSLATIONS
except ImportError:
    from translations import TRANSLATIONS

# ---------------------------------------------------------------------------
# Configuración general y rutas
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Safe AI | Asistente Clínico Inteligente",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "hospital.db"
PREPROCESSOR_PATH = BASE_DIR / "prototype" / "models" / "preprocesador.pkl"
MODEL_PATH = BASE_DIR / "prototype" / "models" / "modelo_riesgo.pkl"
FDA_DATA_PATH = BASE_DIR / "data" / "raw" / "openfda_adverse_events.csv"

# Inicializar idioma en session_state
if "lang" not in st.session_state:
    st.session_state["lang"] = "es"

lang = st.session_state["lang"]
t = TRANSLATIONS.get(lang, TRANSLATIONS["es"])

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-title {
        font-size: 2.1rem;
        font-weight: 800;
        color: #005B94;
        margin-bottom: 0.15rem;
    }
    .sub-title {
        font-size: 1.0rem;
        color: #4A5568;
        margin-bottom: 1.2rem;
    }
    .lang-bar-container {
        background: #F1F5F9;
        border-radius: 12px;
        padding: 6px 12px;
        border: 1px solid #CBD5E1;
        display: flex;
        align-items: center;
        justify-content: flex-end;
    }
    .kpi-card {
        background: #F8FAFC;
        border-radius: 12px;
        padding: 1.2rem;
        border-left: 5px solid #005B94;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .alert-card-danger {
        background: #FFF5F5;
        border: 1px solid #FEB2B2;
        border-left: 6px solid #E53E3E;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-bottom: 1rem;
    }
    .alert-card-warning {
        background: #FFFAF0;
        border: 1px solid #FBD38D;
        border-left: 6px solid #DD6B20;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-bottom: 1rem;
    }
    .alert-card-success {
        background: #F0FFF4;
        border: 1px solid #9AE6B4;
        border-left: 6px solid #38A169;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Carga de recursos y modelos
# ---------------------------------------------------------------------------
@st.cache_resource
def cargar_modelos():
    """Carga el preprocesador y el modelo predictivo de riesgo."""
    prep = joblib.load(PREPROCESSOR_PATH) if PREPROCESSOR_PATH.exists() else None
    model = joblib.load(MODEL_PATH) if MODEL_PATH.exists() else None
    return prep, model


def obtener_conexion():
    """Crea una conexión con la base de datos SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@st.cache_data(ttl=60)
def cargar_catalogos():
    """Carga pacientes, médicos, medicamentos e interacciones."""
    with obtener_conexion() as conn:
        pacientes = pd.read_sql("SELECT * FROM Pacientes ORDER BY nombre", conn)
        medicos = pd.read_sql("SELECT * FROM Medicos ORDER BY nombre", conn)
        medicamentos = pd.read_sql("SELECT * FROM Medicamentos ORDER BY principio_activo", conn)
        interacciones = pd.read_sql("SELECT * FROM Interacciones", conn)
    return pacientes, medicos, medicamentos, interacciones


def obtener_medicacion_activa(id_paciente: int):
    """Consulta los medicamentos recetados a un paciente en los últimos 6 meses."""
    query = """
        SELECT DISTINCT m.id_medicamento, m.principio_activo, m.nombre_comercial, r.dosis, c.fecha
        FROM Consultas c
        JOIN Recetas r ON c.id_consulta = r.id_consulta
        JOIN Medicamentos m ON r.id_medicamento = m.id_medicamento
        WHERE c.id_paciente = ?
        ORDER BY c.fecha DESC
        LIMIT 6
    """
    with obtener_conexion() as conn:
        df_activa = pd.read_sql(query, conn, params=(id_paciente,))
    return df_activa


def verificar_interacciones_deterministas(ids_medicamentos: list[int]):
    """Cruza los medicamentos seleccionados contra la tabla de Interacciones."""
    if len(ids_medicamentos) < 2:
        return []

    placeholders = ",".join(["?"] * len(ids_medicamentos))
    query = f"""
        SELECT 
            i.id_interaccion, i.gravedad, i.descripcion,
            m1.principio_activo AS med1, m1.nombre_comercial AS com1,
            m2.principio_activo AS med2, m2.nombre_comercial AS com2
        FROM Interacciones i
        JOIN Medicamentos m1 ON i.id_medicamento_1 = m1.id_medicamento
        JOIN Medicamentos m2 ON i.id_medicamento_2 = m2.id_medicamento
        WHERE (i.id_medicamento_1 IN ({placeholders}) AND i.id_medicamento_2 IN ({placeholders}))
    """
    with obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(query, ids_medicamentos + ids_medicamentos)
        filas = cursor.fetchall()

    return [dict(f) for f in filas]


# ---------------------------------------------------------------------------
# Sidebar: Barra de Idioma y Acceso Rápido
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🌐 " + t["lang_bar_label"])
    side_lang = st.radio(
        "Selector de idioma sidebar",
        options=["es", "en", "de"],
        format_func=lambda x: {"es": "🇪🇸 Español", "en": "🇬🇧 English", "de": "🇩🇪 Deutsch"}[x],
        index=["es", "en", "de"].index(st.session_state["lang"]),
        key="sidebar_lang_select",
        label_visibility="collapsed"
    )
    if side_lang != st.session_state["lang"]:
        st.session_state["lang"] = side_lang
        st.session_state["top_lang_bar"] = side_lang
        st.session_state["top_lang_radio"] = side_lang
        st.rerun()

    st.divider()
    st.markdown("🏥 **Safe AI Clinical Suite**")
    st.caption("Grupo Hospitalario FritzeFriends\n\n*CDSS Real-Time Audit*")
    st.caption("Latency: < 200 ms | FAERS FDA")


# ---------------------------------------------------------------------------
# Header Institucional con Barra de Idiomas Superior
# ---------------------------------------------------------------------------
col_logo, col_header, col_lang = st.columns([0.8, 5.0, 2.2])
with col_logo:
    st.markdown("<h1 style='text-align: center; font-size: 3.4rem; margin:0;'>🛡️</h1>", unsafe_allow_html=True)
with col_header:
    st.markdown(f"<div class='main-title'>{t['main_title']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub-title'>{t['sub_title']}</div>", unsafe_allow_html=True)
with col_lang:
    st.markdown(f"<div style='text-align: right; margin-bottom: 3px; font-weight: 700; color: #005B94; font-size: 0.85rem;'>🌐 {t['lang_bar_label']}</div>", unsafe_allow_html=True)
    if hasattr(st, "segmented_control"):
        top_lang = st.segmented_control(
            "Top Language Bar",
            options=["es", "en", "de"],
            format_func=lambda x: {"es": "🇪🇸 ES", "en": "🇬🇧 EN", "de": "🇩🇪 DE"}[x],
            default=st.session_state["lang"],
            key="top_lang_bar",
            label_visibility="collapsed"
        )
        if top_lang and top_lang != st.session_state["lang"]:
            st.session_state["lang"] = top_lang
            st.session_state["sidebar_lang_select"] = top_lang
            st.rerun()
    else:
        top_lang = st.radio(
            "Top Language Bar",
            options=["es", "en", "de"],
            format_func=lambda x: {"es": "🇪🇸 ES", "en": "🇬🇧 EN", "de": "🇩🇪 DE"}[x],
            index=["es", "en", "de"].index(st.session_state["lang"]),
            horizontal=True,
            key="top_lang_radio",
            label_visibility="collapsed"
        )
        if top_lang != st.session_state["lang"]:
            st.session_state["lang"] = top_lang
            st.session_state["sidebar_lang_select"] = top_lang
            st.rerun()


# ---------------------------------------------------------------------------
# Carga de datos
# ---------------------------------------------------------------------------
df_pacientes, df_medicos, df_medicamentos, df_interacciones = cargar_catalogos()
preprocessor, model = cargar_modelos()

@st.cache_data(ttl=300)
def cargar_eventos_fda():
    """Carga los eventos adversos reales descargados desde OpenFDA FAERS."""
    if FDA_DATA_PATH.exists():
        return pd.read_csv(FDA_DATA_PATH)
    return pd.DataFrame()


# Tabs de navegación multilingües
tab_prescripcion, tab_dashboard, tab_vademecum, tab_openfda = st.tabs([
    t["tab_prescripcion"],
    t["tab_dashboard"],
    t["tab_vademecum"],
    t["tab_openfda"]
])

# ===========================================================================
# TAB 1: CONSULTA Y PRESCRIPCIÓN CLÍNICA
# ===========================================================================
with tab_prescripcion:
    col_izq, col_der = st.columns([1, 1.4], gap="large")

    with col_izq:
        st.subheader(t["sec1_patient"])
        
        # Selector de Paciente
        opciones_pacientes = {
            f"{row['nombre']} (ID: {row['id_paciente']} - {row['edad']} {t['years']})": row["id_paciente"]
            for _, row in df_pacientes.iterrows()
        }
        paciente_sel = st.selectbox(t["select_patient"], list(opciones_pacientes.keys()))
        id_paciente_actual = opciones_pacientes[paciente_sel]
        datos_paciente = df_pacientes[df_pacientes["id_paciente"] == id_paciente_actual].iloc[0]

        # Resumen del paciente
        col_p1, col_p2, col_p3 = st.columns(3)
        col_p1.metric(t["age"], f"{datos_paciente['edad']} {t['years']}")
        gender_display = t["gender_m"] if datos_paciente["genero"] == "M" else t["gender_f"]
        col_p2.metric(t["gender"], gender_display)
        col_p3.metric(t["condition"], datos_paciente["condiciones_previas"])

        # Médico y Especialidad
        st.divider()
        st.subheader(t["sec2_doctor"])
        opciones_medicos = {
            f"{row['nombre']} — {row['especialidad']}": row["id_medico"]
            for _, row in df_medicos.iterrows()
        }
        medico_sel = st.selectbox(t["select_doctor"], list(opciones_medicos.keys()))
        id_medico_actual = opciones_medicos[medico_sel]
        datos_medico = df_medicos[df_medicos["id_medico"] == id_medico_actual].iloc[0]

        # Medicación previa activa del paciente
        st.divider()
        st.subheader(t["sec3_active_meds"])
        df_activa = obtener_medicacion_activa(id_paciente_actual)
        if not df_activa.empty:
            st.info(t["active_meds_found"].format(count=len(df_activa)))
            for _, m in df_activa.iterrows():
                st.markdown(f"- 💊 **{m['principio_activo']}** *({m['nombre_comercial']})* — `{m['dosis']}` *({t['date_label']}: {m['fecha']})*")
        else:
            st.success(t["no_active_meds"])

    with col_der:
        st.subheader(t["sec4_new_rx"])
        
        diagnostico = st.text_input(t["diagnosis_label"], value=t["diagnosis_default"])

        # Multiselect de nuevos medicamentos
        dict_meds = {
            f"{row['principio_activo']} ({row['nombre_comercial']})": row["id_medicamento"]
            for _, row in df_medicamentos.iterrows()
        }
        
        meds_seleccionados = st.multiselect(
            t["select_meds_label"],
            options=list(dict_meds.keys()),
            help=t["select_meds_help"]
        )

        ids_nuevos = [dict_meds[m] for m in meds_seleccionados]
        ids_activos = df_activa["id_medicamento"].tolist() if not df_activa.empty else []
        ids_totales_paciente = list(set(ids_activos + ids_nuevos))

        num_total_farmacos = len(ids_totales_paciente)

        st.divider()
        st.subheader(t["sec5_audit"])

        if not meds_seleccionados:
            st.warning(t["warn_no_meds"])
        else:
            # 1. Detección Determinista (Reglas Vademécum)
            conflictos = verificar_interacciones_deterministas(ids_totales_paciente)

            if conflictos:
                for c in conflictos:
                    gravedad = c["gravedad"].lower()
                    if gravedad == "grave":
                        st.markdown(f"""
                        <div class='alert-card-danger'>
                            <h4 style='color: #C53030; margin:0 0 5px 0;'>{t['alert_danger_title']}</h4>
                            <b>{t['danger_combo']}</b> {c['med1']} ({c['com1']}) + {c['med2']} ({c['com2']})<br>
                            <b>{t['adverse_effect']}</b> {c['descripcion']}<br>
                            <b>{t['clinical_rec']}</b> <i>{t['danger_rec_text']}</i>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class='alert-card-warning'>
                            <h4 style='color: #DD6B20; margin:0 0 5px 0;'>{t['alert_warning_title']}</h4>
                            <b>{t['warning_combo']}</b> {c['med1']} ({c['com1']}) + {c['med2']} ({c['com2']})<br>
                            <b>{t['adverse_effect']}</b> {c['descripcion']}<br>
                            <b>{t['clinical_rec']}</b> <i>{t['warning_rec_text']}</i>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class='alert-card-success'>
                    <h4 style='color: #276749; margin:0 0 5px 0;'>{t['alert_success_title']}</h4>
                    {t['alert_success_desc']}
                </div>
                """, unsafe_allow_html=True)

            # 2. Score Predictivo de Riesgo (Machine Learning)
            if preprocessor and model:
                st.markdown(f"#### {t['ml_title']}")
                hoy = datetime.now()
                es_fin_de_semana = 1 if hoy.weekday() in [5, 6] else 0

                input_data = pd.DataFrame([{
                    "edad": int(datos_paciente["edad"]),
                    "num_medicamentos": num_total_farmacos,
                    "mes_consulta": hoy.month,
                    "genero": datos_paciente["genero"].lower().strip(),
                    "condiciones_previas": datos_paciente["condiciones_previas"].lower().strip(),
                    "especialidad": datos_medico["especialidad"].lower().strip(),
                    "es_fin_de_semana": es_fin_de_semana,
                    "es_polifarmacia": int(num_total_farmacos >= 3)
                }])

                try:
                    input_proc = preprocessor.transform(input_data)
                    prob_riesgo = float(model.predict_proba(input_proc)[0, 1])
                    pct_riesgo = round(prob_riesgo * 100, 1)

                    col_m1, col_m2 = st.columns([1, 2])
                    with col_m1:
                        if pct_riesgo >= 60:
                            st.metric(t["ml_metric_label"], f"{pct_riesgo}%", delta=t["high_risk"], delta_color="inverse")
                        elif pct_riesgo >= 35:
                            st.metric(t["ml_metric_label"], f"{pct_riesgo}%", delta=t["mod_risk"], delta_color="off")
                        else:
                            st.metric(t["ml_metric_label"], f"{pct_riesgo}%", delta=t["low_risk"])

                    with col_m2:
                        st.progress(prob_riesgo)
                        if num_total_farmacos >= 3:
                            st.caption(t["polypharmacy_alert"])
                except Exception as e:
                    st.caption(f"Error: {e}")

            # Botón de Confirmación
            st.divider()
            col_b1, col_b2 = st.columns([1.5, 1])
            with col_b1:
                confirmar = st.button(t["btn_save_ehr"], type="primary", use_container_width=True)
                if confirmar:
                    try:
                        with obtener_conexion() as conn:
                            cur = conn.cursor()
                            fecha_hoy = datetime.now().strftime("%Y-%m-%d")
                            cur.execute(
                                "INSERT INTO Consultas (id_paciente, id_medico, fecha, diagnostico) VALUES (?, ?, ?, ?)",
                                (id_paciente_actual, id_medico_actual, fecha_hoy, diagnostico)
                            )
                            id_nueva_consulta = cur.lastrowid

                            for id_m in ids_nuevos:
                                cur.execute(
                                    "INSERT INTO Recetas (id_consulta, id_medicamento, dosis) VALUES (?, ?, ?)",
                                    (id_nueva_consulta, id_m, "1 dosis c/8h s/indicación")
                                )
                            conn.commit()
                        st.success(t["msg_consult_saved"].format(id=id_nueva_consulta))
                        st.cache_data.clear()
                    except Exception as err:
                        st.error(t["msg_save_error"].format(err=err))
            with col_b2:
                if st.button(t["btn_new_consult"], use_container_width=True):
                    st.rerun()


# ===========================================================================
# TAB 2: DASHBOARD Y MÉTRICAS HOSPITALARIAS
# ===========================================================================
with tab_dashboard:
    st.subheader(t["dash_title"])
    
    with obtener_conexion() as conn:
        total_pacientes = conn.execute("SELECT COUNT(*) FROM Pacientes").fetchone()[0]
        total_medicos = conn.execute("SELECT COUNT(*) FROM Medicos").fetchone()[0]
        total_consultas = conn.execute("SELECT COUNT(*) FROM Consultas").fetchone()[0]
        total_recetas = conn.execute("SELECT COUNT(*) FROM Recetas").fetchone()[0]
        query_alertas = """
            SELECT COUNT(DISTINCT c.id_consulta)
            FROM Consultas c
            JOIN Recetas r1 ON c.id_consulta = r1.id_consulta
            JOIN Recetas r2 ON c.id_consulta = r2.id_consulta AND r1.id_receta < r2.id_receta
            JOIN Interacciones i
              ON (r1.id_medicamento = i.id_medicamento_1 AND r2.id_medicamento = i.id_medicamento_2)
              OR (r1.id_medicamento = i.id_medicamento_2 AND r2.id_medicamento = i.id_medicamento_1)
        """
        consultas_con_alerta = conn.execute(query_alertas).fetchone()[0]
        tasa_alertas = (consultas_con_alerta / total_consultas * 100) if total_consultas > 0 else 0

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric(t["kpi_patients"], f"{total_pacientes}", t["kpi_cohort"])
    kpi2.metric(t["kpi_consults"], f"{total_consultas}", t["kpi_last_year"])
    kpi3.metric(t["kpi_prescriptions"], f"{total_recetas}", f"{total_recetas/total_consultas:.1f} {t['kpi_per_consult']}")
    kpi4.metric(t["kpi_alert_rate"], f"{tasa_alertas:.1f}%", t["kpi_malpractice"])

    st.divider()
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.markdown(f"##### {t['chart_esp_title']}")
        with obtener_conexion() as conn:
            df_esp = pd.read_sql("""
                SELECT m.especialidad, COUNT(c.id_consulta) AS total_consultas
                FROM Consultas c
                JOIN Medicos m ON c.id_medico = m.id_medico
                GROUP BY m.especialidad
            """, conn)
        
        chart_esp = alt.Chart(df_esp).mark_bar(color="#005B94", cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
            x=alt.X("especialidad:N", title=t["chart_esp_x"]),
            y=alt.Y("total_consultas:Q", title=t["chart_esp_y"]),
            tooltip=["especialidad", "total_consultas"]
        ).properties(height=300)
        st.altair_chart(chart_esp, use_container_width=True)

    with col_g2:
        st.markdown(f"##### {t['chart_meds_title']}")
        with obtener_conexion() as conn:
            df_top_meds = pd.read_sql("""
                SELECT m.principio_activo, COUNT(r.id_receta) AS prescripciones
                FROM Recetas r
                JOIN Medicamentos m ON r.id_medicamento = m.id_medicamento
                GROUP BY m.principio_activo
                ORDER BY prescripciones DESC
                LIMIT 15
            """, conn)

        chart_meds = alt.Chart(df_top_meds).mark_bar(color="#00A896", cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
            x=alt.X("prescripciones:Q", title=t["chart_meds_x"]),
            y=alt.Y("principio_activo:N", sort="-x", title=t["chart_meds_y"]),
            tooltip=["principio_activo", "prescripciones"]
        ).properties(height=300)
        st.altair_chart(chart_meds, use_container_width=True)

    st.markdown("---")
    st.info(f"""
    💡 **{t['dash_title']}:**
    {t['dash_info_p1']}
    {t['dash_info_p2']}
    """)


# ===========================================================================
# TAB 3: VADEMÉCUM Y MATRIZ DE INTERACCIONES
# ===========================================================================
with tab_vademecum:
    st.subheader(t["vad_title"])

    col_v1, col_v2 = st.columns([1, 1.2], gap="large")

    with col_v1:
        st.markdown(f"##### {t['vad_auth_title']}")
        st.dataframe(
            df_medicamentos.rename(columns={
                "id_medicamento": t["vad_col_id"],
                "principio_activo": t["vad_col_active"],
                "nombre_comercial": t["vad_col_brand"]
            }),
            use_container_width=True,
            hide_index=True
        )

    with col_v2:
        st.markdown(f"##### {t['vad_matrix_title']}")
        with obtener_conexion() as conn:
            df_int_view = pd.read_sql("""
                SELECT 
                    m1.principio_activo AS "F1",
                    m2.principio_activo AS "F2",
                    UPPER(i.gravedad) AS "Gravedad",
                    i.descripcion AS "Efecto"
                FROM Interacciones i
                JOIN Medicamentos m1 ON i.id_medicamento_1 = m1.id_medicamento
                JOIN Medicamentos m2 ON i.id_medicamento_2 = m2.id_medicamento
                ORDER BY i.gravedad DESC
            """, conn)
            
        df_int_display = df_int_view.rename(columns={
            "F1": t["vad_col_drug1"],
            "F2": t["vad_col_drug2"],
            "Gravedad": t["vad_col_severity"],
            "Efecto": t["vad_col_effect"]
        })
        st.dataframe(df_int_display, use_container_width=True, hide_index=True)

    st.divider()
    st.markdown(f"##### {t['vad_add_title']}")
    with st.expander(t["vad_expander"]):
        with st.form("form_nueva_interaccion"):
            c_i1, c_i2, c_i3 = st.columns(3)
            with c_i1:
                med1_choice = st.selectbox(t["vad_med1"], df_medicamentos["principio_activo"].tolist(), key="n_m1")
            with c_i2:
                med2_choice = st.selectbox(t["vad_med2"], df_medicamentos["principio_activo"].tolist(), key="n_m2")
            with c_i3:
                sev_options = [t["sev_mild"], t["sev_moderate"], t["sev_severe"]]
                gravedad_choice = st.selectbox(t["vad_severity"], sev_options)
            
            desc_choice = st.text_area(t["vad_desc_label"])
            btn_guardar_int = st.form_submit_button(t["vad_submit_btn"])

            if btn_guardar_int:
                id1 = int(df_medicamentos[df_medicamentos["principio_activo"] == med1_choice]["id_medicamento"].iloc[0])
                id2 = int(df_medicamentos[df_medicamentos["principio_activo"] == med2_choice]["id_medicamento"].iloc[0])

                if id1 == id2:
                    st.error(t["vad_same_err"])
                else:
                    # Mapear gravedad a español estándar en BD
                    sev_map = {
                        t["sev_mild"]: "leve",
                        t["sev_moderate"]: "moderada",
                        t["sev_severe"]: "grave"
                    }
                    gravedad_db = sev_map.get(gravedad_choice, "moderada")
                    id_min, id_max = min(id1, id2), max(id1, id2)
                    try:
                        with obtener_conexion() as conn:
                            cur = conn.cursor()
                            cur.execute(
                                "INSERT OR REPLACE INTO Interacciones (id_medicamento_1, id_medicamento_2, gravedad, descripcion) VALUES (?, ?, ?, ?)",
                                (id_min, id_max, gravedad_db, desc_choice)
                            )
                            conn.commit()
                        st.success(t["vad_success"].format(med1=med1_choice, med2=med2_choice))
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")


# ===========================================================================
# TAB 4: FARMACOVIGILANCIA REAL — OPENFDA FAERS
# ===========================================================================
with tab_openfda:
    st.subheader(t["fda_title"])
    st.markdown(t["fda_desc"])

    df_fda = cargar_eventos_fda()
    if df_fda.empty:
        st.warning(t["fda_no_data"])
    else:
        # Métricas agregadas de OpenFDA
        total_reportes = len(df_fda)
        pct_hosp = (df_fda["hospitalizacion"].sum() / total_reportes) * 100
        pct_vital = (df_fda["riesgo_vital"].sum() / total_reportes) * 100
        pct_muerte = (df_fda["muerte"].sum() / total_reportes) * 100

        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        col_f1.metric(t["fda_kpi_reports"], f"{total_reportes:,}", t["fda_kpi_cohort"])
        col_f2.metric(t["fda_kpi_hosp"], f"{pct_hosp:.1f}%", t["fda_kpi_severe"])
        col_f3.metric(t["fda_kpi_life"], f"{pct_vital:.1f}%", t["fda_kpi_crit"])
        col_f4.metric(t["fda_kpi_death"], f"{pct_muerte:.1f}%", t["fda_kpi_cases"])

        st.divider()

        col_filtro1, col_filtro2 = st.columns([1.5, 2])
        with col_filtro1:
            farmacos_disponibles = [t["fda_all"]] + sorted(df_fda["farmaco_buscado"].dropna().unique().tolist())
            farmaco_filtro = st.selectbox(t["fda_filter_drug"], farmacos_disponibles)
        with col_filtro2:
            solo_hosp = st.checkbox(t["fda_only_hosp"], value=False)

        df_filtrado = df_fda.copy()
        if farmaco_filtro != t["fda_all"]:
            df_filtrado = df_filtrado[df_filtrado["farmaco_buscado"] == farmaco_filtro]
        if solo_hosp:
            df_filtrado = df_filtrado[(df_filtrado["hospitalizacion"] == 1) | (df_filtrado["riesgo_vital"] == 1)]

        st.markdown(f"##### {t['fda_found'].format(count=len(df_filtrado))}")

        columnas_mostrar = [
            "report_id", "farmaco_buscado", "edad", "genero", "num_medicamentos",
            "medicamentos", "reaccion_adversa", "hospitalizacion", "riesgo_vital"
        ]
        df_display = df_filtrado[[c for c in columnas_mostrar if c in df_filtrado.columns]].rename(columns={
            "report_id": t["fda_col_id"],
            "farmaco_buscado": t["fda_col_drug"],
            "edad": t["fda_col_age"],
            "genero": t["fda_col_gender"],
            "num_medicamentos": t["fda_col_num_meds"],
            "medicamentos": t["fda_col_concomitant"],
            "reaccion_adversa": t["fda_col_reaction"],
            "hospitalizacion": t["fda_col_hosp"],
            "riesgo_vital": t["fda_col_vital"]
        })

        st.dataframe(df_display, use_container_width=True, hide_index=True)

        st.info(t["fda_notice"])
