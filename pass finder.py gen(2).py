import tkinter as tk
from tkinter import ttk, scrolledtext
import itertools
from difflib import SequenceMatcher

class MintPasswordRecovery:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Recovery Helper")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Linux Mint color scheme
        self.colors = {
            'bg': '#f5f5f5',
            'sidebar': '#e8e8e8',
            'header': '#9ab87a',
            'header_text': '#ffffff',
            'entry_bg': '#ffffff',
            'text': '#2e3436',
            'button': '#9ab87a',
            'button_hover': '#7d9a5f',
            'border': '#d3d3d3'
        }
        
        self.root.configure(bg=self.colors['bg'])
        self.setup_ui()
        
    def setup_ui(self):
        # Header bar
        header = tk.Frame(self.root, bg=self.colors['header'], height=50)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)
        
        title_label = tk.Label(
            header,
            text="🔐 Password Recovery Helper",
            bg=self.colors['header'],
            fg=self.colors['header_text'],
            font=('Ubuntu', 16, 'bold'),
            anchor='w'
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Main container
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Input section
        left_panel = tk.Frame(main_container, bg=self.colors['sidebar'], relief=tk.FLAT, bd=1)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 5), pady=0, expand=False)
        left_panel.configure(width=350)
        
        # Input fields
        self.create_input_section(left_panel)
        
        # Right panel - Results section
        right_panel = tk.Frame(main_container, bg=self.colors['bg'])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.create_results_section(right_panel)
        
    def create_input_section(self, parent):
        # Title
        title = tk.Label(
            parent,
            text="Account Information",
            bg=self.colors['sidebar'],
            fg=self.colors['text'],
            font=('Ubuntu', 12, 'bold'),
            anchor='w'
        )
        title.pack(fill=tk.X, padx=15, pady=(15, 10))
        
        # Account type
        self.create_field(parent, "Account Type:", "account_type")
        
        # Username
        self.create_field(parent, "Username/Email:", "username")
        
        # Separator
        sep = tk.Frame(parent, bg=self.colors['border'], height=1)
        sep.pack(fill=tk.X, padx=15, pady=15)
        
        # Password hints title
        hints_title = tk.Label(
            parent,
            text="Password Hints",
            bg=self.colors['sidebar'],
            fg=self.colors['text'],
            font=('Ubuntu', 12, 'bold'),
            anchor='w'
        )
        hints_title.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        # Hint fields
        self.create_field(parent, "Main Related Word:", "related_word")
        self.create_field(parent, "Pet Name:", "pet_name")
        self.create_field(parent, "Birth Year:", "birth_year")
        self.create_field(parent, "Favorite Thing:", "favorite")
        self.create_field(parent, "Memorable Place:", "place")
        
        # Generate button
        btn_frame = tk.Frame(parent, bg=self.colors['sidebar'])
        btn_frame.pack(fill=tk.X, padx=15, pady=20)
        
        self.generate_btn = tk.Button(
            btn_frame,
            text="Generate Passwords",
            bg=self.colors['button'],
            fg=self.colors['header_text'],
            font=('Ubuntu', 11, 'bold'),
            relief=tk.FLAT,
            cursor='hand2',
            command=self.generate_passwords,
            activebackground=self.colors['button_hover'],
            activeforeground=self.colors['header_text'],
            bd=0,
            padx=20,
            pady=10
        )
        self.generate_btn.pack(fill=tk.X)
        
        # Bind hover effects
        self.generate_btn.bind('<Enter>', lambda e: self.generate_btn.config(bg=self.colors['button_hover']))
        self.generate_btn.bind('<Leave>', lambda e: self.generate_btn.config(bg=self.colors['button']))
        
    def create_field(self, parent, label_text, field_name):
        frame = tk.Frame(parent, bg=self.colors['sidebar'])
        frame.pack(fill=tk.X, padx=15, pady=5)
        
        label = tk.Label(
            frame,
            text=label_text,
            bg=self.colors['sidebar'],
            fg=self.colors['text'],
            font=('Ubuntu', 10),
            anchor='w'
        )
        label.pack(fill=tk.X, pady=(0, 3))
        
        entry = tk.Entry(
            frame,
            bg=self.colors['entry_bg'],
            fg=self.colors['text'],
            font=('Ubuntu', 10),
            relief=tk.SOLID,
            bd=1,
            highlightthickness=1,
            highlightbackground=self.colors['border'],
            highlightcolor=self.colors['button']
        )
        entry.pack(fill=tk.X, ipady=5)
        
        setattr(self, f'{field_name}_entry', entry)
        
    def create_results_section(self, parent):
        # Results title
        results_header = tk.Frame(parent, bg=self.colors['bg'])
        results_header.pack(fill=tk.X, pady=(0, 10))
        
        results_label = tk.Label(
            results_header,
            text="Generated Password Candidates",
            bg=self.colors['bg'],
            fg=self.colors['text'],
            font=('Ubuntu', 12, 'bold'),
            anchor='w'
        )
        results_label.pack(side=tk.LEFT)
        
        self.count_label = tk.Label(
            results_header,
            text="",
            bg=self.colors['bg'],
            fg=self.colors['button'],
            font=('Ubuntu', 10, 'bold'),
            anchor='e'
        )
        self.count_label.pack(side=tk.RIGHT)
        
        # Results text area
        text_frame = tk.Frame(parent, bg=self.colors['entry_bg'], relief=tk.SOLID, bd=1)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.results_text = scrolledtext.ScrolledText(
            text_frame,
            bg=self.colors['entry_bg'],
            fg=self.colors['text'],
            font=('Ubuntu Mono', 10),
            relief=tk.FLAT,
            wrap=tk.WORD,
            padx=10,
            pady=10,
            state=tk.DISABLED
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Footer with tips
        footer = tk.Frame(parent, bg=self.colors['sidebar'], relief=tk.SOLID, bd=1)
        footer.pack(fill=tk.X, pady=(10, 0))
        
        tips_label = tk.Label(
            footer,
            text="💡 Tips: Try variations with capitalizations, special characters (!,@,#), and numbers (123, years)",
            bg=self.colors['sidebar'],
            fg=self.colors['text'],
            font=('Ubuntu', 9),
            wraplength=500,
            justify=tk.LEFT,
            anchor='w'
        )
        tips_label.pack(fill=tk.X, padx=10, pady=10)
        
    def get_similarity(self, a, b):
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()
    
    def generate_variations(self, base_word, include_numbers=True, include_special=True):
        if not base_word:
            return []
            
        variations = []
        variations.extend([base_word, base_word.lower(), base_word.upper(), base_word.capitalize()])
        
        if include_numbers:
            substitutions = {
                'a': ['@', '4'], 'e': ['3'], 'i': ['1', '!'],
                'o': ['0'], 's': ['5', '$'], 't': ['7'], 'l': ['1']
            }
            
            temp = base_word.lower()
            for char, subs in substitutions.items():
                for sub in subs:
                    variations.append(temp.replace(char, sub))
            
            for num in ['123', '1', '12', '2024', '2025', '!', '!!', '123!']:
                variations.append(base_word + num)
                variations.append(base_word.lower() + num)
                variations.append(base_word.capitalize() + num)
        
        if include_special:
            for char in ['!', '@', '#', '$']:
                variations.append(base_word + char)
                variations.append(char + base_word)
        
        return list(set(variations))
    
    def generate_passwords(self):
        # Get values
        related_word = self.related_word_entry.get().strip()
        pet_name = self.pet_name_entry.get().strip()
        birth_year = self.birth_year_entry.get().strip()
        favorite = self.favorite_entry.get().strip()
        place = self.place_entry.get().strip()
        
        if not related_word:
            self.display_results("⚠️ Please enter at least a 'Main Related Word' to generate passwords.\n")
            return
        
        hints = [h for h in [related_word, pet_name, favorite, place] if h]
        all_candidates = []
        
        # Generate variations
        for hint in hints:
            variations = self.generate_variations(hint)
            all_candidates.extend(variations)
            
            if birth_year:
                for var in variations[:10]:
                    all_candidates.append(var + birth_year)
                    all_candidates.append(birth_year + var)
        
        # Combine hints
        if len(hints) >= 2:
            for combo in itertools.combinations(hints[:3], 2):
                combined = ''.join(combo)
                all_candidates.extend(self.generate_variations(combined, False, False)[:5])
        
        # Remove duplicates and sort
        all_candidates = list(set(all_candidates))
        all_candidates.sort(key=lambda x: self.get_similarity(x, related_word), reverse=True)
        
        # Display results
        self.display_results_list(all_candidates)
        
    def display_results(self, text):
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, text)
        self.results_text.config(state=tk.DISABLED)
        
    def display_results_list(self, candidates):
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        
        self.count_label.config(text=f"{len(candidates)} candidates")
        
        output = "Top 50 Most Likely Passwords:\n"
        output += "=" * 50 + "\n\n"
        
        for i, candidate in enumerate(candidates[:50], 1):
            output += f"{i:2d}. {candidate}\n"
        
        if len(candidates) > 50:
            output += f"\n... and {len(candidates) - 50} more candidates\n"
        
        output += "\n" + "=" * 50 + "\n"
        output += "\n⚠️  SECURITY REMINDER:\n"
        output += "• Only use this for YOUR OWN accounts\n"
        output += "• Consider using a password manager\n"
        output += "• Enable two-factor authentication\n"
        
        self.results_text.insert(tk.END, output)
        self.results_text.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = MintPasswordRecovery(root)
    root.mainloop()
