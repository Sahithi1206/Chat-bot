from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer,ChatterBotCorpusTrainer
from chatterbot.logic import BestMatch
from flask import Flask,render_template,request,jsonify
import requests
import threading
import os
import platform
from gtts import gTTS
import speech_recognition as sr



API_KEY="AIzaSyBAFj3lSe9w-kL_k8661t-pUaCxQMK4HtU"
SEARCH_ENGINE_ID="40c6b7e427c2245d3"



app=Flask(__name__)


bot=ChatBot("Alexa",read_only=True,logic_adapters=["chatterbot.logic.BestMatch"])


rule={
    "hi":"hello how can i help you",
    "who are you": "I'm Alexa the chatbot"

}


lt=ListTrainer(bot)
training_data = []
for key, value in rule.items():
    training_data.append(key)
    training_data.append(value)
lt.train(training_data)


cbt=ChatterBotCorpusTrainer(bot)
cbt.train("chatterbot.corpus.english")


@app.route("/")
def home():
    return render_template("chat.html")


@app.route("/chat",methods=["POST"])
def chat():
    try:
        data=request.json
        user_ip=data.get("message",None)
        is_voice=data.get("voice",False)


        if is_voice:
            user_ip=recording()
            print("Voice Input:", user_ip)
        if not user_ip:
            return jsonify({"reply": "I didn't catch that. Please try again."})
        alexa=response(user_ip)
        speak(alexa)
        return jsonify({"reply":alexa})
   
    except Exception as e:
        print("Error:", str(e))  
        return jsonify({"reply": "An error occurred. Please try again."})
    
    

def response(user_ip):

    if user_ip in rule:
        return rule[user_ip]
    try:
        bres=bot.get_response(user_ip)
        if bres.confidence > 0.7:
            return str(bres.text)
        else:
            google_res=search_google(user_ip)
            return str(google_res)
    except Exception as e:
        print(f"Chatbot Error: {e}")
        
# engine=pyttsx3.init()
# def speak(text):
#     def run():
#         engine.say(text)
#         # engine.runAndWait()
#         while engine._inLoop:
#             engine.iterate()
#     # thread=threading.Thread(target=run)
#     # thread.start()
#     # run()

# def speak(text):
#     if text:
#         def tts():
#             try: 
#                 subprocess.run(["say",text])
#             except Exception as e:
#                 print(f"error...{e}")
#         tts_thread=threading.Thread(target=tts,daemon=True)
#         tts_thread.start()


def recording():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Speak something...")
        recognizer.adjust_for_ambient_noise(source,duration=0.5)
        audio = recognizer.listen(source, timeout=1)

    try:
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("I couldn't understand that.")
    except sr.RequestError:
        print("Error: Could not process the request.")

def speak(text):
    def run_tts():
        if text:
            try:
                tts = gTTS(text=text, lang='en')
                tts.save("speech.mp3")

                system_os = platform.system()
                if system_os == "Darwin":
                    os.system("afplay speech.mp3")
                elif system_os == "Windows":
                    os.system("start speech.mp3")
                elif system_os == "Linux":
                    os.system("mpg321 speech.mp3")
                else:
                    print("Unsupported OS")

                os.remove("speech.mp3")

            except Exception as e:
                print(f"Speech Error: {e}")

    
    tts_thread = threading.Thread(target=run_tts, daemon=True)
    tts_thread.start()



def search_google(query):
    try:
        url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={API_KEY}&cx={SEARCH_ENGINE_ID}"
        response=requests.get(url).json()
        # print("Google Search API Response:", response)
        if "items" in response:
            best_result=response["items"][0].get("snippet","")
            return str(best_result)
        else:
            return "cannot find anything relevent"
    except Exception as e:
        print(f"Google Search Error: {e}")
        return "google error"



if __name__=="__main__":
    app.run(debug=True)

# while True:
#     user_ip=input("user:")
#     print("Alexa:",response(user_ip))



