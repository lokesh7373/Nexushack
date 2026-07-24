from langchain.chat_models import init_chat_model

API_KEY = "xxxxxxx"
url = 'xxxxxxxxx'


def agent_model(model_name='granite4:latest',temp=0.0):

    model = init_chat_model(
        model = model_name,
        base_url = xxxxxxx,
        # base_url = xxxxxxxxxxxx,
        model_provider="ollama",
        temperature = temp
    )

    print(f"        ----------------- ✨ [Model Using] : [{model}] ")
    print()

    return model


def planner_model(model_name='gpt-oss',temp=0.0):  #model_name='gemma3-27B',

    model = init_chat_model(
        model = model_name,
        base_url = url,
        api_key = API_KEY,
        model_provider="openai",
        temperature = temp
    )

    print(f"        ----------------- ✨ [Model Using] : [{model}] ")
    print()

    return model

def master_model(model_name='gpt-oss',temp=0.0):

    model = init_chat_model(
        model = model_name,
        base_url = url,
        api_key = API_KEY,
        model_provider="openai",
        temperature = temp
    )

    print(f"        ----------------- ✨ [Model Using] : [{model}] ")
    print()

    return model



def chatter_model(model_name='gemma3-27B',temp=0.0):

    model = init_chat_model(
        model = model_name,
        base_url = url,
        api_key = API_KEY,
        model_provider="openai",
        temperature = temp
    )

    print(f"        ----------------- ✨ [Model Using] : [{model}] ")
    print()

    return model







