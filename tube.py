import os
from pytubefix import YouTube # Certifique-se de estar usando a biblioteca correta, pytube.
from openai import OpenAI
import time
from moviepy.editor import AudioFileClip
import tiktoken
import requests


client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key = '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',
)

# Função para contar o número de tokens em uma string para um modelo específico
def count_tokens(text, model="gpt-4"):
    # Carregar o codificador de tokens do modelo
    encoding = tiktoken.encoding_for_model(model)
    
    # Codificar a string em tokens
    tokens = encoding.encode(text)
    
    # Retornar o número de tokens
    return len(tokens)

# Função para obter a duração do arquivo de áudio em minutos
def get_audio_duration_in_minutes(audio_file):
    audio_clip = AudioFileClip(audio_file)
    duration_seconds = audio_clip.duration  # Duração em segundos
    audio_clip.close()  # Fechar o arquivo para liberar os recursos
    return duration_seconds / 60  # Converter para minutos

# Função para baixar o áudio do vídeo do YouTube
def download_audio(video_url):
    yt = YouTube(video_url)
    #yt = YouTube(video_url, use_oauth=True, allow_oauth_cache=True)
    print(f"Baixando o áudio do vídeo: {yt.title}")
    ys = yt.streams.get_audio_only()
    audio_file = ys.download(filename="audio.mp4")
    return audio_file


# Função para transcrever o áudio com tentativas de 3 vezes
def transcribe_audio_with_retries(audio_file):
    print("Iniciando a transcrição!")
    attempts = 0
    while attempts < 3:
        try:
            with open(audio_file, "rb") as file_obj:
                transcript = client.audio.transcriptions.create(model="whisper-1", file=file_obj)
            return transcript.text
        except Exception as e:
            attempts += 1
            print(f"Tentativa {attempts} falhou. Exceção: {str(e)}")
            time.sleep(5)  # Aguarda 5 segundos antes de tentar novamente
    print("Falha ao transcrever após 3 tentativas.")
    return None

# Função para resumir o texto usando GPT da OpenAI
def summarize_text(text):
    if text is None:
        return "Não foi possível gerar o resumo pois a transcrição falhou."
    
    # Chamada correta para a API de completions usando GPT-4
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Modelo GPT-4
        messages=[{"role": "user", "content": "Resuma o seguinte texto: " + text}]
    )
    
    # Extração correta do texto do resumo
    summary = response.choices[0].message.content.strip()
    return summary

# Função para remover o arquivo após o uso
def delete_audio_file(audio_file):
    try:
        os.remove(audio_file)
        print(f"Arquivo {audio_file} removido com sucesso.")
    except OSError as e:
        print(f"Erro ao remover o arquivo: {e.strerror}")



# Função que recebe 3 strings e faz uma requisição POST com RequestBody
def send_post_request(string1, string2, string3,string4, string5, string6):
    # URL da API REST
    url = "http://localhost:8089/api/v1/transcription/audioytranscribe"  # Substitua pela URL real da sua API
    
    # Corpo da requisição no formato JSON (RequestBody)
    payload = {
        "transcribe": string1,
        "summary": string2,
        "tokentranscribe": string3,
        "tokensummary": string4,
        "totaltokens": string5,
        "duration": string6
    }
    
    # Cabeçalhos da requisição, incluindo o Content-Type para JSON
    headers = {
        "Content-Type": "application/json",  # Indica que o conteúdo está em JSON
        "X-API-KEY": "1234"  # Caso seja necessário autenticação
    }
    
    try:
        # Faz a requisição POST com os dados no corpo como JSON
        response = requests.post(url, json=payload, headers=headers)
        
        # Verifica se a requisição foi bem-sucedida (status code 200)
        if response.status_code == 200:
            print("Requisição bem-sucedida!")
            print("Resposta:", response.text)
        else:
            print(f"Falha na requisição. Status code: {response.status_code}")
            print("Erro:", response.text)
    
    except requests.exceptions.RequestException as e:
        # Tratar possíveis exceções
        print(f"Erro durante a requisição: {e}")


# Função principal
if __name__ == "__main__":
    video_url = "https://www.youtube.com/watch?v=GC80Dk7eg_A"  # Coloque o URL do vídeo do YouTube aqui
    audio_file = download_audio(video_url)  # Baixa o áudio do vídeo
    transcription = transcribe_audio_with_retries(audio_file)  # Tenta transcrever até 3 vezes
    
    print("transcription:", transcription)
    token_count_transcription = count_tokens(transcription, model="gpt-4")  # Pode substituir pelo modelo desejado, como "gpt-3.5-turbo"
    print(f"Quantidade de tokens - Transcricao: {token_count_transcription}")



    summary = summarize_text(transcription)  # Faz o resumo da transcrição, se disponível
    
    print("Resumo:", summary)
    token_count_summary = count_tokens(summary, model="gpt-4")  # Pode substituir pelo modelo desejado, como "gpt-3.5-turbo"
    print(f"Quantidade de tokens - Resumo: {token_count_summary}")

    
     # Obter a duração do áudio em minutos
    audio_duration = get_audio_duration_in_minutes(audio_file)
    print(f"Duração do áudio: {audio_duration:.2f} minutos")

    totaltokens = token_count_summary+token_count_transcription
    print(f"Total de tokens: {token_count_summary+token_count_transcription}")

    # Remover o arquivo após finalizar o processo
    delete_audio_file(audio_file)

   # send_post_request(transcription,summary,token_count_transcription,token_count_summary,  totaltokens,audio_duration)
