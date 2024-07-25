import shutil
from gradio_client import Client

client = Client("prodia/fast-stable-diffusion")

def Generate_Image(prompt):
    output = client.predict(
        prompt,
        "3d, cartoon, anime, (deformed eyes, nose, ears, nose), bad anatomy, ugly",
        "absolutereality_v181.safetensors [3d9d4d2b]",
        20,
        "DPM++ 2M Karras",
        7.0,
        500,
        500,
        -0.1,
        api_name="/txt2img",
    )
    image_path = "image.png"
    shutil.move(output, image_path)
    #print (image_path) # Debugging
    return image_path
#Generate_Image("knight") #For testing the funtion 