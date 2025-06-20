from AppOpener import close, open as appopen  # for app opening, closing
from webbrowser import open as webopen  # for web browser functionality
from pywhatkit import search, playonyt  # for google search and youtube play
from dotenv import dotenv_values  # to manage environment variables
from bs4 import BeautifulSoup  # for parsing HTML content
from rich import print  # for style console outputs
from groq import Groq  # for AI functionalites
import webbrowser  # for opening url's
import subprocess  # for system interaction
import requests  # for making http request
import keyboard  # for keyboard related actions
import asyncio  # for asynchronous programming
import os  # for operating system functionalities
from time import sleep
# load environment variables
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

# define CSS classes for parsing specific elements element into HTML content
classes = [
    "zCubwf",
    "hgKElc",
    "LTKOO sY7ric",
    "Z0LcW",
    "gsrt vk_bk",
    "FzvWSb YwPhnf",
    "pclqee",
    "tw-Data-text tw-text-small tw-ta",
    "IZ6rdc",
    "O5uR6dv LTKOO",
    "vlzY6d",
    "webanswers-webanswers_table__webanswers-table",
    "dDoNo ikb4Bb gsrt",
    "sXLaOe",
    "LWkfKe",
    "VQF4g",
    "qv3Wpe",
    "kno-rdesc",
    "SPZz6b",
]

#defining user agent for making web requests.
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

#initialize groq client with Groq api key
client = Groq(api_key=GroqAPIKey)

#predefined professional responses for user interactions
professional_responses = [
    "Your Satisfaction is my Top Priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need, don't hesitate to ask."
]
# list to store chatbot messages
messages = []

#SYSTEM message to provide context to the chatbot
SystemChatBot = [{"role":"system","content":f"Hello, I am {os.environ['Username']}, You're a content writer. You have to write content like letters, codes, applications, essays, notes, songs, poems, emails, etc."}]



#Function to perform a Google Search
def GoogleSearch(topic):
    search(topic) #use pywhatkit's search opetation to perform google search
    return True

#Function to generate content using AI and save it in a file
def Content(topic):
    #Nested function to open a file
    def OpenNotepad(File):
        default_text_editor = 'notepad.exe'
        subprocess.Popen([default_text_editor,File])
        
    #Nested Function to generate content using AI Chatbot
    def ContentWriterAI(prompt):
        messages.append({"role":"user","content":f"{prompt}"}) #Adds the user's prompt to the message list
        
        completion = client.chat.completions.create(
            model="mistral-saba-24b",     #specify AI Model
            messages= SystemChatBot + messages,     #include system instructions + chat history
            max_tokens = 2048,  #Limiting maximum tokens in response
            temperature=0.7,    #adjust response randomness
            top_p=1,            #use nucleus sampling for response diversity
            stream=True,        #Enabling streaming response
            stop=None           #Allow the model to determine Stopping Conditions
        )
        
        Answer = "" #Initialising an empty list for response
        
        #process streamed response chunks
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer+=chunk.choices[0].delta.content
                
        Answer = Answer.replace("</s>", "") #Remooves unwanted tokens from the response.
        messages.append({"role":"assistant","content":Answer})
        
        return Answer
        
    topic = topic.replace("Content ","") #removes content from the topic
    ContentByAI = ContentWriterAI(topic)    #generate content using AI
    
    #save the generated content to a text file
    with open (rf"Data\{topic.lower().replace(' ','')}.txt", "w", encoding="utf-8") as file:
        file.write(ContentByAI) #write the content to a file
        file.close()
        
    OpenNotepad(rf"Data\{topic.lower().replace(' ','')}.txt") #OPENING FILE IN NOTEPAD
    return True #indicates success.

    #Function to search a topic on youtube.
def YoutubeSearch(Topic):
    url4Search = f"https://www.youtube.com/results?search_query={Topic}"    #youtube search URL
    webbrowser.open(url4Search)     #searches topic on webbrowser youtube
    return True     #indicates success

#Function to play youtube video
def PlayYouTube(query):
    playonyt(query)   #uses pywhatkit playonyt function to play video
    return True     #indicates success.
    
#Function to open an application or relevant webpage
def OpenApp(app, sess=requests.session()):
    app = app.lower().strip()

    # Handle common names manually
    if app in ["google", "chrome", "google search"]:
        webopen("https://www.google.com/")
        return True
    elif app in ["whatsapp"]:
        try:
            appopen("whatsapp", match_closest=True, output=True, throw_error=True)
            return True
        except:
            print("AppOpener failed. Opening WhatsApp Web instead.")
            webopen("https://web.whatsapp.com/")
            return True
    else:
        try:
            appopen(app, match_closest=True, output=True, throw_error=True)
            return True
        except:
            # Try extracting a link and opening
            def extract_links(html):
                if html is None:
                    return None
                soup = BeautifulSoup(html, 'html.parser')
                links = soup.find_all('a', {'jsname': 'UWckNb'})
                return [link.get('href') for link in links if link.get('href')]

            def search_google(query):
                url = f"https://www.google.com/search?q={query}"
                headers = {"User-Agent": useragent}
                response = sess.get(url, headers=headers)
                return response.text if response.status_code == 200 else None

            html = search_google(app)
            if html:
                links = extract_links(html)
                if links:
                    link = links[0]
                    webopen(link)
                    print(link)
                else:
                    print("No links found.")
            else:
                print("Failed to get search results.")
            return True

    
#function to close an app
def Closeapp(app):
    app = app.lower().strip()

    # Optional: prevent closing Chrome
    if "chrome" in app:
        print("Closing This app is restricted by design.")
        return False
    if "vscode" in app:
        print("Closing This app is restricted by design.")
        return False

    try:
        result = close(app, match_closest=True, output=True, throw_error=True)
        print(f"Attempted to close {app}. Result:\n{result}")
        return True
    except Exception as e:
        print(f"AppOpener failed to close {app}: {e}")
        
        # Fallback using taskkill (Windows)
        try:
            os.system(f"taskkill /f /im {app}.exe")
            print(f"Fallback: taskkill issued for {app}.exe")
            return True
        except Exception as kill_err:
            print(f"Fallback also failed: {kill_err}")
            return False
   #indicates failure
#function to execute system level commands
def System(command):
    
    #nested function to mute system volume
    def mute():
        keyboard.press_and_release("volume mute")
        
    #function for unmute
    def unmute():
        keyboard.press_and_release("volume mute")
    
    def volume_up():
        keyboard.press_and_release("volume up ")        

    def volume_down():
        keyboard.press_and_release("volume down")
            
            #if-else for command execution
    if command=="mute":
        mute()
    elif command=="unmute":
        unmute()
    elif command=="volume down":
        volume_down()
    elif command=="volume up":
        volume_up()
    
    return True     #indicates success

    #asynchronous function to translate and execute commands.
async def TranslateAndExecute(commands: list[str]):
    funcs = []  #list to store synchronous tasks
    
    for command in commands:
        if command.startswith("open "):
            if "open it" in command:
                pass
            if "open file " == command:
                pass
            else:
                fun = asyncio.to_thread(OpenApp, command.removeprefix("open "))     #schedule app opening
                funcs.append(fun)
        elif command.startswith("general "):
            pass
        elif command.startswith("realtime "):
            pass
        elif command.startswith("close "):
            fun = asyncio.to_thread(Closeapp, command.removeprefix("close "))   #schedule app closing
            funcs.append(fun)
        elif command.startswith("play "):
            fun = asyncio.to_thread(PlayYouTube, command.removeprefix("play ")) #schedule youtube playback
            funcs.append(fun)
        elif command.startswith("content "):        #handling content commands
            fun = asyncio.to_thread(Content , command.removeprefix("content "))
            funcs.append(fun)
            
        elif command.startswith("google search "):      #handling google search
            fun = asyncio.to_thread(GoogleSearch, command.removeprefix("google search"))
            funcs.append(fun)
            
        elif command.startswith("youtube search "):         #handling youtube search
            fun = asyncio.to_thread(YoutubeSearch, command.removeprefix("youtube search "))
            funcs.append(fun)
        
        elif command.startswith("system "):     #handling system commands:
            fun = asyncio.to_thread(System, command.removeprefix("system "))
            funcs.append(fun)
            
        else:
            print(f"No Function Found For {command}")
            
    results = await asyncio.gather(*funcs)      #ececuting all tasks concurrently
    
    for result in results:
        if isinstance(result, str):     #processing result
            yield result
        else:
            yield result
            
    #ASYNCHRONOUS FUNCTION to automate command execution
async def Automation(commands: list[str]):
    async for result in TranslateAndExecute(commands):
        pass
        
    return True
    
