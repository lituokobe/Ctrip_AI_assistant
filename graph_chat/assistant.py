import os
from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig

from Ctrip_AI_assistant.graph_chat.base_data_model import ToFlightBookingAssistant, ToBookCarRental, \
    ToHotelBookingAssistant, ToBookExcursion
from Ctrip_AI_assistant.graph_chat.llm_tavily import tavily_tool, llm
from Ctrip_AI_assistant.graph_chat.state import State
from Ctrip_AI_assistant.tools.car_tools import book_car_rental, update_car_rental, cancel_car_rental, search_car_rentals
from Ctrip_AI_assistant.tools.flights_tools import update_ticket_to_new_flight, cancel_ticket, \
    fetch_user_flight_information, search_flights
from Ctrip_AI_assistant.tools.hotels_tools import book_hotel, update_hotel, cancel_hotel, search_hotels
from Ctrip_AI_assistant.tools.retriever_vector import lookup_policy
from Ctrip_AI_assistant.tools.trip_tools import book_excursion, update_excursion, cancel_excursion, \
    search_trip_recommendations

os.environ['LANGCHAIN_TRACING'] = "true"
os.environ['LANGSMITH_ENDPOINT'] = "https://api.smith.langchain.com"
os.environ['LANGSMITH_PROJECT'] = "pr-shadowy-maybe-22"
os.environ['LANGCHAIN_PROJECT'] = "Tuo-Demo"

class CtripAssistant:
    #define a class to be a node in the graph
    def __init__(self, runnable: Runnable):
        """
        initialize assistant's instance
        :param runnable: runnable object, usually is a Runnable
        """
        self.runnable = runnable

    def __call__(self, state: State, config:RunnableConfig):
        """
        call the node, execute assistant's tasks
        :param state: current workflow's tasks
        :param config: configuration including passenger id
        :return:
        """
        while True:
            #create an infinite loop, execute it till the result from self.runnable is valid
            #if the result is invalid (e.g. no tool calls and content is empty or content doesn't meet the requirements), keep the loop going
            # configuration = config.get('configurable', {})
            # user_id = configuration.get('passenger_id', None)
            # state = {**state, 'user_info': user_id} #get passenger id from configuration and add it to state
            result = self.runnable.invoke(state)

            #if runnable is executed, but no valid result
            if not result.tool_calls and ( #if the result has no tool calls and [the content is empty or the first element of the content list has no 'text'], user need to re-input.
                not result.content
                or isinstance(result.content, list)
                and not result.content[0].get('text')
            ):
                messages = state['messages'] + [('user', 'Please provide a true input as reply.')]
                state = {**state, 'messages': messages}
            else: #if we have the valid result, then exit the loop
                break
        return {'messages': result}

#initialize tools
# part_1_tools = [
#     update_ticket_to_new_flight,
#     cancel_ticket,
#     book_car_rental,
#     update_car_rental,
#     cancel_car_rental,
#     book_hotel,
#     update_hotel,
#     cancel_hotel,
#     book_excursion,
#     update_excursion,
#     cancel_excursion,
#     tavily_tool,
#     fetch_user_flight_information,
#     search_flights,
#     lookup_policy,
#     search_car_rentals,
#     search_hotels,
#     search_trip_recommendations,
# ]
#
# safe_tools = [
#     tavily_tool,
#     fetch_user_flight_information,
#     search_flights,
#     lookup_policy,
#     search_car_rentals,
#     search_hotels,
#     search_trip_recommendations,
# ]
#
# sensitive_tools = [
#     update_ticket_to_new_flight,
#     cancel_ticket,
#     book_car_rental,
#     update_car_rental,
#     cancel_car_rental,
#     book_hotel,
#     update_hotel,
#     cancel_hotel,
#     book_excursion,
#     update_excursion,
#     cancel_excursion,
# ]
#
# sensitive_tool_names = { t.name for t in sensitive_tools}

# def create_assistant_node() -> CtripAssistant:
#     """
#     create assistant node
#     :return: assistant node
#     """
# )

primary_assistant_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a customer service assistant for Ctrip travel agency."
            "Your primary responsibility is to search for flight information and company policies to answer customer inquiries."
            "If a customer requests to update or cancel a flight, book a rental car, book a hotel, or get travel recommendations, delegate the task to the appropriate specialized assistant by invoking the corresponding tool. You cannot make these types of changes yourself."
            "Only specialized assistants have the authority to perform these actions for the user."
            "Users are unaware of the existence of different specialized assistants, so do not mention them; simply delegate the task quietly via function calls."
            "Provide detailed information to customers and always review the database before confirming that the information is unavailable."
            "Be persistent when searching. If the first search yields no results, expand the query."
            "If the search is unsuccessful, broaden the search scope before giving up."
            "\n\nCurrent passenger has following flight information:\n<Flights>\n{user_info}\n</Flights>"
            "\nCurrent time: {time}.",
        ),
        ("placeholder", "{messages}"),
    ]
).partial(time = datetime.now())

primary_assistant_tools = [tavily_tool, search_flights, lookup_policy]

assistant_runnable = primary_assistant_prompt | llm.bind_tools(
    primary_assistant_tools + [
        ToFlightBookingAssistant,
        ToBookCarRental,
        ToHotelBookingAssistant,
        ToBookExcursion,
    ]
)

    #return CtripAssistant(runnable) # create an instance



