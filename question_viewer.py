import customtkinter as ctk

class QuestionViewerWindow(ctk.CTkToplevel):
    def __init__(self, parent, qa_pairs):
        super().__init__(parent)
        
        self.title("All Questions & Answers")
        self.geometry("1100x800")
        self.transient(parent)

        self.iconbitmap("ikona.ico")
        
        # --- Ustawienia czcionki ---
        self.base_q_font = 16
        self.current_q_font = 16
        self.current_a_font = 15
        
        self.pair_frames = [] 
        self.q_labels = []
        self.a_labels = []
        self._zoom_job = None 

        # --- Zmienne wyszukiwarki ---
        self.search_matches = []
        self.current_match_idx = -1
        self.last_search_term = ""

        # --- Nagłówek ---
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(20, 10))

        title_label = ctk.CTkLabel(self.header_frame, text="Questions & Answers Database", font=("Segoe UI", 24, "bold"))
        title_label.pack()

        # --- ZMODYFIKOWANY Pasek Wyszukiwania ---
        self.search_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        
        self.search_entry = ctk.CTkEntry(self.search_frame, placeholder_text="Search...", width=250)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<Return>", self.search_next) 
        
        # Przycisk > (działa jak Enter)
        self.search_btn = ctk.CTkButton(self.search_frame, text=">", width=30, command=self.search_next)
        self.search_btn.pack(side="left", padx=(0, 5))
        
        # Strzałka w górę (Poprzedni)
        self.prev_match_btn = ctk.CTkButton(self.search_frame, text="↑", width=30, command=self.search_prev)
        self.prev_match_btn.pack(side="left", padx=2)
        
        # Strzałka w dół (Następny)
        self.next_match_btn = ctk.CTkButton(self.search_frame, text="↓", width=30, command=self.search_next)
        self.next_match_btn.pack(side="left", padx=2)
        
        # Przycisk Zamknij (X)
        self.close_search_btn = ctk.CTkButton(self.search_frame, text="X", width=30, fg_color="#bf3a3a", hover_color="#8d2929", command=self.hide_search_bar)
        self.close_search_btn.pack(side="left", padx=(5, 15))
        
        # Licznik (np. 1 / 8)
        self.search_info_label = ctk.CTkLabel(self.search_frame, text="", text_color="cyan", font=("Segoe UI", 14, "bold"))
        self.search_info_label.pack(side="left")

        # --- Licznik Zooma ---
        self.zoom_label = ctk.CTkLabel(self, text="100%", font=("Segoe UI", 16, "bold"), text_color="gray")
        self.zoom_label.place(relx=0.97, rely=0.03, anchor="ne")

        # --- Guzik "Search" obok licznika ---
        self.search_toggle_btn = ctk.CTkButton(
            self, 
            text="🔍 Search", 
            width=80, 
            height=28,
            fg_color="#3b3b3b",    
            hover_color="#595959", 
            font=("Segoe UI", 12, "bold"),
            command=self.show_search_bar
        )
        # relx=0.92 sprawia, że jest trochę bardziej po lewej niż licznik, ale w tej samej linii pionowej (rely=0.03)
        self.search_toggle_btn.place(relx=0.92, rely=0.03, anchor="ne")

        # --- Kontener Scrollowany ---
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="#242424", bg_color="#242424", corner_radius=0)
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        if not qa_pairs:
            empty_label = ctk.CTkLabel(self.scroll_frame, text="No question bank loaded.", font=("Segoe UI", 16))
            empty_label.pack(pady=40)
            return

        for idx, pair in enumerate(qa_pairs):
            pair_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#2B2B2B", corner_radius=8)
            pair_frame.pack(pady=8) 
            self.pair_frames.append(pair_frame) 

            q_text = f"Question {idx + 1}: {pair['question']}"
            q_label = ctk.CTkLabel(pair_frame, text=q_text, 
                                   font=("Segoe UI", self.current_q_font, "bold"), 
                                   text_color="#F3CD8F", 
                                   justify="center",   
                                   anchor="center",    
                                   width=1000,         
                                   wraplength=960)     
            q_label.pack(padx=20, pady=(15, 5))
            self.q_labels.append(q_label)

            a_text = f"Answer: {pair['answer']}"
            a_label = ctk.CTkLabel(pair_frame, text=a_text, 
                                   font=("Segoe UI", self.current_a_font), 
                                   text_color="white", 
                                   justify="center",   
                                   anchor="center",    
                                   width=1000, 
                                   wraplength=960)
            a_label.pack(padx=20, pady=(0, 15))
            self.a_labels.append(a_label)

        self.bind("<Control-MouseWheel>", self.zoom_text)
        self.bind("<Control-f>", self.show_search_bar)
        self.bind("<Control-F>", self.show_search_bar)
        
    # ==========================================
    # LOGIKA WYSZUKIWARKI 
    # ==========================================
    def show_search_bar(self, event=None):
        self.search_frame.pack(pady=10)
        self.search_entry.focus_set() 

    def hide_search_bar(self):
        self.search_frame.pack_forget()
        self.clear_highlights()
        self.search_entry.delete(0, 'end')
        self.search_info_label.configure(text="")
        self.last_search_term = ""

    def clear_highlights(self):
        for frame in self.pair_frames:
            frame.configure(fg_color="#2B2B2B") 

    def search_next(self, event=None):
        self._execute_search(step=1)

    def search_prev(self, event=None):
        self._execute_search(step=-1)

    def _execute_search(self, step):
        term = self.search_entry.get().lower().strip()
        if not term:
            self.clear_highlights()
            self.search_info_label.configure(text="")
            return

        if term != self.last_search_term:
            self.last_search_term = term
            self.search_matches = []
            self.current_match_idx = -1
            self.clear_highlights()

            for idx, (q_lbl, a_lbl) in enumerate(zip(self.q_labels, self.a_labels)):
                if term in q_lbl.cget("text").lower() or term in a_lbl.cget("text").lower():
                    self.search_matches.append(self.pair_frames[idx])

        if not self.search_matches:
            self.search_info_label.configure(text="0 / 0", text_color="red")
            return

        if self.current_match_idx == -1:
            self.current_match_idx = 0
        else:
            self.current_match_idx = (self.current_match_idx + step) % len(self.search_matches)

        self.search_info_label.configure(text=f"{self.current_match_idx + 1} / {len(self.search_matches)}", text_color="cyan")
        
        self.clear_highlights()
        match_frame = self.search_matches[self.current_match_idx]
        match_frame.configure(fg_color="#5a4211") 
        
        self.update_idletasks() 
        canvas = self.scroll_frame._parent_canvas
        y_pos = match_frame.winfo_y()
        
        bbox = canvas.bbox("all")
        if bbox:
            total_height = bbox[3]
            fraction = max(0.0, (y_pos - 10) / total_height)
            canvas.yview_moveto(fraction)

    # ==========================================
    # LOGIKA ZOOMA
    # ==========================================
    def zoom_text(self, event):
        if event.delta > 0:
            self.current_q_font += 2
            self.current_a_font += 2
        else:
            self.current_q_font -= 2
            self.current_a_font -= 2
            
        self.current_q_font = max(10, min(self.current_q_font, 36))
        self.current_a_font = max(9, min(self.current_a_font, 35))
        
        pct = int((self.current_q_font / self.base_q_font) * 100)
        self.zoom_label.configure(text=f"{pct}%")
        
        if self._zoom_job is not None:
            self.after_cancel(self._zoom_job)
            
        self._zoom_job = self.after(50, self.apply_zoom)
        return "break"
        
    def apply_zoom(self):
        for q_label in self.q_labels:
            q_label.configure(font=("Segoe UI", self.current_q_font, "bold"))
        for a_label in self.a_labels:
            a_label.configure(font=("Segoe UI", self.current_a_font))