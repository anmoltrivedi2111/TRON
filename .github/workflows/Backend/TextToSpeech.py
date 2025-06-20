import pygame
import random
import asyncio
import edge_tts
import os
from dotenv import dotenv_values

# Loading environment from .env
env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice")


# Asynchronous function to convert text into audio file
async def TextToAudioFile(text) -> None:
    File_path = r"Data/speech.mp3"  # defining path where speech file will be saved

    if os.path.exists(File_path):  # checking if file already exists
        os.remove(File_path)  # if it exists, remove it to avoid overwriting errors

    # Create the communication object to generate speech
    communicate = edge_tts.Communicate(text, AssistantVoice, pitch="+5Hz", rate="+12%")
    await communicate.save(
        r"Data\speech.mp3"
    )  # save the generated speech as an mp3 file


# Function to manage Text to Speech Functionality
def TTS(Text, func=lambda r =None: True):
    while True:
        try:
            # Convert text to an audio file asynchronously
            asyncio.run(TextToAudioFile(Text))

            # initiating pygame mixer for audio playback
            pygame.mixer.init()
            pygame.time.delay(200)  #for proper initialization of pygame mixer
            # Load the generated speech file into pygame mixer
            pygame.mixer.music.load(r"Data\speech.mp3")
            pygame.time.delay(300)  #waiting 300ms to load the audio properly
            pygame.mixer.music.play()

            # Loop until the audio is done playing or the function stops
            while pygame.mixer.music.get_busy():
                if func() == False:  # check if the external function returns false
                    break
                pygame.time.Clock().tick(10)  # limit the loop to 1-ticks per second

            return True  # return true if audio played successfully
        except Exception as e:
            print(f"Error in TTS: {e}")

        finally:
            try:
                # CALL THE PROVIDED FUNCTION WITH FALSE TO SIGNAL THE END OF TTS
                func(False)
                pygame.mixer.music.stop()
                pygame.mixer.quit()

            except Exception as e:  # handling exceptions during cleanup
                print(f"Error in finally block: {e}")


# Function to handle Text to Speech with additional responses and long text.
def TextToSpeech(Text, func=lambda r=None: True):
    Data = str(Text).split(".")  # breaks the text into list of sentences

    # List of predefined responses for cases where the text is too long

    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        "The remaining part of the text is now on the chat screen, sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, sir.",
        "Sir, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, sir.",
        "The next part of the text is on the chat screen, sir.",
        "Sir, please check the chat screen for more information.",
        "There's more text on the chat screen for you, sir.",
        "Sir, take a look at the chat screen for additional text.",
        "You'll find more to read on the chat screen, sir.",
        "Sir, check the chat screen for the rest of the text.",
        "The chat screen has the rest of the text, sir.",
        "There's more to see on the chat screen, sir, please look.",
        "Sir, the chat screen holds the continuation of the text.",
        "You'll find the complete answer on the chat screen, kindly check it out sir.",
        "Please review the chat screen for the rest of the text, sir.",
        "Sir, look at the chat screen for the complete answer.",
    ]

    # if the text is very long(more than 4 sentences and 250 words), add a response message
    if len(Data) > 4 and len(Text) >= 250:
        TTS(" ".join(Text.split(".")[0:2]) + ". " + random.choice(responses), func)
    # otherwise, just play the whole text
    else:
        TTS(Text, func)


# Main execution loop
if __name__ == "__main__":
    while True:
        user_input = input("Enter The Text: ").strip()
        if len(user_input) > 0 and ".py" not in user_input.lower():
            TextToSpeech(user_input)