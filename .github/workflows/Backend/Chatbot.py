#importing required libraries

from groq import Groq
from json import load,dump #for reading and writing json files
import datetime
from dotenv import dotenv_values

env_vars = dotenv_values(".env")

#retrieve specific environment variables for username, assistant name, and API key

Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# initializing the groq client using the provided API key
client = Groq(api_key=GroqAPIKey)

#EMPTY LIST FOR STORING MESSAGES
messages =[]

#defining a system message that provides context to the AI chatbot about its role and behaviour.
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

SystemChatBot = [
    {"role":"system","content":System}
]

#Attempt to load the chat-log from JSON file
try:
    with open(r"Data/Chatlog.json","r") as f:
        messages = load(f)
except FileNotFoundError:
#if the file is not found, create an empty json file for storing chat logs
    with open(r"Data/Chatlog.json","w") as f:
        dump([],f)
        
        
#function to create realtime date and time information

def RealtimeInformation():
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")
    
    
    #FORMAT THE INFORMATION INTO A STRING 
    data = f"please use this real-time information if needed,\n "
    data+= f"Day:{day}\nDate : {date}\nMonth : {month}\nYear : {year}.\n"
    data+= f"Time : {hour} hours : {minute} Minutes :{second} seconds.\n"
    
    return data

#Function for modifying the chatbot's response for better formatting

def AnswerModifier(Answer):
    lines = Answer.split('\n') #splits responses into lines
    non_empty_lines = [line for line in lines if line.strip()]  #removes empty lines
    modified_answer = '\n'.join(non_empty_lines) #join the cleaned lines
    return modified_answer

#Main chatbot function for handling user queries
def Chatbot(Query):
    """This function sends the user's Query to the chatbot and returns the AI response."""
    
    try:
        #load the existing chatlogs from json file
        with open(r"Data/Chatlog.json","r") as f:
            messages = load(f)
            
        #Append the user's query to the message list
        messages.append({"role":"user","content":f"{Query}"})
        
        #Make a request to the GROQ API for a response
        completion = client.chat.completions.create(
            model = "llama3-70b-8192",     #specify the AI model to use.
            messages=SystemChatBot + [{"role":"system","content": RealtimeInformation()}] + messages,
            max_tokens=1024,
            temperature=0.7,
            top_p = 1,
            stream=True,
            stop=None            
        )
        
        #initialize empty string to store AI's response
        
        Answer = ""        
        
        #process the streamed response chunks
        for chunk in completion:
            if chunk.choices[0].delta.content:      #check if there is content in the current chunk.
                Answer+= chunk.choices[0].delta.content     #Append the content in the answer.
                
        Answer = Answer.replace("</s>","")      #clean-up any unwanted tokens from the response
        
        #Append the chatbot's response to the message-list.
        messages.append({"role":"assistant","content":Answer})
        
        #Save the updated chatlog from the json file
        with open(r"Data/Chatlog.json","w") as f:
            dump(messages,f,indent=4)
        
        #Return the formatted response
        return AnswerModifier(Answer=Answer)
    except Exception as e:
        print(f"Error {e}")
        
        with open(r"Data/Chatlog.json","w") as f:
            dump([],f,indent=4)
        return Chatbot(Query)
    
    #Main program entry start
if __name__ == "__main__":
    while True:
        user_input = input("Enter your Question : ")
        print(Chatbot(user_input))