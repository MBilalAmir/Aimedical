
import streamlit as st
import speech_recognition as sr
import os
from dotenv import load_dotenv
import requests
import openai
import pyttsx3
import time
import json
from googletrans import Translator
import tempfile
from pydub import AudioSegment
from pydub.playback import play

# Load environment variables
load_dotenv()

# Initialize the recognizer
recognizer = sr.Recognizer()

# Initialize translator
translator = Translator()

# Initialize OpenAI client
#client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
openai.api_key = "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"

# Language codes and names mapping
LANGUAGES = {
    'af': 'Afrikaans', 'sq': 'Albanian', 'am': 'Amharic', 'ar': 'Arabic',
    'hy': 'Armenian', 'az': 'Azerbaijani', 'eu': 'Basque', 'be': 'Belarusian',
    'bn': 'Bengali', 'bs': 'Bosnian', 'bg': 'Bulgarian', 'ca': 'Catalan',
    'ceb': 'Cebuano', 'ny': 'Chichewa', 'zh-cn': 'Chinese (Simplified)',
    'zh-tw': 'Chinese (Traditional)', 'co': 'Corsican', 'hr': 'Croatian',
    'cs': 'Czech', 'da': 'Danish', 'nl': 'Dutch', 'en': 'English',
    'eo': 'Esperanto', 'et': 'Estonian', 'tl': 'Filipino', 'fi': 'Finnish',
    'fr': 'French', 'fy': 'Frisian', 'gl': 'Galician', 'ka': 'Georgian',
    'de': 'German', 'el': 'Greek', 'gu': 'Gujarati', 'ht': 'Haitian Creole',
    'ha': 'Hausa', 'haw': 'Hawaiian', 'iw': 'Hebrew', 'hi': 'Hindi',
    'hmn': 'Hmong', 'hu': 'Hungarian', 'is': 'Icelandic', 'ig': 'Igbo',
    'id': 'Indonesian', 'ga': 'Irish', 'it': 'Italian', 'ja': 'Japanese',
    'jw': 'Javanese', 'kn': 'Kannada', 'kk': 'Kazakh', 'km': 'Khmer',
    'ko': 'Korean', 'ku': 'Kurdish (Kurmanji)', 'ky': 'Kyrgyz', 'lo': 'Lao',
    'la': 'Latin', 'lv': 'Latvian', 'lt': 'Lithuanian', 'lb': 'Luxembourgish',
    'mk': 'Macedonian', 'mg': 'Malagasy', 'ms': 'Malay', 'ml': 'Malayalam',
    'mt': 'Maltese', 'mi': 'Maori', 'mr': 'Marathi', 'mn': 'Mongolian',
    'my': 'Myanmar (Burmese)', 'ne': 'Nepali', 'no': 'Norwegian', 'ps': 'Pashto',
    'fa': 'Persian', 'pl': 'Polish', 'pt': 'Portuguese', 'pa': 'Punjabi',
    'ro': 'Romanian', 'ru': 'Russian', 'sm': 'Samoan', 'gd': 'Scots Gaelic',
    'sr': 'Serbian', 'st': 'Sesotho', 'sn': 'Shona', 'sd': 'Sindhi',
    'si': 'Sinhala', 'sk': 'Slovak', 'sl': 'Slovenian', 'so': 'Somali',
    'es': 'Spanish', 'su': 'Sundanese', 'sw': 'Swahili', 'sv': 'Swedish',
    'tg': 'Tajik', 'ta': 'Tamil', 'te': 'Telugu', 'th': 'Thai', 'tr': 'Turkish',
    'uk': 'Ukrainian', 'ur': 'Urdu', 'uz': 'Uzbek', 'vi': 'Vietnamese',
    'cy': 'Welsh', 'xh': 'Xhosa', 'yi': 'Yiddish', 'yo': 'Yoruba', 'zu': 'Zulu'
}

def listen_to_voice():
    """Capture voice input from microphone and convert to text"""
    with sr.Microphone() as source:
        st.write("Listening... Speak now!")
        audio = recognizer.listen(source)
        
    try:
        st.write("Recognizing...")
        text = recognizer.recognize_google(audio)
        st.write(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        st.write("Sorry, I couldn't understand what you said.")
        return None
    except sr.RequestError as e:
        st.write(f"Could not request results; {e}")
        return None

def generate_ai_response(prompt, system_prompt="You are a helpful assistant."):
    """Generate text using OpenAI"""
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        st.write(f"Error generating AI response: {e}")
        return None

def translate_text(text, target_language):
    """Translate text to target language using Google Translate"""
    try:
        translation = translator.translate(text, dest=target_language)
        return translation.text
    except Exception as e:
        st.write(f"Translation error: {e}")
        
        # Fallback to LibreTranslate if Google Translate fails
        try:
            url = "https://libretranslate.com/translate"
            payload = {
                "q": text,
                "source": "auto",
                "target": target_language,
                "format": "text"
            }
            response = requests.post(url, data=payload)
            result = response.json()
            return result.get("translatedText")
        except Exception as e2:
            st.write(f"Fallback translation error: {e2}")
            return None

def text_to_speech(text, lang='en'):
    """Convert text to speech and play it"""
    tts = gTTS(text=text, lang=lang)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts.save(fp.name)
        audio = AudioSegment.from_mp3(fp.name)
        play(audio)
    os.unlink(fp.name)

def save_conversation(original_text, ai_response, translated_text, target_language):
    """Save conversation history to a JSON file"""
    conversation = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "original_text": original_text,
        "ai_response": ai_response,
        "translated_text": translated_text,
        "target_language": f"{target_language} ({LANGUAGES.get(target_language, 'Unknown')})"
    }
    
    history_file = "conversation_history.json"
    
    try:
        # Load existing history if file exists
        if os.path.exists(history_file):
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        else:
            history = []
        
        # Add new conversation
        history.append(conversation)
        
        # Save updated history
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
            
        st.write(f"Conversation saved to {history_file}")
    except Exception as e:
        st.write(f"Error saving conversation: {e}")

def main():
    st.title("Medical translate Translator with AI")
    st.write("This app will listen to your voice, process it with AI, and translate the response.")
    
    # Set custom system prompt
    system_prompt = st.text_input("Enter a custom system prompt:", 
                                  value="You are a helpful medical assistance that provides clear and concise responses.")
    
    # Language selection
    target_language = st.selectbox("Select target language:", 
                                   options=list(LANGUAGES.keys()), 
                                   format_func=lambda x: f"{x} - {LANGUAGES[x]}")
    
    if st.button("Start Voice Recognition"):
        voice_input = listen_to_voice()
        
        if voice_input:
            st.write("Generating AI response...")
            ai_response = generate_ai_response(voice_input, system_prompt)
            
            if ai_response:
                st.write("AI Response:")
                st.write(ai_response)
                
                st.write(f"Translating to {LANGUAGES[target_language]}...")
                translated_text = translate_text(ai_response, target_language)
                
                if translated_text:
                    st.write("Translated Response:")
                    st.write(translated_text)
                    
                    # Save conversation
                    save_conversation(voice_input, ai_response, translated_text, target_language)
                    
                    # Text-to-speech
                    if st.button("Listen to Translation"):
                        text_to_speech(translated_text, target_language)
                else:
                    st.write("Translation failed. Please try again.")
            else:
                st.write("Failed to generate AI response. Please try again.")

if __name__ == "__main__":
    main()
