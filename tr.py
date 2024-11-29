import os
import time
import ffmpeg
from moviepy.editor import AudioFileClip
from openai import OpenAI
import tiktoken
import whisper

# Configuração do cliente OpenAI


def compress_audio(
    input_file, output_file, bitrate="96k", channels=1, sample_rate=44100
):
    """
    Comprime um arquivo de áudio para o menor tamanho possível no formato MP3.

    Args:
        input_file (str): Caminho do arquivo de entrada.
        output_file (str): Caminho do arquivo de saída.
        bitrate (str): Taxa de bits para compressão (padrão: 8k).
        channels (int): Número de canais de áudio (1 para mono).
        sample_rate (int): Taxa de amostragem em Hz (padrão: 8000 Hz).
    """
    try:
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Arquivo não encontrado: {input_file}")

        (
            ffmpeg.input(input_file)
            .output(
                output_file,
                acodec="libmp3lame",
                ab=bitrate,
                ac=channels,
                ar=sample_rate,
                af="afftdn=nf=-25",
            )
            .run(overwrite_output=True)
        )
        print(f"Compressão concluída! Arquivo gerado: {output_file}")
    except Exception as e:
        print(f"Erro ao comprimir o áudio: {e}")


# Função para transcrever o áudio com tentativas de 3 vezes
def transcribe_audio_with_retries(audio_file):
    print("Iniciando a transcrição!")
    attempts = 0
    while attempts < 3:
        try:
            with open(audio_file, "rb") as file_obj:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1", file=file_obj
                )
            return transcript.text
        except Exception as e:
            attempts += 1
            print(f"Tentativa {attempts} falhou. Exceção: {str(e)}")
            time.sleep(5)  # Aguarda 5 segundos antes de tentar novamente
    print("Falha ao transcrever após 3 tentativas.")
    return None


# Função para resumir o texto usando GPT da OpenAI
def text_speakers(text):
    if text is None:
        return "Não foi possível gerar o resumo pois a transcrição falhou."

    # Chamada correta para a API de completions usando GPT-4
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Modelo GPT-4
        messages=[
            {
                "role": "user",
                "content": (
                    "O texto a seguir é uma transcrição de um áudio. Identifique os locutores (Speakers) para cada fala "
                    "e organize o resultado em formato de lista, indicando claramente o locutor para cada trecho: \n"
                    + text
                ),
            }
        ],
    )

    # Extração correta do texto do resumo
    summary = response.choices[0].message.content.strip()
    return summary


def format_speakers(speakers_text):
    """
    Formata o texto retornado pela função Locutores para exibição organizada.

    Args:
        speakers_text (str): Texto contendo os locutores e suas falas.

    Returns:
        str: Texto formatado de forma organizada.
    """
    if not speakers_text:
        return "Nenhuma informação de locutores disponível."

    # Dividir o texto em linhas para processar cada fala
    lines = speakers_text.splitlines()

    # Adicionar numeração ou indentação para cada linha
    formatted_lines = [f"{idx + 1}. {line}" for idx, line in enumerate(lines)]

    # Combinar as linhas formatadas
    return "\n".join(formatted_lines)


# Função para resumir o texto usando GPT da OpenAI
def summarize_text(text):
    if text is None:
        return "Não foi possível gerar o resumo pois a transcrição falhou."

    # Chamada correta para a API de completions usando GPT-4
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Modelo GPT-4
        messages=[{"role": "user", "content": "Resuma o seguinte texto: " + text}],
    )

    # Extração correta do texto do resumo
    summary = response.choices[0].message.content.strip()
    return summary


def format_text_by_sentences(text):
    """
    Divide o texto em sentenças com base no ponto final e organiza cada sentença em uma nova linha.

    Args:
        text (str): Texto de entrada.

    Returns:
        str: Texto formatado com uma sentença por linha.
    """
    if not text:
        return "Texto vazio ou inválido."

    # Divide o texto em sentenças usando o ponto final como delimitador
    sentences = text.split(".")

    # Remove espaços extras e ignora sentenças vazias
    formatted_sentences = [
        sentence.strip() for sentence in sentences if sentence.strip()
    ]

    # Junta as sentenças com uma nova linha entre elas
    return "\n".join(formatted_sentences) + "."


import ffmpeg
import os


def compress_video(
    input_file, output_file, video_bitrate="500k", audio_bitrate="64k", scale_width=1280
):
    """
    Comprime um arquivo de vídeo para reduzir o tamanho mantendo qualidade balanceada.

    Args:
        input_file (str): Caminho do arquivo de entrada.
        output_file (str): Caminho do arquivo de saída.
        video_bitrate (str): Taxa de bits do vídeo (exemplo: "500k").
        audio_bitrate (str): Taxa de bits do áudio (exemplo: "64k").
        scale_width (int): Largura para redimensionamento opcional (padrão: 1280 para HD).
                          A altura será ajustada proporcionalmente.
    """
    try:
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Arquivo não encontrado: {input_file}")

        # Configura a escala proporcional
        video_scale = f"scale={scale_width}:-1"

        # Compressão com ffmpeg
        (
            ffmpeg.input(input_file)
            .output(
                output_file,
                vcodec="libx264",  # Codec H.264
                b=video_bitrate,  # Taxa de bits do vídeo
                vf=video_scale,  # Redimensionar
                acodec="aac",  # Codec de áudio AAC
                ab=audio_bitrate,  # Taxa de bits do áudio
                ac=2,  # Áudio estéreo
            )
            .run(overwrite_output=True)
        )
        print(f"Compressão de vídeo concluída! Arquivo gerado: {output_file}")
    except Exception as e:
        print(f"Erro ao comprimir o vídeo: {e}")


def compress_video2(
    input_file, output_file, video_bitrate, audio_bitrate, scale_width=960
):
    """
    Comprime um arquivo de vídeo para reduzir o tamanho mantendo qualidade balanceada.

    Args:
        input_file (str): Caminho do arquivo de entrada.
        output_file (str): Caminho do arquivo de saída.
        video_bitrate (str): Taxa de bits do vídeo (exemplo: "350k").
        audio_bitrate (str): Taxa de bits do áudio (exemplo: "48k").
        scale_width (int): Largura para redimensionamento opcional (padrão: 960 para SD).
                          A altura será ajustada proporcionalmente.
    """
    try:
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Arquivo não encontrado: {input_file}")

        # Configura a escala proporcional
        video_scale = f"scale={scale_width}:-1"

        # Compressão com ffmpeg
        (
            ffmpeg.input(input_file)
            .output(
                output_file,
                vcodec="libx264",  # Codec H.264
                b=video_bitrate,  # Taxa de bits do vídeo
                vf=video_scale,  # Redimensionar
                acodec="aac",  # Codec de áudio AAC
                ab=audio_bitrate,  # Taxa de bits do áudio
                ac=1,  # Áudio mono
            )
            .run(overwrite_output=True)
        )
        print(f"Compressão de vídeo concluída! Arquivo gerado: {output_file}")
    except Exception as e:
        print(f"Erro ao comprimir o vídeo: {e}")


def transcribe_audio(audio_file):
    print("Carregando modelo Whisper...")
    model = whisper.load_model("small")  # Use "tiny" ou "small" para mais rapidez
    print("Modelo carregado. Iniciando transcrição...")

    start_time = time.time()

    # Configuração de threading
    options = whisper.DecodingOptions(
        fp16=False,  # Certifique-se de que FP16 está desativado para CPU
        language="en",  # Force o idioma (se souber qual é)
        task="transcribe",  # Apenas transcrição, sem tradução
    )

    # Transcrição
    result = model.transcribe(audio_file, verbose=True)

    end_time = time.time()
    total_time = end_time - start_time

    print(f"\nTexto transcrito:\n{result['text']}")

    # Exibir os timestamps
    # print("Timestamps e segmentos:")
    # for segment in result["segments"]:
    #   print(f"De {segment['start']:.2f}s a {segment['end']:.2f}s: {segment['text']}")

    print(f"\nTranscrição concluída em {total_time:.2f} segundos.")

    return result


if __name__ == "__main__":

    # Arquivos de entrada e saída
    input_audio = "Gravando.m4a"  # Substitua pelo nome do arquivo original
    compressed_audio = "testec.mp3"

    print(f"comprimido....")
    # Comprimir o áudio
    compress_audio(input_audio, compressed_audio)
    # print(f"Áudio comprimido gerado: {compressed_audio}")

    input_video = "video.mp4"  # Caminho para o vídeo original
    output_video = "video_comprimido.mp4"  # Caminho para o vídeo de saída

    # Compressão reduzindo o tamanho do vídeo para metade aproximadamente
    # compress_video2(
    #    input_file=input_video,
    #    output_file=output_video,
    #    video_bitrate="100k",  # Taxa de bits reduzida
    #    audio_bitrate="24k",  # Compressão de áudio
    #    scale_width=960,  # Redimensionar para HD (1280x720)
    # )
    # print(f"video comprimido gerado: {compressed_audio}")

    print(f"whisper....")
    audio_path = "testec.mp3"
    transcribe_audio(audio_path)

    # transcription = transcribe_audio_with_retries(compressed_audio)
    # print(transcription)

    # Formatar o texto
    # formatted_text = format_text_by_sentences(texto)

    # Exibir o texto formatado
    # print(formatted_text)

    # print(sentences)
    # format_text_by_sentences(texto)

    # spearkers = text_speakers(transcription)
    # Exibir os speakers formatados
    # formatted_speakers = format_speakers(spearkers)
    # print(formatted_speakers)

    # Resumir o texto transcrito
    # summary = summarize_text(transcription)
    # print(summary)
