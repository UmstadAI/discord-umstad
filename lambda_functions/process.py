# Processor with OPENAI
# DATA FORMAT WILL BE:
# THREAD ID, THREAD OWNER, THREAD TITLE, THREAD MESSAGES
# Example Thread Link: https://discord.com/channels/1153348653122076673/1213075628748709898
# Guild ID + Thread ID
# Example Message Link: https://discord.com/channels/1153348653122076673/1213072868175384587/1213084598603354172
# Guild ID + Thread ID + Message ID

import json


def lambda_handler(event, context):
    guild_id = event.get("guild_id")
    thread_id = event.get("thread_id")
    title = event.get("title")
    message = event.get("message")
    created_at = event.get("created_at")
    owner = event.get("owner")

    # TODO: Process data

    return {"statusCode": 200, "body": json.dumps("AWS Lambda got the thread")}
