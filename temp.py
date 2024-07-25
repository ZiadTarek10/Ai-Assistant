import os
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Form, File, UploadFile
from fastapi.responses import FileResponse , JSONResponse
from firebase_admin import credentials, firestore, initialize_app
import fitz  # PyMuPDF

import pytesseract
from key import api_key
from groq import Groq, GroqError
from weather import weather_query
from Wikipedia import search_wikipedia
from youtubesummary import get_transcript
from GenerateImage import Generate_Image
from PlayYouTube import get_youtube_video
from Google_sendEmail import process_and_send_email
from shopping import search_jumia
from text_extract_image_caption import extract_text , predict_caption
import pywhatkit
import re
import spacy
import nltk
from nltk.tokenize import word_tokenize
nlp=spacy.load("en_core_web_lg")
nltk.download('averaged_perceptron_tagger')
# Initialize FastAPI app
app = FastAPI()
pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
# Initialize LLAMA3 client
client = Groq(api_key=api_key)
messages = [
    {"role": "system", "content": "You are a friendly human assistant, you have to remember anything user tells and answer all the questions."}
]

# Initialize Firebase
cred = credentials.Certificate('F:/Grad Project/ProjectOnGithub/Ai-Assistant/FirebaseKey3.json')
initialize_app(cred)
db = firestore.client()

def is_question(sentence):

    # Tokenize and tag the sentence
    tokens = word_tokenize(sentence)
    tagged = nltk.pos_tag(tokens)
    
    # Define verb tags
    verb_tags = {'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'}
    
    # Iterate through tagged words
    for i in range(len(tagged) - 1):
        if tagged[i][1] == 'WP' and tagged[i + 1][1] in verb_tags:
            return "weather_query"
        else:
            continue

def extract_song_and_artist(text):
    # Use SpaCy for named entity recognition
    doc = nlp(text)
    song_name = None
    artist_name = None

    # Use NLTK for tokenization and basic POS tagging
    tokens = word_tokenize(text)
    pos_tags = nltk.pos_tag(tokens)
    
    # Extract artist name using SpaCy's named entity recognition
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            artist_name = ent.text
    
    # Extract song name by checking the word before 'by'
    for i in range(len(pos_tags)):
        if pos_tags[i] == ('by', 'IN') and i > 0:
            song_name = pos_tags[i-1][0]  # Return the word before "by"
    
    return song_name, artist_name


def extract_url(question):
    # Use regular expressions to find URL in the question
    url_pattern = re.compile(r'https?://\S+')
    return url_pattern


# Query the Llama3 model
def query_llama3(question: str) -> str:
    global messages
    messages.append({"role": "user", "content": question})

    doc = nlp(question.lower())
    entities = {ent.label_: ent.text.lower() for ent in doc.ents}
    tokens = word_tokenize(question.lower())
    words = {token.text.lower() for token in doc}
    songs=["hear","listen","play"]

    if 'weather' in tokens and is_question(question.lower()):
        classification = is_question(question.lower())
        if classification == "weather_query":
            # Activate weather retrieval function
            response=weather_query()



    if "wikipedia" in tokens and "search" in tokens:
        about_index = tokens.index("about") if "about" in tokens else -1
        if about_index != -1:
            # Check for entities after the word "about"
            for ent in doc.ents:
                if ent.start > about_index:
                    topic = ent.text
                    result = f'search about {topic}'
                    response = search_wikipedia(result)


    elif "summarize"in tokens and "video" in tokens:
        video_url = question.replace("summarize video", "").strip()  # Extract video URL from question
        transcript = get_transcript(video_url)
        response = query_llama3(transcript + " Summarize this script in short.")



    elif "send" in tokens and "email" in tokens:
        response =   process_and_send_email(question.lower()) 





    
    elif any(song in words for song in songs):
        song, artist = extract_song_and_artist(question.lower())
        if song and artist:
            response=get_youtube_video(song)




    elif "search jumia" in question.lower():
        product_name = question.replace("search jumia", "").strip()   
        response = search_jumia(product_name)  
    elif "generate image" in question.lower():
        image_prompt = question.replace("generate image", "").strip()  # Extract image description from question
        image_path = Generate_Image(image_prompt)
        response = f"Image generated and saved to: {image_path}"
        messages.append({"role": "assistant", "content": response})
        return image_path  # Return the path of the generated image directly
    else:
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama3-8b-8192"
        )
        response = chat_completion.choices[0].message.content

    messages.append({"role": "assistant", "content": response})
    return response

# Store interaction in Firestore
def store_interaction(user_id, question, response):
    user_ref = db.collection('users').document(user_id)
    doc = user_ref.get()
    interaction = {'question': question, 'response': response}
    if doc.exists:
        user_ref.update({
            'interactions': firestore.ArrayUnion([interaction])
        })
    else:
        user_ref.set({
            'interactions': [interaction]
        })

# Retrieve stored interactions from Firestore
def get_stored_interactions(user_id):
    user_ref = db.collection('Users').document(user_id)
    doc = user_ref.get()

    if doc.exists:
        data = doc.to_dict()
        interactions = data.get('interactions', [])
        return interactions
    else:
        return []

# Handle user question
def handle_user_question(user_id: str, question: str) -> str:
    global messages
    interactions = get_stored_interactions(user_id)
    for interaction in interactions:
        if isinstance(interaction, dict):
            messages.append({"role": "user", "content": interaction['question']})
            messages.append({"role": "assistant", "content": interaction['response']})
    response = query_llama3(question)
    store_interaction(user_id, question, response)
    return response

def store_user_input(user_id, user_input):
    # Reference to the user's document in Firestore
    user_doc_ref = db.collection('users').document(user_id)
    
    # Try to get the document
    user_doc = user_doc_ref.get()
    
    if user_doc.exists:
        # Document exists, append the new interaction to the existing interactions
        user_data = user_doc.to_dict()
        interactions = user_data.get('interactions', [])
        interactions.append(user_input)
        user_doc_ref.update({'interactions': interactions})
    else:
        # Document does not exist, create it with the new interaction
        user_doc_ref.set({'interactions': [user_input]})
def store_user_data(user_id, question, response):
    # Reference to the user's document in Firestore
    user_ref = db.collection('users').document(user_id)
    interaction = {'question': question, 'response': response}
    user_ref.set({
            'interactions': [interaction]
        })        
@app.post("/ask")
async def ask_question(user_id: str = Form(...), question: str = Form(...), file: Optional[UploadFile] = File(None)):
    if 'summarize the pdf' in question.lower():
        if file:
            # If a PDF file is uploaded, extract its text content
            pdf_content = ""
            pdf_document = fitz.open(stream=file.file.read(), filetype="pdf")
            for page_num in range(pdf_document.page_count):
                page = pdf_document.load_page(page_num)
                pdf_content += page.get_text()
            pdf_document.close()
            response = query_llama3(pdf_content + " Summarize the following document.")
          
            return {"response": response}
    elif 'extract' in question.lower():
        if file:
            try:
                image_data = await file.read()

                # Apply both functions
                extracted_text = extract_text(image_data)
                caption = predict_caption(image_data)
                if extracted_text =="":
                    extracted_text="no text"
                elif caption =="":
                    caption="no caption just text"

                query_llama3(f"the image is: {caption}. contain text: {extracted_text}")
                response = query_llama3(" describe this image like it is infront of you")
                return {"response": response}
            except Exception as e:
                
                raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    else:
        # Handle normal text question
        response = handle_user_question(user_id, question)
        if 'generate image' in question.lower():
            # If the response is an image path, return the image file
            image_path = response
            if os.path.exists(image_path):
                return FileResponse(image_path)
            else:
                raise HTTPException(status_code=404, detail="Image not found")
        return {"response": response}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
