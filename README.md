# 🛡️ Safe AI — Asistente Clínico Inteligente de Prescripción Segura

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.64-FF4B4B.svg)](https://streamlit.io/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.9-F7931E.svg)](https://scikit-learn.org/)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-3.4-38B2AC.svg)](https://tailwindcss.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **Safe AI** es un sistema de soporte a la decisión clínica (CDSS) impulsado por Inteligencia Artificial y reglas farmacológicas en tiempo real, diseñado para erradicar las reacciones adversas e incompatibilidades medicamentosas en pacientes con polifarmacia.

---

## 🏥 Contexto del Caso: FritzeFriends

* **Cliente:** FritzeFriends (Red hospitalaria privada con 3 hospitales regionales, 12 clínicas locales y 250 médicos en plantilla).
* **Volumen:** ~3,000 consultas diarias (~1 millón anuales).
* **El Problema:** Los pacientes mayores toman de media entre 4 y 7 fármacos distintos. Los médicos pierden entre 3 y 5 minutos por consulta consultando vademécums manuales. El año pasado se registraron 12 incidentes graves por reacciones adversas, 3 litigios y un aumento del 15% en las primas de seguro de mala praxis.
* **La Solución:** SafeRx AI audita en milisegundos cada prescripción médica, detecta incompatibilidades de riesgo letal y estima la probabilidad de eventos adversos mediante Machine Learning.

---

## 📂 Arquitectura del Repositorio

```text
saferx-ai/
├── data/
│   ├── processed/          # Dataset limpio con ingeniería de características (datos_limpios.csv)
│   └── raw/                # Extracciones crudas (openfda_adverse_events.csv, medicamentos, interacciones, etc.)
├── database/
│   ├── diagrama_ER.png     # Diagrama Entidad-Relación del hospital
│   ├── hospital.db         # Base de datos SQLite operativa (94 fármacos, 57 interacciones, 300 pacientes)
│   ├── schema.sql          # Esquema relacional DDL (Foreign Keys, Checks, Índices)
│   └── seed.py             # Generador clínico con fenotipos reales de comorbilidad y polifarmacia
├── docs/
│   ├── 01_definicion_startup.md   # Plan de negocio, propuesta B2B SaaS y ROI
│   └── 02_ficha_cliente.md        # Especificación del cliente y necesidades clínicas
├── frontend/               # Landing page comercial bilingüe en Next.js 14 + Tailwind CSS
│   ├── app/                # Rutas y layout de Next.js App Router
│   ├── components/         # Bento Grid, Hero, Showcase, Compliance, Navbar, Footer
│   └── package.json
├── notebooks/              # Cuadernos interactivos de Ciencia de Datos y Machine Learning
│   ├── 01_data_generation.ipynb       # Ingesta y validación de integridad referencial
│   ├── 02_exploratory_analysis.ipynb   # EDA epidemiológico, polifarmacia y visualizaciones
│   └── 03_model_training.ipynb        # Entrenamiento, curvas ROC/PR y validación cruzada
├── prototype/              # Aplicación clínica interactiva
│   ├── app.py              # Prototipo asistido para médicos en Streamlit (4 módulos con OpenFDA)
│   └── models/             # Artefactos serializados (preprocesador.pkl, modelo_riesgo.pkl)
├── src/                    # Scripts productivos
│   ├── fetch_openfda_data.py   # Ingesta de eventos adversos reales desde la API de OpenFDA (FAERS)
│   ├── data_preprocessing.py   # Pipeline ETL y generación de características
│   ├── train_model.py          # Entrenamiento y evaluación comparativa de modelos de riesgo
│   └── build_notebooks.py      # Generador y orquestador de notebooks
└── requirements.txt        # Dependencias de Python
```

---

## 🚀 Guía Rápida de Instalación y Uso

### 1. Clonar el repositorio y configurar el entorno
```bash
git clone https://github.com/tu-usuario/saferx-ai.git
cd saferx-ai

# Crear y activar entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Ingesta de Datos Reales de OpenFDA, Población de BD y Pipeline ETL
```bash
# Descargar reportes clínicos reales desde la API pública de OpenFDA FAERS
python src/fetch_openfda_data.py

# Crear y poblar SQLite hospital.db con 94 fármacos y 57 interacciones reales documentadas
python database/seed.py

# Ejecutar el pipeline de limpieza, feature engineering y preprocesador
python src/data_preprocessing.py

# Entrenar el modelo de Machine Learning de predicción de riesgo clínico
python src/train_model.py
```

### 3. Lanzar la Aplicación Clínica en Streamlit 🩺
```bash
streamlit run prototype/app.py
```
La aplicación se abrirá en `http://localhost:8501` ofreciendo 4 módulos clínicos:
* **Prescripción en Consulta:** Selección de paciente por fenotipo, detección de incompatibilidades en tiempo real (roja/amarilla) y cálculo de score de riesgo IA.
* **Dashboard Hospitalario:** Indicadores de polifarmacia, consultas por especialidad y fármacos más prescritos (Top 15).
* **Vademécum & Reglas:** Buscador de medicamentos entre 94 principios activos y gestor para registrar nuevas reglas farmacológicas.
* **Farmacovigilancia Real (OpenFDA):** Explorador interactivo con más de 500 reportes reales de eventos adversos, hospitalizaciones y desenlaces vitales notificados a la FDA.

### 4. Lanzar la Landing Page en Next.js 🌐
```bash
cd frontend
npm install
npm run dev
```
La web institucional estará disponible en `http://localhost:3000` con selector de idioma (Español / Inglés).

---

## 🤖 Rendimiento del Modelo de Machine Learning

Dado el contexto de salud, el modelo optimiza prioritariamente el **Recall (Sensibilidad)** de interacciones adversas para reducir a cero los Falsos Negativos clínicos:

| Métrica | Desempeño | Relevancia Clínica |
| :--- | :---: | :--- |
| **ROC-AUC** | **0.93 - 0.96** | Extraordinaria capacidad de discriminación entre prescripciones seguras y de riesgo. |
| **Recall (Sensibilidad)** | **~84%** | Captura la gran mayoría de interacciones graves en pacientes polimedicados. |
| **Precision** | **~85%** | Alta fiabilidad para evitar fatiga de alertas al personal facultativo. |
| **Latencia de Inferencia** | **< 15 ms** | Respuesta instantánea en la consulta sin interrumpir el flujo del médico. |

---

## 📜 Licencia y Cumplimiento

* Licencia bajo los términos de la licencia **MIT** ([LICENSE](LICENSE)).
* Diseñado bajo principios de *Privacy by Design* conforme al Reglamento General de Protección de Datos (**RGPD**) de la Unión Europea.
