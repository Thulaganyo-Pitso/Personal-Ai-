import sys
import os
import re
import markdown
import base64
from youtube_transcript_api import YouTubeTranscriptApi
from PyQt6.QtWidgets import (QApplication, QWidget, QLineEdit, QPushButton, QLabel,
                              QStatusBar, QTextEdit, QVBoxLayout, QHBoxLayout,
                              QFileDialog, QTabWidget)
from PyQt6.QtGui import QIcon
from openai import OpenAI


def extract_video_id(input_string):
    if re.match(r'https?:\/\/', input_string):
        if 'youtube.com' in input_string:
            match = re.search(r'v=([^&]*)', input_string)
            if match:
                return match.group(1)
        elif 'youtu.be' in input_string:
            match = re.search(r'youtu\.be/([^&]*)', input_string)
            if match:
                return match.group(1)
    return input_string


class AppWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Thulaganyo's YT Summarizer")
        self.setWindowIcon(QIcon('transcription.png'))
        self.resize(900, 650)
        self.setStyleSheet('font-size: 14px;')

        self.layout_main = QVBoxLayout()
        self.setLayout(self.layout_main)

        self.chat_history = []
        self.transcript_context = ""

        self.init_ui()

    def init_ui(self):
        self.tabs = QTabWidget()
        self.layout_main.addWidget(self.tabs)

        self.yt_tab = QWidget()
        self.yt_layout = QVBoxLayout()
        self.yt_tab.setLayout(self.yt_layout)
        self.tabs.addTab(self.yt_tab, "YouTube")

        self.chat_tab = QWidget()
        self.chat_layout = QVBoxLayout()
        self.chat_tab.setLayout(self.chat_layout)
        self.tabs.addTab(self.chat_tab, "Chat with Beans")

        self.status_bar = QStatusBar()
        self.layout_main.addWidget(self.status_bar)

        self._build_yt_tab()
        self._build_chat_tab()

    def _build_yt_tab(self):
        input_row = QHBoxLayout()
        self.yt_layout.addLayout(input_row)

        input_row.addWidget(QLabel('Video ID:'))
        self.video_input = QLineEdit()
        self.video_input.setFixedWidth(500)
        self.video_input.setPlaceholderText('Enter video ID or URL')
        input_row.addWidget(self.video_input)
        input_row.addStretch()

        self.yt_layout.addWidget(QLabel('Transcript:'))
        self.transcript_edit = QTextEdit()
        self.yt_layout.addWidget(self.transcript_edit)

        btn_row = QHBoxLayout()
        self.yt_layout.addLayout(btn_row)

        btn_download = QPushButton('&Download Transcript')
        btn_download.setFixedWidth(175)
        btn_download.clicked.connect(self.download_transcript)
        btn_row.addWidget(btn_download)

        btn_summarize = QPushButton('&Summarize Transcript')
        btn_summarize.setFixedWidth(175)
        btn_summarize.clicked.connect(self.summarize_transcript)
        btn_row.addWidget(btn_summarize)

        btn_image = QPushButton('&Upload Image')
        btn_image.setFixedWidth(150)
        btn_image.clicked.connect(self.analyze_image)
        btn_row.addWidget(btn_image)

        btn_row.addStretch()

    def _build_chat_tab(self):
        self.chat_layout.addWidget(QLabel('Chat with Beans (Thulaganyo\'s son):'))

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_layout.addWidget(self.chat_display)

        input_row = QHBoxLayout()
        self.chat_layout.addLayout(input_row)

        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText('Ask anything Beans...')
        self.chat_input.returnPressed.connect(self.send_chat)
        input_row.addWidget(self.chat_input)

        btn_send = QPushButton('Send')
        btn_send.setFixedWidth(80)
        btn_send.clicked.connect(self.send_chat)
        input_row.addWidget(btn_send)

        btn_clear = QPushButton('Clear')
        btn_clear.setFixedWidth(80)
        btn_clear.clicked.connect(self.clear_chat)
        input_row.addWidget(btn_clear)

        btn_use_transcript = QPushButton('Load Transcript into Chat')
        btn_use_transcript.clicked.connect(self.load_transcript_to_chat)
        self.chat_layout.addWidget(btn_use_transcript)

    def download_transcript(self):
        video_id = self.video_input.text()
        if not video_id:
            self.status_bar.showMessage('Please enter a video ID or URL')
            return
        self.status_bar.clearMessage()
        video_id = extract_video_id(video_id)
        try:
            fetcher = YouTubeTranscriptApi()
            transcript = fetcher.fetch(video_id)
            transcript_text = '\n'.join([part.text for part in transcript])
            self.transcript_edit.setPlainText(transcript_text)
            self.transcript_context = transcript_text
        except Exception as e:
            self.transcript_edit.setPlainText(f'Error: {e}')

    def summarize_transcript(self):
        transcript_text = self.transcript_edit.toPlainText()
        if not transcript_text:
            self.status_bar.showMessage('Transcript is empty.')
            return
        self.status_bar.clearMessage()
        self.status_bar.showMessage('Summarizing...')
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a brutally honest AI assistant. You always tell the truth, never sugarcoat anything, and you refer to the user as 'Pere'."
                    },
                    {
                        "role": "user",
                        "content": f"Summarize the video transcript below into bullet points, be direct:\n\n{transcript_text}"
                    }
                ],
                model="dolphin-llama3:latest",
                temperature=0.3
            )
            html_content = markdown.markdown(chat_completion.choices[0].message.content)
            self.transcript_edit.setHtml(html_content)
            self.transcript_context = transcript_text
            self.status_bar.showMessage('Done.')
        except Exception as e:
            self.transcript_edit.setPlainText(f'Error: {e}')
            self.status_bar.showMessage('Error.')

    def analyze_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 'Open Image', '', 'Images (*.png *.jpg *.jpeg *.webp *.gif)'
        )
        if not file_path:
            return
        self.status_bar.showMessage('Analyzing image...')
        with open(file_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        ext = file_path.split('.')[-1].lower()
        media_type_map = {
            'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
            'png': 'image/png', 'webp': 'image/webp', 'gif': 'image/gif'
        }
        media_type = media_type_map.get(ext, 'image/jpeg')
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:{media_type};base64,{image_data}"}
                            },
                            {
                                "type": "text",
                                "text": "Describe and analyze this image in detail. Be brutally honest."
                            }
                        ]
                    }
                ],
                model="llava:latest",
                temperature=0.5
            )
            html_content = markdown.markdown(chat_completion.choices[0].message.content)
            self.transcript_edit.setHtml(html_content)
            self.status_bar.showMessage('Image analyzed.')
        except Exception as e:
            self.transcript_edit.setPlainText(f'Error: {e}')
            self.status_bar.showMessage('Error analyzing image.')

    def load_transcript_to_chat(self):
        transcript = self.transcript_edit.toPlainText()
        if not transcript:
            self.status_bar.showMessage('No transcript to load.')
            return
        self.transcript_context = transcript
        self.chat_history = []
        self.chat_display.setPlainText("Transcript loaded! You can now ask questions about it Pere.")
        self.status_bar.showMessage('Transcript loaded into chat.')

    def send_chat(self):
        user_message = self.chat_input.text().strip()
        if not user_message:
            return
        self.chat_input.clear()

        self.chat_display.append(f"<b>Papa:</b> {user_message}<br>")

        system_prompt = """You are Beans, Thulaganyo's personal AI assistant.
You are brutally honest, fun, sharp, and direct.
You call the user 'Mon Pere' naturally in conversation.
You help with studies, mark schemes, and general questions.
You never sugarcoat anything and always tell the truth."""

        messages = [{"role": "system", "content": system_prompt}]

        if self.transcript_context:
            messages.append({
                "role": "system",
                "content": f"Here is the transcript/context:\n\n{self.transcript_context[:6000]}"
            })

        messages.extend(self.chat_history)
        messages.append({"role": "user", "content": user_message})

        try:
            self.status_bar.showMessage('Thinking...')
            response = client.chat.completions.create(
                messages=messages,
                model="dolphin-llama3:latest",
                temperature=0.7
            )
            ai_reply = response.choices[0].message.content
            self.chat_history.append({"role": "user", "content": user_message})
            self.chat_history.append({"role": "assistant", "content": ai_reply})

            if len(self.chat_history) > 20:
                self.chat_history = self.chat_history[-20:]

            html_reply = markdown.markdown(ai_reply)
            self.chat_display.append(f"<b>Beans:</b> {html_reply}<br>")
            self.status_bar.showMessage('Done.')
        except Exception as e:
            self.chat_display.append(f"<b>Error:</b> {e}<br>")
            self.status_bar.showMessage('Error.')

    def clear_chat(self):
        self.chat_history = []
        self.transcript_context = ""
        self.chat_display.clear()
        self.status_bar.showMessage('Chat cleared.')


if __name__ == "__main__":
    client = OpenAI(
        api_key="ollama",
        base_url="http://localhost:11434/v1"
    )

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setStyleSheet(open('cool.css').read())

    app_window = AppWindow()
    app_window.show()

    sys.exit(app.exec())
