from googlesearch import search
from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values


env_vars = dotenv_values(".env")

# retrieve specific environment variables for username, assistant name, and API key

Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# initializing the groq client using the provided API key
client = Groq(api_key=GroqAPIKey)

# Defining System Instructions
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

# loading chatlog and creating one if doesnt exist
try:
    with open(r"Data/Chatlog.json", "r") as f:
        messages = load(f)
except:
    with open(r"Data/Chatlog.json", "w") as f:
        dump([], f)


def GoogleSearch(Query):
    results = list(search(Query, advanced=True, num_results=5))
    Answer = f"The Search Results for {Query} are : \n[start]\n"

    for i in results:
        Answer += f"Title : {i.title}\n Description : {i.description}\n\n"

        Answer += "[end]"
        return Answer


# Function to clean up and make the answer breif and short
def AnswerModifier(Answer):
    lines = Answer.split("\n")
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = "\n".join(non_empty_lines)
    return modified_answer


SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can i help you?"},
]


def Information():
    data = ""
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")

    data += "Use this Real-time Information if needed\n"
    data += f"Day : {day}"
    data += f"Date : {date}"
    data += f"Month : {month}"
    data += f"Year : {year}"
    data += f"Time : {hour} Hours, {minute} Minutes, {second} Seconds"
    return data


# Function to handle Real-time search and Response generation
def RealtimeSearchEngine(prompt):
    global SystemChatBot, messages

    # loading chatlog from json file
    with open(r"Data/Chatlog.json", "r") as f:
        messages = load(f)
    messages.append({"role": "user", "content": f"{prompt}"})

    # add search result to the system chatbot messages
    SystemChatBot.append({"role": "system", "content": GoogleSearch(prompt)})

    # generating response using Groq client
    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=SystemChatBot
        + [{"role": "system", "content": Information()}]
        + messages,
        temperature=0.7,
        max_tokens=2048,
        top_p=1,
        stream=True,
        stop=None,
    )

    Answer = ""

    # concatinate response chunks from the Streaming output

    for chunk in completion:
        if chunk.choices[0].delta.content:
            Answer += chunk.choices[0].delta.content

    # clean-up response
    Answer = Answer.strip().replace("</s>", "")
    messages.append({"role": "assistant", "content": Answer})

    # saving the update chatlog in json file
    with open(r"Data/Chatlog.json", "w") as f:
        dump(messages, f, indent=4)

    # remove the most recent system messages from the chatbot conversation
    SystemChatBot.pop()
    return AnswerModifier(Answer=Answer)


if __name__ == "__main__":
    while True:
        prompt = input("Enter Your Query: ")
        print(RealtimeSearchEngine(prompt))
