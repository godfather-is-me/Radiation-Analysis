import streamlit as st

import intro
import process

analysis = process.Analysis("microW/m2")

def draw_sidebar():
    topics = [
        "Introduction",
        "Room Analysis",
        "Room Graph"
    ]

    st.sidebar.title("Contents")
    page = st.sidebar.radio("Radio", topics, label_visibility="collapsed")

    if page == topics[0]:
        intro.draw_all()
    if page == topics[1]:
        process.draw_all(analysis)
    if page == topics[2]:
        analysis.calculate_avg()

def draw_main():
    draw_sidebar()

draw_main()