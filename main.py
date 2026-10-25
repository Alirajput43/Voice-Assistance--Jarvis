
# Libraries
import subprocess
import os
from google import genai
from dotenv import load_dotenv
import speech_recognition as sr
import webbrowser
import pyttsx3
import musiclibrary
import requests
import time


load_dotenv()
newsapi = os.getenv("NEWS_API_KEY")
Gemini_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=Gemini_API_KEY) if Gemini_API_KEY else None

LANG = "en-IN"
r = sr.Recognizer()
r.dynamic_energy_threshold = True   # auto adjust according to noise
r.pause_threshold = 0.8             # sentence ends after this limit of silence
r.non_speaking_duration = 0.5       # record ke shuru/akhir ki khamoshi

def ask_ai(question):
    if client is None:
        return "API not found.Check your .env file."

    try:
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=question
        )

        return response.text or "Sorry, could not find the answer to your question."

    except Exception as e:
        print("AI Error:", e)
        return "Sorry sir, there was an error generating the response."



def speak(text):
    engine = pyttsx3.init()
    engine.setProperty("rate", 175)
    engine.setProperty("volume", 1.0)
    engine.say(str(text))
    engine.runAndWait()
    time.sleep(0.3)



def proceedCommand(c):
    c = c.lower().strip()

    # for Opening  websites.

    # for opening a wesite, say "open <website name>".
    websites = {
        "google": "https://www.google.com",
        "facebook": "https://www.facebook.com",
        "youtube": "https://www.youtube.com",
        "instagram": "https://www.instagram.com",
        "linkedin": "https://www.linkedin.com",
    }

    for name, url in websites.items():
        if f"open {name}" in c:
            speak(f"Opening {name}")
            webbrowser.open(url)
            return
    # for opening desktop apps.

    # for opening a desktop app, say "open <app name>".
    app_commands = {
        "notepad": ["open notepad", "open note pad"],
        "chrome": ["open chrome", "open krome"],
    }

    for app, phrases in app_commands.items():
        if any(phrase in c for phrase in phrases):
            speak(f"Opening {app}")
            open_app(app)
            return

    # for playing music.

    # for playing music, say "play <song name>".
    if c.lower().startswith("play"):
        song = c.lower().split(" ")[1]
        link = musiclibrary.music[song]
        speak(f"Playing {song}")
        webbrowser.open(link)

    # for playing news.

    # for listening news, say "tell me the news".
    elif "tell me the news" in c.lower():
        news =c.lower().split(" ")[3]

        news = requests.get(f"https://newsapi.org/v2/top-headlines?country=us&apiKey={newsapi}", timeout=10)
    
        if news.status_code == 200:
             data= news.json()
             articles = data["articles"]

             for article in articles[:5]:
                speak("Here are the top news headlines:")
                speak(article["title"])

        else:
            print("Error:", news.status_code)
            speak("Sorry,could not play the news. There is an error in your code.")
            print(news.text)

    else:
        answer = ask_ai(c)
        print("Jarvis:", answer)
        speak(answer)





# Function for  opening apps.           
def open_app(app_name):
    if app_name == "notepad":
        subprocess.Popen(["notepad.exe"])

    elif app_name == "chrome":
        subprocess.Popen([
            "cmd", "/c", "start", "", "chrome"
        ], shell=False)

    elif app_name == "vscode":
        subprocess.Popen(["code"])

    else:
        print("Application command could not be recognized.")



# Main programe

if __name__=="__main__":
    speak("Initializing jarvis")
    r = sr.Recognizer()
    
    while True:

        try:
            with sr.Microphone() as source:
                print("Listening...")
                r.adjust_for_ambient_noise(source, duration=1.5)
                r.energy_threshold *= 0.8  
                # listen for wake word.. 
                audio = r.listen(source, timeout=5, phrase_time_limit=3)
                word = r.recognize_google(audio)

                if((word.lower() == "alpha") or (word.lower()=="alfa") or (word.lower()=="jarvis")  or (word.lower()=="alpha")):
                    speak("Yes sir, how may I help you.")
                # Listen for command
                elif (word.lower()== "deactivate"):
                    print("Deactivated")
                    speak("Deactivated")
                    break
            
            with sr.Microphone() as source:
                print("Say Open + item name to open something, or Say Close to exit..")
                r.energy_threshold *= 0.8  
                audio = r.listen(source,timeout=5,phrase_time_limit=6)
                command = r.recognize_google(audio)
            # listen for question
            with sr.Microphone() as source:
                print("Ask you question for getting answer from Ai.")
                r.adjust_for_ambient_noise(source, duration=1.5)
                r.energy_threshold *= 0.8   
                audio = r.listen(source, timeout=12, phrase_time_limit=10)
                command = r.recognize_google(audio)
                print("Command:", command)
            proceedCommand(command)

        except Exception as e:
            print("Error; {0}".format(e))