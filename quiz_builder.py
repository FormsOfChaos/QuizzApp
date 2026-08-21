import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import json
import os

class QuizBuilderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quiz Builder")
        self.root.geometry("750x780")
        self.root.iconbitmap("ikona.ico")
        
        self.questions = []
        self.question_id = 0
        self.loaded_file_name = "No file loaded"
        
        self.label = ctk.CTkLabel(self.root, text="Loaded File: No file loaded | Total Questions: 0", font=("Helvetica", 13, "bold"))
        self.label.pack(pady=5)
        
        self.create_widgets()
        self.update_label()
    
    def create_widgets(self):
        frame = ctk.CTkFrame(self.root, corner_radius=0)
        frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        # Question Label and Textbox
        self.question_label = ctk.CTkLabel(frame, text="1. Paste Question Text Paragraph:", font=("Helvetica", 12, "bold"))
        self.question_label.pack(pady=5)
        self.question_textbox = ctk.CTkTextbox(frame, height=220, width=650, wrap="word")
        self.question_textbox.pack(pady=5)
        
        # Answer Label and Textbox
        self.answer_label = ctk.CTkLabel(frame, text="2. Paste Target Text For Spellchecking:", font=("Helvetica", 12, "bold"))
        self.answer_label.pack(pady=5)
        self.answer_textbox = ctk.CTkTextbox(frame, height=100, width=650, wrap="word")
        self.answer_textbox.pack(pady=5)
        
        # Add Question Button
        self.add_button = ctk.CTkButton(frame, text="Add Question", command=self.add_question)
        self.add_button.pack(pady=5)
        
        # Save / Export JSON Button
        self.save_button = ctk.CTkButton(frame, text="Save / Export JSON", fg_color="green", hover_color="darkgreen", command=self.save_questions)
        self.save_button.pack(pady=5)
        
        # Load Existing JSON Button
        self.load_button = ctk.CTkButton(frame, text="Load Existing JSON to Append", command=self.load_questions)
        self.load_button.pack(pady=5)
        
        # Queue Frame
        self.queue_frame = ctk.CTkScrollableFrame(frame, height=180, width=650)
        self.queue_frame.pack(pady=10)
    
    def add_question(self):
        question = self.question_textbox.get("1.0", tk.END).strip()
        answer = self.answer_textbox.get("1.0", "end-1c").strip()
        
        if question and answer:
            # Dynamically determine next safe incremental ID to prevent duplicates
            next_id = max([q['id'] for q in self.questions]) + 1 if self.questions else 0
            
            # NEW STRUCTURE
            new_question = {
                "id": next_id,
                "topic": "Manual Entry",
                "difficulty": "medium",
                "question": {
                    "question_id": f"q_{next_id}",
                    "text": question
                },
                "options": [],
                "correct_answer": {
                    "answer_id": f"a_{next_id}",
                    "text": answer
                }
            }
            
            self.questions.append(new_question)
            self.question_textbox.delete("1.0", tk.END)
            self.answer_textbox.delete("1.0", tk.END)
            self.update_label()
            self.render_queue()
        else:
            messagebox.showerror("Error", "Both question and answer are required.")
    
    def load_questions(self):
        default_dir = os.path.join(os.getcwd(), "Questions Database")
        file_path = filedialog.askopenfilename(
            initialdir=default_dir,
            filetypes=[("JSON files", "*.json")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                
                # FIXED DATA EXTRACTION: Safely extracts data whether it has the parent 'questions' key or not
                if isinstance(data, dict) and "questions" in data:
                    loaded_questions = data["questions"]
                elif isinstance(data, list):
                    loaded_questions = data
                else:
                    loaded_questions = []
                
                self.questions = []
                if loaded_questions:
                    self.questions.extend(loaded_questions)
                    self.question_id = max(q['id'] for q in loaded_questions) + 1
                else:
                    self.question_id = 0
                
                self.loaded_file_name = os.path.basename(file_path)
                self.update_label()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load questions: {str(e)}")
            self.render_queue()
    
    def save_questions(self):
        if not self.questions:
            messagebox.showwarning("Empty Batch", "There are no questions in memory to export!")
            return
            
        default_dir = os.path.join(os.getcwd(), "Questions Database")
        file_path = filedialog.asksaveasfilename(
            initialdir=default_dir,
            defaultextension=".json", 
            filetypes=[("JSON files", "*.json")]
        )
        if file_path:
            try:
                # FIXED DATA WRAPPER: Guarantees your file matches the master game parent schema structure
                output_data = {"questions": self.questions}
                
                with open(file_path, 'w', encoding='utf-8') as file:
                    json.dump(output_data, file, indent=4, ensure_ascii=False)
                
                # Full RAM state cleanups to prevent duplicate appending loops
                self.questions = []
                self.question_id = 0
                self.loaded_file_name = "No file loaded"
                self.update_label()
                messagebox.showinfo("Success", "Questions saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save questions: {str(e)}")
            self.render_queue()
    
    def update_label(self):
        total_questions = len(self.questions)
        self.label.configure(text=f"Loaded File: {self.loaded_file_name} | Total Questions inside Memory: {total_questions}")
    
    def render_queue(self):
        for widget in self.queue_frame.winfo_children():
            widget.destroy()
        
        for i, q in enumerate(self.questions):
            item_frame = ctk.CTkFrame(self.queue_frame, corner_radius=5)
            item_frame.pack(fill=tk.X, padx=5, pady=5)
            
            item_label = ctk.CTkLabel(item_frame, text=f"Item {i + 1}:", anchor="w", font=("Helvetica", 11, "bold"))
            item_label.pack(side=tk.LEFT, padx=5, pady=5)
            
            q_text = q['question']['text']
            a_text = q['correct_answer']['text'] if isinstance(q['correct_answer'], dict) else q.get('correct_answer', '')
            item_text = f"Q: {q_text[:40]}... | A: {a_text[:25]}..."
            item_preview = ctk.CTkLabel(item_frame, text=item_text, anchor="w", wraplength=500)
            item_preview.pack(side=tk.LEFT, padx=5, pady=5)
            
            edit_button = ctk.CTkButton(item_frame, text="Edit/Pull", command=lambda q=q: self.edit_question(q))
            edit_button.pack(side=tk.RIGHT, padx=5, pady=5)
    
    def edit_question(self, question):
        self.question_textbox.delete("1.0", "end")
        self.question_textbox.insert("1.0", question['question']['text'])
        
        a_text = question['correct_answer']['text'] if isinstance(question['correct_answer'], dict) else question.get('correct_answer', '')
        self.answer_textbox.insert("1.0", a_text)
        
        self.questions.remove(question)
        self.update_label()
        self.render_queue()

if __name__ == "__main__":
    root = ctk.CTk()
    app = QuizBuilderApp(root)
    root.mainloop()