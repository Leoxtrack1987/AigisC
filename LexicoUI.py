from tkinter import scrolledtext
from Lexico import Lexico
import tkinter as tk

class LexicalAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Analizador Léxico")
        self.root.geometry("1200x600")
        
        # Instancia del analizador léxico
        self.lexico = Lexico()

        # Frame superior para editor y tabla en columnas
        top_frame = tk.Frame(root)
        top_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        left_frame = tk.Frame(top_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        left_frame.columnconfigure(0, weight=7)
        
        tk.Label(left_frame, text="Editor de Código:").pack()
        self.code_editor = scrolledtext.ScrolledText(left_frame, height=15)
        self.code_editor.pack(fill=tk.BOTH, expand=True)

       
        right_frame = tk.Frame(top_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        right_frame.columnconfigure(0, weight=3)
        
        tk.Label(right_frame, text="Tabla de Símbolos:").pack()
        self.symbol_display = scrolledtext.ScrolledText(right_frame, height=15)
        self.symbol_display.pack(fill=tk.BOTH, expand=True)


        self.compile_btn = tk.Button(root, text="Compilar", command=self.compile_code, background="#32b4f0", font=('Arial', 10, 'bold'),)
        self.compile_btn.pack(padx=20, pady=20)
        

        # Área de errores
        tk.Label(root, text="Errores Léxicos:").pack()
        self.error_display = scrolledtext.ScrolledText(root, height=7, fg="red")
        self.error_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def compile_code(self):
        code = self.code_editor.get("1.0", tk.END)
        
        # Tokenizar usando la clase Lexico
        tokens = self.lexico.tokenize(code)
        
        # Separar errores
        errors = []
        symbol_table = []
        
        for token in tokens:
            if not token.valido:
                errors.append(f"Error léxico: '{token.valor}' en línea {token.linea}, columna {token.columna}")
            symbol_table.append((token.linea, token.valor, token.tipo))

        # Mostrar errores
        self.error_display.delete("1.0", tk.END)
        if errors:
            self.error_display.insert(tk.END, "\n".join(errors))
        else:
            self.error_display.insert(tk.END, "No se encontraron errores léxicos.")

        # Mostrar tabla de símbolos
        self.symbol_display.delete("1.0", tk.END)
        self.symbol_display.insert(tk.END, f"{'No Línea':<10}{'Token':<20}{'Descripción'}\n")
        self.symbol_display.insert(tk.END, "-"*50 + "\n")
        for line, token, desc in symbol_table:
            self.symbol_display.insert(tk.END, f"{line:<10}{token:<20}{desc}\n")