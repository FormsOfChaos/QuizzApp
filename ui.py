import customtkinter as ctk
from tkinter import filedialog
import json
import random
import logic
import textwrap
from question_viewer import QuestionViewerWindow
from help_viewer import HelpViewerWindow

class QuizApp(ctk.CTk):
    def __init__(self, quiz_logic):
        super().__init__()
        self.logic = quiz_logic
        self.title("QuizzApp")

        self.iconbitmap("ikona.ico")
        
        # 80% rozmiaru ekranu
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        win_w = int(screen_width * 0.8)
        win_h = int(screen_height * 0.8)
        x = int((screen_width / 2) - (win_w / 2))
        y = int((screen_height / 2) - (win_h / 2))
        self.geometry(f"{win_w}x{win_h}+{x}+{y}")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.current_options = []
        self.active_quiz_path = ""  
        self.create_widgets()

    def create_widgets(self):
        self.config_panel = ctk.CTkFrame(self, width=260)
        self.config_panel.pack(side="left", fill="y", padx=10, pady=10)

        self.file_label = ctk.CTkLabel(self.config_panel, text="File Management", font=("Segoe UI", 14, "bold"))
        self.file_label.pack(pady=(10, 5))

        self.bank_var = ctk.StringVar(value="Select JSON Bank...")
        self.bank_dropdown = ctk.CTkOptionMenu(
            self.config_panel, 
            variable=self.bank_var, 
            values=self.get_available_jsons(), 
            command=self.load_selected_bank
        )
        self.bank_dropdown.pack(pady=5, fill="x", padx=10)

        self.regular_mode_btn = ctk.CTkButton(self.config_panel, text="Play Regular Mode", fg_color="#3a7ebf", hover_color="#1f538d", command=self.play_regular_mode)
        self.regular_mode_btn.pack(pady=(15, 5), fill="x", padx=10)

        self.hard_mode_btn = ctk.CTkButton(self.config_panel, text="Play Hard Mode", fg_color="#bf3a3a", hover_color="#8d2929", command=self.play_hard_mode)
        self.hard_mode_btn.pack(pady=5, fill="x", padx=10)

        self.redemption_btn = ctk.CTkButton(self.config_panel, text="Play Redemption Mode", fg_color="#3abf70", hover_color="#298d4f", command=self.play_redemption_mode)
        self.redemption_btn.pack(pady=5, fill="x", padx=10)

        self.self_made_btn = ctk.CTkButton(self.config_panel, text="Play Self Made Mode", fg_color="#8e44ad", hover_color="#732d91", command=self.play_self_made_mode)
        self.self_made_btn.pack(pady=5, fill="x", padx=10)

        self.create_playlist_btn = ctk.CTkButton(self.config_panel, text="➕ Create Custom Playlist", fg_color="#6c3483", hover_color="#512e5f", command=self.open_playlist_creator)
        self.create_playlist_btn.pack(pady=(0, 5), fill="x", padx=10)

        self.separator = ctk.CTkFrame(self.config_panel, height=2, fg_color="gray")
        self.separator.pack(fill="x", pady=15, padx=10)

        self.mode_label = ctk.CTkLabel(self.config_panel, text="Answering Mode", font=("Segoe UI", 14, "bold"))
        self.mode_label.pack(pady=(0, 5))
        
        self.mode_var = ctk.StringVar(value="Multiple Choice")
        self.mode_switch = ctk.CTkOptionMenu(self.config_panel, variable=self.mode_var, values=["Multiple Choice", "Handwritten Input"], command=self.toggle_mode_view)
        self.mode_switch.pack(pady=10, fill="x", padx=10)

        self.builder_separator = ctk.CTkFrame(self.config_panel, height=2, fg_color="gray")
        self.builder_separator.pack(fill="x", pady=15, padx=10)

        self.scores_btn = ctk.CTkButton(self.config_panel, text="📊 View Scores", command=self.show_scores_screen, fg_color="#8e44ad", hover_color="#732d91")
        self.scores_btn.pack(pady=5, fill="x", padx=10)

        self.builder_separator2 = ctk.CTkFrame(self.config_panel, height=2, fg_color="gray")
        self.builder_separator2.pack(fill="x", pady=15, padx=10)

        self.open_builder_btn = ctk.CTkButton(self.config_panel, text="Open Quiz Builder", command=self.open_builder_window)
        self.open_builder_btn.pack(pady=5, fill="x", padx=10)
        
        self.open_questions_btn = ctk.CTkButton(
            self.config_panel, 
            text="Open Questions",
            command=self.open_questions_viewer_callback 
        )
        self.open_questions_btn.pack(pady=5, fill="x", padx=10)

        self.help_btn = ctk.CTkButton(
            self.config_panel,
            text="❔ Help",
            command=self.open_help_window,
            fg_color="#555555",      
            hover_color="#333333"
        )
        self.help_btn.pack(pady=(20, 5), fill="x", padx=10)

        self.main_panel = ctk.CTkFrame(self)
        self.main_panel.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.welcome_frame = ctk.CTkFrame(self.main_panel, fg_color="transparent")
        self.welcome_frame.pack(fill="both", expand=True)

        welcome_title = ctk.CTkLabel(self.welcome_frame, text="Welcome to QuizzApp", font=("Segoe UI", 36, "bold"), text_color="cyan")
        welcome_title.pack(pady=(150, 20))

        welcome_instr = ctk.CTkLabel(self.welcome_frame, text="Please select and load a Question Bank\nfrom the File Management menu on the left to begin.", font=("Segoe UI", 16))
        welcome_instr.pack(pady=10)

        glhf_label = ctk.CTkLabel(self.welcome_frame, text="GL HF", font=("Segoe UI", 20, "bold"), text_color="#e67e22")
        glhf_label.pack(pady=30)

        self.game_frame = ctk.CTkFrame(self.main_panel, fg_color="transparent")
        self.scores_frame = ctk.CTkFrame(self.main_panel, fg_color="transparent")
        
        self.question_label = ctk.CTkLabel(self.game_frame, text="", font=("Segoe UI", 22, "bold"), wraplength=1000, justify="center", anchor="center")

        self.choice_frame = ctk.CTkFrame(self.game_frame, fg_color="transparent")

        self.option_buttons = []
        for i in range(4):
            card = ctk.CTkLabel(
                self.choice_frame, 
                text="", 
                fg_color="#F4ECD8", 
                text_color="black",
                font=("Segoe UI", 15),
                justify="left",     
                anchor="w",         
                corner_radius=8,
                wraplength=1000     
            )
            self.option_buttons.append(card)

        self.text_frame = ctk.CTkFrame(self.game_frame, fg_color="transparent")
        self.handwritten_entry = ctk.CTkTextbox(self.text_frame, height=100, wrap="word", font=("Segoe UI", 14))
        self.handwritten_entry.pack(pady=5, fill="x")
        self.handwritten_entry.bind("<Return>", self.on_enter_pressed)

        self.text_submit_btn = ctk.CTkButton(self.text_frame, text="Verify spelling", fg_color="green", hover_color="darkgreen", command=self.submit_text_answer)
        self.text_submit_btn.pack(pady=5)

        # 🟢 Usunięto stary highlight_frame stąd
        self.feedback_label = ctk.CTkLabel(self.game_frame, text="", font=("Segoe UI", 14, "bold"))
        
        self.self_made_checkbox_var = ctk.BooleanVar(value=False)
        self.self_made_checkbox = ctk.CTkCheckBox(
            self.game_frame, 
            text="Add to Self Made Playlist (Custom practice mode)", 
            variable=self.self_made_checkbox_var,
            onvalue=True, offvalue=False,
            command=self.on_self_made_toggled,
            text_color="gray",
            font=("Segoe UI", 12)
        )

        self.next_btn = ctk.CTkButton(
            self.game_frame, 
            text="Next Question →", 
            state="disabled", 
            command=self.next_question, 
            fg_color=("#3a7ebf", "#1f538d"),
            font=("Segoe UI", 18, "bold"), 
            height=55,                      
            width=300                       
        )

    def on_enter_pressed(self, event):
        if event.state & 0x0001:
            return
        self.submit_text_answer()
        return "break"
    
    def show_game_screen(self):
        if hasattr(self, 'welcome_frame'):
            self.welcome_frame.pack_forget()
        self.scores_frame.pack_forget()
        self.game_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
    def get_available_jsons(self):
        import os
        try:
            folder_path = "Questions Database"
            files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
            return files if files else ["No JSON files found"]
        except Exception:
            return ["Error reading directory"]

    def load_selected_bank(self, filename):
        import os
        if filename in ["No JSON files found", "Select JSON Bank...", "Error reading directory"] or not filename:
            self.show_error_popup("No Database Found", "Please add JSON files to 'Questions Database' or create one in Quiz Builder.")
            self.bank_var.set("Select JSON Bank...")
            return
            
        self.show_game_screen() 
        filepath = os.path.join("Questions Database", filename)
            
        if os.path.exists(filepath):
            try:
                self.save_current_game_state() 
                self.active_quiz_path = filepath
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.logic.load_questions(json.load(f))
                self.feedback_label.configure(text=f"Loaded {filename} successfully!", text_color="green")
                self.update_mode_buttons_ui("regular") 
                self.check_resume_or_continue(filepath, lambda: self.show_intensity_screen())
            except Exception as e:
                self.feedback_label.configure(text=f"Error: {str(e)}", text_color="red")
        else:
            self.feedback_label.configure(text="File not found!", text_color="red")

    def show_error_popup(self, title, message):
        popup = ctk.CTkToplevel(self)
        popup.title(title)
        popup.geometry("400x180")
        popup.transient(self)
        popup.grab_set()
        
        lbl = ctk.CTkLabel(popup, text=message, font=("Segoe UI", 13), wraplength=350)
        lbl.pack(pady=25, padx=20)
        btn = ctk.CTkButton(popup, text="Understood", command=popup.destroy)
        btn.pack(pady=5)

    def show_correction_popup(self, correct_text, analysis=None):
        popup = ctk.CTkToplevel(self)
        popup.title("Incorrect Answer")
        popup.geometry("980x650") # 🟢 Zwiększona wysokość, by pomieścić nowy element
        popup.transient(self)
        popup.grab_set()

        title_lbl = ctk.CTkLabel(popup, text="Incorrect!", font=("Segoe UI", 24, "bold"), text_color="red")
        title_lbl.pack(pady=(20, 5))
        
        # 🟢 NOWE: Fuzja Spellcheckera do Pop-upa
        if analysis:
            spell_lbl = ctk.CTkLabel(popup, text="Spelling Analysis:", font=("Segoe UI", 16, "bold"), text_color="cyan")
            spell_lbl.pack(pady=(0, 5))
            
            # Używamy CTkTextbox, ponieważ bezbłędnie radzi sobie z zawijaniem długiego tekstu
            spell_box = ctk.CTkTextbox(popup, height=100, font=("Courier New", 18, "bold"), fg_color="#2B2B2B", wrap="word")
            spell_box.pack(pady=5, padx=35, fill="x")
            
            # Konfigurujemy tagi kolorystyczne wewnątrz TextBoxa
            spell_box.tag_config("correct", foreground="#3abf70") # Zielony
            spell_box.tag_config("incorrect", foreground="#bf3a3a") # Czerwony
            
            for char, matches in analysis:
                tag = "correct" if matches else "incorrect"
                spell_box.insert("end", char, tags=(tag,))
                
            spell_box.configure(state="disabled") # Blokujemy przed edycją przez użytkownika

        desc_lbl = ctk.CTkLabel(popup, text="The correct answer was:", font=("Segoe UI", 16))
        desc_lbl.pack(pady=(10, 5))

        scroll = ctk.CTkScrollableFrame(popup, width=830, height=200, fg_color="#F3CD8F", corner_radius=8)
        scroll.pack(pady=5, fill="both", expand=True, padx=35)

        import textwrap
        wrapped_lines = []
        for line in correct_text.split('\n'):
            p_strip = line.strip()
            if p_strip:
                wrapped = textwrap.fill(p_strip, width=105)
                wrapped_lines.append(wrapped)
            else:
                wrapped_lines.append("")
                
        formatted_correct = "\n".join(wrapped_lines)

        correct_lbl = ctk.CTkLabel(
            scroll, 
            text=formatted_correct, 
            font=("Segoe UI", 15, "bold"), 
            text_color="black", 
            justify="left", 
            anchor="w"
        )
        correct_lbl.pack(pady=15, padx=15, fill="both", expand=True)

        btn = ctk.CTkButton(popup, text="Continue", font=("Segoe UI", 16, "bold"), command=popup.destroy, fg_color="#3a7ebf", hover_color="#1f538d", height=40)
        btn.pack(pady=20)

    def play_regular_mode(self):
        current_bank = self.bank_var.get()
        if not current_bank or not current_bank.endswith(".json"):
            self.show_error_popup("Error", "Choose Quizz first dumbo!")
            return
            
        self.show_game_screen()
        self.load_selected_bank(current_bank)
        self.feedback_label.configure(text="Returned to Regular Mode!", text_color="green")
        self.update_mode_buttons_ui("regular")

    def restart_current_quiz(self):
        self.show_game_screen()
        if not self.logic.questions:
            self.feedback_label.configure(text="No active quiz to restart!", text_color="yellow")
            return
        self.logic.shuffle_and_restart()
        self.display_question()

    def toggle_mode_view(self, mode):
        for widget in self.game_frame.winfo_children():
            widget.pack_forget()
            
        self.question_label.configure(text="Mode switched. Please select a mode to play.", font=("Segoe UI", 18, "bold"))
        self.question_label.pack(pady=20)
        
        self.clear_highlights()
        self.handwritten_entry.delete("1.0", 'end')
        self.logic.reset_quiz()
        self.lock_choices()
        self.next_btn.configure(state="disabled")
        self.update_mode_buttons_ui("none")

    def update_mode_buttons_ui(self, active_mode):
        self.regular_mode_btn.configure(fg_color="#3a7ebf", border_width=0)
        self.hard_mode_btn.configure(fg_color="#bf3a3a", border_width=0)
        self.redemption_btn.configure(fg_color="#3abf70", border_width=0)
        self.self_made_btn.configure(fg_color="#8e44ad", border_width=0)
        
        if active_mode == "regular":
            self.regular_mode_btn.configure(fg_color="#1f538d", border_width=2, border_color="white")
        elif active_mode == "hard":
            self.hard_mode_btn.configure(fg_color="#8d2929", border_width=2, border_color="white")
        elif active_mode == "redemption":
            self.redemption_btn.configure(fg_color="#298d4f", border_width=2, border_color="white")
        elif active_mode == "self_made":
            self.self_made_btn.configure(fg_color="#732d91", border_width=2, border_color="white")

    def open_builder_window(self):
        self.logic.open_quiz_builder(self)

    def open_questions_viewer_callback(self):
        import os
        import json
        
        if not getattr(self, 'active_quiz_path', "") or not os.path.exists(self.active_quiz_path):
            self.show_error_popup("Error", "Load a question bank first!")
            return
            
        try:
            with open(self.active_quiz_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
                
            q_list = raw_data.get("questions", []) if isinstance(raw_data, dict) else raw_data
            
            qa_pairs = []
            for q_obj in q_list:
                q_data = q_obj.get("question", "")
                q_text = q_data.get("text", "") if isinstance(q_data, dict) else str(q_data)
                
                ans_data = q_obj.get("correct_answer", "")
                ans_text = str(ans_data.get("text", "")) if isinstance(ans_data, dict) else str(ans_data)
                
                qa_pairs.append({
                    "question": q_text.strip(),
                    "answer": ans_text.strip() if ans_text else "No answer provided"
                })
            
            viewer = QuestionViewerWindow(self, qa_pairs)
            
        except Exception as e:
            self.show_error_popup("Error", f"Failed to read the file: {str(e)}")

    def open_help_window(self):
        HelpViewerWindow(self)

    def play_hard_mode(self):
        current_bank = self.bank_var.get()
        if not current_bank or not current_bank.endswith(".json"):
            self.show_error_popup("Error", "Choose Quizz first dumbo!")
            return
            
        self.show_game_screen()
        import os
        base_name = os.path.basename(current_bank).replace(".json", "")
        suffix = "mc" if self.mode_var.get() == "Multiple Choice" else "written"
        path = f"special_quizzes/hard_mode_{suffix}_{base_name}.json"
        self.load_special_quiz(path, f"🔥 HARD MODE: {base_name} 🔥", "hard")

    def play_redemption_mode(self):
        current_bank = self.bank_var.get()
        if not current_bank or not current_bank.endswith(".json"):
            self.show_error_popup("Error", "Choose Quizz first dumbo!")
            return
            
        self.show_game_screen()
        import os
        base_name = os.path.basename(current_bank).replace(".json", "")
        suffix = "mc" if self.mode_var.get() == "Multiple Choice" else "written"
        path = f"special_quizzes/redemption_mode_{suffix}_{base_name}.json"
        self.load_special_quiz(path, f"⭐ REDEMPTION MODE: {base_name} ⭐", "redemption")

    def load_special_quiz(self, path, title_text, mode_type):
        import os
        self.update_mode_buttons_ui(mode_type)
        if hasattr(self, 'intensity_container') and self.intensity_container.winfo_exists():
            self.intensity_container.destroy()
            
        self.clear_highlights()
        self.choice_frame.pack_forget()
        self.text_frame.pack_forget()
        self.self_made_checkbox.pack_forget()
        self.feedback_label.configure(text="")
        
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            self.question_label.configure(text="Keep playing to unlock this feature", font=("Segoe UI", 18, "bold"))
            self.question_label.pack(pady=20)
            self.logic.reset_quiz()
            return
            
        try:
            self.save_current_game_state()
            self.active_quiz_path = path
            with open(path, 'r', encoding='utf-8') as f:
                self.logic.load_questions(json.load(f))
            self.check_resume_or_continue(path, lambda: self.show_intensity_screen(title_text=title_text))
        except Exception as e:
            self.question_label.configure(text=f"Error loading mode: {str(e)}", text_color="red")

    def show_intensity_screen(self, title_text=""):
        self.clear_highlights()
        self.choice_frame.pack_forget()
        self.text_frame.pack_forget()
        self.handwritten_entry.delete("1.0", 'end')
        self.next_btn.pack_forget() 
        self.self_made_checkbox.pack_forget()

        if hasattr(self, 'intensity_container') and self.intensity_container.winfo_exists():
            self.intensity_container.destroy()

        prompt_str = f"{title_text}\n\nHow are you feeling today?\nChoose your material range:" if title_text else "How are you feeling today?\nChoose your material range:"
        self.question_label.configure(text=prompt_str, font=("Segoe UI", 18, "bold"), justify="center")
        self.question_label.pack(pady=(10, 10))

        self.intensity_container = ctk.CTkFrame(self.game_frame, fg_color="transparent")
        self.intensity_container.pack(pady=10, fill="both", expand=True)

        percentages = [0.3, 0.6, 0.8, 1.0]
        labels = ["30% (Light Session)", "60% (Solid Practice)", "80% (Hardcore)", "100% (Full Material)"]
        colors = ["#3abf70", "#3a7ebf", "#e67e22", "#bf3a3a"]

        for pct, lbl, col in zip(percentages, labels, colors):
            btn = ctk.CTkButton(
                self.intensity_container,
                text=lbl,
                font=("Segoe UI", 15, "bold"),
                fg_color=col,
                hover_color="#1f538d",
                height=45,
                command=lambda p=pct: self.start_quiz_with_intensity(p)
            )
            btn.pack(pady=8, fill="x", padx=80)

    def start_quiz_with_intensity(self, percentage):
        try:
            import random
            if hasattr(self, 'intensity_container') and self.intensity_container.winfo_exists():
                self.intensity_container.pack_forget()

            self.logic.reset_quiz()
            total_questions = len(self.logic.questions)
            if total_questions > 0:
                target_count = int(total_questions * percentage)
                target_count = max(4, target_count)
                target_count = min(target_count, total_questions)
                self.logic.questions = random.sample(self.logic.questions, target_count)

            self.feedback_label.configure(text=f"Loaded {len(self.logic.questions)} questions for this run!", text_color="cyan")
            self.display_question()
        except Exception as e:
            self.show_error_popup("Crash Error", str(e))

    def display_question(self):
        self.clear_highlights()
        self.handwritten_entry.configure(state="normal") 
        self.handwritten_entry.delete("1.0", 'end')
        self.next_btn.configure(state="disabled")
        self.current_question_attempted = False 
        self.choice_locked = False 

        for widget in self.game_frame.winfo_children():
            widget.pack_forget() 
        
        current_q = self.logic.get_current_question()
        if not current_q:
            self.question_label.configure(text="End of Quiz dataset reached!", font=("Segoe UI", 22, "bold"), justify="center")
            self.question_label.pack(pady=30)
            return

        q_data = current_q.get("question", "")
        q_text = q_data.get("text", "") if isinstance(q_data, dict) else q_data
        
        current_num = self.logic.current_question_index + 1
        total_num = len(self.logic.questions)
        formatted_question = f"{str(q_text).strip()}  ({current_num}/{total_num})"
        
        self.question_label.configure(text=formatted_question, font=("Segoe UI", 22, "bold"), justify="center")
        self.question_label.pack(pady=(10, 15), fill="x", padx=10)
        
        if hasattr(self, 'self_made_checkbox_var'):
            is_self_made = self.logic.check_if_self_made(current_q, self.mode_var.get(), self.bank_var.get())
            self.self_made_checkbox_var.set(is_self_made)
        
        # ==========================================
        # WYGLĄD: MULTIPLE CHOICE MODE
        # ==========================================
        if self.mode_var.get() == "Multiple Choice":
            self.current_options = self.logic.get_dynamic_options(current_q)
            import textwrap
            for idx, card in enumerate(self.option_buttons):
                if idx < len(self.current_options):
                    raw_text = str(self.current_options[idx]).strip()
                    cleaned_lines = []
                    for paragraph in raw_text.split('\n'):
                        p_strip = paragraph.strip()
                        if p_strip:
                            wrapped = textwrap.fill(p_strip, width=105)
                            cleaned_lines.append(wrapped)
                    
                    final_text = "  " + "\n  ".join(cleaned_lines)
                    line_count = final_text.count('\n') + 1
                    calculated_height = max(40, line_count * 22 + 12)

                    card.configure(
                        text=final_text, 
                        fg_color="#EED9B7", 
                        text_color="black",
                        font=("Segoe UI", 16, "bold"),
                        height=calculated_height,
                        width=980, 
                        anchor="w"
                    )
                    card.bind("<Button-1>", lambda event, i=idx: self.submit_choice(i))
                    card.pack(pady=3, padx=5, ipadx=10, ipady=8)
                else:
                    card.pack_forget()

            self.choice_frame.pack(fill="both", expand=True, padx=5, pady=0)
            
            self.feedback_label.pack(pady=10)

            self.self_made_checkbox.configure(text="Add to Self Made Playlist") 
            self.self_made_checkbox.pack(in_=self.game_frame, anchor="e", padx=60, pady=(5, 5))

            self.next_btn.configure(width=220, height=45, font=("Segoe UI", 16, "bold"))
            self.next_btn.pack(in_=self.game_frame, anchor="e", padx=60, pady=(0, 20))

        # ==========================================
        # WYGLĄD: WRITTEN MODE
        # ==========================================
        else:
            self.text_frame.pack(fill="both", expand=True, padx=20, pady=0)
            
            self.handwritten_entry.configure(
                fg_color="#F3CD8F", 
                text_color="black",
                font=("Segoe UI", 16, "bold"),
                corner_radius=8,
                border_width=0 
            )
            
            self.handwritten_entry.pack(pady=(60, 15), padx=150, fill="both", expand=True)
            
            self.text_submit_btn.configure(font=("Segoe UI", 16, "bold"), height=45, width=200)
            self.text_submit_btn.pack(pady=10)

            self.feedback_label.pack(pady=10)
            
            self.self_made_checkbox.configure(text="Add to Self Made Playlist (Custom practice mode)")
            self.self_made_checkbox.pack(in_=self.game_frame, anchor="center", pady=10)
            
            self.next_btn.configure(width=250, height=50, font=("Segoe UI", 16, "bold"))
            self.next_btn.pack(in_=self.game_frame, anchor="center", pady=10)

    def submit_choice(self, index):
        if getattr(self, 'choice_locked', False):
            return
        self.choice_locked = True

        current_q = self.logic.get_current_question()
        selected = self.current_options[index]
        ans_data = current_q.get("correct_answer", "")
        correct = str(ans_data.get("text", "")) if isinstance(ans_data, dict) else str(ans_data)

        self.logic.session_total += 1
        if selected == correct:
            self.logic.session_correct += 1
            self.logic.log_question_success(current_q, self.mode_var.get(), self.active_quiz_path, self.bank_var.get())
            self.option_buttons[index].configure(fg_color="#A5D6A7") 
            self.feedback_label.configure(text="Correct answer selected!", text_color="green")
        else:
            self.logic.log_question_failure(current_q, self.mode_var.get(), self.bank_var.get())
            self.option_buttons[index].configure(fg_color="#FFCDD2") 
            self.feedback_label.configure(text="Incorrect answer!", text_color="red")
            self.show_correction_popup(correct) 
        
        self.lock_choices()
        self.next_btn.configure(state="normal")

    def lock_choices(self):
        for card in self.option_buttons:
            card.unbind("<Button-1>")

    def submit_text_answer(self):
        user_text = self.handwritten_entry.get("1.0", "end-1c").strip()
        if not user_text:
            self.feedback_label.configure(text="Please type an answer first!", text_color="yellow")
            return

        current_q = self.logic.get_current_question()
        if not current_q:
            self.feedback_label.configure(text="No active question found!", text_color="red")
            return

        ans_data = current_q.get("correct_answer", "")
        correct = str(ans_data.get("text", "")) if isinstance(ans_data, dict) else str(ans_data)
        # ... początek funkcji zostaje bez zmian ...
        
        self.clear_highlights()

        norm_user = self.normalize_for_comparison(user_text)
        norm_correct = self.normalize_for_comparison(correct)

        # --- NOWE: Fuzzy Matching ---
        import difflib
        similarity = difflib.SequenceMatcher(None, norm_user, norm_correct).ratio()
        
        # Próg tolerancji: 0.85 oznacza, że program wybaczy do 15% błędów w tekście
        THRESHOLD = 0.85
        is_fuzzy_match = similarity >= THRESHOLD

        is_first_try = not getattr(self, 'current_question_attempted', False)
        self.current_question_attempted = True

        if is_fuzzy_match:
            if is_first_try:
                self.logic.session_total += 1
                self.logic.session_correct += 1
                self.logic.log_question_success(current_q, self.mode_var.get(), self.active_quiz_path, self.bank_var.get())
            
            # Dodatkowy bajer: informuje, jeśli odpowiedź zaliczono pomimo literówki
            if similarity < 1.0:
                self.feedback_label.configure(text=f"Accepted with minor typos! ({int(similarity*100)}% match)", text_color="green")
            else:
                self.feedback_label.configure(text="Perfect match!", text_color="green")
                
            self.next_btn.configure(state="normal")
            self.handwritten_entry.configure(state="disabled") 
        else:
            # Jeśli błąd jest zbyt duży, robimy starą analizę do pop-upa
            analysis = self.logic.check_handwritten_mistake(norm_user, norm_correct)
            
            if is_first_try:
                self.logic.session_total += 1
                self.logic.log_question_failure(current_q, self.mode_var.get(), self.bank_var.get())
                
            self.feedback_label.configure(text=f"Incorrect! Too many typos ({int(similarity*100)}% match)", text_color="red")
            self.show_correction_popup(correct, analysis=analysis) 
            self.next_btn.configure(state="normal")
            self.handwritten_entry.configure(state="disabled") 

    def clear_highlights(self):
        # 🟢 Czysto i schludnie. Żadnych pozostałości po starym highlight_frame
        self.feedback_label.configure(text="")

    def update_score_mode_buttons_ui(self, active_mode):
        self.score_mc_btn.configure(fg_color="#3a7ebf", border_width=0)
        self.score_wr_btn.configure(fg_color="#3a7ebf", border_width=0)
        
        if active_mode == "Multiple Choice":
            self.score_mc_btn.configure(fg_color="#1f538d", border_width=2, border_color="white")
        elif active_mode == "Handwritten Input":
            self.score_wr_btn.configure(fg_color="#1f538d", border_width=2, border_color="white")

    def show_scores_screen(self):
        if hasattr(self, 'welcome_frame'):
            self.welcome_frame.pack_forget()
            
        self.game_frame.pack_forget()
        for widget in self.scores_frame.winfo_children():
            widget.destroy()
            
        self.scores_frame.pack(fill="both", expand=True)

        self.update_mode_buttons_ui("none")
            
        gen_data = self.logic.get_general_score()
        gen_correct = gen_data.get("overall_correct", 0)
        gen_total = gen_data.get("overall_total", 0)
        gen_pct = round((gen_correct / gen_total * 100)) if gen_total > 0 else 0
        
        title_lbl = ctk.CTkLabel(self.scores_frame, text="Overall General Score", font=("Segoe UI", 16, "bold"))
        title_lbl.pack(pady=(20, 5))
        
        score_lbl = ctk.CTkLabel(self.scores_frame, text=f"{gen_pct}%", font=("Segoe UI", 42, "bold"), text_color="cyan")
        score_lbl.pack(pady=(0, 20))
        
        btn_frame = ctk.CTkFrame(self.scores_frame, fg_color="transparent")
        btn_frame.pack(pady=10, fill="x", padx=40)
        
        self.score_mc_btn = ctk.CTkButton(btn_frame, text="Multiple Choice", command=lambda: self.load_score_answering_mode("Multiple Choice"))
        self.score_mc_btn.pack(side="left", expand=True, padx=10)
        
        self.score_wr_btn = ctk.CTkButton(btn_frame, text="Written Input", command=lambda: self.load_score_answering_mode("Handwritten Input"))
        self.score_wr_btn.pack(side="right", expand=True, padx=10)
        
        self.score_content_frame = ctk.CTkFrame(self.scores_frame, fg_color="transparent")
        self.score_content_frame.pack(fill="both", expand=True, pady=10, padx=20)
        
    def load_score_answering_mode(self, answering_mode_str):
        self.update_score_mode_buttons_ui(answering_mode_str)

        for widget in self.score_content_frame.winfo_children():
            widget.destroy()
            
        import os
        valid_banks = []
        folder_path = "Questions Database"
        if os.path.exists(folder_path):
            valid_banks = [f for f in os.listdir(folder_path) if f.endswith('.json')]

        if not valid_banks:
            ctk.CTkLabel(self.score_content_frame, text=f"No JSON banks found in 'Questions Database'.", text_color="yellow").pack(pady=20)
            return
            
        self.score_bank_var = ctk.StringVar(value="Select Bank...")
        dropdown = ctk.CTkOptionMenu(
            self.score_content_frame, 
            variable=self.score_bank_var, 
            values=valid_banks, 
            command=lambda val: self.load_game_modes_for_bank(val, answering_mode_str)
        )
        dropdown.pack(pady=10)
        
        self.category_content_frame = ctk.CTkFrame(self.score_content_frame, fg_color="transparent")
        self.category_content_frame.pack(fill="both", expand=True, pady=5)
        
    def load_game_modes_for_bank(self, bank_name, answering_mode_str):
        for widget in self.category_content_frame.winfo_children():
            widget.destroy()
            
        game_modes = ["Regular Mode", "Hard Mode", "Redemption Mode", "Self Made Mode"]
        
        self.game_mode_var = ctk.StringVar(value="Select Game Mode...")
        dropdown = ctk.CTkOptionMenu(
            self.category_content_frame, 
            variable=self.game_mode_var, 
            values=game_modes,
            command=lambda val: self.display_scores_final(val, bank_name, answering_mode_str)
        )
        dropdown.pack(pady=10)
        
        self.results_frame = ctk.CTkFrame(self.category_content_frame, fg_color="transparent")
        self.results_frame.pack(fill="both", expand=True, pady=10)
        
    def display_scores_final(self, game_mode_str, bank_name, answering_mode_str):
        for widget in self.results_frame.winfo_children():
            widget.destroy()
            
        if game_mode_str == "Hard Mode":
            cat = "hard"
        elif game_mode_str == "Redemption Mode":
            cat = "redemption"
        elif game_mode_str == "Self Made Mode":
            cat = "self_made"
        else:
            cat = "regular"
            
        cat_history = self.logic.get_category_history(cat)
        mode_data = cat_history.get(answering_mode_str, {})
        
        bank_base = bank_name.replace(".json", "")
        tries = []
        for saved_key, attempts_list in mode_data.items():
            if bank_base in saved_key:
                tries.extend(attempts_list)
        
        if not tries:
            ctk.CTkLabel(self.results_frame, text=f"No tries recorded for {bank_name} in {game_mode_str}.", text_color="yellow").pack(pady=20)
            return
            
        total_c = sum(t["correct"] for t in tries)
        total_t = sum(t["total"] for t in tries)
        pct = round((total_c / total_t * 100)) if total_t > 0 else 0
        
        avg_lbl = ctk.CTkLabel(self.results_frame, text=f"Bank Average: {pct}%", font=("Segoe UI", 18, "bold"), text_color="green")
        avg_lbl.pack(pady=10)
        
        scroll = ctk.CTkScrollableFrame(self.results_frame, width=400, height=200)
        scroll.pack(pady=10, fill="both", expand=True)
        
        for idx, t in enumerate(tries):
            c = t["correct"]
            tot = t["total"]
            t_pct = round((c / tot * 100)) if tot > 0 else 0
            row = ctk.CTkFrame(scroll, fg_color="#1f538d", corner_radius=5)
            row.pack(fill="x", pady=2, padx=10)
            lbl = ctk.CTkLabel(row, text=f"Attempt {idx + 1}:   {c} / {tot}   ({t_pct}%)", font=("Segoe UI", 13, "bold"))
            lbl.pack(pady=5)

    def next_question(self):
        if self.logic.advance_question():
            self.display_question()
        else:
            summary_frame = ctk.CTkFrame(self.game_frame, fg_color=self.game_frame.cget("fg_color"))
            summary_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
            
            self.logic.log_run_score(self.mode_var.get(), self.active_quiz_path, self.logic.session_correct, self.logic.session_total)
            
            score_text = f"Evaluation Complete!\nFinal Score: {self.logic.session_correct} / {self.logic.session_total}"
            score_label = ctk.CTkLabel(summary_frame, text=score_text, font=("Segoe UI", 20, "bold"), text_color="cyan")
            score_label.pack(pady=20)
            
            restart_btn = ctk.CTkButton(summary_frame, text="🔀 Shuffle & Restart", command=self.restart_current_quiz, fg_color="#e67e22", hover_color="#d35400")
            restart_btn.pack(pady=10)
            
            if self.logic.session_missed:
                missed_title = ctk.CTkLabel(summary_frame, text="Items Missed This Run:", font=("Segoe UI", 14, "bold"), text_color="red")
                missed_title.pack(pady=10)
                scroll_box = ctk.CTkScrollableFrame(summary_frame, width=450, height=250)
                scroll_box.pack(pady=10, fill="both", expand=True, padx=40)
                for item in self.logic.session_missed:
                    item_lbl = ctk.CTkLabel(scroll_box, text=f"• {item}", font=("Segoe UI", 12), anchor="w")
                    item_lbl.pack(pady=2, fill="x", padx=10)
            else:
                perfect_lbl = ctk.CTkLabel(summary_frame, text="⭐ Perfect Run! No mistakes made! ⭐", font=("Segoe UI", 16, "bold"), text_color="green")
                perfect_lbl.pack(pady=20)
                
            self.next_btn.configure(state="disabled")

    def normalize_for_comparison(self, text):
        import re
        if not text: return ""
        
        text = text.lower()
        
        pl_chars = {'ą':'a', 'ć':'c', 'ę':'e', 'ł':'l', 'ń':'n', 'ó':'o', 'ś':'s', 'ź':'z', 'ż':'z'}
        for pl, base in pl_chars.items():
            text = text.replace(pl, base)
            
        text = re.sub(r'[^a-z0-9\s]', '', text)
        
        return re.sub(r'\s+', ' ', text).strip()

    def on_self_made_toggled(self):
        current_q = self.logic.get_current_question()
        if not current_q: return
        is_checked = self.self_made_checkbox_var.get()
        self.logic.toggle_self_made(current_q, self.mode_var.get(), self.bank_var.get(), is_checked)

    def open_playlist_creator(self):
        current_bank = self.bank_var.get()
        if not current_bank or not current_bank.endswith(".json") or not self.logic.questions:
            self.show_error_popup("Error", "Load a question bank first!")
            return
            
        popup = ctk.CTkToplevel(self)
        popup.title("Create Custom Playlist")
        popup.geometry("650x600")
        popup.transient(self)
        popup.grab_set()
        
        name_frame = ctk.CTkFrame(popup, fg_color="transparent")
        name_frame.pack(pady=10, fill="x", padx=20)
        ctk.CTkLabel(name_frame, text="Playlist Name:", font=("Segoe UI", 14, "bold")).pack(side="left", padx=5)
        name_entry = ctk.CTkEntry(name_frame, width=300)
        name_entry.pack(side="left", padx=5)
        
        scroll_frame = ctk.CTkScrollableFrame(popup, width=600, height=400)
        scroll_frame.pack(pady=10, fill="both", expand=True, padx=20)
        
        checkboxes = {}
        for q in self.logic.questions:
            q_id = str(q.get("id"))
            q_text = q.get("question", "")
            if isinstance(q_text, dict): q_text = q_text.get("text", "")
            q_text_abridged = (str(q_text)[:75] + '...') if len(str(q_text)) > 75 else str(q_text)
            
            var = ctk.BooleanVar(value=False)
            cb = ctk.CTkCheckBox(scroll_frame, text=q_text_abridged, variable=var, font=("Segoe UI", 12))
            cb.pack(anchor="w", pady=4, padx=5)
            checkboxes[q_id] = (var, q)
            
        def save_playlist():
            p_name = name_entry.get().strip()
            if not p_name:
                self.show_error_popup("Error", "Enter a playlist name!")
                return
            selected_qs = [q for q_id, (var, q) in checkboxes.items() if var.get()]
            if not selected_qs:
                self.show_error_popup("Error", "Select at least one question!")
                return
                
            success = self.logic.save_custom_playlist(p_name, current_bank, self.mode_var.get(), selected_qs)
            if success:
                popup.destroy()
                self.feedback_label.configure(text=f"Playlist '{p_name}' created!", text_color="green")
            else:
                self.show_error_popup("Error", "Failed to save playlist.")
                
        save_btn = ctk.CTkButton(popup, text="Save Playlist", font=("Segoe UI", 14, "bold"), fg_color="green", hover_color="darkgreen", command=save_playlist)
        save_btn.pack(pady=10)

    def play_self_made_mode(self):
        current_bank = self.bank_var.get()
        if not current_bank or not current_bank.endswith(".json"):
            self.show_error_popup("Error", "Choose Quizz first dumbo!")
            return
            
        self.show_game_screen()
        self.update_mode_buttons_ui("self_made")
        
        if hasattr(self, 'intensity_container') and self.intensity_container.winfo_exists():
            self.intensity_container.destroy()
        if hasattr(self, 'self_made_intro_container') and self.self_made_intro_container.winfo_exists():
            self.self_made_intro_container.destroy()
            
        self.clear_highlights()
        self.choice_frame.pack_forget()
        self.text_frame.pack_forget()
        self.next_btn.pack_forget()
        self.self_made_checkbox.pack_forget()
        self.feedback_label.configure(text="")
        
        self.question_label.configure(text="✨ SELF MADE MODE ✨\n\nChoose a playlist to practice:", font=("Segoe UI", 18, "bold"))
        self.question_label.pack(pady=20)
        
        # Zmienione na ScrollableFrame, by pomieścić wiele playlist
        self.self_made_intro_container = ctk.CTkScrollableFrame(self.game_frame, fg_color="transparent")
        self.self_made_intro_container.pack(pady=10, fill="both", expand=True)
        
        default_path = self.logic.get_self_made_path(self.mode_var.get(), current_bank)
        def_btn = ctk.CTkButton(self.self_made_intro_container, text="⭐ Default Playlist", font=("Segoe UI", 16, "bold"), height=45, fg_color="#8e44ad", hover_color="#732d91", command=lambda p=default_path, n="Default Playlist": self.prepare_self_made_quiz(p, n))
        def_btn.pack(pady=10, fill="x", padx=80)
        
        custom_playlists = self.logic.get_custom_playlists(self.mode_var.get(), current_bank)
        for p_name, p_path in custom_playlists:
            row = ctk.CTkFrame(self.self_made_intro_container, fg_color="transparent")
            row.pack(pady=5, fill="x", padx=80)
            
            c_btn = ctk.CTkButton(row, text=f"📂 {p_name}", font=("Segoe UI", 15, "bold"), height=40, fg_color="#2980b9", hover_color="#1f618d", command=lambda p=p_path, n=p_name: self.prepare_self_made_quiz(p, n))
            c_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
            
            del_btn = ctk.CTkButton(row, text="X", font=("Segoe UI", 14, "bold"), width=40, height=40, fg_color="#c0392b", hover_color="#922b21", command=lambda p=p_path: self.delete_playlist_ui(p))
            del_btn.pack(side="right")

    def delete_playlist_ui(self, path):
        self.logic.delete_custom_playlist(path)
        self.play_self_made_mode() 

    def prepare_self_made_quiz(self, path, playlist_name):
        import os
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            self.show_error_popup("Empty Playlist", f"Playlist '{playlist_name}' is empty!")
            return
            
        for widget in self.self_made_intro_container.winfo_children():
            widget.destroy()
            
        self.active_quiz_path = path
        self.question_label.configure(text=f"✨ {playlist_name.upper()} ✨\n\nReady to practice?", font=("Segoe UI", 18, "bold"))
        
        lets_go_btn = ctk.CTkButton(self.self_made_intro_container, text="🚀 Let's goooo", font=("Segoe UI", 16, "bold"), height=45, fg_color="#e67e22", hover_color="#d35400", command=lambda: self.start_self_made_quiz(path))
        lets_go_btn.pack(pady=10, fill="x", padx=80)
        
        list_btn = ctk.CTkButton(self.self_made_intro_container, text="📋 Questions List", font=("Segoe UI", 15, "bold"), height=45, fg_color="#3a7ebf", hover_color="#1f538d", command=lambda: self.show_self_made_list(path, playlist_name))
        list_btn.pack(pady=10, fill="x", padx=80)
        
        back_btn = ctk.CTkButton(self.self_made_intro_container, text="← Back to Playlists", font=("Segoe UI", 14), height=35, fg_color="#7f8c8d", hover_color="#616a6b", command=self.play_self_made_mode)
        back_btn.pack(pady=20, fill="x", padx=120)

    def show_self_made_list(self, path, playlist_name="Self Made Questions"):
        import json
        popup = ctk.CTkToplevel(self)
        popup.title(playlist_name)
        popup.geometry("600x480")
        popup.transient(self)
        popup.grab_set()
        
        title_lbl = ctk.CTkLabel(popup, text="Select questions to remove:", font=("Segoe UI", 15, "bold"))
        title_lbl.pack(pady=10)
        
        scroll_frame = ctk.CTkScrollableFrame(popup, width=540, height=340)
        scroll_frame.pack(pady=5, fill="both", expand=True, padx=15)
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                questions = json.load(f).get("questions", [])
        except:
            questions = []
            
        checkboxes = {}
        for q in questions:
            q_id = str(q.get("id"))
            q_text = q.get("question", "")
            if isinstance(q_text, dict): q_text = q_text.get("text", "")
            q_text_abridged = (str(q_text)[:75] + '...') if len(str(q_text)) > 75 else str(q_text)
            
            var = ctk.BooleanVar(value=False)
            cb = ctk.CTkCheckBox(scroll_frame, text=q_text_abridged, variable=var, font=("Segoe UI", 12))
            cb.pack(anchor="w", pady=4, padx=5)
            checkboxes[q_id] = var
            
        def delete_selected():
            ids_to_remove = [q_id for q_id, var in checkboxes.items() if var.get()]
            if ids_to_remove:
                # 🟢 Przekazujemy dokładną ścieżkę do playlisty, którą edytujemy
                self.logic.remove_self_made_questions(self.mode_var.get(), self.bank_var.get(), ids_to_remove, custom_path=path)
                popup.destroy()
                # 🟢 Wracamy do konkretnej playlisty, zamiast głównego menu
                self.prepare_self_made_quiz(path, playlist_name) 
                
        del_btn = ctk.CTkButton(popup, text="Delete Selected", font=("Segoe UI", 14, "bold"), fg_color="red", hover_color="darkred", command=delete_selected)
        del_btn.pack(pady=10)

    def start_self_made_quiz(self, path):
                try:
                    import json, random
                    if hasattr(self, 'self_made_intro_container') and self.self_made_intro_container.winfo_exists():
                        self.self_made_intro_container.pack_forget()
                        
                    with open(path, 'r', encoding='utf-8') as f:
                        self.logic.load_questions(json.load(f))
                    
                    random.shuffle(self.logic.questions) 
                    self.display_question()
                except Exception as e:
                    self.show_error_popup("Crash Error", str(e))
    # ==========================================
    # AUTO-SAVE & RESUME UI LOGIC
    # ==========================================
    def save_current_game_state(self):
        if not getattr(self, 'active_quiz_path', ""):
            return
            
        typed_text = ""
        # Zapisuje tekst tylko jeśli jesteśmy w trybie pisemnym i pole jest na ekranie
        if self.mode_var.get() == "Handwritten Input" and self.handwritten_entry.winfo_ismapped():
            typed_text = self.handwritten_entry.get("1.0", "end-1c").strip()
            
        self.logic.save_current_state(self.mode_var.get(), self.active_quiz_path, typed_text)

    def on_closing(self):
        # Odpalane przy kliknięciu "X" na oknie
        self.save_current_game_state()
        self.destroy()

    def check_resume_or_continue(self, path, new_game_callback):
        saved = self.logic.load_saved_state()
        if saved and saved.get("file_path") == path and saved.get("mode") == self.mode_var.get():
            popup = ctk.CTkToplevel(self)
            popup.title("Resume Game?")
            popup.geometry("500x200")
            popup.transient(self)
            popup.grab_set()
            
            ctk.CTkLabel(popup, text="Found a saved game state for this quiz.\nWould you like to resume?", font=("Segoe UI", 16, "bold")).pack(pady=20)
            
            def on_yes():
                popup.destroy()
                self.resume_saved_game(saved)
                
            def on_no():
                self.logic.clear_saved_state()
                popup.destroy()
                new_game_callback()
                
            btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
            btn_frame.pack(pady=10)
            ctk.CTkButton(btn_frame, text="Yes, Resume", fg_color="green", hover_color="darkgreen", command=on_yes).pack(side="left", padx=10)
            ctk.CTkButton(btn_frame, text="No, Start Fresh", fg_color="red", hover_color="darkred", command=on_no).pack(side="left", padx=10)
        else:
            new_game_callback()

    def resume_saved_game(self, saved_data):
        self.logic.questions = saved_data["questions"]
        self.logic.current_question_index = saved_data["current_index"]
        self.logic.session_correct = saved_data["session_correct"]
        self.logic.session_total = saved_data["session_total"]
        self.logic.session_missed = saved_data["session_missed"]
        
        # Czyszczenie ekranów, jeśli jakieś wiszą
        if hasattr(self, 'intensity_container') and self.intensity_container.winfo_exists():
            self.intensity_container.destroy()
        if hasattr(self, 'self_made_intro_container') and self.self_made_intro_container.winfo_exists():
            self.self_made_intro_container.destroy()
            
        self.display_question()
        
        # Odtwarzanie wpisanego tekstu z klawiatury
        typed_text = saved_data.get("typed_text", "")
        if self.mode_var.get() == "Handwritten Input" and typed_text:
            self.handwritten_entry.insert("1.0", typed_text)

if __name__ == "__main__":
    import sys
    import os
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(application_path)
    
    logic_instance = logic.QuizLogic()
    app = QuizApp(logic_instance)
    app.mainloop()