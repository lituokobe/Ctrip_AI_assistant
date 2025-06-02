import os
import shutil
import sqlite3
import pandas as pd
from Ctrip_AI_assistant.tools import backup_file, local_file

def update_dates():
    """
    Update the date in the database, to match current date time.

    Parameters:
        file (str): path of the current database file.

    Returns:
        str: path of the updated database file.
    """



    # Use backup file to cover local file, as an initialization for each run
    shutil.copy(backup_file, local_file)  # If there is already a file with the same name, it will be covered by shutil.copy

    conn = sqlite3.connect(local_file)
    print(type(conn))

    #Obtain names of all the tables
    tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn).name.tolist()
    tdf = {}

    # Read the data of each table
    for t in tables:
        tdf[t] = pd.read_sql(f"SELECT * from {t}", conn)


    # Find the min of actual_departure as an example
    example_time = pd.to_datetime(tdf["flights"]["actual_departure"].replace("\\N", pd.NaT)).min()
    current_time = pd.to_datetime("now").tz_localize(example_time.tz)
    time_diff = current_time - example_time

    # update book_date in bookings
    tdf["bookings"]["book_date"] = (
            pd.to_datetime(tdf["bookings"]["book_date"].replace("\\N", pd.NaT), utc=True) + time_diff
    )

    # list of dates that need to be updated
    datetime_columns = ["scheduled_departure", "scheduled_arrival", "actual_departure", "actual_arrival"]
    for column in datetime_columns:
        tdf["flights"][column] = (
                pd.to_datetime(tdf["flights"][column].replace("\\N", pd.NaT)) + time_diff
        )

    # write the updates back to the database
    for table_name, df in tdf.items():
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        del df  # clear RAM
    del tdf  # clear RAM

    conn.commit()
    conn.close()

    return local_file


if __name__ == '__main__':

    # update the date
    db = update_dates()