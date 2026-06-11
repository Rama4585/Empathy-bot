from config import client

# OPENAI
def process_audio(file_path):
    with open(file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
    
    prompt = "Ты — эксперт по эмоциональному интеллекту..." # (вставь свой полный промпт здесь)
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": transcript.text}]
    )
    return transcript.text, response.choices[0].message.content
  
