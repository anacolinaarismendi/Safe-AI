import streamlit as st

if "lang" not in st.session_state:
    st.session_state["lang"] = "es"

st.write("Current lang:", st.session_state["lang"])

with st.sidebar:
    side_lang = st.radio("Side", ["es", "en", "de"], key="side")
    if side_lang != st.session_state["lang"]:
        st.session_state["lang"] = side_lang
        st.session_state["top"] = side_lang
        st.rerun()

top_lang = st.radio("Top", ["es", "en", "de"], key="top", horizontal=True)
if top_lang != st.session_state["lang"]:
    st.session_state["lang"] = top_lang
    st.session_state["side"] = top_lang
    st.rerun()
