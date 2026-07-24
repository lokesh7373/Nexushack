#######################################
########### PYTHON IMPORTS  ###########
#######################################

import json, uuid
import socket
import streamlit as st
import traceback
import operator

from pydantic import BaseModel, Field
from typing import Annotated,Literal, TypedDict, List, Set, Optional

from utils.llms import agent_model, master_model
from utils.prompts import get_quadruped_prompt
from utils.client_communication import receive_full_response
# from utils.lars_context import OBJECTS

#######################################
######### LANGGRAPH IMPORTS  ##########
#######################################

from langgraph.graph import StateGraph, START, END

#######################################
######### LANGCHAIN IMPORTS ###########
#######################################

from langchain_core.prompts import PromptTemplate
from langchain.tools import tool
from langchain.agents import create_agent

#######################################
######### COMMUNICATION CLIENT ########
#######################################

SERVER_IP = 'x.x.x.x'
PORT = xxxx
ADDR = (SERVER_IP,PORT)

#######################################
############### Streamlit #############
#######################################

if 'current plan' in st.session_state:
    
    log_expander = st.expander('Logs',expanded=True)

    with log_expander:
        col1, col2 = st.columns(2,border=True)
    with log_expander:
        with col1:
            st.write('- :green[Plan Id] :',st.session_state['current plan id'])
            st.write(f"- **Master Model** : :violet[**{st.session_state['master_selected']}**]")
            st.write(f"- **Agent Model**  : :orange[**{st.session_state['agent_selected']}**]")
            with st.expander(":blue[Plan]"):
                st.write(st.session_state['current plan'])
            st.divider()

st.divider()
master_col, agv_col = st.columns(2,width='stretch',border=True)

with master_col:
    st.header(':grey[Master]',text_alignment='center',divider=True,anchor=False)
with agv_col:
    st.header(':grey[Quadruped]',text_alignment='center',divider=True,anchor=False)

if 'agent_selected' in st.session_state:
    agent_model_selected = st.session_state['agent_selected']
    agent_llm = agent_model(agent_model_selected)

if 'master_selected' in st.session_state:
    master_model_selected = st.session_state['master_selected']
    master_llm = master_model(master_model_selected)


#######################################
############### Agent Tools ###########
#######################################

@tool
def get_camera_feed():
    """
    The robot can get camera feed using this funciton
    """

    print('             | --- Pick Tool Invoked : ✅')

    # Command For Isaac Sim Server
    message = {
        'id' : str(uuid.uuid4()),
        'type' : 'task',
        'action' : 'get camera feed',
        'parameters' : None,
        'action_completed' : False
    }

    # Client For Communicating With IsaacSim Server 
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print()
    print(f'                 --- [CLIENT] Connecting To Isaac Sim Server : ⏳')
    
    client.connect(ADDR)
    client.send(json.dumps(message).encode())

    response = client.recv(4096)
    if response:
        print(f'                 --- [CLIENT] Connected To Isaac Sim Server  : ✅')
        print(f'                 --- [CLIENT] ACK Recieved                   : {json.loads(response.decode())}')
       
    print(f'                 --- [CLIENT] Waiting For Command Execution  : ⏳')
    print()
    response_decoded = receive_full_response(sock=client)
    print(f'                 --- [CLIENT] Command Status                 : {response_decoded}')

    if response_decoded['status'] == 'Pick Command Executed':
        client.close()

    return response_decoded['status']

@tool
def navigate(machine:Literal[0,1,4,5,7], meter:Literal[0,1,2,3,4]):
    """
    Quad can navigate to a machine and meter area using this tool
    """
    print('             | --- Navigate Tool Invoked : ✅')

    # Command For Isaac Sim Server
    message = {
        'id' : str(uuid.uuid4()),
        'type' : 'task',
        'action' : 'navigation',
        'parameters' : {'machine':f'{machine}','meter':f'{meter}'},
        'action_completed' : False
    }

    # Client For Communicating With IsaacSim Server 
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print()
    print('                 --- [CLIENT] Connecting To Isaac Sim Server : ⏳')
    
    client.connect(ADDR)
    client.send(json.dumps(message).encode())

    response = client.recv(4096)
    if response:
        print(f'                 --- [CLIENT] Connected To Isaac Sim Server  : ✅')
        print(f'                 --- [CLIENT] ACK Recieved : {json.loads(response.decode())}')

    print()
    print(f'                 --- [CLIENT] Waiting For Command Execution  : ⏳')
    print()

    response_decoded = receive_full_response(sock=client)
    print(f'                 --- [CLIENT] Command Status                 : {response_decoded}')

    if response_decoded['status'] == 'Navigation Command Executed':
        client.close()

    return response_decoded['status']

#######################################
############### SCHEMAS ###############
#######################################

# Planner Schema
class PlannerStepSchema(BaseModel):
    step_no : int = Field(description='Denotes the current step number')
    robot_type : Literal["ARM","QUADRUPED"] = Field(description='Robot needed for executing the action')
    action : str = Field(description='The action to perform')
    dependencies : Optional[List[int]] = Field(description='Any dependency with previous step')
    
class PlannerSchema(BaseModel):
    plan : List[PlannerStepSchema]

# Lars Schema
class LarsSchema(TypedDict):
    
    plan : PlannerSchema
    plan_execution_order : List

    completed_steps: Annotated[Set[int],operator.or_]

    actionsTo_execute : List[int] 
    actions_execution_mode : str

    quad_response : List[str]
    arm_response : List[str]

#######################################
############## MASTER NODE ############
#######################################

def Master(state:LarsSchema):

    plan_execution_order = state['plan_execution_order']
    steps_completed = state['completed_steps']

    flattened = [x for item in plan_execution_order for x in (item if isinstance(item,list) else [item] )]
    if len(flattened) == len(steps_completed):
        return {"actionTo_execute": [], "actions_execution_mode":"Plan Executed"}

    else:
        # Deciding Plan Execution Mode and Steps To Execute
        with master_col:
            st.divider()
            st.markdown(f":green-badge[Steps Completed ] : **{state['completed_steps']}**")

            for steps_to_execute in plan_execution_order:
                if steps_to_execute not in steps_completed:

                    st.space()
                    st.markdown(f":violet-badge[Master Command ] : **Action = {steps_to_execute} | Mode = Sequential** ")

                    return {"actionsTo_execute":[steps_to_execute], "actions_execution_mode":"Sequential"}
        
def route_master_instruction(state:LarsSchema):
    
    if state['actions_execution_mode'] == "Plan Executed":
        print("_______________________________From : Master Router")
        print()
        print('Plan Executed')
        print()

        del st.session_state['current plan']
        del st.session_state['current plan id']

        with master_col:
            st.space()
            st.subheader('Master Router ->',divider=True,anchor=False)
            st.divider()
            st.success("Plan Executed")
        
        return 'Plan Executed'
    
    else:
        return 'QUADRUPED'
       
    

#######################################
############ QUADRUPED NODE ###########
#######################################


def quadAgent(state:LarsSchema):

    step_no = None
    for action_no in state['actionsTo_execute']:
        if state['plan'][action_no-1].robot_type == "QUADRUPED":
            step_no = state['plan'][action_no-1].step_no
            action_to_perform = state['plan'][action_no-1].action

            # Terminal Logging
            print(f"        | 🤖 -- [QUADRUPED-Node] :")
            print()
            print('             --- Action Recieved  : ', action_to_perform)
            
            
            # Streamlit Logging
            if state['actions_execution_mode'] == 'Sequential':
                with agv_col:
                    st.divider()
                    st.markdown(f':orange-badge[Action To Perform] : {action_to_perform}')
                    st.space()
                    st.markdown(":green-badge[Agent Response] :")

    
    messages = [{'role':'system','content': get_quadruped_prompt()},
                {"role": "human", "content": action_to_perform}]

    agent = create_agent(
        model=agent_llm,
        tools=[navigate, get_camera_feed]
    )

    print()
    print('             --- Calling quadAgent : ⏳')
    print()
    
    response = agent.invoke({'messages':messages})

    print()
    print('             --- Agent Response : ')   
    print()

    # Storing Agent Response For Streamlit Logging When Executing In Parallel
    response_for_streamlit_when_parallel = []
    response_for_streamlit_when_parallel.append(step_no)

    for msg in response['messages'][2:]:
        if msg.content:
            print('               --- ',msg.content)

            response_for_streamlit_when_parallel.append(msg.content)

            # Streamlit Logging
            if state['actions_execution_mode'] == 'Sequential':
                with agv_col:
                    st.write(f" - {msg.content}")


    print()
    print('             --- Step Completed : ',action_to_perform)

    # Streamlit Logging
    if state['actions_execution_mode'] == 'Sequential':
        with agv_col:
            st.space()
            st.success(f"Completed Step : {step_no}")
            st.divider()
    
    if state['actions_execution_mode'] == 'Parallel':
        return {'completed_steps': {step_no}, 'quad_response': response_for_streamlit_when_parallel}
    else:
        return {'completed_steps': {step_no}}
    

    
#######################################
############## LARS GRAPH #############
#######################################

if __name__ == '__main__':

    print("    ✨ [Plan Executor] : ")
    print()

    if 'current plan' not in st.session_state:
        st.divider()
        st.warning('No Active Plan, Please give a command',width=350)
        print(" --------------------- No Active Plan ")
        print()

    else:

        print(" --------------------- Executing Plan : ",st.session_state['current plan id'])
        print()

        lars = StateGraph(LarsSchema)

        lars.add_node('master', Master)
        lars.add_node('quad', quadAgent)
        
        lars.add_edge(START,'master')

        lars.add_conditional_edges('master',route_master_instruction,
                                {'QUADRUPED':'quad',
                                'Plan Executed':END})

        lars.add_edge('quad','master')
       
        print(" --------------------- Compiling LangGraph : ")
        print()

        with log_expander:
            with col1:
                with st.spinner("Compiling LangGraph",show_time=True):
                    lars_wk = lars.compile()
                st.success("Lars LangGraph Workflow Compiled")

            with col2:
                st.subheader(":grey[Compiled LangGraph]",text_alignment='center')
                with st.expander("Compiled Graph",expanded=True):
                    st.image(lars_wk.get_graph().draw_mermaid_png())
                st.divider()

        initial_state = {'plan' : st.session_state['current plan'],
                         'plan_execution_order' : st.session_state['current_plan_execution_order']}

        try :

            print(" --------------------- Invoking LangGraph : ")
            print()

            with log_expander:
                with col1:
                    with st.spinner("Invoking Lars LangGraph Workflow",show_time=True):
                        final_state = lars_wk.invoke(initial_state)
            
            with log_expander:
                with col1:
                    st.success("Plan Executed")
                    
            print(" --------------------- Plan Executed : ")
            print()

            print(" --------------------- Status : ")
            print()
            print(final_state)

        except Exception as e:
            
            print("Error Occured :",e)
            with log_expander:
                with col2:
                    st.subheader(":grey[Error]",text_alignment='center',anchor=False)
                    st.space()
                    st.error("Error Occured :")
                    st.write(f"- :orange[{e}]")
                    st.write(f"- :orange[{type(e)}]")

                    with st.expander("Traceback"):
                        st.write(f":red[{traceback.format_exc()}]")