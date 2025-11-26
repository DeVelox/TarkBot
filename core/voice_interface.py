"""
TarkBot Voice Interface
Handles audio recording and speech-to-text using Groq Whisper
"""

import os
import numpy as np
import sounddevice as sd
import soundfile as sf
from groq import Groq
import re
from num2words import num2words
import re
from num2words import num2words


def record_audio(duration=5, sample_rate=16000):
    """Record audio from microphone for specified duration."""
    audio_data = sd.rec(
        int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype="int16"
    )
    sd.wait()
    return audio_data.flatten(), sample_rate


def save_audio_to_wav(audio_data, sample_rate, filename="temp_audio.wav"):
    """Save audio data to WAV file."""
    sf.write(filename, audio_data, sample_rate, subtype="PCM_16")
    return filename


def transcribe_audio(audio_data, sample_rate):
    """Transcribe audio using Groq Whisper."""
    # Save to temp file
    temp_file = save_audio_to_wav(audio_data, sample_rate)

    try:
        # Use Groq client for transcription
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        with open(temp_file, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(temp_file, file),
                model="whisper-large-v3-turbo",
                response_format="text",
            )

        return str(transcription).strip()

    finally:
        # Clean up temp file
        if os.path.exists(temp_file):
            os.remove(temp_file)


def convert_numbers_to_words(text):
    """Convert numbers in text to words for better TTS pronunciation."""

    def replace_number(match):
        number = int(match.group().replace(",", ""))
        return num2words(number)

    # Handle all numbers, including those with commas
    text = re.sub(r"\b\d{1,3}(?:,\d{3})*\b", replace_number, text)

    return text


def synthesize_speech(text):
    """Synthesize speech using Groq TTS with number-to-text conversion."""
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    # Convert numbers to words for better pronunciation
    processed_text = convert_numbers_to_words(text)

    temp_file = "temp_speech.wav"
    response = client.audio.speech.create(
        model="playai-tts",
        voice="Basil-PlayAI",
        input=processed_text,
        response_format="wav",
    )

    response.write_to_file(temp_file)

    # Play the audio
    play_audio_file(temp_file)

    # Clean up
    os.remove(temp_file)


def synthesize_speech_with_original_text(text):
    """Synthesize speech with number conversion, but return original text for display."""
    synthesize_speech(text)
    return text


def play_audio_file(filename):
    """Play audio file using sounddevice."""
    data, samplerate = sf.read(filename)
    sd.play(data, samplerate)
    sd.wait()


def get_voice_input(duration=5):
    """Record and transcribe voice input."""
    audio_data, sample_rate = record_audio(duration=duration)
    text = transcribe_audio(audio_data, sample_rate)
    return text
