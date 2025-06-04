from typing import Callable
from langchain_core.messages import ToolMessage


#
def create_entry_node(assistant_name: str, new_dialog_state: str) -> Callable:
    """
    This is a function framework: It creates an entry node function that is invoked when the dialog state transitions.
    The function generates a new dialog message and updates the dialog state.

    :param assistant_name: The name or description of the new assistant.
    :param new_dialog_state: The new dialog state to update to.
    :return: Returns a function that processes the dialog state based on the given assistant_name and new_dialog_state.
    """

    def entry_node(state: dict) -> dict:
        """
        Based on current dialog state, generate new dialog message and update dialog state.

        :param state: current dialog state, including all messages.
        :return: dictionary including new messages and updated dialog state.包含新消息和更新后的对话状态的字典。
        """
        # obtain the tool call from the last messages
        tool_call_id = state["messages"][-1].tool_calls[0]["id"]

        return {
            "messages": [
                ToolMessage(
                    content=f"current assistant is {assistant_name}. Please review the above conversation between main assistant and the user."
                            f"If user's intent is not satisfied, use the provided tools to help user. Remember, you are {assistant_name}."
                            "and booking, update or other operations are not completed, until the appropriate tool is called."
                            "Is user changes mind or need help for other tasks, please call CompleteOrEscalate and let the main assistant to take over."
                            "Do not mention who you are, only act as an agent of assistant.",
                    tool_call_id=tool_call_id,
                )
            ],
            "dialog_state": new_dialog_state,
        }

    return entry_node