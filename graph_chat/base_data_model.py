from pydantic import BaseModel, Field


class CompleteOrEscalate(BaseModel):  # define the data model class
    """
    A tool used to mark the current task as completed and/or escalate control of the conversation to the main assistant,
    allowing the main assistant to reroute the conversation based on user needs.
    """

    cancel: bool = True  # cancel the task by default
    reason: str  # reason of cancelling or escalation

    class Config:  # Inner class Config: json_schema_extra: this includes some example data
        json_schema_extra = {
            "example": {
                "cancel": True,
                "reason": "User has changed mind on current task.",
            },
            "example2": {
                "cancel": True,
                "reason": "I have complete the task",
            },
            "example3": {
                "cancel": False,
                "reason": "I need to search user's email or calendar to have more information.",
            },
        }


class ToFlightBookingAssistant(BaseModel):
    """
    delegate the task to flight booking assistant who specializes in flight checking, updating and canceling.
    """

    request: str = Field(
        description="Any questions that flight booking assistant needs to clarify before continuing."
    )


class ToBookCarRental(BaseModel):  #  （POVO）
    """
    delegate the task to car rental booking assistant.
    """

    location: str = Field(
        description="location where user wants to book a car rental"
    )
    start_date: str = Field(description="car rental start date")
    end_date: str = Field(description="car rental end date")
    request: str = Field(
        description="Any extra info or requestion about the car rental booking from user."
    )

    class Config:
        json_schema_extra = {
            "Example": {
                "location": "Basel",
                "start_date": "2025-07-01",
                "end_date": "2025-07-05",
                "request": "I need sedan with auto-gear.",
            }
        }


class ToHotelBookingAssistant(BaseModel):
    """
    delegate the task to hotel booking assistant.
    """

    location: str = Field(
        description="The location of the hotel that used wants to book."
    )
    checkin_date: str = Field(description="checkin date")
    checkout_date: str = Field(description="checkout date")
    request: str = Field(
        description="Any extra info or requestion about the hotel booking from user."
    )

    class Config:
        json_schema_extra = {
            "Example": {
                "location": "Zurich",
                "checkin_date": "2025-08-15",
                "checkout_date": "2025-08-20",
                "request": "I prefer hotels near the city center with a good view.",
            }
        }


class ToBookExcursion(BaseModel):
    """
    delegate the task to excursion booking assistant who specializes in excursion recommendation.
    """

    location: str = Field(
        description="User wants a booking of excursion in the location of the travel."
    )
    request: str = Field(
        description="Any extra info or requestion about the excursion recommendation from user."
    )

    class Config:
        json_schema_extra = {
            "Example": {
                "location": "Lucerne",
                "request": "User is interested in outdoor activities and sight-seeing.",
            }
        }
