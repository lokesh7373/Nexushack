import streamlit as st
import random

st.title(':grey[Streamlit Session State]',text_alignment='center',anchor=False)
st.divider()

col1, col2, col3 = st.columns(3,border=True)


def main():
    
    print('_____________________________________________')
    print()
    print(f"    ⭐ [{st.session_state['client_ip']}][Streamlit Session State Page] : ")
    print()
    print("       --------------------- Showing Current Session State")
    print()

    columns = [col2, col3]

    for col_index, key in enumerate(st.session_state):

        if key == 'chat_history':
            with col1:
                st.space()
                st.header(f":blue[{key}]",text_alignment='center')
                st.space()
                st.write(st.session_state[key])

            continue

        with columns[col_index%2]:
            st.space()
            st.subheader(f":blue[{key}]")
            st.space()
            st.write('-',st.session_state[key])
            st.divider()



if __name__ == '__main__':
    main()