from langchain_core.messages import ToolMessage
from langgraph.constants import END
from langgraph.graph import StateGraph
from langgraph.prebuilt import tools_condition

from Ctrip_AI_assistant.graph_chat.agent_assistant import update_flight_runnable, update_flight_sensitive_tools, update_flight_safe_tools, \
    book_car_rental_runnable, book_car_rental_safe_tools, book_car_rental_sensitive_tools, book_hotel_runnable, \
    book_hotel_safe_tools, book_hotel_sensitive_tools, book_excursion_runnable, book_excursion_safe_tools, \
    book_excursion_sensitive_tools
from Ctrip_AI_assistant.graph_chat.assistant import CtripAssistant
from Ctrip_AI_assistant.graph_chat.base_data_model import CompleteOrEscalate
from Ctrip_AI_assistant.graph_chat.entry_node import create_entry_node
from Ctrip_AI_assistant.tools.tools_handler import create_tool_node_with_fallback


# child graph of flight booking assistant
def build_flight_graph(builder: StateGraph) -> StateGraph:
    """build child graph of flight booking assistant"""
    # add entry note, use it when updating or cancelling the flight
    builder.add_node(
        "enter_update_flight",
        create_entry_node("Flight Updates & Booking Assistant", "update_flight"),  # create entry node, assign assistant name and new dialog state
    )
    builder.add_node("update_flight", CtripAssistant(update_flight_runnable))  # add node to process updating flights
    builder.add_edge("enter_update_flight", "update_flight")  # add edge to connect entry node and the process node

    # add nodes for sensitive tools and safe tools
    builder.add_node(
        "update_flight_sensitive_tools",
        create_tool_node_with_fallback(update_flight_sensitive_tools),
    )
    builder.add_node(
        "update_flight_safe_tools",
        create_tool_node_with_fallback(update_flight_safe_tools),
    )

    def route_update_flight(state: dict):
        """
        flight update process based on current state route

        :param state: dictionary of current dialog state
        :return: node name of next step
        """
        route = tools_condition(state)  # decide next step
        if route == END:
            return END
        tool_calls = state["messages"][-1].tool_calls  # check tool call of the last message
        did_cancel = any(tc["name"] == CompleteOrEscalate.__name__ for tc in tool_calls)  # check if CompleteOrEscalate is called
        if did_cancel:
            return "leave_skill"  # if user requests to cancel or exit, move to node of leave_skill
        safe_tool_names = [t.name for t in update_flight_safe_tools]  # obtain all safe tool names
        if all(tc["name"] in safe_tool_names for tc in tool_calls):  # if all tools called are safe tools
            return "update_flight_safe_tools"  # move to node of safe tools
        return "update_flight_sensitive_tools"  # otherwise move to node of sensitive tools

    # add edges to connect nodes of sensitive tools and safe tools back to "update_flight"
    builder.add_edge("update_flight_sensitive_tools", "update_flight")
    builder.add_edge("update_flight_safe_tools", "update_flight")

    # route flight update process based on conditions
    builder.add_conditional_edges(
        "update_flight",
        route_update_flight,
        ["update_flight_sensitive_tools", "update_flight_safe_tools", "leave_skill", END],
    )

    # this node is for exits of all child assistants
    def pop_dialog_state(state: dict) -> dict:
        """
        pop dislog state and return to main assistant
        this makes the full graph can clearly follow the dialog stream, assign the control to specific child graph based on needs
        :param state: dictionary of curren dialog state
        :return: dictionary including new dialog state and messages
        """
        messages = []
        if state["messages"][-1].tool_calls:
            # note: currently we don't process scenario where LLM executes multiple tool calls concurrently
            messages.append(
                ToolMessage(
                    content="Recovering dialog with main assistant. Please review the previous dialog and assist the user based on requirements.",
                    tool_call_id=state["messages"][-1].tool_calls[0]["id"],
                )
            )
        return {
            "dialog_state": "pop",  # update the dialog state as 'pop'
            "messages": messages,  # return to the message list
        }

    # add leave skill node and connect it back to main assistant
    builder.add_node("leave_skill", pop_dialog_state)
    builder.add_edge("leave_skill", "primary_assistant")
    return builder


# child graph of car rental booking assistant
def build_car_graph(builder: StateGraph) -> StateGraph:
    # add entry note, use it when booking car rental
    builder.add_node(
        "enter_book_car_rental",
        create_entry_node("Car Rental Assistant", "book_car_rental"),   # create entry node, assign assistant name and new dialog state
    )
    builder.add_node("book_car_rental", CtripAssistant(book_car_rental_runnable))  # add node to process booking car rental
    builder.add_edge("enter_book_car_rental", "book_car_rental")  # add edge to connect entry node and the process node

    # add nodes for sensitive tools and safe tools
    builder.add_node(
        "book_car_rental_safe_tools",
        create_tool_node_with_fallback(book_car_rental_safe_tools),
    )
    builder.add_node(
        "book_car_rental_sensitive_tools",
        create_tool_node_with_fallback(book_car_rental_sensitive_tools),
    )

    def route_book_car_rental(state: dict):
        """
        car rental booking process based on current state route

        :param state: dictionary of current dialog state
        :return: node name of next step
        """
        route = tools_condition(state)  # decide next step
        if route == END:
            return END
        tool_calls = state["messages"][-1].tool_calls  # check tool call of the last message
        did_cancel = any(tc["name"] == CompleteOrEscalate.__name__ for tc in tool_calls)  # check if CompleteOrEscalate is called
        if did_cancel:
            return "leave_skill"  # if user requests to cancel or exit, move to node of leave_skill
        safe_toolnames = [t.name for t in book_car_rental_safe_tools]  # obtain all safe tool names
        if all(tc["name"] in safe_toolnames for tc in tool_calls):  # if all tools called are safe tools
            return "book_car_rental_safe_tools"  # move to node of safe tools
        return "book_car_rental_sensitive_tools"  # otherwise move to node of sensitive tools

    # add edges to connect nodes of sensitive tools and safe tools back to "book_car_rental"
    builder.add_edge("book_car_rental_sensitive_tools", "book_car_rental")
    builder.add_edge("book_car_rental_safe_tools", "book_car_rental")

    # route car rental booking process based on conditions
    builder.add_conditional_edges(
        "book_car_rental",
        route_book_car_rental,
        [
            "book_car_rental_safe_tools",
            "book_car_rental_sensitive_tools",
            "leave_skill",
            END,
        ],
    )
    return builder



# child graph of hotel booking assistant
def builder_hotel_graph(builder: StateGraph) -> StateGraph:
    # add entry note, use it when booking hotel
    builder.add_node(
        "enter_book_hotel",
        create_entry_node("Hotel Booking Assistant", "book_hotel"),  # create entry node, assign assistant name and new dialog state
    )
    builder.add_node("book_hotel", CtripAssistant(book_hotel_runnable))  # add node to process booking hotel
    builder.add_edge("enter_book_hotel", "book_hotel")  # add edge to connect entry node and the process node

    # add nodes for sensitive tools and safe tools
    builder.add_node(
        "book_hotel_safe_tools",
        create_tool_node_with_fallback(book_hotel_safe_tools),
    )
    builder.add_node(
        "book_hotel_sensitive_tools",
        create_tool_node_with_fallback(book_hotel_sensitive_tools),
    )

    def route_book_hotel(state: dict):
        """
        hotel booking process based on current state route

        :param state: dictionary of current dialog state
        :return: node name of next step
        """
        route = tools_condition(state)  # decide next step
        if route == END:
            return END
        tool_calls = state["messages"][-1].tool_calls  # check tool call of the last message
        did_cancel = any(tc["name"] == CompleteOrEscalate.__name__ for tc in tool_calls)  # check if CompleteOrEscalate is called
        if did_cancel:
            return "leave_skill"  # if user requests to cancel or exit, move to node of leave_skill
        safe_toolnames = [t.name for t in book_hotel_safe_tools]  # obtain all safe tool names
        if all(tc["name"] in safe_toolnames for tc in tool_calls):  # if all tools called are safe tools
            return "book_hotel_safe_tools"  #move to node of safe tools
        return "book_hotel_sensitive_tools"  # otherwise move to node of sensitive tools

    # add edges to connect nodes of sensitive tools and safe tools back to "book_hotel"
    builder.add_edge("book_hotel_sensitive_tools", "book_hotel")
    builder.add_edge("book_hotel_safe_tools", "book_hotel")

    # route hotel booking process based on conditions
    builder.add_conditional_edges(
        "book_hotel",
        route_book_hotel,
        ["leave_skill", "book_hotel_safe_tools", "book_hotel_sensitive_tools", END],
    )
    return builder



# child graph of excursion booking assistant
def builder_excursion_graph(builder: StateGraph) -> StateGraph:
    # add entry note, use it when booking excursion
    builder.add_node(
        "enter_book_excursion",
        create_entry_node("Excursion Booking Assistant", "book_excursion"),   # create entry node, assign assistant name and new dialog state
    )
    builder.add_node("book_excursion", CtripAssistant(book_excursion_runnable))  # add node to process booking excursion
    builder.add_edge("enter_book_excursion", "book_excursion")  # add edge to connect entry node and the process node

    # add nodes for sensitive tools and safe tools
    builder.add_node(
        "book_excursion_safe_tools",
        create_tool_node_with_fallback(book_excursion_safe_tools),
    )
    builder.add_node(
        "book_excursion_sensitive_tools",
        create_tool_node_with_fallback(book_excursion_sensitive_tools),
    )

    def route_book_excursion(state: dict):
        """
        excursion booking process based on current state route

        :param state: dictionary of current dialog state
        :return: node name of next step
        """
        route = tools_condition(state)  # decide next step
        if route == END:
            return END
        tool_calls = state["messages"][-1].tool_calls  # check tool call of the last message
        did_cancel = any(tc["name"] == CompleteOrEscalate.__name__ for tc in tool_calls)  # check if CompleteOrEscalate is called
        if did_cancel:
            return "leave_skill"  # if user requests to cancel or exit, move to node of leave_skill
        safe_toolnames = [t.name for t in book_excursion_safe_tools]  # obtain all safe tool names
        if all(tc["name"] in safe_toolnames for tc in tool_calls):  # if all tools called are safe tools
            return "book_excursion_safe_tools"  # move to node of safe tools
        return "book_excursion_sensitive_tools"  # otherwise move to node of sensitive tools

    # add edges to connect nodes of sensitive tools and safe tools back to "book_excursion"
    builder.add_edge("book_excursion_sensitive_tools", "book_excursion")
    builder.add_edge("book_excursion_safe_tools", "book_excursion")

    # route excursion booking process based on conditions
    builder.add_conditional_edges(
        "book_excursion",
        route_book_excursion,
        ["book_excursion_safe_tools", "book_excursion_sensitive_tools", "leave_skill", END],
    )
    return builder
