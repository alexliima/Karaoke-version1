import os
import sys
import threading
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import pygame

# ── Paleta ────────────────────────────────────────────────────────────────────
BG       = "#080810"
SURFACE  = "#0f0f1a"
CARD     = "#12121f"
CARD2    = "#16162a"
BORDER   = "#1e1e35"
BORDER2  = "#2a2a50"
ACCENT   = "#00f5c8"   # ciano neon
ACCENT2  = "#7b5ea7"   # roxo médio
ACCENT3  = "#ff4d8d"   # rosa neon
TEXT     = "#e8e4ff"
TEXT_DIM = "#5a5880"
TEXT_MID = "#9893b8"
SUCCESS  = "#00f5c8"
ERROR    = "#ff4d8d"

ctk.set_appearance_mode("dark")


# Helpers
def fmt_time(s):
    s = max(0, int(s))
    return f"{s // 60:02d}:{s % 60:02d}"


# TonSlider
class TonSlider(ctk.CTkFrame):
    def __init__(self, master, **kw):
        super().__init__(master, fg_color="transparent", **kw)
        self._val = 0
        self.columnconfigure(1, weight=1)

        # Label título
        ctk.CTkLabel(
            self, text="TRANSPOSIÇÃO DE TOM",
            font=("Courier New", 9, "bold"), text_color=TEXT_DIM
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 6))

        self._btn_dec = ctk.CTkButton(
            self, text="−", width=36, height=36,
            fg_color=CARD2, hover_color=BORDER2,
            border_width=1, border_color=BORDER2,
            font=("Courier New", 16, "bold"), text_color=ACCENT,
            corner_radius=8, command=self._dec
        )
        self._btn_dec.grid(row=1, column=0, padx=(0, 8))

        self._slider = ctk.CTkSlider(
            self, from_=-12, to=12,
            height=14,
            progress_color=ACCENT2,
            button_color=ACCENT,
            button_hover_color=ACCENT3,
            fg_color=BORDER,
            command=self._on_slide
        )
        self._slider.set(0)
        self._slider.grid(row=1, column=1, sticky="ew")

        self._btn_inc = ctk.CTkButton(
            self, text="+", width=36, height=36,
            fg_color=CARD2, hover_color=BORDER2,
            border_width=1, border_color=BORDER2,
            font=("Courier New", 16, "bold"), text_color=ACCENT,
            corner_radius=8, command=self._inc
        )
        self._btn_inc.grid(row=1, column=2, padx=(8, 0))

        self._label = ctk.CTkLabel(
            self, text="± 0 semitons",
            font=("Courier New", 11, "bold"), text_color=ACCENT
        )
        self._label.grid(row=2, column=0, columnspan=3, pady=(6, 0))

    def _on_slide(self, v):
        self._val = round(v)
        self._update_label()

    def _dec(self):
        self._val = max(-12, self._val - 1)
        self._slider.set(self._val)
        self._update_label()

    def _inc(self):
        self._val = min(12, self._val + 1)
        self._slider.set(self._val)
        self._update_label()

    def _update_label(self):
        sinal = "+" if self._val > 0 else ("−" if self._val < 0 else "±")
        n = abs(self._val)
        self._label.configure(text=f"{sinal} {n} semiton{'s' if n != 1 else ''}")

    def get(self):
        return self._val


# AudioPlayer
class AudioPlayer(ctk.CTkFrame):
    def __init__(self, master, **kw):
        super().__init__(
            master, fg_color=CARD2, corner_radius=12,
            border_width=1, border_color=BORDER2, **kw
        )
        pygame.mixer.init()

        self._file = None
        self._playing = False
        self._duration = 0
        self._pos = 0.0          # posição (em segundos)

        self.columnconfigure(1, weight=1)

        # Botão play/pause
        self._btn = ctk.CTkButton(
            self, text="▶", width=48, height=48,
            fg_color=ACCENT, hover_color=ACCENT3,
            text_color=BG, font=("Courier New", 18, "bold"),
            corner_radius=24, command=self._toggle, state="disabled"
        )
        self._btn.grid(row=0, column=0, padx=16, pady=16, rowspan=2)

        # Nome do arquivo
        self._name_lbl = ctk.CTkLabel(
            self, text="Nenhum arquivo carregado",
            font=("Courier New", 10), text_color=TEXT_DIM, anchor="w"
        )
        self._name_lbl.grid(row=0, column=1, sticky="ew", padx=(0, 16), pady=(12, 0))

        # Seekbar
        self._slider = ctk.CTkSlider(
            self, from_=0, to=100, height=14,
            progress_color=ACCENT,
            button_color=ACCENT3,
            button_hover_color=ACCENT,
            fg_color=BORDER,
            command=self._seek_manual
        )
        self._slider.set(0)
        self._slider.grid(row=1, column=1, sticky="ew", padx=(0, 16), pady=(0, 12))

        # Timer
        self._time_lbl = ctk.CTkLabel(
            self, text="00:00 / 00:00",
            font=("Courier New", 10, "bold"), text_color=TEXT_MID
        )
        self._time_lbl.grid(row=1, column=2, padx=12)

        self._update_loop()

    def load(self, filepath):
        self.stop()
        self._file = filepath
        try:
            sound = pygame.mixer.Sound(filepath)
            self._duration = sound.get_length()
            del sound
        except Exception:
            self._duration = 0

        nome = os.path.basename(filepath)
        display = nome[:42] + "…" if len(nome) > 42 else nome
        self._name_lbl.configure(text=display, text_color=TEXT)
        self._slider.configure(to=max(1, self._duration))
        self._slider.set(0)
        self._pos = 0.0
        self._btn.configure(state="normal")
        self._time_lbl.configure(text=f"00:00 / {fmt_time(self._duration)}")

    def _toggle(self):
        if not self._file:
            return
        if self._playing:
            pygame.mixer.music.pause()
            self._playing = False
            self._btn.configure(text="▶")
        else:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.unpause()
            else:
                pygame.mixer.music.load(self._file)
                pygame.mixer.music.play(start=self._pos)
            self._playing = True
            self._btn.configure(text="⏸")

    def stop(self):
        pygame.mixer.music.stop()
        self._playing = False
        self._pos = 0.0
        self._btn.configure(text="▶")
        self._slider.set(0)
        self._time_lbl.configure(text=f"00:00 / {fmt_time(self._duration)}")

    def _seek_manual(self, val):
        self._pos = float(val)
        if self._file:
            pygame.mixer.music.load(self._file)
            pygame.mixer.music.play(start=self._pos)
            if not self._playing:
                pygame.mixer.music.pause()
        self._time_lbl.configure(text=f"{fmt_time(self._pos)} / {fmt_time(self._duration)}")

    def _update_loop(self):
        if self._playing:
            if pygame.mixer.music.get_busy():
                self._pos += 0.1
                if self._pos >= self._duration > 0:
                    self._pos = self._duration
                    self.stop()
                else:
                    self._slider.set(self._pos)
                    self._time_lbl.configure(
                        text=f"{fmt_time(self._pos)} / {fmt_time(self._duration)}"
                    )
            else:
                # Terminou 
                self._playing = False
                self._btn.configure(text="▶")

        self.after(100, self._update_loop)


# KaraokeApp
class KaraokeApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Karaokê")
        self.geometry("740x820")
        self.minsize(680, 720)
        self.configure(fg_color=BG)
        self._resultado_path = None
        self._build_ui()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=36, pady=(28, 0))
        header.columnconfigure(0, weight=1)

        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            title_frame, text="🎤",
            font=("Segoe UI Emoji", 36), text_color=ACCENT
        ).grid(row=0, column=0, padx=(0, 12))

        title_text = ctk.CTkFrame(title_frame, fg_color="transparent")
        title_text.grid(row=0, column=1)
        ctk.CTkLabel(
            title_text, text="KARAOKÊ PRO",
            font=("Courier New", 28, "bold"), text_color=TEXT
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            title_text, text="remove vocal · transpõe tom · toca na hora",
            font=("Courier New", 10), text_color=TEXT_DIM
        ).grid(row=1, column=0, sticky="w")

        # Separador decorativo
        sep = ctk.CTkFrame(self, fg_color=BORDER2, height=1)
        sep.grid(row=1, column=0, sticky="ew", padx=36, pady=(16, 0))

        # Corpo
        body = ctk.CTkScrollableFrame(self, fg_color="transparent", scrollbar_button_color=BORDER2)
        body.grid(row=2, column=0, sticky="nsew", padx=0, pady=0)
        body.columnconfigure(0, weight=1)

        # Card de input
        input_card = ctk.CTkFrame(
            body, fg_color=CARD, corner_radius=16,
            border_width=1, border_color=BORDER
        )
        input_card.grid(row=0, column=0, sticky="ew", padx=36, pady=(20, 12))
        input_card.columnconfigure(0, weight=1)

        ctk.CTkLabel(
            input_card, text="LINK DO YOUTUBE",
            font=("Courier New", 9, "bold"), text_color=TEXT_DIM, anchor="w"
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(16, 4))

        self._url_entry = ctk.CTkEntry(
            input_card,
            placeholder_text="https://youtube.com/watch?v=...",
            height=46,
            fg_color=SURFACE,
            border_color=BORDER2,
            border_width=1,
            text_color=TEXT,
            placeholder_text_color=TEXT_DIM,
            font=("Courier New", 12)
        )
        self._url_entry.grid(row=1, column=0, padx=20, sticky="ew")

        # Tom slider
        self._ton_ctrl = TonSlider(input_card)
        self._ton_ctrl.grid(row=2, column=0, padx=20, pady=16, sticky="ew")

        # Botão principal
        self._btn_proc = ctk.CTkButton(
            input_card,
            text="✦  CRIAR KARAOKÊ",
            height=52,
            fg_color=ACCENT,
            hover_color=ACCENT3,
            text_color=BG,
            font=("Courier New", 14, "bold"),
            corner_radius=10,
            command=self._iniciar
        )
        self._btn_proc.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")

        # Card de progresso
        prog_card = ctk.CTkFrame(
            body, fg_color=CARD, corner_radius=16,
            border_width=1, border_color=BORDER
        )
        prog_card.grid(row=1, column=0, sticky="ew", padx=36, pady=12)
        prog_card.columnconfigure(0, weight=1)

        ctk.CTkLabel(
            prog_card, text="STATUS",
            font=("Courier New", 9, "bold"), text_color=TEXT_DIM, anchor="w"
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(16, 4))

        self._status_lbl = ctk.CTkLabel(
            prog_card, text="Aguardando URL...",
            font=("Courier New", 11), text_color=TEXT_MID, anchor="w"
        )
        self._status_lbl.grid(row=1, column=0, sticky="w", padx=20)

        self._progress = ctk.CTkProgressBar(
            prog_card,
            height=6,
            progress_color=ACCENT,
            fg_color=BORDER,
            corner_radius=3
        )
        self._progress.set(0)
        self._progress.grid(row=2, column=0, sticky="ew", padx=20, pady=(8, 16))

        # Card do player
        player_card = ctk.CTkFrame(
            body, fg_color=CARD, corner_radius=16,
            border_width=1, border_color=BORDER
        )
        player_card.grid(row=2, column=0, sticky="ew", padx=36, pady=12)
        player_card.columnconfigure(0, weight=1)

        ctk.CTkLabel(
            player_card, text="PLAYER",
            font=("Courier New", 9, "bold"), text_color=TEXT_DIM, anchor="w"
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(16, 4))

        self._player = AudioPlayer(player_card)
        self._player.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 16))

        # Card de ações
        action_card = ctk.CTkFrame(
            body, fg_color=CARD, corner_radius=16,
            border_width=1, border_color=BORDER
        )
        action_card.grid(row=3, column=0, sticky="ew", padx=36, pady=(12, 28))
        action_card.columnconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(
            action_card, text="AÇÕES",
            font=("Courier New", 9, "bold"), text_color=TEXT_DIM, anchor="w"
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=20, pady=(16, 8))

        btn_style = dict(
            height=42, corner_radius=8,
            font=("Courier New", 11, "bold"),
            border_width=1
        )

        self._btn_pasta = ctk.CTkButton(
            action_card, text="📁  Abrir Pasta",
            fg_color="transparent", border_color=BORDER2,
            hover_color=CARD2, text_color=TEXT_MID,
            command=self._abrir_pasta, **btn_style
        )
        self._btn_pasta.grid(row=1, column=0, padx=(20, 6), pady=(0, 20), sticky="ew")

        self._btn_limpar = ctk.CTkButton(
            action_card, text="🗑  Limpar Cache",
            fg_color="transparent", border_color="#3a1a2a",
            hover_color="#2a1020", text_color=ERROR,
            command=self._confirmar_limpeza, **btn_style
        )
        self._btn_limpar.grid(row=1, column=1, padx=6, pady=(0, 20), sticky="ew")

        self._btn_nova = ctk.CTkButton(
            action_card, text="↺  Novo",
            fg_color="transparent", border_color=BORDER2,
            hover_color=CARD2, text_color=TEXT_MID,
            command=self._resetar, **btn_style
        )
        self._btn_nova.grid(row=1, column=2, padx=(6, 20), pady=(0, 20), sticky="ew")

    # Lógica
    def _iniciar(self):
        url = self._url_entry.get().strip()
        if not url:
            messagebox.showwarning("URL vazia", "Por favor, insira um link do YouTube.")
            return
        self._btn_proc.configure(state="disabled", text="Processando...")
        threading.Thread(
            target=self._processar_thread,
            args=(url, self._ton_ctrl.get()),
            daemon=True
        ).start()

    def _processar_thread(self, url, semitons):
        try:
            import karaoke
            res, voc, orig = karaoke.processar(
                url, semitons,
                progress_callback=lambda m, p: self.after(0, self._atualizar_p, m, p)
            )
            self._resultado_path = res
            self.after(0, lambda: self._player.load(res))
            self.after(0, lambda: self._btn_proc.configure(state="normal", text="✦  CRIAR KARAOKÊ"))
        except Exception as e:
            self.after(0, lambda err=e: messagebox.showerror("Erro", str(err)))
            self.after(0, lambda: self._btn_proc.configure(state="normal", text="✦  CRIAR KARAOKÊ"))

    def _atualizar_p(self, msg, pct):
        self._status_lbl.configure(text=msg)
        self._progress.set(pct / 100)

    def _confirmar_limpeza(self):
        if messagebox.askyesno(
            "Limpar Cache",
            "Isso apagará todas as músicas baixadas e processadas.\n\nContinuar?"
        ):
            try:
                # Para a música e libera o arquivo do pygame ANTES de apagar
                self._player.stop()
                pygame.mixer.music.unload()   # solta o handle do arquivo no Windows
                pygame.mixer.quit()           # fecha o mixer completamente
                pygame.mixer.init()           # reinicia pronto para o próximo uso

                import karaoke
                msg = karaoke.limpar_arquivos()
                self._resetar()
                messagebox.showinfo("Pronto!", msg)
            except Exception as e:
                messagebox.showerror("Erro ao limpar", str(e))

    def _abrir_pasta(self):
        pasta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "separado")
        os.makedirs(pasta, exist_ok=True)
        if sys.platform == "win32":
            os.startfile(pasta)
        elif sys.platform == "darwin":
            import subprocess
            subprocess.Popen(["open", pasta])
        else:
            import subprocess
            subprocess.Popen(["xdg-open", pasta])

    def _resetar(self):
        self._player.stop()
        self._url_entry.delete(0, "end")
        self._progress.set(0)
        self._status_lbl.configure(text="Aguardando URL...", text_color=TEXT_MID)
        self._resultado_path = None


if __name__ == "__main__":
    app = KaraokeApp()
    app.mainloop()
