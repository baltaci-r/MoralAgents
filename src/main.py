import os, sys, json, time

from typing import Annotated, TypedDict
from functools import partial

from langgraph.graph import END, StateGraph, add_messages
from langgraph.types import Command
from langchain_core.messages import HumanMessage, AnyMessage
from langchain_ollama.chat_models import ChatOllama
from langchain_openai import ChatOpenAI

from prompts import get_prompts


def extract_think_tags(response):
    
    if isinstance(response.content, str):
        message = response.content.split('[/INST]')[-1].strip()
        if '<think>' in message and '</think>' in message:
            reasoning = message[message.find('<think>')+7:message.find('</think>')].strip()
            message = message[message.find('</think>')+8:].strip()
            return message, reasoning
        else:
            return message, ''
    else: 
        message = response.text()
        reasoning = response.additional_kwargs['reasoning']['summary']
        if reasoning:
            return message, reasoning[-1]['text']
        else:
            return message, ''


class CustomMessagesState(TypedDict):
    num_agents: int
    num_rounds: int
    scenario: str
    subject: str
    history: str
    onboardings: list
    messages: Annotated[list[AnyMessage], add_messages]
    opinions: Annotated[list[AnyMessage], add_messages]


def agent(state: CustomMessagesState, index: str, onboarding: str, conversants: str):
    name = f"Agent_{index}"
    system_prompt = f"You are {name}. "
    history = state['history']
    if len(history) == 0:
        history_ = "You are the first to speak in the group discussion."
    else:
        history_ = history

    argument = prompts['ARGUMENT'].format(onboarding=onboarding, argument=state['messages'][index-1].content) if onboarding else ""
    user_prompt = prompts['DISCUSSION_1'].format(conversants=conversants, scenario=state['scenario'], subject=state['subject']) + argument + prompts['DISCUSSION_2'].format(history=history_)

    messages =  [
        {"role": "system", "content": system_prompt}, 
        {"role": "user", "content": user_prompt}
    ]

    result = llm.invoke(messages)
    output_message, reasoning = extract_think_tags(result)

    return Command(
        update={
            "messages": [HumanMessage(content=output_message, reasoning=reasoning, name=name, onboarding=onboarding, phase='discussion')],
            "history": history + f"\n\n{name}: {output_message}" if history else f"{name}: {output_message}"
            },
        goto='superviser'
    ) 

def onboarding(state: CustomMessagesState, index: str, onboarding: str):
    name = f"Agent_{index}"
    if not onboarding:
        return Command(
        update={
            "messages": [HumanMessage(content="",  reasoning="", name=name,onboarding=onboarding, phase='onboarding')]
        },
        goto='superviser'
    )
    
    system_prompt = f"You are {name}. "
    user_prompt = prompts['ONBOARDING'].format(scenario=state['scenario'], subject=state['subject'], onboarding=onboarding)
    messages =  [
        {"role": "system", "content": system_prompt}, 
        {"role": "user", "content": user_prompt}
    ]
    result = llm.invoke(messages)
    output_message, reasoning = extract_think_tags(result)

    return Command(
        update={
            "messages": [HumanMessage(content=output_message, reasoning=reasoning, name=name, onboarding=onboarding, phase='onboarding')],
            },
        goto='superviser'
    )

def reflection(state: CustomMessagesState, index: str, onboarding: str):
    name = f"Agent_{index}"
    system_prompt = f"You are {name}. "
    if state['num_agents'] == 1:
        user_prompt = prompts['REFLECTION_SINGLE'].format(scenario=state['scenario'], subject=state['subject'])
    else:
        argument = prompts['ARGUMENT'].format(onboarding=onboarding, argument=state['messages'][index-1].content) if onboarding else ""
        user_prompt = prompts['REFLECTION_1'].format(scenario=state['scenario'], subject=state['subject']) + argument + prompts['REFLECTION_2'].format(history=state['history']) 

    messages =  [
        {"role": "system", "content": system_prompt}, 
        {"role": "user", "content": user_prompt}
    ]

    result = llm.invoke(messages)
    output_message, reasoning = extract_think_tags(result)

    return Command(
        update={
            "messages": [HumanMessage(content=output_message, reasoning=reasoning,  name=name, onboarding=onboarding, phase='reflection')],
            },
        goto='superviser'
    ) 


def superviser(state: CustomMessagesState):
    last_message = state['messages'][-1]
    if not last_message.content:
        return Command(
            update={
                "opinions": [HumanMessage(content="", reasoning="", name=last_message.name, onboarding=last_message.onboarding, phase=last_message.phase)]
                },
            goto=router(state)
        ) 

    system_prompt = "You are a helpful assistant. "
    user_prompt = prompts['EXTRACT_OPINION'].format(last_message.content)
    messages =  [
        {"role": "system", "content": system_prompt}, 
        {"role": "user", "content": user_prompt}
    ]
    result = llm.invoke(messages)
    output_message, _ = extract_think_tags(result)

    return Command(
        update={
            "opinions": [HumanMessage(content=output_message, reasoning="", name=last_message.name, onboarding=last_message.onboarding, phase=last_message.phase)]
            },
        goto=router(state)
        )


def router(state):
    # Number of agents, number of rounds
    num_agents = state['num_agents']
    num_rounds = state['num_rounds']

    # Count how many messages have been posted in each phase
    i_onboarding = sum(1 for msg in state['messages'] if msg.phase == 'onboarding')
    i_discussion = sum(1 for msg in state['messages'] if msg.phase == 'discussion')
    i_reflection = sum(1 for msg in state['messages'] if msg.phase == 'reflection')

    # IF one agent, no onboarding or discussion is possible
    if num_agents == 1:
        if i_reflection < num_rounds:
            return "superviser"
        else:
            return END

    # 1) Onboarding phase: each agent gets exactly one onboarding
    if i_onboarding < num_agents:
        return f"onboarding_{i_onboarding + 1}"

    # 2) Discussion phase: total of num_rounds * num_agents messages
    total_discussion_steps = num_rounds * num_agents
    if i_discussion < total_discussion_steps:
        next_agent_index = i_discussion % num_agents
        return f"agent_{next_agent_index + 1}"

    # 3) Reflection phase: each agent has exactly one reflection
    if i_reflection < num_agents:
        return f"reflection_{i_reflection + 1}"

    # 4) Done
    return END


def get_conversants(ind, num_agents):
    if num_agents==1:
        return ""
    conversants = [f"Agent_{agent+1}" for agent in range(num_agents) if agent+1!=ind]
    if len(conversants) == 1:
        return conversants[0]
    elif len(conversants) == 2:
        return f"{conversants[0]} and {conversants[1]}"
    else:
        return f"{', '.join(conversants[:-1])}, and {conversants[-1]}"


def run_example(scenario, subject, onboardings):
    workflow = StateGraph(CustomMessagesState)
    workflow.add_node('superviser', superviser)
    for ind, onboarding_ in enumerate(onboardings, start=1): 
        conversants = get_conversants(ind, len(onboardings))
        workflow.add_node(f'agent_{ind}', partial(agent, index=ind, onboarding=onboarding_, conversants=conversants))
        workflow.add_node(f'onboarding_{ind}', partial(onboarding, index=ind, onboarding=onboarding_))
        workflow.add_node(f'reflection_{ind}', partial(reflection, index=ind, onboarding=onboarding_))
    
    if len(onboardings)==1:
        workflow.set_entry_point('reflection_1')
    else: 
        workflow.set_entry_point('onboarding_1')
        
    graph = workflow.compile()

    initial_state = {
        "scenario": scenario,
        "subject": subject,
        "num_agents": len(onboardings),
        "num_rounds": num_rounds,
        "history": "", 
        "onboardings": onboardings
    }

    events = graph.invoke(initial_state, {"recursion_limit": 100})
    return events



if __name__ == '__main__': 


    dataset = sys.argv[1]
    model_name = sys.argv[2]
    num_attempts = int(sys.argv[3])
    temperature = float(sys.argv[4])
    save_dir = sys.argv[5]
    num_rounds = int(sys.argv[6])
    onboardings = sys.argv[7]
    num_ctx = int(sys.argv[8])

    onboardings = [onboarding.strip("\"") for onboarding in onboardings.split(',')]
    onboardings_ = 'n'*len(onboardings) if all(onboarding == "" for onboarding in onboardings) else "".join(onboardings)
    num_agents = len(onboardings)

    if num_agents==1:
        assert num_rounds == 1

    assert dataset in ['keshmirian', 'greene', 'korner', 'oxford_utilitarianism_scale', 'cni']
    with open(f'data/{dataset}/data.json', 'r') as f: 
        data = json.load(f)

    if model_name.startswith('gpt'):
        llm = ChatOpenAI(model=model_name, temperature=temperature, api_key=os.environ['OPENAI_API_KEY'])
    elif model_name.startswith('o'):
        reasoning = { "effort": "medium",  "summary": "auto"}
        llm = ChatOpenAI(model=model_name, use_responses_api=True, model_kwargs={"reasoning": reasoning}, api_key=os.environ['OPENAI_API_KEY'])
    else:
        llm = ChatOllama(model=model_name, temperature=temperature, num_ctx=num_ctx)

    prompts = get_prompts(dataset)

    for example in data:
        for attempt in range(num_attempts):
            save_path = '{}/{}_ob{}_{}.jsonl'.format(save_dir, example['index'], onboardings_, attempt+1)
            if os.path.exists(save_path):
                print(f"✔ {save_path}", end=' ')
                continue
            
            print(f"Processing: {save_path}")
            print('='*40, f"dataset: {dataset} | example: {example['index']} | attempt: {attempt+1}", '='*40,  flush=True)
            start_time = time.time()
            responses = run_example(example['scenario'], example['subject'], onboardings)
            print("Saving to", save_path,  flush=True)
            with open(save_path, 'w') as f:
                assert len(responses['messages']) == len(responses['opinions'])
                for message, opinion in zip(responses['messages'], responses['opinions']):
                    f.write(json.dumps({"name": message.name, "phase": message.phase, "onboarding": message.onboarding, "opinion": opinion.content, "message": message.content, "reasoning": message.reasoning})+'\n')
            end_time = time.time()
            print(f" => Iteration time: {end_time - start_time:.2f} seconds", flush=True)

print("Done")