import streamlit as st

if "lang" not in st.session_state:
    st.session_state["lang"] = "es"

st.write("Current lang:", st.session_state["lang"])

with st.sidebar:
    side_lang = st.radio("Side", ["es", "en", "de"], index=["es", "en", "de"].index(st.session_state["lang"]), key="side")
    if side_lang != st.session_state["lang"]:
        st.session_state["lang"] = side_lang
        st.rerun()

top_lang = st.radio("Top", ["es", "en", "de"], index=["es", "en", "de"].index(st.session_state["lang"]), key="top", horizontal=True)
if top_lang != st.session_state["lang"]:
    st.session_state["lang"] = top_lang
    st.rerun()
