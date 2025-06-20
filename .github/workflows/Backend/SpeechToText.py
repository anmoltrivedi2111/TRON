#importing libraries
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import mtranslate as mt
import time

#loading environment from env file
env_vars = dotenv_values(".env")

InputLanguage = env_vars.get("InputLanguage")  #getiing input language

#Html Code for speech recognition Interface

HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new webkitSpeechRecognition() || new SpeechRecognition();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            };

            recognition.onend = function() {
                recognition.start();
            };
            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
            output.innerHTML = "";
        }
    </script>
</body>
</html>'''

#Replacing the Html code language settings with the input language for environment variables

HtmlCode = str(HtmlCode).replace("recognition.lang = '';", f"recognition.lang= '{InputLanguage}';")

#write the modified html code to the file
with open(r"Data/Voice.html","w") as f:
    f.write(HtmlCode)

#getting current working directory
current_dir = os.getcwd()

#generating file path for html file
Link = f"{current_dir}/Data/Voice.html"

#SETTING CHROME OPTIONS FOR WEBDRIVER
chrome_options = Options()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.142.86 Safari/537.36"
chrome_options.add_argument(f'user-agent={user_agent}')
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument("--headless=new")

#Initialize the chrome Webdriver using the ChromeDriverManager
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service,options=chrome_options)

#Defining path for temporary Files
TempDirPath = rf"{current_dir}/Frontend/Files"

#Function to set the assistant's status by writing it to a file

def SetAssistantStatus(Status):
    with open(rf'{TempDirPath}/Status.data',"w",encoding='utf-8') as file:
        file.write(Status)
        
#Function for modifying query for proper punctuation and formatting
def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    
    question_words = ["how","what","who","where","when","why","which","whose","whom","can you","what's","where's","how's","can you"]        

#Checking if the Query is a question and adding a question mark if necessary
    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.','?','!']:
            new_query = new_query[:-1] + "?"
    
        else:
            new_query +="?"
    else:
        #Adding a period if the query is not a question.
        if query_words[-1][-1] in ['.','?','!']:
            new_query = new_query[:-1] + "."
        else:
            new_query+= "."
            
    return new_query.capitalize()

#Function to Translate text into english using mtranslate library
def UniversalTranslator(Text):
    english_translation = mt.translate(Text, "en", "auto")
    return english_translation.capitalize()

#Function to perform speech recognition using webdriver
def SpeechRecognition(timeout=15):
    try:
        # Open the HTML speech interface
        driver.get("file:///" + Link)
        driver.find_element(by=By.ID, value="start").click()
        
        start_time = time.time()
        
        while True:
            # Timeout condition to prevent infinite freeze
            if time.time() - start_time > timeout:
                print("Timed out waiting for speech input.")
                driver.find_element(by=By.ID, value="end").click()
                return "No Input"

            try:
                Text = driver.find_element(by=By.ID, value="output").text
                
                if Text:
                    driver.find_element(by=By.ID, value="end").click()
                    
                    if InputLanguage.lower() == "en" or "en" in InputLanguage.lower():
                        return QueryModifier(Text)
                    else:
                        SetAssistantStatus("Translating...")
                        return QueryModifier(UniversalTranslator(Text))
            except Exception as e:
                print("Inner loop error:", e)
            
            time.sleep(0.5)  # Prevent CPU overuse and allow time for results
    except Exception as e:
        print("SpeechRecognition failed:", e)
        return None
#main execution block
if __name__ == "__main__":
    while True:
        #Continuously perform speech recognition and print the recognized text
        Text = SpeechRecognition()
        print(Text)