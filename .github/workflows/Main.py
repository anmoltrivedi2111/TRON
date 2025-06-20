from Frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus,
)
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import Chatbot
from Backend.TextToSpeech import TextToSpeech
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import threading
import json
import os
import subprocess

env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
DefaultMessage = f""" Welcome {Username} : Hello {Assistantname}, How Are You?
    {Assistantname} : Welcome {Username}. I am doing well. How May I Help You? """
subprocesses = []

Functions = [
    "open",
    "close",
    "play",
    "system",
    "content",
    "google search",
    "youtube search",
]


def ShowDefaultChatIfNoChat():
    File = open(r"Data/Chatlog.json", "r", encoding="utf-8")
    if len(File.read()) < 5:
        with open(TempDirectoryPath("Database.data"), "w", encoding="utf-8") as file:
            file.write("")

        with open(TempDirectoryPath("Responses.data"), "w", encoding="utf-8") as file:
            file.write(DefaultMessage)


def ReadChatLogJson():
    with open(r"Data/ChatLog.json", "r", encoding="utf-8") as file:
        chatlog_data = json.load(file)
    return chatlog_data


def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"User : {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"Assistant: {entry['content']}\n"
    formatted_chatlog = formatted_chatlog.replace("User", Username + " ")
    formatted_chatlog = formatted_chatlog.replace("Assistant", Assistantname + " ")

    with open(TempDirectoryPath("Database.data"), "w", encoding="utf-8") as file:
        file.write(AnswerModifier(formatted_chatlog))


def ShowChatsOnGUI():
    File = open(TempDirectoryPath("Database.data"), "r", encoding="utf-8")
    data = File.read()
    if len(str(data)) > 0:
        lines = data.split("\n")
        result = "\n".join(lines)
        File.close()
        File = open(TempDirectoryPath("Responses.data"), "w", encoding="utf-8")
        File.write(result)
        File.close()


def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChat()
    ChatLogIntegration()
    ShowChatsOnGUI()


InitialExecution()

# def srecognition():
#     Query = SpeechRecognition()
#     print("Recognized:",Query)
    


def MainExecution():
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""

    SetAssistantStatus("Listening...")
    print("SR Activating")
    
    Query = SpeechRecognition()
    
    print("Activated")
    ShowTextToScreen(f"{Username} : {Query}")
    SetAssistantStatus("Thinking...")
    print("FLDMM activating")
    Decision = FirstLayerDMM(Query)
    print("Activated DMM")

    print("")
    print(f"Decision : {Decision}")
    print("")

    G = any([i for i in Decision if i.startswith("general")])
    R = any([i for i in Decision if i.startswith("realtime")])

    Mearged_query = " and ".join(
        [
            " ".join(i.split()[1:])
            for i in Decision
            if i.startswith("general") or i.startswith("realtime")
        ]
    )

    for queries in Decision:
        if "generate " in queries:
            ImageGenerationQuery = str(queries)
            ImageExecution = True

    for queries in Decision:
        if TaskExecution == False:
            if any(queries.startswith(func) for func in Functions):
                print("Automation Running")
                run(Automation(list(Decision)))
                print("Automation Run..")
                TaskExecution = True
                
                
    if ImageExecution == True:
        print("ImageGeneration Triggered. ")
        with open(r'Frontend\Files\imageGeneration.data', "w") as file:
            file.write(f"{ImageGenerationQuery},True")
        
        # with open("Frontend\Files\imageGeneration.data","r") as file:
        #     Data: str = file.read()
    
        # prompt,status = Data.split(",")
    
    # try:
    #     subprocess.run(["python","generation_starter.py",prompt], check=True)
    
    # except subprocess.CalledProcessError as e1:
    #     print("ImageGeneration Failed: ", e1 )

    if G and R or R:
        SetAssistantStatus("Searching...")
        Answer = RealtimeSearchEngine(QueryModifier(Mearged_query))
        ShowTextToScreen(f"{Assistantname} : {Answer}")
        SetAssistantStatus("Answering...")
        TextToSpeech(Answer)
        return True

    else:
        for Queries in Decision:

            if "None" in Queries:
                pass
    
            elif "general" in Queries:
                SetAssistantStatus("Thinking...")
                QueryFinal = Queries.replace("general ", "")
                Answer = Chatbot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer)
                return True

            elif "realtime" in Queries:
                SetAssistantStatus("Searching...")
                QueryFinal = Queries.replace("realtime ", "")
                Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer)
                return True

            elif "exit" in Queries:
                QueryFinal = "Okay, Bye!"
                Answer = Chatbot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer)
                SetAssistantStatus("Answering...")
                os._exit(1)


def FirstThread():
    while True:

        currentStatus = GetMicrophoneStatus()

        if currentStatus == "True":
            print("MainExecution initializing")
            MainExecution()
            print("ME initialized")
        else:
            AIStatus = GetAssistantStatus()

            if "Available..." in AIStatus:
                sleep(0.1)
            else:
                SetAssistantStatus("Available...")


def SecondThread():
    GraphicalUserInterface()


if __name__ == "__main__":
    print("Thread Starting")
    thread2 = threading.Thread(target=FirstThread, daemon=True)
    print("Thread2 Initialized")
    thread2.start()
    print("Thread2 running")
    print("SecondThread Starting")
    SecondThread()
    print("SecondThread Running")