import streamlit as st

def title():
    st.markdown("# Radiation Analysis \n-----")

    introduction = (
        """
        The following project creates a data analysis pipeline to understand trends and exposure to 
        radiation in the form of EMR and EMF. The given app is run via `streamlit`. 
        The web app will take you through the following content - \n
        
        1. Room Analysis
        - Raw Analysis
        - Outlier Analysis
        - Inlier Analyis
        - Exposure Averages
        
        2. Room Graph
        - Averaging graph
        
        """
    )

    submit = (
        "Use the button below to submit files with relevant radiation data."
    )

    st.markdown(introduction)

def draw_all():
    title()