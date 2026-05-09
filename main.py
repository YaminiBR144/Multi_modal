import streamlit as st
from googletrans import Translator
from PIL import Image
import pytesseract
import speech_recognition as sr
from gtts import gTTS
import os
import json
import cv2
import tempfile

# If using Windows, uncomment and give your Tesseract path
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ----------------------------------
# PAGE SETTINGS
# ----------------------------------
st.set_page_config(
    page_title="Multi-Modal Translator Studio",
    layout="wide"
)

st.title("🌍 Multi-Modal Translator Studio")

translator = Translator()

# ----------------------------------
# LANGUAGE OPTIONS
# ----------------------------------
languages = {
    "English": "en",
    "Hindi": "hi",
    "French": "fr",
    "Spanish": "es",
    "German": "de",
    "Tamil": "ta",
    "Kannada": "kn"
}

# ----------------------------------
# HISTORY FILE
# ----------------------------------
HISTORY_FILE = "history.json"

if not os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "w") as f:
        json.dump([], f)

# ----------------------------------
# SAVE HISTORY
# ----------------------------------
def save_history(input_text, translated_text, lang):
    
    with open(HISTORY_FILE, "r") as f:
        history = json.load(f)

    history.append({
        "input": input_text,
        "translated": translated_text,
        "language": lang
    })

    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)

# ----------------------------------
# SIDEBAR MENU
# ----------------------------------
menu = st.sidebar.selectbox(
    "Choose Mode",
    [
        "Text Translator",
        "Image Translator",
        "Voice Translator",
        "Live Camera Translator",
        "History"
    ]
)

# ==================================
# TEXT TRANSLATOR
# ==================================
if menu == "Text Translator":

    st.header("📝 Text Translator")

    text = st.text_area("Enter Text")

    lang_name = st.selectbox(
        "Select Language",
        list(languages.keys())
    )

    lang = languages[lang_name]

    if st.button("Translate"):

        if text.strip() != "":

            translated = translator.translate(
                text,
                dest=lang
            ).text

            st.success(translated)

            save_history(
                text,
                translated,
                lang_name
            )

            st.download_button(
                "Download Translation",
                translated,
                file_name="translation.txt"
            )

# ==================================
# IMAGE TRANSLATOR
# ==================================
elif menu == "Image Translator":

    st.header("🖼️ Image Translator")

    uploaded_file = st.file_uploader(
        "Upload Image",
        type=["jpg", "jpeg", "png"]
    )

    lang_name = st.selectbox(
        "Select Language",
        list(languages.keys())
    )

    lang = languages[lang_name]

    if uploaded_file:

        image = Image.open(uploaded_file)

        st.image(image)

        extracted_text = pytesseract.image_to_string(image)

        st.subheader("Extracted Text")
        st.write(extracted_text)

        if extracted_text.strip() != "":

            translated = translator.translate(
                extracted_text,
                dest=lang
            ).text

            st.subheader("Translated Text")
            st.success(translated)

            save_history(
                extracted_text,
                translated,
                lang_name
            )

# ==================================
# VOICE TRANSLATOR
# ==================================
elif menu == "Voice Translator":

    st.header("🎤 Voice Translator")

    lang_name = st.selectbox(
        "Select Language",
        list(languages.keys())
    )

    lang = languages[lang_name]

    if st.button("Start Recording"):

        recognizer = sr.Recognizer()

        try:
            with sr.Microphone() as source:

                st.info("Speak Now...")

                audio = recognizer.listen(
                    source,
                    timeout=5
                )

                text = recognizer.recognize_google(audio)

                st.subheader("Recognized Text")
                st.write(text)

                translated = translator.translate(
                    text,
                    dest=lang
                ).text

                st.subheader("Translated Text")
                st.success(translated)

                save_history(
                    text,
                    translated,
                    lang_name
                )

                tts = gTTS(
                    translated,
                    lang=lang
                )

                temp_file = tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".mp3"
                )

                tts.save(temp_file.name)

                audio_file = open(
                    temp_file.name,
                    "rb"
                )

                st.audio(audio_file.read())

        except Exception as e:
            st.error(f"Error: {e}")

# ==================================
# LIVE CAMERA TRANSLATOR
# ==================================
elif menu == "Live Camera Translator":

    st.header("📷 Live Camera Translator")

    lang_name = st.selectbox(
        "Select Language",
        list(languages.keys())
    )

    lang = languages[lang_name]

    if st.button("Start Camera"):

        cap = cv2.VideoCapture(0)

        st.warning("Press Q to stop camera")

        while True:

            ret, frame = cap.read()

            if not ret:
                break

            gray = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2GRAY
            )

            text = pytesseract.image_to_string(gray)

            if text.strip() != "":

                translated = translator.translate(
                    text,
                    dest=lang
                ).text

                cv2.putText(
                    frame,
                    translated[:40],
                    (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2
                )

            cv2.imshow(
                "Live Translator",
                frame
            )

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()

# ==================================
# HISTORY
# ==================================
elif menu == "History":

    st.header("📜 Translation History")

    with open(HISTORY_FILE, "r") as f:
        history = json.load(f)

    if len(history) == 0:
        st.info("No History Found")

    else:
        for item in reversed(history):

            st.subheader(f"🌐 {item['language']}")

            st.write("Input:")
            st.code(item["input"])

            st.write("Translated:")
            st.success(item["translated"])

            st.markdown("---")
