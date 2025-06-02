from sqlite3 import connect, Cursor
from datetime import date, datetime
from typing import Optional, Union

from langchain_core.tools import tool

from Ctrip_AI_assistant.tools import db
from Ctrip_AI_assistant.tools.location_trans import transform_location

@tool
def search_hotels(
        location: Optional[str] = None,
        name: Optional[str] = None
) -> list[dict]:
    """
    search hotel based on location and name

    parameters:
        location (Optional[str])
        name (Optional[str])

    Returns:
        list[dict]: dictionary with hotels that satisfy the requirement
    """

    conn = connect(db)
    cursor = conn.cursor()
    location = transform_location(location)
    query = "SELECT * FROM hotels WHERE 1=1"
    params = []

    if location:
        query += " AND location LIKE ?"
        params.append(f"%{location}%")
    if name:
        query += " AND name LIKE ?"
        params.append(f"%{name}%")

    print('SQL to search hotel: ' + query, 'Parameters: ', params)
    cursor.execute(query, params)
    results = cursor.fetchall()
    print('Result of hotel searching: ', results)
    conn.close()

    return [
        dict(zip([column[0] for column in cursor.description], row)) for row in results
    ]


@tool
def book_hotel(hotel_id: int) -> str:
    """
    Book hotel based on hotel id

    Parameters:
        hotel_id (int)

    Returns:
        str: If the hotel is successfully booked
    """
    conn = connect(db)
    cursor = conn.cursor()

    cursor.execute("UPDATE hotels SET booked = 1 WHERE id = ?", (hotel_id,))
    conn.commit()

    if cursor.rowcount > 0:
        conn.close()
        return f"Hotel {hotel_id} is booked successfully."
    else:
        conn.close()
        return f"Cannot find hotel with ID {hotel_id}."


@tool
def update_hotel(
        hotel_id: int,
        checkin_date: Optional[Union[datetime, date]] = None,
        checkout_date: Optional[Union[datetime, date]] = None,
) -> str:
    """
    Update hotel checkin and checkout dates based on hotel ID.

    Parameters:
        hotel_id (int)
        checkin_date (Optional[Union[datetime, date]])
        checkout_date (Optional[Union[datetime, date]])

    Returns:
        str: if the dates are updated successfully.
    """
    conn = connect(db)
    cursor = conn.cursor()

    if checkin_date:
        cursor.execute(
            "UPDATE hotels SET checkin_date = ? WHERE id = ?", (checkin_date, hotel_id)
        )
    if checkout_date:
        cursor.execute(
            "UPDATE hotels SET checkout_date = ? WHERE id = ?", (checkout_date, hotel_id)
        )

    conn.commit()

    if cursor.rowcount > 0:
        conn.close()
        return f"Hotel {hotel_id} is successfully updated."
    else:
        conn.close()
        return f"Cannot find hotel with {hotel_id}."


@tool
def cancel_hotel(hotel_id: int) -> str:
    """
    根据ID取消酒店预订。

    参数:
        hotel_id (int): 要取消的酒店预订的ID。

    返回:
        str: 表明酒店预订是否成功取消的消息。
    """
    conn = connect(db)
    cursor = conn.cursor()

    # 将booked字段设置为0来表示取消预订
    cursor.execute("UPDATE hotels SET booked = 0 WHERE id = ?", (hotel_id,))
    conn.commit()

    if cursor.rowcount > 0:
        conn.close()
        return f"Hotel {hotel_id} 成功取消。"
    else:
        conn.close()
        return f"未找到ID为 {hotel_id} 的酒店。"
