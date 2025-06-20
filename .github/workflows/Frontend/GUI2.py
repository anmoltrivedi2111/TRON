import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
import imageio
import threading

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class TronUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Tron - AI Assistant")
        self.root.geometry("600x700")
        self.root.resizable(False, False)

        # Top Frame for Home & Chats
        top_frame = ctk.CTkFrame(master=root, height=50, corner_radius=0)
        top_frame.pack(fill="x")

        self.home_button = ctk.CTkButton(master=top_frame, text="Home", width=70, command=self.home_action)
        self.home_button.pack(side="left", padx=10, pady=10)

        self.chats_button = ctk.CTkButton(master=top_frame, text="Chats", width=70, command=self.chats_action)
        self.chats_button.pack(side="left", pady=10)

        # Center GIF acting as Mic
        self.gif_label = tk.Label(root, bg="#1a1a1a", cursor="hand2")
        self.gif_label.pack(pady=50)
        self.gif_label.bind("<Button-1>", self.mic_action)

        self.load_gif("Frontend/Graphics/Tron-blue1.gif")  # Replace with your gif name

        # Text Entry Area
        self.entry = ctk.CTkEntry(master=root, placeholder_text="Type your query here...", width=400)
        self.entry.pack(pady=20, side="left", padx=(50, 10))

        self.send_button = ctk.CTkButton(master=root, text="Send", command=self.send_action)
        self.send_button.pack(side="left", padx=10)

    def load_gif(self, gif_path):
        gif = imageio.mimread(gif_path)
        self.frames = [ImageTk.PhotoImage(Image.fromarray(frame)) for frame in gif]
        self.frame_index = 0
        self.update_gif()

    def update_gif(self):
        self.gif_label.config(image=self.frames[self.frame_index])
        self.frame_index = (self.frame_index + 1) % len(self.frames)
        self.root.after(100, self.update_gif)

    # Dummy button actions
    def mic_action(self, event=None):
        print("🎤 Mic activated...")

    def send_action(self):
        user_input = self.entry.get()
        print(f"User typed: {user_input}")
        self.entry.delete(0, tk.END)

    def home_action(self):
        print("🏠 Home clicked")

    def chats_action(self):
        print("💬 Chats clicked")


if __name__ == "__main__":
    root = ctk.CTk()
    app = TronUI(root)
    root.mainloop()
