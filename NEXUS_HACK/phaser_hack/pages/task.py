import streamlit as st

import time
import json,uuid

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate

from utils.env_info import ROBOTS, LOCATION_INFO
from utils.llms import planner_model, chatter_model

from utils.prompts import get_planner_prompt
from utils.schemas import PlannerSchema
from langchain_core.tools import tool


#######################################
##### Streamlit Session State #########
#######################################


############################### Initialize chat history

def init_session_state():

    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] =  [] #[{"role":"system", "content" : get_chatter_prompt()}]

    if 'plan_history' not in st.session_state:
        st.session_state['plan_history'] = []

    if 'plans_status' not in st.session_state:
        st.session_state['plans_status'] = []
    
    # Initializing Models

    if 'chatter_selected' not in st.session_state:
        st.session_state['chatter_selected'] = 'gemma3-27B'
    
    if 'planner_selected' not in st.session_state:
        st.session_state['planner_selected'] = 'gemma3-27B'
    
    if 'master_selected' not in st.session_state:
        st.session_state['master_selected'] = 'gpt-oss'
    
    if 'agent_selected' not in st.session_state:
        st.session_state['agent_selected'] = 'granite4:latest'

init_session_state()

#######################################
##### Streamlit Pop Up Message ########
#######################################

def session_reset_button_toast():
    st.toast("⚠️  Resetting Session History")

def chat_reset_button_toast():
    st.toast("⚠️  Resetting Chat History")


#######################################
##### Streamlit Chat Layout ######
#######################################

st.markdown(
    """
    <style>
        /* 1. Flip the entire message row (Avatar to the right) */
        [data-testid="stChatMessage"]:has(div[aria-label="Chat message from user"]) {
            flex-direction: row-reverse;
            text-align: right;
        }

        /* 2. Fix the alignment of the text container itself */
        [data-testid="stChatMessage"]:has(div[aria-label="Chat message from user"]) [data-testid="stChatMessageContent"] {
            display: flex;
            flex-direction: column;
            align-items: flex-end; /* This pushes the text block to the right */
            width: 100%;
        }

        /* 3. Ensure the actual text inside the markdown behaves */
        [data-testid="stChatMessage"]:has(div[aria-label="Chat message from user"]) [data-testid="stChatMessageContent"] div {
            text-align: right;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Icons
avatar = {'user':':material/for_you:',
          'ai' : ':material/mode_cool:',
          'assistant' : ':material/mode_cool:'}


#######################################
##### Streamlit Design Layout #########
#######################################


st.title(':blue[LUMA]',text_alignment='center',width='stretch',anchor=False)
st.divider()

col1, col2 = st.columns([0.55,0.45],width='stretch',border=True)
col3, col4 = st.columns([0.55,0.45],width='stretch')

with col1:
    with st.chat_message('ai',avatar=avatar['ai']):
        st.write("Hi 👋, How Can I Help You Today :blue[**?**]",unsafe_allow_html=True)

############################### Right Side Content

with col2:
    st.write("Camera Feed")
         
with col3:
    if st.button(':red[Reset Chat History]',width='stretch'):

        st.session_state.clear()

        session_reset_button_toast()
        init_session_state()
        st.rerun()

with col4:
    if st.button(':red[Reset Current Session]',width='stretch'):

        st.toast("⚠️  Resetting Session History")

        st.session_state.clear()
        init_session_state()
        st.rerun()
        
###############################################################
##### Display chat messages from history on app rerun #########
###############################################################

# Left Side Content

# with col1:
#     with st.expander(':grey[Plan History]'):
#         for msg in st.session_state['plan_history']:
#             with st.chat_message(msg['role'],avatar=avatar[msg['role']]):
#                 st.write(msg['content'],unsafe_allow_html=True)


with col1:
        for msg in st.session_state['chat_history']:
                if msg['role'] != 'system':
                    with st.chat_message(msg['role'],avatar=avatar[msg['role']]):
                        st.write(msg['content'],unsafe_allow_html=True)



#######################################
############### Planner ###############
#######################################


def get_plan(task) -> PlannerSchema:
    
    print(f"    ✨ [{st.session_state['client_ip']}][Planner] : ")
    print()
    print("        --------------------- Waiting For Response")
    print()


    try :
        model = planner_model(st.session_state['planner_selected'])
        
        parser = PydanticOutputParser(pydantic_object=PlannerSchema)
        
        template = PromptTemplate(
            template=get_planner_prompt(),
            input_variables=['task','robots','locations_info']
        )
        
        prompt = template.invoke(
            {
                'task' : task,
                'robots' : ROBOTS,
                'locations_info' : LOCATION_INFO,
            }
        )
        
        with st.spinner(":blue[Generating Plan ..]"):
            with st.chat_message('ai',avatar=avatar['ai'] ):
                ai_message = st.write_stream((chunk.content for chunk in model.stream(prompt)),cursor='..')
            
        # History For Chatter Model
        st.session_state['chat_history'].append({'role':'assistant','content':ai_message})
        print("        --------------------- Plan Generated")
        print()
        
        # Streamlit ui plan history logger
        st.session_state['plan_history'].append({'role':'user','content':task})
        st.session_state['plan_history'].append({'role':'assistant','content':ai_message})

        # Parsing Plan From Str To Predefined Schema
        plan_parsed = parser.parse(ai_message)

        
        # Creating Plan Execution Order
        plan_execution_order=[]

        for step in plan_parsed.plan:
            plan_execution_order.append(step.step_no)


        # Creating Unique Id For The Generated Plan
        plan_id = str(uuid.uuid4())
        st.session_state['plans_status'].append({plan_id : {'status':'plan generated',
                                                            'plan':plan_parsed,
                                                            'plan_execution_order':plan_execution_order}
                                                })

        return plan_parsed, plan_id
    
    except Exception as e:

        st.divider()
        with st.expander("Error"):
            st.error(f"Error : {e}")
            st.error(f"Error Type : {type(e)}")

def main():
    
    # Initialize the seesion state
    init_session_state()
    current_plan_id = None

    print('_____________________________________________')
    print()
    print(f"    ⭐ [{st.session_state['client_ip']}][Task Page] : ")
    print()
    print("     --------------------- Waiting For Command")
    print()
    
    # Text Command
    user_input = st.chat_input("Ask Lars")
        

    if user_input :

        st.session_state['chat_history'].append({'role':"user",'content':user_input})

        with col1:

            # Write the user input to streamlit ui
            with st.chat_message("user",avatar=avatar['user']):
                st.write(user_input)

            current_plan, current_plan_id = get_plan(user_input)
            
           
        for plan in st.session_state['plans_status']:
            for id in plan:
                if current_plan_id:

                    if (id == current_plan_id) and (plan[id]['status'] != 'Plan Executed'):

                        print(" --------------------- New Plan : ",current_plan_id)
                        print()

                        st.divider()
                        st.session_state['current plan'] = current_plan.plan
                        st.session_state['current plan id'] = current_plan_id
                        st.session_state['current_plan_execution_order'] = plan[id]['plan_execution_order']

                        _,_,_,execute_col,_,_,_ = st.columns(7)
                        with execute_col:
                            st.page_link(page=st.Page('./pages/task_status.py'),label=":blue[**Execute Task :material/arrow_forward:**]")
                        

        

            
            
if __name__ == '__main__':
    main()