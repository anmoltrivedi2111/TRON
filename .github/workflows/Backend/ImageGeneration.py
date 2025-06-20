import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import get_key
import os 
from time import sleep

# function to open and display image based on the given prompt
def open_images(prompt):
    folder_path = r"Data/GeneratedImages"   #folder where images are stored
    prompt = prompt.replace(' ','_')    #REPLACING SPACES WITH UNDERSCORES
    
    #GENERATING FILENAMES FOR THE IMAGES
    Files = [f"{prompt}{i}.jpeg" for i in range(1,5)]
    
    for jpg_file in Files:
        img_path = os.path.join(folder_path,jpg_file)
        
        try:
            img = Image.open(img_path)
            print(f"Opening image {img_path}")
            img.show()
            sleep(1)
        
        except IOError:
            print(f"Unable to Open Image.. {img_path}")
            
#API details Huggingface stablediffusion model
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {get_key('.env','HuggingFaceApiKey')}"}

# function to send query to huggingface api
async def query(payload):
    response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
    return response.content

# async function to generate image based on given prompt
async def generate_images(prompt: str):
    tasks = []
    
    #creating 4 image generation tasks
    for _ in range(4):
        payload = {
            "inputs": f"{prompt} quality=4K, sharpness=maximum, Ultra High details, high resolution, seed={randint(0,1000000)}"
        }
        task = asyncio.create_task(query(payload))
        tasks.append(task)
        
    #WAIT for all tasks to complete
    image_bytes_list = await asyncio.gather(*tasks)
    
    #saving generated images to files
    for i, image_bytes in enumerate(image_bytes_list):
        with open(rf"Data\GeneratedImages\{prompt.replace(' ','_')}{i+1}.jpeg","wb") as f:
            f.write(image_bytes)
            
#wrapper function to generate and open images

async def GenerateImages(prompt: str):
    asyncio.run(generate_images(prompt))
    open_images(prompt)
    
#Main loop to monitor for image generation request

    
def StartGen(prompt):
    while True:
            
        try:
            with open(r"Frontend/Files/imageGeneration.data","r") as f:
                Data: str = f.read()
                    
            prompt, status = Data.split(",")
                
            #if status indicates image generation request
            if status=="True":
                print("Generating Image....")
                GenerateImages(prompt=prompt)
                    
                with open(r"Frontend/Files/imageGeneration.data","w") as f:
                    f.write("False,False")
                    break
                
            else:
                sleep(1)
        except Exception as e:
            print(f"error generating image {e}")



with open(r"Frontend/Files/imageGeneration.data","r") as f:
                    Data: str = f.read()
                    
                    prompt, status = Data.split(",")
                    


StartGen(prompt)