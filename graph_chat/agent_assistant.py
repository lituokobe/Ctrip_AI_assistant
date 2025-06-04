from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate

from Ctrip_AI_assistant.graph_chat.base_data_model import CompleteOrEscalate
from Ctrip_AI_assistant.graph_chat.llm_tavily import llm
from Ctrip_AI_assistant.tools.car_tools import search_car_rentals, book_car_rental, update_car_rental, cancel_car_rental
from Ctrip_AI_assistant.tools.flights_tools import search_flights, update_ticket_to_new_flight, cancel_ticket
from Ctrip_AI_assistant.tools.hotels_tools import search_hotels, book_hotel, update_hotel, cancel_hotel
from Ctrip_AI_assistant.tools.trip_tools import search_trip_recommendations, book_excursion, update_excursion, cancel_excursion

# flight booking assistant
flight_booking_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an assistant specializing in flight inquiries, rescheduling, and bookings."
            "When users need help updating their reservations, the main assistant will delegate the task to you."
            "Please confirm the updated flight details with the customer and inform them of any additional fees."
            "Be persistent when searching. If the first search does not yield results, expand the query scope."
            "If you need more information or the customer changes their mind, escalate the task back to the main assistant."
            "Remember, a booking is only considered complete after the relevant tools have been successfully used."
            "\n\nCurrent user flight information:\n<Flights>\n{user_info}\n</Flights>"
            "\nCurrent time: {time}."
            "\n\nIf the user needs assistance and none of your tools apply, then"
            '"CompleteOrEscalate" the conversation to the main assistant. Do not waste the user’s time. Do not fabricate invalid tools or functionalities.',
        ),
        ("placeholder", "{messages}"),
    ]
).partial(time=datetime.now())

# define safe and sensitive tools
update_flight_safe_tools = [search_flights]
update_flight_sensitive_tools = [update_ticket_to_new_flight, cancel_ticket]

# combine all the tools
update_flight_tools = update_flight_safe_tools + update_flight_sensitive_tools

# create a runnable, bind the template and tools, including CompleteOrEscalate tool.
update_flight_runnable = flight_booking_prompt | llm.bind_tools(
    update_flight_tools + [CompleteOrEscalate]
)

# hotel booking assistant
book_hotel_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an assistant specializing in hotel bookings."
            "When users need help reserving a hotel, the main assistant will delegate the task to you."
            "Search for available hotels based on the user's preferences and confirm the booking details with the customer."
            "Be persistent when searching. If the first search does not yield results, expand the query scope."
            "If you need more information or the customer changes their mind, escalate the task back to the main assistant."
            "Remember, a booking is only considered complete after the relevant tools have been successfully used."
            "\nCurrent time: {time}."
            "\n\nIf the user needs assistance and none of your tools apply, then"
            '"CompleteOrEscalate" the conversation to the main assistant. Do not waste the user’s time. Do not fabricate invalid tools or functionalities.'
            "\n\nHere are some examples where you should CompleteOrEscalate:\n"
            " - 'What’s the weather like this season?'\n"
            " - 'I’ll think about it, maybe book separately'\n"
            " - 'I need to figure out my transportation there'\n"
            " - 'Oh, wait, I haven’t booked my flight yet, I’ll do that first'\n"
            " - 'The hotel booking is confirmed'",
        ),
        ("placeholder", "{messages}"),
    ]
).partial(time=datetime.now())

# define safe and sensitive tools
book_hotel_safe_tools = [search_hotels]
book_hotel_sensitive_tools = [book_hotel, update_hotel, cancel_hotel]

# combine all the tools
book_hotel_tools = book_hotel_safe_tools + book_hotel_sensitive_tools

# create a runnable, bind the template and tools, including CompleteOrEscalate tool.
book_hotel_runnable = book_hotel_prompt | llm.bind_tools(
    book_hotel_tools + [CompleteOrEscalate]
)

# car rental booking assistant
book_car_rental_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an assistant specializing in car rental bookings."
            "When users need help reserving a rental car, the main assistant will delegate the task to you."
            "Search for available rental cars based on the user's preferences and confirm the booking details with the customer."
            "Be persistent when searching. If the first search does not yield results, expand the query scope."
            "If you need more information or the customer changes their mind, escalate the task back to the main assistant."
            "Remember, a booking is only considered complete after the relevant tools have been successfully used."
            "\nCurrent time: {time}."
            "\n\nIf the user needs assistance and none of your tools apply, then"
            '"CompleteOrEscalate" the conversation to the main assistant. Do not waste the user’s time. Do not fabricate invalid tools or functionalities.'
            "\n\nHere are some examples where you should CompleteOrEscalate:\n"
            " - 'What’s the weather like this season?'\n"
            " - 'What flight options are available?'\n"
            " - 'I’ll think about it, maybe book separately'\n"
            " - 'Oh, wait, I haven’t booked my flight yet, I’ll do that first'\n"
            " - 'The car rental booking is confirmed'",
        ),
        ("placeholder", "{messages}"),
    ]
).partial(time=datetime.now())

# define safe and sensitive tools
book_car_rental_safe_tools = [search_car_rentals]
book_car_rental_sensitive_tools = [
    book_car_rental,
    update_car_rental,
    cancel_car_rental,
]

# combine all the tools
book_car_rental_tools = book_car_rental_safe_tools + book_car_rental_sensitive_tools

# create a runnable, bind the template and tools, including CompleteOrEscalate tool.
book_car_rental_runnable = book_car_rental_prompt | llm.bind_tools(
    book_car_rental_tools + [CompleteOrEscalate]
)

# excursion booking assistant
book_excursion_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an assistant specializing in excursion bookings."
            "When users need help booking a recommended excursion, the main assistant will delegate the task to you."
            "Search for available excursions based on the user's preferences and confirm the booking details with the customer."
            "If you need more information or the customer changes their mind, escalate the task back to the main assistant."
            "Be persistent when searching. If the first search does not yield results, expand the query scope."
            "Remember, a booking is only considered complete after the relevant tools have been successfully used."
            "\nCurrent time: {time}."
            "\n\nIf the user needs assistance and none of your tools apply, then"
            '"CompleteOrEscalate" the conversation to the main assistant. Do not waste the user’s time. Do not fabricate invalid tools or functionalities.'
            "\n\nHere are some examples where you should CompleteOrEscalate:\n"
            " - 'I’ll think about it, maybe book separately'\n"
            " - 'I need to figure out my transportation there'\n"
            " - 'Oh, wait, I haven’t booked my flight yet, I’ll do that first'\n"
            " - 'The excursion booking is confirmed!'",
        ),
        ("placeholder", "{messages}"),
    ]
).partial(time=datetime.now())

# define safe and sensitive tools
book_excursion_safe_tools = [search_trip_recommendations]
book_excursion_sensitive_tools = [book_excursion, update_excursion, cancel_excursion]

# combine all the tools
book_excursion_tools = book_excursion_safe_tools + book_excursion_sensitive_tools

# create a runnable, bind the template and tools, including CompleteOrEscalate tool.
book_excursion_runnable = book_excursion_prompt | llm.bind_tools(
    book_excursion_tools + [CompleteOrEscalate]
)
