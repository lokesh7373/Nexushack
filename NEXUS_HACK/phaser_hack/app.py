import streamlit as st

# Layouts And Configs
st.set_page_config(page_title='Lars',layout='wide')

############################### Connected Client

headers = st.context.headers.get('User-Agent')
client_ip = st.context.ip_address

if 'client_ip' not in st.session_state:
    st.session_state['client_ip'] = client_ip

if 'headers' not in st.session_state:
    st.session_state['headers'] = headers

def main():

    pages = {
        ":blue[:material/home:]"   : [st.Page('./pages/home.py',title='Lars')],

        ":blue[:material/key:]" : [st.Page('./pages/session_state.py',title='Session State')],

        "Execute" : [st.Page('./pages/task.py',title='Task'),st.Page('./pages/task_status.py',title='Task Status')] }
    
    selected_page = st.navigation(pages,position='top',expanded=True)
    selected_page.run()

if __name__ == '__main__':
    main()