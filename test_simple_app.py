#!/usr/bin/env python3
"""
Simple Streamlit test app
"""
import streamlit as st

st.title("🔧 RepairGPT Test")
st.write("This is a simple test to check if Streamlit is working properly.")

if st.button("Test Button"):
    st.success("✅ Streamlit is working!")

st.write("Current time:", str(st.session_state.get('timestamp', 'Not set')))