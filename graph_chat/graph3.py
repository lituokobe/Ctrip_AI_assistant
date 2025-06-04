import uuid

from langchain_core.messages import ToolMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.prebuilt import tools_condition

from Ctrip_AI_assistant.graph_chat.assistant import assistant_runnable, CtripAssistant, primary_assistant_tools
from Ctrip_AI_assistant.graph_chat.base_data_model import ToFlightBookingAssistant, ToBookCarRental, \
    ToHotelBookingAssistant, ToBookExcursion
from Ctrip_AI_assistant.graph_chat.build_child_graph import build_flight_graph, builder_hotel_graph, build_car_graph, \
    builder_excursion_graph
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
#add edges
builder.add_edge(START, 'fetch_user_info')

#add child graph of 4 special assistant
builder = build_flight_graph(builder)
builder = builder_hotel_graph(builder)
builder = build_car_graph(builder)
builder = builder_excursion_graph(builder)

#add main assistant
builder.add_node('primary_assistant', CtripAssistant(assistant_runnable))
builder.add_node('primary_assistant_tools', create_tool_node_with_fallback(primary_assistant_tools))

def route_primary_assistant(state: dict):
    """
    Based on current state, decide which child assistant node to route to.
    :param state: dictionary of current dialog state
    :return: node name of next step
    """
    route = tools_condition(state)  # decide next step
    if route == END:
        return END  # if the ending condition is satisfied, return END
    tool_calls = state["messages"][-1].tool_calls  # get the tool call in the last message
    if tool_calls:
        if tool_calls[0]["name"] == ToFlightBookingAssistant.__name__:
            return "enter_update_flight"  #go to flight update node
        elif tool_calls[0]["name"] == ToBookCarRental.__name__:
            return "enter_book_car_rental"  # go to car rental booking node
        elif tool_calls[0]["name"] == ToHotelBookingAssistant.__name__:
            return "enter_book_hotel"  # go to hotel booking node
        elif tool_calls[0]["name"] == ToBookExcursion.__name__:
            return "enter_book_excursion"  # go to excursion booking node
        return "primary_assistant_tools"  # otherwise go to primary assistant node
    raise ValueError("Invalid route")  # If cannot find appropriate tool calls, raise an error


#add conditional edges
builder.add_conditional_edges(
    "primary_assistant",
    route_primary_assistant,
    [
        "enter_update_flight",
        "enter_book_car_rental",
        "enter_book_hotel",
        "enter_book_excursion",
        "primary_assistant_tools",
        END,
    ]
)

builder.add_edge('primary_assistant_tools', 'primary_assistant')

# Every child graph with assigned task can respond to user directly. When user replies, we hope to return to current graph
def route_to_workflow(state: dict) -> str:
    """
    If we are in a state of being assigned, directly route to respective assistant.
    :param state: dictionary of current dialog state
    :return: the node name to go
    """
    dialog_state = state.get("dialog_state")
    if not dialog_state:
        return "primary_assistant"  # of no dialog state, return to main assistant
    return dialog_state[-1]  # otherwise return to the last assistant


builder.add_conditional_edges("fetch_user_info", route_to_workflow)  # route based on user info

memory = MemorySaver()
graph = builder.compile(
    checkpointer=memory,
    interrupt_before=[
        "update_flight_sensitive_tools",
        "book_car_rental_sensitive_tools",
        "book_hotel_sensitive_tools",
        "book_excursion_sensitive_tools",
    ]
)


#draw the graph
# draw_graph(graph, 'graph5.png')

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
                result = graph.stream(
                    {
                        "messages":[
                            ToolMessage(
                                tool_call_id=event["messages"][-1].tool_calls[0]["id"],
                                name="rejection_handler",  # Add tool name explicitly
                                content=f"User rejected the tool call, reason is '{user_input}'.",
                            )
                        ]
                    },
                    config,
                )
                # print messages
                for event in events:
                    _print_event(event, _printed)

