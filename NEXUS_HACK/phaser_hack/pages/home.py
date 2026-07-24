import streamlit as st
import os
import pandas as pd
from numpy.random import default_rng as rng


st.space()
col1, col2 = st.columns([0.6,0.4],vertical_alignment='center')
st.space('large')
col3, col4 = st.columns([0.9,0.1])

def main():

    print('_____________________________________________')
    print()
    print(st.session_state['headers'])
    print()
    print(f"Client - [{st.session_state['client_ip']}] : Connected ")
    
    print()
    print()
    print(" ⭐ ⭐ ⭐ ⭐ ⭐ ⭐ ⭐ ⭐ ⭐ ⭐ ⭐")
    print()
    print()
    print(f"    ✨ [{st.session_state['client_ip']}][Home Page] : ")
    print()
    print()
    
    st.toast(":green[View In Full Screen [F11]]")

    with col1:
        st.image(os.path.join(os.path.dirname(__file__), "../images/home.jpg"))
    
    with col2:
        st.title(":blue[L]:grey[arge] :blue[U]:grey[ction] :blue[M]:grey[obotic] :blue[A]:grey[ystem]",text_alignment='center',anchor=False)
        st.divider()
    
    with col3:
        st.write(':blue[**Phaser Hackathon : Lokesh Tejaswini Umer**]')

    with col4:
        st.page_link(page=st.Page('./pages/task.py'),label=":blue[**Try Me :material/arrow_forward:**]")

if __name__ == '__main__':
    main()