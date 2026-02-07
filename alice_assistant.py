from gtts import gTTS
import speech_recognition as sr
import datetime
import wikipedia
import webbrowser
import os
import re
import smtplib
import pywhatkit
import tkinter as tk
from tkinter import scrolledtext, simpledialog
from PIL import Image, ImageTk, ImageSequence
from tkinter import filedialog
import requests
import speedtest
import PyPDF2
import psutil
import pyautogui
import time
import subprocess
import operator
import vlc
import playsound
import random
import speedtest
from newsapi import NewsApiClient

player = None
music_folder = r"D:\College\Projects\Project\Music"
current_song_index = -1


def speak(text):
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        filename = f"temp_{int(time.time())}.mp3"  # Unique filename
        tts.save(filename)
        playsound.playsound(filename, True)  # Blocking playback
        os.remove(filename)
    except PermissionError:
        print(f"Permission denied when handling {filename}.")
        pass
    except Exception as e:
        print(f"Error in speak: {e}")
        pass

def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)
    try:
        command = r.recognize_google(audio, language='en')
        print(f"You: {command}")
        return command.lower()
    except Exception as e:
        # Instead of just returning "", raise to catch outside
        raise e

def recognize_intent(text):
    # (same intent recognition as before)
    if re.search(r'\b(wikipedia|who is|tell me about)\b', text):
        return 'wikipedia'
    elif 'youtube' in text:
        return 'youtube'
    elif 'google' in text:
        return 'google'
    elif 'time' in text:
        return 'time'
    elif 'date' in text:
        return 'date'
    elif 'code' in text:
        return 'open_code'
    elif 'exit' in text or 'quit' in text:
        return 'exit'
    elif 'open' in text and '.com' in text:
        return 'open_website'
    elif 'send email' in text:
        return 'send_email'
    elif 'send whatsapp' in text or 'whatsapp message' in text:
        return 'send_whatsapp'
    elif 'weather' in text or 'temperature' in text:
        return 'weather'
    elif 'news' in text:
        return 'news'
    elif 'read pdf' in text:
        return 'read_pdf'
    elif 'open app' in text:
        return 'open_app'
    elif 'close app' in text:
        return 'close_app'
    elif 'play music' in text:
        return 'play_music'
    elif 'stop music' in text:
        return 'stop_music'
    elif 'next song' in text or 'switch song' in text:
        return 'next_song'
    elif 'previous song' in text:
        return 'previous_song'    
    elif 'screen record' in text:
        return 'screen_record'
    elif 'internet speed' in text or 'check internet speed' in text:  
        return 'internet_speed'
    elif 'calculate' in text:
        return 'calculate'
    return 'unknown'

def read_pdf():
    try:
        pdf_path = filedialog.askopenfilename(title="Select PDF file", filetypes=[("PDF files", "*.pdf")])
        if not pdf_path:
            speak("No PDF file selected.")
            return
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            if len(reader.pages) == 0:
                speak("This PDF is empty.")
                return
            text = reader.pages[0].extract_text()
            if text.strip():
                speak(text)
            else:
                speak("Could not extract text from the first page.")
    except Exception as e:
        speak("Failed to read PDF.")
        print(e)

def play_music(volume=50):
    global player, playlist, current_song_index
    try:
        playlist = [os.path.join(music_folder, f) for f in os.listdir(music_folder) if f.endswith('.mp3')]
        if not playlist:
            speak("No music files found.")
            return
        current_song_index = random.randint(0, len(playlist) - 1)
        song = playlist[current_song_index]
        player = vlc.MediaPlayer(song)
        player.audio_set_volume(volume)
        player.play()
        speak(f"Playing {os.path.basename(song)} at volume {volume}")
    except Exception as e:
        speak("Failed to play music.")
        print(e)

def next_song():
    global player, playlist, current_song_index
    if not playlist:
        speak("No music loaded. Please play music first.")
        return
    current_song_index = (current_song_index + 1) % len(playlist)
    song = playlist[current_song_index]
    if player:
        player.stop()
    player = vlc.MediaPlayer(song)
    player.audio_set_volume(70)
    player.play()
    speak(f"Now playing: {os.path.basename(song)}")

def previous_song():
    global player, playlist, current_song_index
    if not playlist:
        speak("No music loaded.")
        return
    current_song_index = (current_song_index - 1) % len(playlist)
    song = playlist[current_song_index]
    if player:
        player.stop()
    player = vlc.MediaPlayer(song)
    player.audio_set_volume(70)
    player.play()
    speak(f"Now playing: {os.path.basename(song)}")

def stop_music():
    global player
    if player:
        player.stop()
        speak("Music stopped.")
    else:
        speak("No music is playing.")

def adjust_volume(volume):
    global player
    if player:
        player.audio_set_volume(volume)
        speak(f"Volume set to {volume}")
    else:
        speak("No music is playing, can't adjust volume.")       

def open_app():
    speak("Please tell me the app name to open.")
    app_name = take_command()
    if app_name:
        try:
            # Basic mapping, extend as needed
            apps = {
                "notepad": "notepad.exe",
                "calculator": "calc.exe",
                "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                "vlc": r"C:\Program Files\VideoLAN\VLC\vlc.exe",
            }
            path = apps.get(app_name.lower())
            if path:
                subprocess.Popen(path)
                speak(f"Opening {app_name}")
            else:
                speak(f"Sorry, I don't know how to open {app_name}")
        except Exception as e:
            speak(f"Failed to open {app_name}")
            print(e)
    else:
        speak("No app name detected.")   

def close_app():
    speak("Please tell me the app name to close.")
    app_name = take_command()
    if app_name:
        try:
            for proc in psutil.process_iter():
                if app_name.lower() in proc.name().lower():
                    proc.kill()
                    speak(f"{app_name} has been closed.")
                    return
            speak(f"{app_name} is not running.")
        except Exception as e:
            speak(f"Failed to close {app_name}")
            print(e)
    else:
        speak("No app name detected.")         

def screen_record():
    speak("Screenshot will be taken in 5 seconds.")
    time.sleep(1)
    screen = pyautogui.screenshot()
    screen.save("screenshot.png")
    speak("Screen recorded and saved as screenshot.png.")

def get_weather(city):
    api_key = "e2ae2655b7f23ebb21a794597a94a6ba"  # <-- Replace with your OpenWeatherMap API key
    base_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(base_url)
        data = response.json()
        if data["cod"] != 200:
            speak("Sorry, I couldn't find the weather for that city.")
            return
        weather_desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        weather_report = f"The weather in {city} is {weather_desc} with a temperature of {temp} degree Celsius and humidity of {humidity} percent."
        speak(weather_report)
    except Exception as e:
        speak("Sorry, I couldn't retrieve the weather information.")

def internet_speed():
    try:
        response = requests.get("https://api.fast.com/netflix-speedtest")        
        data = response.json()
        download_speed = data['download'] / 1_000_000  
        
        speak(f"Download speed is {download_speed:.2f} megabits per second.")
    
    except Exception as e:
        speak("Failed to get internet speed using Fast.com API.")
        print(f"Error: {e}")
 
def calculate():
    speak("Please tell me the math expression to calculate.")
    expr = take_command()
    if expr:
        try:
            # Remove words and keep numbers/operators
            expr = expr.lower()
            expr = expr.replace('x', '*').replace('into', '*').replace('plus', '+').replace('minus', '-').replace('divide', '/')
            # Only allow digits and operators
            expr = re.sub(r'[^0-9\+\-\*\/\.\(\) ]', '', expr)
            result = eval(expr)
            speak(f"The result is {result}")
        except Exception as e:
            speak("Sorry, I couldn't calculate that.")
            print(e)
    else:
        speak("No expression detected.")

def get_news():
    api_key = "9094c80893384cf08f3afb6929a75ee4"  
    url = f"https://newsapi.org/v2/top-headlines?country=us&category=business&apiKey={api_key}"

    try:
        response = requests.get(url)
        news_data = response.json()

        if news_data["status"] != "ok" or not news_data["articles"]:
            speak("Sorry, I couldn't fetch the news.")
            return

        speak("Here are the top news headlines.")
        for i, article in enumerate(news_data["articles"][:5], start=1):
            speak(f"Headline {i}: {article['title']}")
            time.sleep(1)  # Slight delay between headlines

    except Exception as e:
        print(f"Error: {e}")
        speak("Sorry, there was an error fetching the news.")       
# (Keep your other function definitions unchanged: read_pdf, open_app, close_app, play_music, stop_music, screen_record, internet_speed, calculate, get_weather, get_news...)

def process_command(text=None):
    """
    If text is None, tries to get voice input.
    Else uses text directly.
    """
    if text is None:
        # Try voice input
        try:
            query = take_command()
        except Exception:
            # Mic failed, fallback to text input popup
            speak("Microphone is not working. Please type your command.")
            query = simpledialog.askstring("Input", "Type your command:")
            if not query:
                speak("No command entered.")
                return
    else:
        query = text

    intent = recognize_intent(query.lower())


    if intent == 'wikipedia':
        topic = re.sub(r"(wikipedia|who is|tell me about)", "", query, flags=re.IGNORECASE).strip()
        try:
            result = wikipedia.summary(topic, sentences=2)
            speak(result)
        except Exception as e:
            speak("Sorry, I couldn't find that.")
    elif intent == 'weather':
        speak("Please tell me the city name.")
        city = take_command() if text is None else None
        if city is None:
            # fallback to input box
            city = simpledialog.askstring("Input", "Enter city name for weather:")
        if city:
            get_weather(city)
        else:
            speak("I didn't catch the city name.")
    elif intent == 'youtube':
        speak("Opening YouTube")
        webbrowser.open("https://youtube.com")
    elif intent == 'google':
        speak("Opening Google")
        webbrowser.open("https://google.com")
    elif intent == 'time':
        speak(f"The time is {datetime.datetime.now().strftime('%H:%M:%S')}")
    elif intent == 'date':
        speak(f"Today's date is {datetime.datetime.now().strftime('%Y-%m-%d')}")
    elif intent == 'open_code':
        code_path = "C:\\Path\\To\\Your\\Code.exe"
        try:
            os.startfile(code_path)
        except Exception as e:
            speak("Code editor path is not set correctly.")
    elif intent == 'open_website':
        site = query.split("open")[-1].strip()
        if not site.startswith("http"):
            site = "https://" + site
        speak(f"Opening {site}")
        webbrowser.open(site)
    elif intent == 'send_email':
        speak("What should the email say?")
        content = take_command() if text is None else None
        if content is None:
            content = simpledialog.askstring("Input", "Enter email content:")
        to = "fexota8432@nomrista.com"
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login('pawangowda1326@gmail.com', 'hnzh pjal ojrs ofds')
            server.sendmail('pawangowda1326@gmail.com', to, content)
            server.quit()
            speak("Email has been sent.")
        except Exception as e:
            speak("Sorry, I couldn't send the email.")
            print(e)
    elif intent == 'send_whatsapp':
        speak("What should the message say?")
        message = take_command() if text is None else None
        if message is None:
            message = simpledialog.askstring("Input", "Enter WhatsApp message:")
        speak("Please say the phone number including country code, like plus nine one...")
        phone_number = take_command() if text is None else None
        if phone_number is None:
            phone_number = simpledialog.askstring("Input", "Enter phone number including country code (+91...)")
        phone_number = phone_number.replace("plus", "+").replace(" ", "")
        try:
            hour = datetime.datetime.now().hour
            minute = datetime.datetime.now().minute + 2
            pywhatkit.sendwhatmsg_instantly(phone_number, message, 10)
            speak("WhatsApp message sent.")
        except Exception as e:
            speak("Failed to send WhatsApp message.")
            print(e)
    elif intent == 'news':
        get_news()
    elif intent == 'read_pdf':
        read_pdf()
    elif intent == 'open_app':
        open_app()
    elif intent == 'close_app':
        close_app()
    elif intent == 'play_music':
        play_music()
    elif intent == 'next_song':
        next_song()
    elif intent == 'previous_song':
        previous_song()    
    elif intent == 'stop_music':
        stop_music()
    elif intent == 'screen_record':
        screen_record()
    elif intent == 'internet_speed':
        speak("Checking your internet speed.")
        webbrowser.open("https://fast.com")
    elif intent == 'calculate':
        calculate()
    elif intent == 'exit':
        speak("Goodbye!")
        root.quit()
    else:
        speak("I’m not sure how to help with that.")

# GUI Setup 
root = tk.Tk()
root.title("Virtual Assistant - Alice")
gif = Image.open(r"D:\College\Projects\Project\circle.gif")
frames = [ImageTk.PhotoImage(frame.copy().convert('RGBA')) for frame in ImageSequence.Iterator(gif)]

def update(index):
    frame = frames[index]
    background_label.configure(image=frame)
    root.after(100, update, (index + 1) % len(frames))

background_label = tk.Label(root)
background_label.place(x=0, y=0, relwidth=1, relheight=1)
update(0)

center_text = tk.Label(root, text="Alice", font=("JetBrains Mono", 28, "italic"), fg="white", bg="#180522")
center_text.place(relx=0.51, rely=0.1, anchor='center')

button_frame = tk.Frame(root, bg="#ffffff")
button_frame.place(relx=0.5, rely=0.85, anchor='center')

listen_button = tk.Button(button_frame, text="🎙 Speak", command=lambda: process_command(None), font=("Arial", 14), bg="#00cc99")
listen_button.grid(row=0, column=0, padx=10)

#Text input fallback
text_input_button = tk.Button(button_frame, text="⌨️ Text Input", command=lambda: process_command_text_popup(), font=("Arial", 14), bg="#3399ff")
text_input_button.grid(row=0, column=2, padx=10)

exit_button = tk.Button(button_frame, text="❌ Exit", command=root.quit, font=("Arial", 14), bg="#ff6666")
exit_button.grid(row=0, column=1, padx=10)

# Chat interface functions 

def process_command_text_popup():
    user_input = simpledialog.askstring("Input", "Type your command:")
    if user_input:
        process_command(user_input)
    else:
        speak("No command entered.")

# Start App
speak("Hello Pawan and chiranthana! I'm Alice, your assistant. Click the Speak button or the Text Input button to give me a command.")
root.geometry("800x600")
root.mainloop()
