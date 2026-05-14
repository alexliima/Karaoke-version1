import os
import sys
import shutil

# Caminho da pasta onde o script está
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Caminho FFmpeg
ffmpeg_path = os.path.join(BASE_DIR, "bin")
os.environ["PATH"] += os.pathsep + ffmpeg_path
os.environ["PYTHONUTF8"] = "1"

import subprocess
import librosa
import soundfile as sf
import numpy as np


def limpar_arquivos():
    """Remove as pastas de download e processamento para liberar espaço."""
    import time

    pastas = [
        os.path.join(BASE_DIR, "downloads"),
        os.path.join(BASE_DIR, "separado"),
    ]
    removidas = []
    for caminho in pastas:
        if not os.path.exists(caminho):
            continue
        for tentativa in range(3):         
            try:
                shutil.rmtree(caminho)
                removidas.append(os.path.basename(caminho))
                break
            except PermissionError as e:
                if tentativa < 2:
                    time.sleep(0.6)         # dá tempo pro SO liberar o arquivo
                else:
                    raise Exception(
                        f"Não foi possível apagar '{caminho}'.\n"
                        f"Verifique se algum arquivo está aberto em outro programa.\n\nDetalhe: {e}"
                    )

    if removidas:
        return f"Pastas removidas: {', '.join(removidas)}"
    return "Nenhuma pasta encontrada para limpar."


def baixar_audio(url, progress_callback=None):
    """Baixa o áudio do YouTube em formato WAV."""
    pasta_saida = os.path.join(BASE_DIR, "downloads")
    os.makedirs(pasta_saida, exist_ok=True)

    if progress_callback:
        progress_callback("Conectando ao YouTube...", 5)

    cmd = [
        "yt-dlp",
        "-x",
        "--audio-format", "wav",
        "--audio-quality", "0",
        "-o", os.path.join(pasta_saida, "%(title)s.%(ext)s"),
        "--print", "after_move:filepath",
        url,
    ]

    if progress_callback:
        progress_callback("Baixando áudio...", 15)

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
    )

    if result.returncode != 0:
        raise Exception(f"Erro ao baixar: {result.stderr}")

    linhas = [l.strip() for l in (result.stdout or "").strip().split("\n") if l.strip()]
    for linha in reversed(linhas):
        if linha.endswith(".wav") and os.path.exists(linha):
            return linha

    # Fallback
    arquivos = [
        os.path.join(pasta_saida, f)
        for f in os.listdir(pasta_saida)
        if f.endswith(".wav")
    ]
    if arquivos:
        return max(arquivos, key=os.path.getmtime)

    raise Exception("Não foi possível encontrar o arquivo baixado.")


def separar_vocal(arquivo_audio, progress_callback=None):
    """Usa Demucs para separar vocal e instrumental."""
    pasta_saida = os.path.join(BASE_DIR, "separado")

    if progress_callback:
        progress_callback("Separando vocal com IA (pode demorar)...", 35)

    cmd = [
        sys.executable, "-m", "demucs",
        "--two-stems=vocals",
        "-o", pasta_saida,
        arquivo_audio,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")

    if result.returncode != 0:
        raise Exception(f"Erro no Demucs: {result.stderr}")

    nome_base = os.path.splitext(os.path.basename(arquivo_audio))[0]
    instrumental = os.path.join(pasta_saida, "htdemucs", nome_base, "no_vocals.wav")
    vocal = os.path.join(pasta_saida, "htdemucs", nome_base, "vocals.wav")

    if not os.path.exists(instrumental):
        raise Exception(f"Arquivo instrumental não encontrado: {instrumental}")

    if progress_callback:
        progress_callback("Separação concluída!", 75)

    return instrumental, vocal


def transpor_tom(arquivo_audio, semitons, arquivo_saida=None, progress_callback=None):
    """Transpõe o tom em X semitons."""
    if semitons == 0:
        if progress_callback:
            progress_callback("Tom sem alteração.", 90)
        return arquivo_audio

    if progress_callback:
        progress_callback(f"Transpondo tom em {semitons:+d} semitons...", 85)

    y, sr = librosa.load(arquivo_audio, sr=None, mono=False)

    if y.ndim == 2:
        y_shifted = np.array([
            librosa.effects.pitch_shift(y[0], sr=sr, n_steps=float(semitons)),
            librosa.effects.pitch_shift(y[1], sr=sr, n_steps=float(semitons)),
        ])
    else:
        y_shifted = librosa.effects.pitch_shift(y, sr=sr, n_steps=float(semitons))

    if arquivo_saida is None:
        base, ext = os.path.splitext(arquivo_audio)
        sinal = "+" if semitons > 0 else ""
        arquivo_saida = f"{base}_tom{sinal}{semitons}{ext}"

    data = y_shifted.T if y_shifted.ndim == 2 else y_shifted
    sf.write(arquivo_saida, data, sr)

    if progress_callback:
        progress_callback("Tom ajustado!", 95)

    return arquivo_saida


def processar(url, semitons=0, progress_callback=None):
    """Pipeline completo: baixar → separar → transpor."""
    arquivo = baixar_audio(url, progress_callback=progress_callback)

    if progress_callback:
        progress_callback("Áudio baixado com sucesso!", 25)

    instrumental, vocal = separar_vocal(arquivo, progress_callback=progress_callback)
    resultado = transpor_tom(instrumental, semitons, progress_callback=progress_callback)

    if progress_callback:
        progress_callback("Tudo pronto! 🎉", 100)

    return resultado, vocal, arquivo
