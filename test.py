from typing import Literal, AnyMessage

from langchain_core.messages import AnyMessage


class State(TypedDict):
    """
    define the structure of state dictionary
    :param
    messages: list of messages
    user_info: user informatino
    """
    messages: list[AnyMessage]
    dialog_state: list[
        Literal[
                "assistant",
                "update_flight",
                "book_car_rental",
                "book_hotel",
                "book_excursion"
            ]
        ]