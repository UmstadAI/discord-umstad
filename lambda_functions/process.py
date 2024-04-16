# Processor with OPENAI
# DATA FORMAT WILL BE:
# THREAD ID, THREAD OWNER, THREAD TITLE, THREAD MESSAGES
# Example Thread Link: https://discord.com/channels/1153348653122076673/1213075628748709898
# Guild ID + Thread ID
# Example Message Link: https://discord.com/channels/1153348653122076673/1213072868175384587/1213084598603354172
# Guild ID + Thread ID + Message ID

import json


def lambda_handler(event, context=None):
    print(type(event))
    guild_id = event.get("guild_id")
    thread_id = event.get("thread_id")
    title = event.get("title")
    message = event.get("message")
    created_at = event.get("created_at")
    owner_id = event.get("owner_id")

    # TODO: Process data
    print("Guild ID: ", guild_id)
    print("Thread ID:", thread_id)
    print("Title: ", title)
    print("Message: ", message)
    print("Created AT: ", created_at)
    print("Owner: ", owner_id)

    

    return {"statusCode": 200, "body": json.dumps("AWS Lambda got the thread")}
