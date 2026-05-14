# 🎤 Karaokê

Remove o vocal de qualquer música do YouTube e transpõe o tom na hora.

## Requisitos

- Python 3.10 ou 3.11 — [python.org](https://python.org/downloads)
- FFmpeg — [baixar aqui](https://github.com/BtbN/FFmpeg-Builds/releases)

## Como usar

1. Coloque os executáveis do FFmpeg (`ffmpeg.exe`, `ffprobe.exe`, `ffplay.exe`) dentro da pasta `bin/`
2. Dê dois cliques em `iniciar.bat`
3. Na primeira vez ele instala as dependências automaticamente (pode demorar)
4. Cole o link do YouTube, ajuste o tom e clique em **Criar Karaokê**

## Estrutura

```
KAR/
├── iniciar.bat
├── ui.py
├── karaoke.py
├── requirements.txt
└── bin/         ← coloque o FFmpeg aqui
```