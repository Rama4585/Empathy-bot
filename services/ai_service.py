from config import client

# ============
# OPENAI
# ============
def process_audio(file_path):
    with open(file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)

    prompt = """
Ты — эксперт по эмоциональному интеллекту и эффективной коммуникации.

Проанализируй текст голосового сообщения и представь результат строго по пунктам:

1. Анализ эмоций:
Определи явные и скрытые эмоции отправителя (гнев, неуверенность, манипуляция, радость и т.д.).

2. Суть сообщения:
Что человек на самом деле хочет донести до меня?
(убери лишнюю "воду").

3. Варианты ответа:

Дружелюбный/креативный:
[Текст]

Профессиональный:
[Текст]

Личные границы:
[Вежливый отказ или установление дистанции]

Важно:
Пиши лаконично,
без лишних вступлений и заключений.
Только по делу.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": transcript.text}
        ]
    )

    return transcript.text, response.choices[0].message.content

  
