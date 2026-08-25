import random
import os
import json
import customtkinter as ctk
from quiz_builder import QuizBuilderApp

class QuizLogic:
    def __init__(self):
        self.questions = []
        self.current_question_index = 0
        
        # Ensure our isolated data directory exists right away
        os.makedirs("special_quizzes", exist_ok=True)
        # 🟢 NOWE: Tworzymy folder na bazy wiedzy!
        os.makedirs("Questions Database", exist_ok=True)
        os.makedirs("special_quizzes/custom_playlists", exist_ok=True)
        
        # Running session counters for scorecard summary wrap-ups
        self.session_correct = 0
        self.session_total = 0
        self.session_missed = []

    def reset_quiz(self):
        self.current_question_index = 0
        self.session_correct = 0
        self.session_total = 0
        self.session_missed = []

    def load_questions(self, data):
        self.reset_quiz()  # Reset session counters right here on a fresh file read!
        
        # Extract the list array out of the master parent JSON wrapper object
        if isinstance(data, dict) and "questions" in data:
            self.questions = data["questions"]
        elif isinstance(data, list):
            self.questions = data
        else:
            self.questions = []
            
        # 🟢 NOWE: Tworzymy i zasilamy globalną pulę odpowiedzi!
        if not hasattr(self, 'global_answer_pool'):
            self.global_answer_pool = set()
            
        for q in self.questions:
            ans = q.get("correct_answer", {}).get("text", "")
            ans_str = str(ans).strip()
            # Zabezpieczenie: wrzucamy tylko rzeczywiste, niepuste stringi
            if ans_str:
                self.global_answer_pool.add(ans_str)
                
        self.current_question_index = 0
        self.session_correct = 0
        self.session_total = 0
        self.session_missed = []

    def get_current_question(self):
        if self.current_question_index < len(self.questions):
            return self.questions[self.current_question_index]
        return None
    
    def get_dynamic_options(self, current_q):
        correct_answer_text = current_q.get("correct_answer", {}).get("text", "")
        if not isinstance(correct_answer_text, str):
            correct_answer_text = str(correct_answer_text).strip()
        else:
            correct_answer_text = correct_answer_text.strip()

        # Zbieramy odpowiedzi z aktualnego, małego zestawu JSON
        all_answers_set = set()
        for q in self.questions:
            ans_text = q.get("correct_answer", {}).get("text", "")
            ans_str = str(ans_text).strip()
            # Zabezpieczenie przed "złymi" (pustymi) opcjami
            if ans_str: 
                all_answers_set.add(ans_str)
                
        # 🟢 NOWE: Zasilamy pulę błędnych odpowiedzi naszym zasobem globalnym
        if hasattr(self, 'global_answer_pool'):
            all_answers_set.update(self.global_answer_pool)

        # Zabezpieczenie 2: Upewniamy się, że poprawna odpowiedź nie wyląduje w "błędnych"
        if correct_answer_text in all_answers_set:
            all_answers_set.remove(correct_answer_text)

        all_answers_list = list(all_answers_set)
        
        # 🟢 Zabezpieczenie 3 (Fallback): Jeśli program nadal ma za mało odpowiedzi (np. załadowano tylko 1 pytanie i to od razu w trybie Hard Mode)
        while len(all_answers_list) < 3:
            all_answers_list.append(f"Zastępcza opcja {len(all_answers_list) + 1}")

        # Zawsze losujemy dokładnie 3 opcje
        wrong_options = random.sample(all_answers_list, 3)
        options = [correct_answer_text] + wrong_options
        
        random.shuffle(options)
        return options

    def get_all_qa_pairs(self):
        """Zwraca czystą listę słowników z pytaniami i odpowiedziami."""
        pairs = []
        for q_obj in getattr(self, 'questions', []): 
            # Wyciągamy pytanie 
            q_data = q_obj.get("question", "")
            q_text = q_data.get("text", "") if isinstance(q_data, dict) else str(q_data)
            
            # 🟢 POPRAWKA: Prawidłowy klucz to "correct_answer"
            ans_data = q_obj.get("correct_answer", "")
            ans_text = str(ans_data.get("text", "")) if isinstance(ans_data, dict) else str(ans_data)
            
            if not ans_text:
                ans_text = "Brak odpowiedzi"
            
            pairs.append({
                "question": q_text.strip(),
                "answer": ans_text.strip()
            })
        return pairs
    
    def check_handwritten_mistake(self, user_text, correct_text):
        evaluation = []
        u_len = len(user_text)
        c_len = len(correct_text)
        for i in range(max(u_len, c_len)):
            if i < u_len and i < c_len:
                if user_text[i] == correct_text[i]:
                    evaluation.append((user_text[i], True))
                else:
                    evaluation.append((user_text[i], False))
            elif i < u_len:
                evaluation.append((user_text[i], False))
            else:
                evaluation.append(("_", False))
        return evaluation

    def shuffle_and_restart(self):
        import random
        self.reset_quiz()
        # Mix up the order of the questions list if it's not empty
        if self.questions:
            random.shuffle(self.questions)

    def advance_question(self):
        # Safely increment our tracker position
        self.current_question_index += 1
        # Check if we are still within the boundaries of the list pool
        if self.current_question_index < len(self.questions):
            return True
        return False

    def open_quiz_builder(self, app_root):
        builder_window = ctk.CTkToplevel(app_root)
        builder_window.title("Quiz Builder Workspace")
        builder_window.geometry("750x780")
        QuizBuilderApp(builder_window)
        
        # 🟢 NOWE: Wiąże okno z główną aplikacją, wymuszając je ZAWSZE na wierzchu
        builder_window.transient(app_root)
        
        # 🟢 NOWE: Przenosi kursor i pełną uwagę systemu na to okno
        builder_window.focus_force()

    def log_question_failure(self, current_q, mode_str, base_bank_file):
        import os, json
        suffix = self.get_mode_suffix(mode_str)        
        # 🟢 NOWE: Wyciągamy nazwę bazową quizu, żeby plik Hard Mode był unikalny dla niego
        base_name = os.path.basename(base_bank_file).replace(".json", "") if base_bank_file else "unknown"
        path = f"special_quizzes/hard_mode_{suffix}_{base_name}.json"
        stats_path = "special_quizzes/stats_tracker.json"
        
        q_data = current_q.get("question", "")
        q_text = q_data.get("text", "") if isinstance(q_data, dict) else q_data
        if q_text not in self.session_missed:
            self.session_missed.append(q_text)

        q_id = str(current_q.get("id", ""))
        
        if q_id:
            # Używamy base_name także w identyfikatorze powtórzeń, by uniknąć pomyłek
            mode_key = f"{q_id}_{suffix}_{base_name}"
            if os.path.exists(stats_path) and os.path.getsize(stats_path) > 0:
                try:
                    with open(stats_path, 'r', encoding='utf-8') as f:
                        stats = json.load(f)
                    stats[mode_key] = 0 
                    with open(stats_path, 'w', encoding='utf-8') as f:
                        json.dump(stats, f, indent=4)
                except Exception as e:
                    print(f"Error resetting stats: {e}")
            
        existing_questions = []
        if os.path.exists(path) and os.path.getsize(path) > 0:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                    existing_questions = existing_data.get("questions", [])
            except:
                existing_questions = []
                
        if not any(str(q.get("id")) == q_id for q in existing_questions):
            existing_questions.append(current_q)
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump({"questions": existing_questions}, f, indent=4, ensure_ascii=False)
            except Exception as e:
                print(f"Error saving failure log: {e}")

    def log_question_success(self, current_q, mode_str, currently_loaded_path, base_bank_file):
        import os, json
        q_id = str(current_q.get("id", ""))
        if not q_id:
            return
            
        suffix = self.get_mode_suffix(mode_str)
        # 🟢 NOWE: Unikalne nazwy dla Redemption Mode
        base_name = os.path.basename(base_bank_file).replace(".json", "") if base_bank_file else "unknown"
        
        stats_path = "special_quizzes/stats_tracker.json"
        hard_mode_path = f"special_quizzes/hard_mode_{suffix}_{base_name}.json"
        redemption_path = f"special_quizzes/redemption_mode_{suffix}_{base_name}.json"
        
        stats = {}
        if os.path.exists(stats_path) and os.path.getsize(stats_path) > 0:
            try:
                with open(stats_path, 'r', encoding='utf-8') as f:
                    stats = json.load(f)
            except:
                stats = {}
                
        mode_key = f"{q_id}_{suffix}_{base_name}"
        stats[mode_key] = stats.get(mode_key, 0) + 1
        
        try:
            with open(stats_path, 'w', encoding='utf-8') as f:
                json.dump(stats, f, indent=4)
        except:
            pass
            
        if stats[mode_key] >= 10 and currently_loaded_path and "hard_mode_" in currently_loaded_path:
            redemp_questions = []
            if os.path.exists(redemption_path) and os.path.getsize(redemption_path) > 0:
                try:
                    with open(redemption_path, 'r', encoding='utf-8') as f:
                        redemp_questions = json.load(f).get("questions", [])
                except:
                    redemp_questions = []
            if not any(str(q.get("id")) == q_id for q in redemp_questions):
                redemp_questions.append(current_q)
                try:
                    with open(redemption_path, 'w', encoding='utf-8') as f:
                        json.dump({"questions": redemp_questions}, f, indent=4, ensure_ascii=False)
                except: pass
                    
            if os.path.exists(hard_mode_path) and os.path.getsize(hard_mode_path) > 0:
                try:
                    with open(hard_mode_path, 'r', encoding='utf-8') as f:
                        hm_questions = json.load(f).get("questions", [])
                    hm_questions = [q for q in hm_questions if str(q.get("id")) != q_id]
                    with open(hard_mode_path, 'w', encoding='utf-8') as f:
                        json.dump({"questions": hm_questions}, f, indent=4, ensure_ascii=False)
                except:
                    pass

    def log_run_score(self, mode_str, file_path, correct, total):
        if total == 0:
            return
            
        import os, json
        
        bank_name = os.path.basename(file_path) if file_path else "Unknown"
        # 🟢 Rozszerzenie o obsługę Redemption, Hard oraz Self Made
        if "hard_mode" in bank_name:
            category = "hard"
        elif "redemption_mode" in bank_name:
            category = "redemption"
        elif "self_made" in bank_name:
            category = "self_made"
        else:
            category = "regular"
            
        gen_path = "special_quizzes/scores_general.json"
        gen_data = {"overall_correct": 0, "overall_total": 0}
        if os.path.exists(gen_path) and os.path.getsize(gen_path) > 0:
            try:
                with open(gen_path, 'r', encoding='utf-8') as f:
                    gen_data = json.load(f)
            except:
                pass
                
        gen_data["overall_correct"] += correct
        gen_data["overall_total"] += total
        
        with open(gen_path, 'w', encoding='utf-8') as f:
            json.dump(gen_data, f, indent=4)
            
        cat_path = f"special_quizzes/scores_{category}.json"
        cat_data = {"Multiple Choice": {}, "Handwritten Input": {}}
        if os.path.exists(cat_path) and os.path.getsize(cat_path) > 0:
            try:
                with open(cat_path, 'r', encoding='utf-8') as f:
                    cat_data = json.load(f)
            except:
                pass
                
        if mode_str not in cat_data:
            cat_data[mode_str] = {}
        if bank_name not in cat_data[mode_str]:
            cat_data[mode_str][bank_name] = []
            
        cat_data[mode_str][bank_name].append({"correct": correct, "total": total})
        
        with open(cat_path, 'w', encoding='utf-8') as f:
            json.dump(cat_data, f, indent=4)
            
    def get_general_score(self):
        import os, json
        gen_path = "special_quizzes/scores_general.json"
        if os.path.exists(gen_path) and os.path.getsize(gen_path) > 0:
            try:
                with open(gen_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except: pass
        return {"overall_correct": 0, "overall_total": 0}
        
    def get_category_history(self, category):
        import os, json
        cat_path = f"special_quizzes/scores_{category}.json"
        if os.path.exists(cat_path) and os.path.getsize(cat_path) > 0:
            try:
                with open(cat_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except: pass
        return {"Multiple Choice": {}, "Handwritten Input": {}, "Fill the Gaps": {}}

    def get_self_made_path(self, mode_str, base_bank_file):
        import os
        base_name = os.path.basename(base_bank_file).replace(".json", "") if base_bank_file else "unknown"
        suffix = self.get_mode_suffix(mode_str)
        return f"special_quizzes/self_made_{suffix}_{base_name}.json"

    def toggle_self_made(self, current_q, mode_str, base_bank_file, is_checked):
        import os, json
        if not current_q or not current_q.get("id"): return
        path = self.get_self_made_path(mode_str, base_bank_file)
        
        existing_questions = []
        if os.path.exists(path) and os.path.getsize(path) > 0:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    existing_questions = json.load(f).get("questions", [])
            except: pass
                
        q_id = str(current_q.get("id"))
        is_present = any(str(q.get("id")) == q_id for q in existing_questions)
        
        if is_checked and not is_present:
            existing_questions.append(current_q)
        elif not is_checked and is_present:
            existing_questions = [q for q in existing_questions if str(q.get("id")) != q_id]
            
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump({"questions": existing_questions}, f, indent=4, ensure_ascii=False)
        except: pass

    def check_if_self_made(self, current_q, mode_str, base_bank_file):
        import os, json
        if not current_q or not current_q.get("id"): return False
        path = self.get_self_made_path(mode_str, base_bank_file)
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            return False
        try:
            with open(path, 'r', encoding='utf-8') as f:
                existing = json.load(f).get("questions", [])
            return any(str(q.get("id")) == str(current_q.get("id")) for q in existing)
        except: return False

    # Podmień definicję tej metody na poniższą:
    def remove_self_made_questions(self, mode_str, base_bank_file, ids_to_remove, custom_path=None):
        import os, json
        # Używamy ścieżki domyślnej, chyba że podano niestandardową
        path = custom_path if custom_path else self.get_self_made_path(mode_str, base_bank_file)
        if not os.path.exists(path) or os.path.getsize(path) == 0: return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                existing = json.load(f).get("questions", [])
            existing = [q for q in existing if str(q.get("id")) not in ids_to_remove]
            with open(path, 'w', encoding='utf-8') as f:
                json.dump({"questions": existing}, f, indent=4, ensure_ascii=False)
        except: pass
    def save_custom_playlist(self, playlist_name, base_bank_file, mode_str, selected_questions):
        import os, json
        base_name = os.path.basename(base_bank_file).replace(".json", "") if base_bank_file else "unknown"
        suffix = self.get_mode_suffix(mode_str)
        
        # Filtrujemy nazwę z niedozwolonych znaków dla plików
        safe_name = "".join([c for c in playlist_name if c.isalnum() or c in " _-"]).strip()
        path = f"special_quizzes/custom_playlists/{safe_name}_{suffix}_{base_name}.json"
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump({"questions": selected_questions}, f, indent=4, ensure_ascii=False)
            return True
        except:
            return False
            
    def get_custom_playlists(self, mode_str, base_bank_file):
        import os
        base_name = os.path.basename(base_bank_file).replace(".json", "") if base_bank_file else "unknown"
        suffix = self.get_mode_suffix(mode_str)
        folder = "special_quizzes/custom_playlists"
        if not os.path.exists(folder): return []
        
        suffix_search = f"_{suffix}_{base_name}.json"
        playlists = []
        for f in os.listdir(folder):
            if f.endswith(suffix_search):
                p_name = f.replace(suffix_search, "")
                playlists.append((p_name, os.path.join(folder, f)))
        return playlists
    
    def delete_custom_playlist(self, path):
        import os
        if os.path.exists(path):
            try: os.remove(path)
            except: pass

    # ==========================================
    # SAVE & RESUME STATE LOGIC
    # ==========================================
    def save_current_state(self, mode_str, file_path, typed_text=""):
        import os, json
        # Nie zapisujemy, jeśli quiz się skończył lub w ogóle nie wystartował
        if not hasattr(self, 'questions') or not self.questions or self.current_question_index >= len(self.questions):
            self.clear_saved_state()
            return
            
        save_data = {
            "mode": mode_str,
            "file_path": file_path,
            "questions": self.questions,
            "current_index": self.current_question_index,
            "session_correct": self.session_correct,
            "session_total": self.session_total,
            "session_missed": self.session_missed,
            "typed_text": typed_text
        }
        try:
            with open("special_quizzes/save_state.json", 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=4, ensure_ascii=False)
        except: pass

    def load_saved_state(self):
        import os, json
        path = "special_quizzes/save_state.json"
        if not os.path.exists(path): return None
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: return None
        
    def clear_saved_state(self):
        import os
        path = "special_quizzes/save_state.json"
        if os.path.exists(path):
            try: os.remove(path)
            except: pass

    def get_mode_suffix(self, mode_str):
        if mode_str == "Multiple Choice": return "mc"
        elif mode_str == "Handwritten Input": return "written"
        else: return "gaps"

    def generate_gapped_text(self, text, ratio=0.7, min_len=4):
        import re, random
        # Wyciąga słowa bez znaków interpunkcyjnych
        words = re.findall(r'\b\w+\b', text)
        valid_words = list(set([w for w in words if len(w) >= min_len]))
        
        num_to_remove = int(len(valid_words) * ratio)
        if num_to_remove == 0 and valid_words: num_to_remove = 1
        words_to_remove = random.sample(valid_words, min(num_to_remove, len(valid_words)))
        
        gapped_text = text
        for w in words_to_remove:
            # Podmienia całe słowa na odpowiednią liczbę podłóg
            gapped_text = re.sub(rf'\b{w}\b', '_' * len(w), gapped_text)
        return gapped_text

    def check_word_mistake(self, user_text, correct_text):
        import difflib
        u_words = user_text.split()
        c_words = correct_text.split()
        matcher = difflib.SequenceMatcher(None, u_words, c_words)
        analysis = []
        # Analizuje różnice wyraz po wyrazie dla trybu Fill the Gaps
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                for w in c_words[j1:j2]:
                    analysis.append((w + " ", True))
            elif tag in ('replace', 'insert'):
                for w in c_words[j1:j2]:
                    analysis.append((w + " ", False))
        return analysis