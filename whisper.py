import openai
import config
openai.api_key = config.openai_token
audio_file= open("./documents/pat_again_2.m4a", "rb")
transcript = openai.Audio.translate("whisper-1", audio_file)
print(transcript)