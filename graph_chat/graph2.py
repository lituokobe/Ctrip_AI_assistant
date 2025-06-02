import uuid

from langchain_core.messages import ToolMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.prebuilt import tools_condition

from Ctrip_AI_assistant.graph_chat.assistant import create_assistant_node, part_1_tools, safe_tools, \
    sensitive_tool_names, sensitive_tools
from Ctrip_AI_assistant.graph_chat.draw_png import draw_graph
from Ctrip_AI_assistant.graph_chat.state import State
from Ctrip_AI_assistant.tools.init_db import update_dates
from Ctrip_AI_assistant.tools.tools_handler import create_tool_node_with_fallback, _print_event
from Ctrip_AI_assistant.tools.flights_tools import fetch_user_flight_information

#define a construction object for the graph
builder = StateGraph(State)

def get_user_info(state: State):
    """
    get passenger's flight info and update state dictionary
    :param state: current state dictionary
    :return: new state dictionary including user inf
    """
    return {"user_info": fetch_user_flight_information.invoke({})}

#fetch_user_info is executed first, meaning we can get user's flight information before doing anything
builder.add_node('fetch_user_info', get_user_info)

#define a function as a node (it can be runnable or a defined class)
builder.add_node('assistant', create_assistant_node())

#add a nodes of safe and sensitive tools with fallback mechanism
builder.add_node('safe_tools', create_tool_node_with_fallback(safe_tools))
builder.add_node('sensitive_tools', create_tool_node_with_fallback(sensitive_tools))

#add edges
builder.add_edge(START, 'fetch_user_info')

builder.add_edge('fetch_user_info', 'assistant')

def route_condition_tools(state: State) -> str:
    """
    base on current state to decide which node to execute next
    :param state: current state
    :return: str name of next string
    """
    next_node = tools_condition(state) # LangGraph default function, return tools or __end__
    if next_node == END:
        return END

    ai_message = state['messages'][-1]
    tool_call = ai_message.tool_calls[0]
    if tool_call['name'] in sensitive_tool_names:
        return 'sensitive_tools'
    return 'safe_tools'

builder.add_conditional_edges(
    "assistant",
    route_condition_tools,
    ['safe_tools', 'sensitive_tools', END]
)

builder.add_edge('sensitive_tools', 'assistant')

builder.add_edge('safe_tools', 'assistant')

#checkpointer to let graph's state last. This is the full RAM of the graph
memory = MemorySaver()

#compile graph, set up the checkpointer, configure interruption point
graph = builder.compile(checkpointer=memory, interrupt_before=['sensitive_tools'])

#draw the graph
draw_graph(graph, 'graph3.png')

session_id = str(uuid.uuid4())
update_dates() #make sure the database is updated before every testing

config = {
    "configurable": {
        #passenger_id is for flight tool to get flight info
        "passenger_id": "3442 587242",
        #checkpointer is visited by thread_id
        "thread_id": session_id,
    }
}

_printed = set() #initiate a set, to avoid duplicate printing

#execute flow
while True:
    question = input("User: ")
    if question.lower() in ["quit", "exit"]:
        print("The chat is over, see you!")
        break
    else:
        events = graph.stream({"messages": ("user", question)}, config, stream_mode = "values")
        #print messages
        for event in events:
            _print_event(event, _printed)

        current_state = graph.get_state(config)
        if current_state.next:
            user_input = input(
                "Do you approve above operation? input 'y' to continue, otherwise specify your requests.\n"
            )
            if user_input.strip().lower() == "y":
                #continue
                events = graph.stream(None, config, stream_mode="values")
                # print messages
                for event in events:
                    _print_event(event, _printed)
            else:
                result = graph.stream({
                    "messages": [
                        ToolMessage(
                            tool_call_id=event["messages"][-1].tool_calls[0]["id"],
                            content = f"User rejected the tool call, reason is '{user_input}'.",
                        )
                    ],
                }, config)
                # print messages
                for event in events:
                    _print_event(event, _printed)

