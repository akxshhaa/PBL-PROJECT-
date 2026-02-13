import re
import pandas as pd
from itertools import zip_longest



def preprocess(data):
    pattern = r'\[(\d{1,2}/\d{1,2}/\d{2,4}),\s*\d{1,2}:\d{2}:\d{2}\s?(?:AM|PM|am|pm)?\]'
    messages = re.split(pattern, data)[1:]
    dates=re.findall(pattern,data)

    df = pd.DataFrame(list(zip_longest(messages, dates, fillvalue=None)), columns=['user_message', 'message_date'])
    df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%y', errors='coerce')
    df.rename(columns={'message_date': 'date'}, inplace=True)
    users = []
    messages = []

    for message in df['user_message']:
        entry = re.split(r'([\w\W]+?):\s', message)  # added 'r' to fix the invalid escape sequence
        if len(entry) > 2 and entry[1]:
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)
    df['year'] = df['date'].dt.year
    df['day'] = df['date'].dt.day
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    return df
