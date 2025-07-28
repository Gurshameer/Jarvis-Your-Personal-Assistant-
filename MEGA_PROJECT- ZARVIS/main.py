# 'import' keyword is used to bring external python modules into current python file
# 'as' keyword is used to give a nickname to our library
#api key: AIzaSyAAIEb6kmim81nBsHHLmOCk6nBr1oOqEm4

import speech_recognition as sr        #speech to text online module provides various 
import webbrowser as wb                #used to opening web pages in a user's default browser
import pyttsx3 as p3                   #basic text to speech module
import musicLibrary                    #custom file contains dictionary of  music names with their yt links
import os                              #to access any files/folders from the user's desktop
from openai import OpenAI    # openrouter integration(ans from LLM's like mistral)
import datetime

# now importing threading for asynchronous process of logging the response of llm in background,
# either user says"stop jarvis" or not 
import threading
stop_speaking = False       # global flag to controll stopping feature
ttsx = None               # global engine will be initialized in init_engine()

# creating a object of recognizer (has a collection of speech recognition functionalities)
recognizer = sr.Recognizer()

def init_engine():
    global ttsx
    ttsx = p3.init()
    ttsx.setProperty('rate', 180)  # Optional: Adjust speaking speed

# initialize OpenRouter-compatible OpenAI client
client = OpenAI(
    api_key="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",  
    base_url="https://openrouter.ai/api/v1"
)

def speak(text):
    global ttsx
    if not ttsx:
        init_engine()
    print(f"[Speaking]: {text}")
    ttsx.say(text)
    ttsx.runAndWait()

# log the response of llm to a log file
def log_response(question , answer):
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("llm_log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(f"[{time}]\n")
        log_file.write(f"User: {question}\n")
        log_file.write(f"LLM: {answer}\n")
        log_file.write("="*50 + "\n")
        

 # LLM response function 
def ask_openrouter(prompt):
    try:
        response = client.chat.completions.create(
            model="mistralai/mixtral-8x7b-instruct",
            messages=[
                {"role": "system", "content": "Respond briefly in 1-2 sentences suitable for voice assistants."},
                {"role": "user", "content": prompt}
            ]
        )
        answer = response.choices[0].message.content.strip()
        log_response(prompt, answer)
        speak(answer)
        return answer
    except Exception as e:
        error_msg = f"Error: {e}"
        log_response(prompt, error_msg)
        speak("Sorry, something went wrong while talking to the web.")
        return error_msg





def processCommand(c):
    if "open google" in c.lower():
        speak("opening google now")
        wb.open("https://google.com")

    elif "open youtube" in c.lower():
        speak("opening youtube now")
        wb.open("https://youtube.com")

    elif "open brave" in c.lower():
        speak("opening brave now")
        wb.open("https://brave.com")
    
    elif "open linkedin" in c.lower():
        speak("opening linkedin now")
        wb.open("https://linkedin.com")
    
    elif "open downloads" in c.lower():
        speak("Opening Downloads folder")
        os.system("start shell:downloads")

    elif "play" in c.lower():
        try:
            song = c.lower().split(" ", 1)[1].strip()
            link = musicLibrary.music.get(song)
            if link:
                speak(f"Playing {song}")
                wb.open(link)
            else:
                speak(f"Sorry, I couldn't find {song} in your music library.")
        except IndexError:
            speak("Please say the song name after 'play'")
        
    elif "shutdown" in c.lower():
        speak("Goodbye sir, shutting myself down.")
        exit() 
        
# here i have added the functionality of gemini to answer the ques from web
    elif "ask web" in c or  "ask gemini" in c:
        if "ask web" in c:
            query = c.replace("ask web", "").strip()
        else:
             query = c.replace("ask gemini", "").strip()
        
        if query:
            speak("Let me search that for you...")
            print("Searching........")
            result = ask_openrouter(query)
        else:
            speak("Please say what you'd like me to search.")
        pass

    elif "stop jarvis" in c.lower():
        global stop_speaking
        stop_speaking = True
        if ttsx:
            ttsx.stop()
        init_engine()  # Reset engine to ensure future speaks work

        




if __name__ == "__main__":
    init_engine()
    speak("Initializing jarvis....")
    while True:
        # first listen for the wake keyord "jarvis"
        r = sr.Recognizer()
        try:
            # obtain audio from microphone
            with sr.Microphone() as source:
                print("Listening....")
            # timeout: maximum no of seconds that this will wait for phrase before giving up and throwing error
                print("Recognizing word!!")
            #  phrase_time_limit: maximum number of seconds that this will allow a phrase to 
            # continue before stopping and returning the part of the phrase processed before the time limit was reached.
                audio = r.listen(source,timeout=2,phrase_time_limit=5)
            # command in sr to take various speech recognition modules within it
            word = r.recognize_google(audio)
            if(word.lower() == 'jarvis'):
                speak("yes sir !!")
                # listen to command
                with sr.Microphone() as source:
                    print("Jarvis Active....")
                    audio = r.listen(source)
                    command = r.recognize_google(audio)
                    processCommand(command)

        except Exception as e:
            print("Error")