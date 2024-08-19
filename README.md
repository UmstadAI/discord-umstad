# Discord Umstad Bot for MINA Protocol Server
A Discord Bot which uses zkApp Umstad infrastructure. Supports, helps users in MINA Protocol Discord Channels with Command Prefix, Slash Commands, Automatized Answers and Chat Interface.

**Automated Responses for Forum Threads:** The Umstad bot can answer the question immediately when a forum thread opened in the zkapps-questions forum channel.

**Command Prefix & Slash Commands:** The Umstad bot can get involved the conversation in spesific channels with command prefix or slash commands.

**Chat Interface:** People can use Direct Message interface for asking to the zkApp Umstad.

**24/7 Availability:** It will provide online 24/7 assistance to people.

**Searcher Functionality:**  Umstad bot can query the Vector DB and find related threads and answer with their information(thread IDs, thread titles) etc.

## Setup

Create .env file in the root folder:
```
DISCORD_TOKEN=XXXXXXXX
SEARCHER_DISCORD_TOKEN=XXXXXXXXXX
THREAD_UPLOADER_DISCORD_TOKEN=XXXXXXXXXXXX

OPENAI_API_KEY=XXXXXXXX
AUTH_TOKEN=XXXXXXXXX

PINECONE_API_KEY=XXXXXXXXXXX
PINECONE_ENVIRONMENT=XXXXXXXXX
```

Discord bot must have write and read permissions.

## Usage & Bots

#### Umstad Bot
```bot.py``` in the root folder. Uses ```commands.py```, ```message.py``` and ```forum_listener.py```

- Slash Command with getting previous messages with number.
- Command prefix _!umstad_ can call the bot.
- Can be used with DM.
- It listens recently created threads, if AI Support is needed, answers. Posts threads to api named lambda functions, currently FAST API.

#### Search Bot
It is an AI Search Engine, which gets threads from Pinecone Vector DB which are uploaded by thread uploader and lambda functions.
Uses demo-search vector or search vector.

##### How to Run
1. Clone the repository and create .env file like [in there](#setup)
2. Build Docker:
```sh
docker build -t searchumstad .
```

3. Stop and remove if it is working:
```sh
docker stop searchumstad_container
docker rm searchumstad_container
```

3. Run the Docker Container:
```sh
docker run --name searchumstad_container searchumstad
```

#### Thread Uploader Bot
In ```thread_uploader/bot.py```,
- Scans the forum channel 
- If these threads are not in tiny db, 
- Decides if active threads are solved. 
- Uses ```process_thread.py``` and post the thread data to lambda uploader.

#### Archived Getter and Uploader
In ```thread_uploader/archived_getter.py``` and ```archived_uploader.py```
- Gets archived threads and export them as ```payloads.json``` process and upload them to vector db.

## How To Run

Need 4 terminals, each of them requires activated env.
```source venv/bin/activate````

In config.py
```IS_THREAD_PROCESSOR_DONE = True```

1. In the root folder to run main bot:
```python bot.py````

2. In the root folder to run thread searcher bot:
```python search_bot.py````

3. In the thread_uploader folder to run thread scanner and uploader bot:
```python thread_uploader/bot.py````

4. In the lambda_functions folder to run helper api to process thread data:
```cd lambda_functions && uvicorn main:app --host 127.0.0.1 --port 8000```
