# Karaokê

Remove o vocal de qualquer música do YouTube e transpõe o tom na hora.

## Requisitos

- Python 3.11.9 — [python.org](https://python.org/downloads/source)
- FFmpeg — [baixar aqui](https://ffmpeg.org/download.html)

## Como usar

1. Crie dentro da pasta principal 'Karaoke-version1-main' uma pasta chamada 'bin'
2. Coloque os executáveis do FFmpeg (`ffmpeg.exe`, `ffprobe.exe`, `ffplay.exe`) dentro da pasta `bin/`
3. Dê dois cliques em `iniciar.bat`
4. Na primeira vez ele instala as dependências automaticamente (pode demorar)
5. Cole o link do YouTube, ajuste o tom e clique em **Criar Karaokê**

## Estrutura

```
KAR/
├── iniciar.bat
├── ui.py
├── karaoke.py
├── requirements.txt
└── bin/         ← coloque o FFmpeg aqui
```
