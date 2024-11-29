import os
import time
import whisper
import ffmpeg


def compress_audio(
    input_file, output_file, bitrate="96k", channels=1, sample_rate=44100
):
    """
    Comprime um arquivo de áudio para reduzir tamanho e melhorar qualidade.
    """
    try:
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Arquivo não encontrado: {input_file}")

        print("Iniciando compressão do áudio...")
        (
            ffmpeg.input(input_file)
            .output(
                output_file,
                acodec="libmp3lame",
                ab=bitrate,
                ac=channels,
                ar=sample_rate,
                af="afftdn=nf=-25",  # Reduz ruídos
            )
            .run(overwrite_output=True)
        )
        print(f"Compressão concluída! Arquivo gerado: {output_file}")
    except Exception as e:
        print(f"Erro ao comprimir o áudio: {e}")


def transcribe_audio(audio_file, model_name):
    """
    Transcreve um arquivo de áudio usando o Whisper.
    """
    try:
        print(f"Carregando modelo Whisper ({model_name})...")
        model = whisper.load_model(model_name)  # Carrega o modelo diretamente
        print(f"Modelo {model_name} carregado. Iniciando transcrição...")

        start_time = time.time()

        # Transcrição
        result = model.transcribe(
            audio_file,
            fp16=False,  # Certifique-se de que FP16 está desativado para CPU
            task="transcribe",  # Apenas transcrição
            verbose=True,  # Mostra informações detalhadas
        )

        end_time = time.time()
        total_time = end_time - start_time

        print(f"\nTexto transcrito:\n{result['text']}")

        print("\nTimestamps e segmentos:")
        for segment in result["segments"]:
            start_seconds = int(
                segment["start"]
            )  # Converte o início para segundos inteiros
            end_seconds = int(segment["end"])  # Converte o fim para segundos inteiros

            # Formatar em MM:SS
            start_time = f"{start_seconds // 60:02}:{start_seconds % 60:02}"
            end_time = f"{end_seconds // 60:02}:{end_seconds % 60:02}"
            print(f"{start_time} - {end_time}: {segment['text']}")

        # Converter para minutos e segundos
        minutes = int(total_time // 60)  # Minutos inteiros
        seconds = int(total_time % 60)  # Segundos restantes

        print(f"\nTranscrição concluída em {minutes} minutos e {seconds} segundos.")

        return result
    except Exception as e:
        print(f"Erro na transcrição: {e}")


if __name__ == "__main__":
    # Arquivos de entrada e saída
    input_audio = "aula.mp3"  # Substitua pelo nome do arquivo original
    compressed_audio = "aula2.mp3"

    # Escolha o arquivo para transcrição (original ou comprimido)
    use_compressed_audio = False  # Alterne para False se quiser usar o original

    if use_compressed_audio:
        print("Compressão do áudio ativada...")
        compress_audio(input_audio, compressed_audio)
        audio_path = compressed_audio
    else:
        print("Usando o áudio original para transcrição...")
        audio_path = input_audio

    print("Iniciando transcrição com Whisper...")
    transcribe_audio(audio_path, model_name="small")

    # medium #small #large #tiny #base
