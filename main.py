import streamlit as st

import intro
import process

EMR = process.Analysis("microW/m2")
MF = process.Analysis("mG")
EF = process.Analysis("V/m")

def draw_sidebar():
    topics = [
        "Introduction",
        "EMF Analysis",
        "EMF Graph",
        "EF Analysis",
        "MF Analysis"
    ]

    st.sidebar.title("Contents")
    page = st.sidebar.radio("Radio", topics, label_visibility="collapsed")

    if page == topics[0]:
        intro.draw_all()
    if page == topics[1]:
        process.draw_all(EMR)
    if page == topics[2]:
        EMR.calculate_avg()
    if page == topics[3]:
        process.draw_all(EF)
    if page == topics[4]:
        process.draw_all(MF)


def draw_main():
    draw_sidebar()

draw_main()