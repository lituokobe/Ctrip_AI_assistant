
from typing import TypedDict, Annotated, Optional, Literal
from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages

def update_dialog_stack(left: list[str], right:Optional[str])->list[str]:
    """
    Update the dialog state stack
    :param left: current state stack
    :param right: new state or action to add to the stack. If none, no action;
                  if 'pop', pop up the top (last one) of the stack; otherwise add it to the stack.
    :return: updates stack
    """
    if right is None:
        return left
    if right == 'pop':
        return left[:-1] #remove the last one of the stack
    return left + [right]


#class of state
class State(TypedDict):
    """
    define the structure of state dictionary
    :param
    messages: list of messages
    user_info: user informatino
    """
    messages: Annotated[list[AnyMessage], add_messages]
    user_info: str
    dialog_state: Annotated[
        list[ #the element must be from the following five strings
            Literal[
                "assistant",
                "update_flight",
                "book_car_rental",
                "book_hotel",
                "book_excursion"
            ]
        ],
        update_dialog_stack
    ]

