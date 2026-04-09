import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from threading import Thread
import google.generativeai as genai

# Configure Gemini API key and model
genai.configure(api_key="___YOUR_KEY___")
try:
    model = genai.GenerativeModel("__YOUR_MODEL___")
except:
    model = genai.GenerativeModel("__YOUR_MODEL___")

chat = model.start_chat()

def chat_with_gemini(prompt):
    try:
        response = chat.send_message(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error: {str(e)}"

class GeminiChatGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Scriptbot")
        self.root.geometry("600x500")

        # Chat display area with scroll
        self.chat_display = ScrolledText(root, wrap=tk.WORD, state=tk.DISABLED, font=("Helvetica", 12))
        self.chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Define color tags
        self.chat_display.tag_config("user_tag", foreground="blue")
        self.chat_display.tag_config("bot_tag", foreground="green")

        # Frame for entry and send button
        input_frame = tk.Frame(root)
        input_frame.pack(padx=10, pady=5, fill=tk.X)

        # Entry widget for user to type message
        self.user_input = tk.Entry(input_frame, font=("Helvetica", 14))
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.user_input.bind("<Return>", self.send_message)

        # Send button
        send_button = tk.Button(input_frame, text="Send", command=self.send_message)
        send_button.pack(side=tk.RIGHT)

        # Greeting in chat window
        self._append_chat_text("Scriptbot: Hi! Type your message and press Enter or Send.\n\n", sender="bot")

    def _append_chat_text(self, text, sender="bot"):
        self.chat_display.config(state=tk.NORMAL)
        tag = "bot_tag" if sender == "bot" else "user_tag"
        self.chat_display.insert(tk.END, text, tag)
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)

    def send_message(self, event=None):
        user_text = self.user_input.get().strip()
        if not user_text:
            return
        if user_text.lower() in ["quit", "exit", "bye"]:
            self._append_chat_text("You: " + user_text + "\n", sender="user")
            self._append_chat_text("Scriptbot: Goodbye!\n\n", sender="bot")
            self.root.after(1000, self.root.destroy)
            return

        self.user_input.delete(0, tk.END)
        self._append_chat_text("You: " + user_text + "\n", sender="user")

        # Run Gemini chat in background thread to avoid UI freeze
        Thread(target=self.get_response, args=(user_text,), daemon=True).start()

    def get_response(self, prompt):
        response = chat_with_gemini(prompt)
        self._append_chat_text("\nScriptbot: " + response + "\n\n", sender="bot")

def main():
    root = tk.Tk()
    app = GeminiChatGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
