import tkinter as tk
from PIL import Image, ImageTk
import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
import random
import os
import string
import threading
import time

import openai
from groq import Groq

# Function to generate a random string for the audio filename
def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

# Function to play audio and animate the mouth
def talk(args):
    global animating
    animating = True
    tts = gTTS(text=args, lang='tl')
    random_string = get_random_string(4).lower()
    audio_file = os.path.join(os.getcwd(), random_string + '-audio.mp3')
    tts.save(audio_file)
    
    # Stop the eye blinking while talking
    stop_eye_blinking()

    # Start the mouth animation in a separate thread
    animation_thread = threading.Thread(target=animate_mouth, daemon=True)
    animation_thread.start()
    
    # Play the audio in the main thread
    playsound(audio_file)
    
    # Stop the mouth animation after the audio finishes
    stop_mouth_animation()

    # Clean up the audio file after playing
    os.remove(audio_file)
    print(args)

    # Resume eye blinking after talking
    start_eye_blinking()

# Function to animate the mouth by switching between two images
def animate_mouth():
    global animating
    while animating:
        canvas.itemconfig(face_image_container, image=face_open_img)
        root.update()
        time.sleep(0.1)  # Mouth open duration

        if not animating:  # Check if we should stop animating
            break

        canvas.itemconfig(face_image_container, image=face_closed_img)
        root.update()
        time.sleep(0.1)  # Mouth closed duration

# Function to stop the mouth animation
def stop_mouth_animation():
    global animating
    animating = False
    canvas.itemconfig(face_image_container, image=face_closed_img)  # Reset to closed mouth

# Function to animate eye blinking
def blink_eyes():
    global blinking
    while blinking:
        time.sleep(random.uniform(2, 4))  # Wait before blinking
        canvas.itemconfig(face_image_container, image=face_blink_img)
        root.update()
        time.sleep(0.2)  # Blink duration
        if blinking:
            canvas.itemconfig(face_image_container, image=face_closed_img)
            root.update()

# Function to start eye blinking
def start_eye_blinking():
    global blinking
    blinking = True
    blinking_thread = threading.Thread(target=blink_eyes, daemon=True)
    blinking_thread.start()

# Function to stop eye blinking
def stop_eye_blinking():
    global blinking
    blinking = False

# Set up the Groq client
client = Groq(
    api_key="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",
)

messages = []
language = "Tagalog"
attitude = "funny and quirky"
aitype = "cool friend"
messages.append({"role": "user",
                 "content": 'You must speak ' + language + '. Act as a ' + attitude + aitype +
                            '. Respond with plain sentences, not more than 5 sentences.'})

print("Your new assistant is ready!")

def listen_and_respond():
    recognizer = sr.Recognizer()
    while True:
        with sr.Microphone() as source:
            print('listening')
            audio = recognizer.listen(source)

            try:
                print('processing')
                message = recognizer.recognize_google(audio, language='en')
                print(f"Ken: {message}")
                messages.append({"role": "user", "content": message})

                # Generate response from AI
                response = client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=messages)
                reply = response.choices[0].message.content
                print(reply)
                messages.append({"role": "assistant", "content": reply})

                # Talk (play audio and animate mouth)
                talk(reply)
                print("\Ylona: " + reply + "\n")

            except Exception as e:
                print(e)
                continue

# Set up Tkinter window for the animated face
root = tk.Tk()
root.title("Talking Face")

# Get screen dimensions
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Load the face images (closed mouth, open mouth, and blinking)
face_closed_img = Image.open("bg1.jpg")
face_open_img = Image.open("bg2.jpg")
face_blink_img = Image.open("bg3.jpg")

# Calculate new image size to maintain aspect ratio
original_width, original_height = face_closed_img.size
aspect_ratio = original_width / original_height

if original_width / screen_width > original_height / screen_height:
    new_width = screen_width
    new_height = int(new_width / aspect_ratio)
else:
    new_height = screen_height
    new_width = int(new_height * aspect_ratio)

# Resize images
face_closed_img = face_closed_img.resize((new_width, new_height), Image.ANTIALIAS)
face_open_img = face_open_img.resize((new_width, new_height), Image.ANTIALIAS)
face_blink_img = face_blink_img.resize((new_width, new_height), Image.ANTIALIAS)

# Convert images to Tkinter format
face_closed_img = ImageTk.PhotoImage(face_closed_img)
face_open_img = ImageTk.PhotoImage(face_open_img)
face_blink_img = ImageTk.PhotoImage(face_blink_img)

# Create a Canvas widget to display the face
canvas = tk.Canvas(root, width=screen_width, height=screen_height)
canvas.pack()

# Display the face with the mouth closed initially
face_image_container = canvas.create_image(screen_width//2, screen_height//2, image=face_closed_img)

# Start the eye blinking animation
start_eye_blinking()

# Start the speech recognition and response loop in a separate thread
listen_thread = threading.Thread(target=listen_and_respond, daemon=True)
listen_thread.start()

# Start Tkinter event loop
root.mainloop()
