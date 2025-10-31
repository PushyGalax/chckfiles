######################################################################
##                   Michel Bermond, 19/09/2025                     ##
##                       APST2607 reserved                          ##
######################################################################

######################################################################
##                          MODULE main.py                          ##
##                            Description                           ##
##        this program compare  a archive with a reference          ##
##          files and report any missing or extra files.            ##
######################################################################

#### import
import os
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, ttk, simpledialog
import json
import datetime
import hashlib


#### GUI Class
class ArchiveComparerGUI:
    def __init__(self, root):
        """
        Initialize the GUI for the Archive Comparer application.
        """
        self.root = root
        self.root.title("Comparateur d'Archives - APST2607")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        # Configure modern styling
        self.setup_styles()
        
        # Set modern color scheme
        self.colors = {
            'primary': '#2E86AB',      # Professional blue
            'secondary': '#A23B72',    # Accent purple
            'success': '#F18F01',      # Orange for success
            'danger': '#C73E1D',       # Red for errors
            'background': '#F5F7FA',   # Light gray background
            'surface': '#FFFFFF',      # White surface
            'text_primary': '#2D3748', # Dark gray text
            'text_secondary': '#718096', # Light gray text
            'border': '#E2E8F0'        # Light border
        }
        
        # Configure root window
        self.root.configure(bg=self.colors['background'])
        
        # Current comparison result
        self.current_report = None
        
        # Large console window reference
        self.large_console_window = None
        self.large_console_text = None
        
        # Setup the beautiful GUI
        self.setup_gui()
    
    def setup_styles(self):
        """
        Configure modern ttk styles for the application.
        """
        style = ttk.Style()
        
        # Configure modern button style
        style.configure('Modern.TButton',
                       padding=(20, 10),
                       font=('Segoe UI', 9, 'bold'))
        
        # Configure special compare button style with visible colors
        style.configure('Compare.TButton',
                       padding=(20, 10),
                       font=('Segoe UI', 9, 'bold'),
                       relief='raised',
                       borderwidth=2)
        
        # Map states for compare button to ensure visibility
        style.map('Compare.TButton',
                 relief=[('pressed', 'sunken')],
                 borderwidth=[('pressed', 2)])
        
        # Try alternative approach - configure with theme colors
        try:
            style.theme_use('clam')  # Use clam theme for better color support
        except:
            pass  # If clam theme not available, continue with default
        
        # Configure entry style
        style.configure('Modern.TEntry',
                       padding=(10, 8),
                       font=('Segoe UI', 9))
        
        # Configure label style
        style.configure('Title.TLabel',
                       font=('Segoe UI', 12, 'bold'),
                       foreground='#2D3748')
        
        style.configure('Subtitle.TLabel',
                       font=('Segoe UI', 10),
                       foreground='#4A5568')
        
        style.configure('Header.TLabel',
                       font=('Segoe UI', 14, 'bold'),
                       foreground='#1A202C')
        
        # Configure frame styles
        style.configure('Card.TFrame',
                       relief='flat',
                       borderwidth=1)
        
        style.configure('Header.TFrame',
                       relief='flat',
                       borderwidth=0)
    
    def setup_gui(self):
        """
        Create and arrange all beautiful GUI components.
        """
        # Main container with padding
        main_container = ttk.Frame(self.root, style='Header.TFrame', padding="20")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(3, weight=1)
        
        # Header Section
        self.create_header(main_container)
        
        # Input Section
        self.create_input_section(main_container)
        
        # Action Buttons Section
        self.create_action_section(main_container)
        
        # Results Console Section
        self.create_console_section(main_container)
        
        # Status Bar
        self.create_status_bar(main_container)
        
    def create_action_section(self, parent):
        """
        Create a beautiful action buttons section.
        """
        action_frame = ttk.LabelFrame(parent, text=" ⚡ Actions ", 
                                    padding="20", style='Card.TFrame')
        action_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Create the primary compare button with custom styling
        compare_btn = tk.Button(
            action_frame,
            text="🔍 Comparer les Archives",
            command=self.compare_archives_gui,
            font=('Segoe UI', 9, 'bold'),
            bg='#2E86AB',          # Blue background
            fg='white',            # White text
            activebackground='#1E5B7A',  # Darker blue when pressed
            activeforeground='white',     # White text when pressed
            relief='flat',
            borderwidth=0,
            padx=20,
            pady=10,
            cursor='hand2'
        )
        compare_btn.grid(row=0, column=0, padx=10, pady=5, sticky=(tk.W, tk.E))
        
        # Create other buttons with ttk
        other_buttons = [
            ("📤 Exporter Résultat", self.export_result, 0, 1),
            ("📥 Importer Résultat", self.import_result, 0, 2),
            ("🗑️ Vider Console", self.clear_console, 0, 3),
            ("🖥️ Grande Console", self.open_large_console, 1, 0),
            ("🔍 Détecter Doublons", self.detect_duplicates, 1, 1)
        ]
        
        for text, command, row, col in other_buttons:
            btn = ttk.Button(action_frame, text=text, command=command, style='Modern.TButton')
            btn.grid(row=row, column=col, padx=10, pady=5, sticky=(tk.W, tk.E))
        
        # Configure column weights for equal distribution
        for i in range(4):
            action_frame.columnconfigure(i, weight=1)
    
    def create_console_section(self, parent):
        """
        Create a beautiful console section.
        """
        console_frame = ttk.LabelFrame(parent, text=" 📊 Results Console ", 
                                     padding="15", style='Card.TFrame')
        console_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        console_frame.columnconfigure(0, weight=1)
        console_frame.rowconfigure(0, weight=1)
        
        # Create console with custom styling
        self.console = scrolledtext.ScrolledText(
            console_frame, 
            wrap=tk.WORD, 
            height=25, 
            width=90,
            font=('Consolas', 9),
            bg='#1E1E1E',           # Dark background
            fg='#FFFFFF',           # White text
            insertbackground='#FFFFFF',  # White cursor
            selectbackground='#264F78',  # Selection color
            relief='flat',
            borderwidth=1
        )
        self.console.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure text tags for colored output
        self.console.tag_configure('timestamp', foreground='#569CD6')  # Blue for timestamps
        self.console.tag_configure('success', foreground='#4EC9B0')    # Green for success
        self.console.tag_configure('error', foreground='#F44747')      # Red for errors
        self.console.tag_configure('warning', foreground='#FFCC02')    # Yellow for warnings
        self.console.tag_configure('info', foreground='#9CDCFE')       # Light blue for info
        self.console.tag_configure('missing', foreground='#F48771')    # Light red for missing
        self.console.tag_configure('extra', foreground='#B5CEA8')      # Light green for extra
        self.console.tag_configure('modified', foreground='#DCDCAA')   # Light yellow for modified
    
    def create_status_bar(self, parent):
        """
        Create a beautiful status bar.
        """
        status_frame = ttk.Frame(parent, style='Header.TFrame')
        status_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(15, 0))
        status_frame.columnconfigure(1, weight=1)
        
        # Status icon
        self.status_icon = ttk.Label(status_frame, text="✅", font=('Segoe UI', 10))
        self.status_icon.grid(row=0, column=0, padx=(0, 10))
        
        # Status text
        self.status_var = tk.StringVar()
        self.status_var.set("Ready to compare archives")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, 
                               style='Subtitle.TLabel')
        status_label.grid(row=0, column=1, sticky=tk.W)
        
        # Version info
        version_label = ttk.Label(status_frame, text="v2.0", 
                                style='Subtitle.TLabel')
        version_label.grid(row=0, column=2, sticky=tk.E)
        
        # Progress bar (initially hidden)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            status_frame,
            variable=self.progress_var,
            mode='determinate',
            length=200,
            style='Modern.Horizontal.TProgressbar'
        )
        # Initially hide the progress bar
        self.progress_bar.grid_remove()
        
        # Initialize with welcome message
        self.log_message("✨ Welcome to Archive Comparer v2.0!")
        self.log_message("🎯 Professional Archive Integrity Verification Tool")
        self.log_message("📋 Select your directories and click 'Compare Archives' to begin")
        self.update_status("Ready to compare archives", "✅")

    def show_progress_bar(self, maximum_value=100):
        """
        Afficher la barre de progression.
        """
        self.progress_var.set(0)
        self.progress_bar.configure(maximum=maximum_value)
        self.progress_bar.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0))
        self.root.update_idletasks()
    
    def update_progress_bar(self, value):
        """
        Mettre à jour la barre de progression.
        """
        self.progress_var.set(value)
        self.root.update_idletasks()
    
    def hide_progress_bar(self):
        """
        Cacher la barre de progression.
        """
        self.progress_bar.grid_remove()
        self.root.update_idletasks()
    
    def create_header(self, parent):
        """
        Create a beautiful header section.
        """
        header_frame = ttk.Frame(parent, style='Header.TFrame')
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        header_frame.columnconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(header_frame, text="🗂️ Comparateur d'Archives", style='Header.TLabel')
        title_label.grid(row=0, column=0, pady=(0, 5))
        
        # Subtitle
        subtitle_label = ttk.Label(header_frame, 
                                 text="Outil Professionnel de Vérification d'Intégrité d'Archives - APST2607",
                                 style='Subtitle.TLabel')
        subtitle_label.grid(row=1, column=0, pady=(0, 5))
        
        # Developer info
        dev_label = ttk.Label(header_frame,
                             text="Développé par Michel Bermond - Association Prévention Santé au Travail 2607",
                             font=('Segoe UI', 8),
                             foreground='#718096')
        dev_label.grid(row=2, column=0, pady=(0, 10))
        
        # Separator
        separator = ttk.Separator(header_frame, orient='horizontal')
        separator.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def create_input_section(self, parent):
        """
        Create a beautiful input section with cards.
        """
        input_frame = ttk.LabelFrame(parent, text=" 📁 Sélection des Répertoires ", 
                                   padding="20", style='Card.TFrame')
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        input_frame.columnconfigure(1, weight=1)
        
        # Reference Path
        ref_icon = ttk.Label(input_frame, text="📚", font=('Segoe UI', 12))
        ref_icon.grid(row=0, column=0, padx=(0, 10), pady=8, sticky=tk.W)
        
        ttk.Label(input_frame, text="Répertoire de Référence:", style='Title.TLabel').grid(
            row=0, column=1, sticky=tk.W, pady=8)
        
        self.ref_path_var = tk.StringVar()
        ref_frame = ttk.Frame(input_frame)
        ref_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        ref_frame.columnconfigure(0, weight=1)
        
        self.ref_path_entry = ttk.Entry(ref_frame, textvariable=self.ref_path_var, 
                                      style='Modern.TEntry', width=60)
        self.ref_path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ref_browse_btn = ttk.Button(ref_frame, text="📂 Parcourir", 
                                  command=self.browse_ref_path, style='Modern.TButton')
        ref_browse_btn.grid(row=0, column=1)
        
        # Extracted Path
        ext_icon = ttk.Label(input_frame, text="📦", font=('Segoe UI', 12))
        ext_icon.grid(row=2, column=0, padx=(0, 10), pady=8, sticky=tk.W)
        
        ttk.Label(input_frame, text="Répertoire Extrait:", style='Title.TLabel').grid(
            row=2, column=1, sticky=tk.W, pady=8)
        
        self.extract_path_var = tk.StringVar()
        ext_frame = ttk.Frame(input_frame)
        ext_frame.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        ext_frame.columnconfigure(0, weight=1)
        
        self.extract_path_entry = ttk.Entry(ext_frame, textvariable=self.extract_path_var, 
                                          style='Modern.TEntry', width=60)
        self.extract_path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ext_browse_btn = ttk.Button(ext_frame, text="📂 Parcourir", 
                                  command=self.browse_extract_path, style='Modern.TButton')
        ext_browse_btn.grid(row=0, column=1)
        
        # Output File
        out_icon = ttk.Label(input_frame, text="💾", font=('Segoe UI', 12))
        out_icon.grid(row=4, column=0, padx=(0, 10), pady=8, sticky=tk.W)
        
        ttk.Label(input_frame, text="Exporter le Rapport vers:", style='Title.TLabel').grid(
            row=4, column=1, sticky=tk.W, pady=8)
        
        self.output_file_var = tk.StringVar()
        out_frame = ttk.Frame(input_frame)
        out_frame.grid(row=5, column=1, columnspan=2, sticky=(tk.W, tk.E))
        out_frame.columnconfigure(0, weight=1)
        
        self.output_file_entry = ttk.Entry(out_frame, textvariable=self.output_file_var, 
                                         style='Modern.TEntry', width=60)
        self.output_file_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        out_browse_btn = ttk.Button(out_frame, text="💾 Enregistrer sous", 
                                  command=self.browse_output_file, style='Modern.TButton')
        out_browse_btn.grid(row=0, column=1)
    
    def log_message(self, message, tag=None):
        """
        Add a beautifully formatted message to both consoles with timestamp and colors.
        """
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Format the complete message
        full_message = f"[{timestamp}] {message}"
        
        # Determine message type and color (with French translations)
        if ("✨" in message or "✅" in message or 
            "successfully" in message.lower() or "success" in message.lower() or
            "réussi" in message.lower() or "parfaitement" in message.lower() or
            "terminé avec succès" in message.lower() or "aucun doublon" in message.lower()):
            tag = 'success'
        elif ("❌" in message or 
              "error" in message.lower() or "failed" in message.lower() or
              "erreur" in message.lower() or "échec" in message.lower()):
            tag = 'error'
        elif ("⚠️" in message or 
              "warning" in message.lower() or "attention" in message.lower() or
              "impossible" in message.lower() or "interrompue" in message.lower()):
            tag = 'warning'
        elif ("🔍" in message or "🔄" in message or "📊" in message or "🔐" in message or
              "checking" in message.lower() or "scanning" in message.lower() or
              "analyse" in message.lower() or "comparaison" in message.lower() or
              "vérification" in message.lower() or "traitement" in message.lower() or
              "génération" in message.lower()):
            tag = 'info'
        elif ("MISSING" in message or "MANQUANTS" in message or "manquant" in message.lower()):
            tag = 'missing'
        elif ("EXTRA" in message or "SUPPLÉMENTAIRES" in message or "supplémentaire" in message.lower()):
            tag = 'extra'
        elif ("MODIFIED" in message or "MODIFIÉS" in message or "modifié" in message.lower() or
              "doublons" in message.lower() or "duplicate" in message.lower()):
            tag = 'modified'
        
        # Add to main console
        self.console.insert(tk.END, f"[{timestamp}] ", 'timestamp')
        self.console.insert(tk.END, f"{message}\n", tag)
        self.console.see(tk.END)
        
        # Add to large console if it exists
        if self.large_console_text and self.large_console_window and self.large_console_window.winfo_exists():
            try:
                self.large_console_text.insert(tk.END, f"[{timestamp}] ", 'timestamp')
                self.large_console_text.insert(tk.END, f"{message}\n", tag)
                self.large_console_text.see(tk.END)
            except tk.TclError:
                # Large console window was closed
                self.large_console_window = None
                self.large_console_text = None
        
        self.root.update()
    
    def open_large_console(self):
        """
        Ouvrir une fenêtre de console large pour gérer des volumes massifs de données.
        """
        if self.large_console_window and self.large_console_window.winfo_exists():
            # Amener la fenêtre existante au premier plan
            self.large_console_window.lift()
            self.large_console_window.focus_force()
            return
        
        # Créer une nouvelle fenêtre de console large
        self.large_console_window = tk.Toplevel(self.root)
        self.large_console_window.title("🖥️ Grande Console - Comparateur d'Archives")
        self.large_console_window.geometry("1400x800")
        self.large_console_window.minsize(1000, 600)
        
        # Configurer la fenêtre
        self.large_console_window.configure(bg='#2D3748')
        
        # Créer le cadre principal
        main_frame = ttk.Frame(self.large_console_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titre
        title_label = ttk.Label(main_frame, 
                               text="🖥️ Grande Console - Optimisée pour l'Analyse de Gros Volumes",
                               font=('Segoe UI', 14, 'bold'),
                               foreground='#2E86AB')
        title_label.pack(pady=(0, 10))
        
        # Étiquette d'information
        info_label = ttk.Label(main_frame,
                              text="💡 Cette console peut gérer efficacement 144K+ fichiers et de gros jeux de données",
                              font=('Segoe UI', 10),
                              foreground='#718096')
        info_label.pack(pady=(0, 10))
        
        # Créer le cadre de la console
        console_frame = ttk.Frame(main_frame)
        console_frame.pack(fill=tk.BOTH, expand=True)
        
        # Créer un grand texte avec défilement et paramètres optimisés
        self.large_console_text = scrolledtext.ScrolledText(
            console_frame,
            wrap=tk.NONE,  # Pas de retour à la ligne pour une meilleure performance
            height=40,
            width=120,
            font=('Consolas', 9),
            bg='#1E1E1E',
            fg='#FFFFFF',
            insertbackground='#FFFFFF',
            selectbackground='#264F78',
            relief='flat',
            borderwidth=1,
            maxundo=20,  # Limit undo operations for performance
            undo=True
        )
        self.large_console_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for colored output (same as main console)
        tags = {
            'timestamp': '#569CD6',
            'success': '#4EC9B0',
            'error': '#F44747',
            'warning': '#FFCC02',
            'info': '#9CDCFE',
            'missing': '#F48771',
            'extra': '#B5CEA8',
            'modified': '#DCDCAA'
        }
        
        for tag, color in tags.items():
            self.large_console_text.tag_configure(tag, foreground=color)
        
        # Add control buttons frame
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Control buttons
        clear_btn = ttk.Button(control_frame, text="🗑️ Clear Large Console", 
                              command=self.clear_large_console, style='Modern.TButton')
        clear_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        save_btn = ttk.Button(control_frame, text="💾 Sauvegarder Sortie Console", 
                             command=self.save_console_output, style='Modern.TButton')
        save_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        find_btn = ttk.Button(control_frame, text="🔍 Rechercher dans Console", 
                             command=self.find_in_console, style='Modern.TButton')
        find_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Information de performance
        perf_label = ttk.Label(control_frame,
                              text="⚡ Optimisé pour les jeux de données de 96GB+",
                              font=('Segoe UI', 8),
                              foreground='#4EC9B0')
        perf_label.pack(side=tk.RIGHT)
        
        # Copier le contenu existant vers la grande console
        if self.console.get("1.0", tk.END).strip():
            # Copier le contenu avec le formatage approprié
            self._copy_console_content_with_tags()
        
        # Message de bienvenue avec couleurs
        self.large_console_text.insert(tk.END, "🖥️ Grande console initialisée pour le traitement de gros volumes!\n", 'success')
        self.large_console_text.insert(tk.END, "💪 Prête à gérer des jeux de données massifs (96GB+, 144K+ fichiers)\n", 'info')
        self.large_console_text.see(tk.END)
    
    def _copy_console_content_with_tags(self):
        """
        Copier le contenu de la console principale vers la grande console avec les balises de couleur appropriées.
        """
        try:
            # Get all content from main console
            content = self.console.get("1.0", tk.END)
            lines = content.split('\n')
            
            for line in lines:
                if not line.strip():
                    continue
                    
                # Parse timestamp and message
                if line.startswith('[') and '] ' in line:
                    timestamp_end = line.find('] ') + 2
                    timestamp = line[:timestamp_end]
                    message = line[timestamp_end:]
                    
                    # Add timestamp with color
                    self.large_console_text.insert(tk.END, timestamp, 'timestamp')
                    
                    # Determine message color (with French translations)
                    tag = None
                    if ("✨" in message or "✅" in message or 
                        "successfully" in message.lower() or "success" in message.lower() or
                        "réussi" in message.lower() or "parfaitement" in message.lower() or
                        "terminé avec succès" in message.lower() or "aucun doublon" in message.lower()):
                        tag = 'success'
                    elif ("❌" in message or 
                          "error" in message.lower() or "failed" in message.lower() or
                          "erreur" in message.lower() or "échec" in message.lower()):
                        tag = 'error'
                    elif ("⚠️" in message or 
                          "warning" in message.lower() or "attention" in message.lower() or
                          "impossible" in message.lower() or "interrompue" in message.lower()):
                        tag = 'warning'
                    elif ("🔍" in message or "🔄" in message or "📊" in message or "🔐" in message or
                          "checking" in message.lower() or "scanning" in message.lower() or
                          "analyse" in message.lower() or "comparaison" in message.lower() or
                          "vérification" in message.lower() or "traitement" in message.lower() or
                          "génération" in message.lower()):
                        tag = 'info'
                    elif ("MISSING" in message or "MANQUANTS" in message or "manquant" in message.lower()):
                        tag = 'missing'
                    elif ("EXTRA" in message or "SUPPLÉMENTAIRES" in message or "supplémentaire" in message.lower()):
                        tag = 'extra'
                    elif ("MODIFIED" in message or "MODIFIÉS" in message or "modifié" in message.lower() or
                          "doublons" in message.lower() or "duplicate" in message.lower()):
                        tag = 'modified'
                    
                    # Add message with color
                    self.large_console_text.insert(tk.END, message + '\n', tag)
                else:
                    # Line without timestamp
                    self.large_console_text.insert(tk.END, line + '\n')
                    
        except Exception as e:
            # If copying fails, just add the raw content
            content = self.console.get("1.0", tk.END)
            self.large_console_text.insert("1.0", content)
    
    def update_status(self, message, icon="✅"):
        """
        Update the status bar with icon and message.
        """
        self.status_icon.config(text=icon)
        self.status_var.set(message)
    
    def browse_ref_path(self):
        """
        Browse for reference directory.
        """
        path = filedialog.askdirectory(title="Select Reference Directory")
        if path:
            self.ref_path_var.set(path)
            self.log_message(f"📚 Reference path set to: {path}")
            self.update_status("Reference directory selected", "📚")
    
    def browse_extract_path(self):
        """
        Browse for extracted directory.
        """
        path = filedialog.askdirectory(title="Select Extracted Directory")
        if path:
            self.extract_path_var.set(path)
            self.log_message(f"📦 Extracted path set to: {path}")
            self.update_status("Extracted directory selected", "📦")
    
    def browse_output_file(self):
        """
        Browse for output file location.
        """
        path = filedialog.asksaveasfilename(
            title="Save Result As",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if path:
            self.output_file_var.set(path)
            self.log_message(f"💾 Output file set to: {path}")
            self.update_status("Export location selected", "💾")
    
    def clear_console(self):
        """
        Vider la console avec un bel effet d'animation.
        """
        self.console.delete(1.0, tk.END)
        self.log_message("🗑️ Console vidée et prête pour de nouvelles opérations")
        self.update_status("Console vidée", "🗑️")
    
    def clear_large_console(self):
        """
        Vider la grande console et ajouter un message de bienvenue coloré.
        """
        if self.large_console_text:
            self.large_console_text.delete(1.0, tk.END)
            self.large_console_text.insert(tk.END, "🗑️ Grande console vidée et prête pour les gros volumes de données!\n", 'success')
            self.large_console_text.insert(tk.END, "💡 All colors are working properly for enhanced readability\n", 'info')
    
    def save_console_output(self):
        """
        Save the large console output to a file.
        """
        if not self.large_console_text:
            return
        
        file_path = filedialog.asksaveasfilename(
            title="💾 Save Console Output",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("Log files", "*.log"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                content = self.large_console_text.get("1.0", tk.END)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.log_message(f"💾 Console output saved to: {file_path}")
                messagebox.showinfo("✅ Save Successful", f"Console output saved to:\n{file_path}")
            except Exception as e:
                self.log_message(f"❌ Error saving console output: {str(e)}")
                messagebox.showerror("❌ Save Error", str(e))
    
    def find_in_console(self):
        """
        Find text in the large console.
        """
        if not self.large_console_text:
            return
        
        search_term = tk.simpledialog.askstring("🔍 Find in Console", "Enter search term:")
        if search_term:
            # Clear previous search highlights
            self.large_console_text.tag_remove('search_highlight', '1.0', tk.END)
            
            # Configure search highlight tag
            self.large_console_text.tag_configure('search_highlight', 
                                                 background='#FFFF00', 
                                                 foreground='#000000')
            
            # Find and highlight all occurrences
            start = '1.0'
            count = 0
            while True:
                pos = self.large_console_text.search(search_term, start, tk.END, nocase=True)
                if not pos:
                    break
                end = f"{pos}+{len(search_term)}c"
                self.large_console_text.tag_add('search_highlight', pos, end)
                start = end
                count += 1
            
            if count > 0:
                # Go to first occurrence
                first_pos = self.large_console_text.search(search_term, '1.0', tk.END, nocase=True)
                self.large_console_text.see(first_pos)
                messagebox.showinfo("🔍 Search Results", f"Found {count} occurrences of '{search_term}'")
            else:
                messagebox.showinfo("🔍 Search Results", f"'{search_term}' not found")
    
    def compare_archives_gui(self):
        """
        Effectuer la comparaison d'archives depuis les entrées GUI avec de belles mises à jour de progression.
        """
        ref_path = self.ref_path_var.get().strip()
        extract_path = self.extract_path_var.get().strip()
        
        if not ref_path or not extract_path:
            messagebox.showerror("❌ Chemins Manquants", 
                               "Veuillez spécifier les chemins de référence et d'extraction.")
            return
        
        if not os.path.exists(ref_path):
            messagebox.showerror("❌ Chemin Non Trouvé", 
                               f"Le chemin de référence n'existe pas:\n{ref_path}")
            return
        
        if not os.path.exists(extract_path):
            messagebox.showerror("❌ Chemin Non Trouvé", 
                               f"Le chemin d'extraction n'existe pas:\n{extract_path}")
            return
        
        try:
            # Afficher la barre de progression
            self.show_progress_bar(100)
            
            self.update_status("Comparaison des archives...", "🔄")
            self.log_message("🚀 Démarrage de la comparaison complète des archives...")
            self.log_message(f"📚 Référence: {ref_path}")
            self.log_message(f"📦 Extrait: {extract_path}")
            
            # Effectuer la comparaison avec progression
            self.current_report = compare_archives_with_progress(extract_path, ref_path, self.update_progress_with_bar)
            
            # Afficher de beaux résultats
            self.display_comparison_results(self.current_report)
            
            # Mettre à jour le statut basé sur les résultats
            total_issues = (self.current_report.get('num_missing', 0) + 
                          self.current_report.get('num_extra', 0) + 
                          self.current_report.get('num_modified', 0))
            
            if total_issues == 0:
                self.update_status("✨ Les archives correspondent parfaitement!", "✨")
            else:
                self.update_status(f"⚠️ Trouvé {total_issues} différences", "⚠️")
            
        except Exception as e:
            error_msg = f"❌ Erreur pendant la comparaison: {str(e)}"
            self.log_message(error_msg)
            messagebox.showerror("❌ Erreur de Comparaison", str(e))
            self.update_status("Échec de la comparaison", "❌")
        finally:
            # Cacher la barre de progression
            self.hide_progress_bar()
            messagebox.showerror("❌ Comparison Error", str(e))
            self.update_status("Comparison failed", "❌")
    
    def update_progress(self, message):
        """
        Mettre à jour les messages de progression pendant la comparaison avec un beau formatage.
        """
        # Ajouter des icônes appropriées aux messages de progression
        if "Scanning reference" in message:
            message = f"🔍 {message.replace('Scanning reference', 'Analyse de référence')}"
        elif "Scanning extracted" in message:
            message = f"🔍 {message.replace('Scanning extracted', 'Analyse extrait')}"
        elif "Comparing file lists" in message:
            message = f"📝 {message.replace('Comparing file lists', 'Comparaison des listes de fichiers')}"
        elif "Checking integrity" in message:
            message = f"🔐 {message.replace('Checking integrity', 'Vérification d\'intégrité')}"
        elif "Generating final report" in message:
            message = f"📊 {message.replace('Generating final report', 'Génération du rapport final')}"
        
        self.log_message(message)

    def update_progress_with_bar(self, message, progress_percent=None):
        """
        Mettre à jour les messages de progression avec barre de progression pendant la comparaison.
        """
        # Ajouter des icônes appropriées aux messages de progression
        if "Scanning reference" in message:
            message = f"🔍 {message.replace('Scanning reference', 'Analyse de référence')}"
            if progress_percent is None:
                progress_percent = 10
        elif "Scanning extracted" in message:
            message = f"🔍 {message.replace('Scanning extracted', 'Analyse extrait')}"
            if progress_percent is None:
                progress_percent = 30
        elif "Comparing file lists" in message:
            message = f"📝 {message.replace('Comparing file lists', 'Comparaison des listes de fichiers')}"
            if progress_percent is None:
                progress_percent = 60
        elif "Checking integrity" in message:
            message = f"🔐 {message.replace('Checking integrity', 'Vérification d\'intégrité')}"
            if progress_percent is None:
                progress_percent = 80
        elif "Generating final report" in message:
            message = f"📊 {message.replace('Generating final report', 'Génération du rapport final')}"
            if progress_percent is None:
                progress_percent = 95
        
        self.log_message(message)
        
        # Mettre à jour la barre de progression si un pourcentage est fourni
        if progress_percent is not None:
            self.update_progress_bar(progress_percent)
        self.update_status(message, "🔄")
    
    def display_comparison_results(self, report):
        """
        Afficher les résultats de comparaison dans un arbre explorateur de fichiers magnifiquement formaté.
        """
        self.log_message("═══════════════════════════════════════════════════════")
        self.log_message("📊 RÉSUMÉ DES RÉSULTATS DE COMPARAISON", 'info')
        self.log_message("═══════════════════════════════════════════════════════")
        
        # Affichage des statistiques magnifique
        stats = [
            ("📄 Fichiers manquants", report['num_missing'], 'missing'),
            ("📄 Fichiers supplémentaires", report['num_extra'], 'extra'),
            ("🔄 Fichiers modifiés", report.get('num_modified', 0), 'modified'),
            ("📁 Dossiers manquants", report.get('num_missing_dirs', 0), 'missing'),
            ("📁 Dossiers supplémentaires", report.get('num_extra_dirs', 0), 'extra'),
            ("✅ Fichiers identiques", report.get('num_common', 0), 'success')
        ]
        
        for label, count, tag in stats:
            self.log_message(f"{label}: {count}", tag)
        
        # For backward compatibility with old reports
        if 'missing_directories' not in report:
            enhanced_report = self._enhance_report_with_directories(report)
        else:
            enhanced_report = report
        
        # Display missing files and directories
        if enhanced_report['missing_files'] or enhanced_report.get('missing_directories', []):
            missing_tree = {}
            
            # Add missing directories
            for dir_path in enhanced_report.get('missing_directories', []):
                self._add_item_to_tree(missing_tree, dir_path, 'missing', is_directory=True)
            
            # Add missing files
            for file_path in enhanced_report['missing_files']:
                self._add_item_to_tree(missing_tree, file_path, 'missing', is_directory=False)
            
            self.log_message("\n📋 FICHIERS ET DOSSIERS MANQUANTS", 'missing')
            self.log_message("─" * 50)
            if missing_tree:
                self._display_tree(missing_tree, "", "")
            else:
                self.log_message("  (Aucun fichier ou dossier manquant)", 'success')
        
        # Display extra files and directories
        if enhanced_report['extra_files'] or enhanced_report.get('extra_directories', []):
            extra_tree = {}
            
            # Add extra directories
            for dir_path in enhanced_report.get('extra_directories', []):
                self._add_item_to_tree(extra_tree, dir_path, 'extra', is_directory=True)
            
            # Add extra files
            for file_path in enhanced_report['extra_files']:
                self._add_item_to_tree(extra_tree, file_path, 'extra', is_directory=False)
            
            self.log_message("\n📋 FICHIERS ET DOSSIERS SUPPLÉMENTAIRES", 'extra')
            self.log_message("─" * 50)
            if extra_tree:
                self._display_tree(extra_tree, "", "")
            else:
                self.log_message("  (Aucun fichier ou dossier supplémentaire)", 'success')
        
        # Display modified files
        if enhanced_report.get('modified_files', []):
            modified_tree = {}
            
            for file_info in enhanced_report['modified_files']:
                file_path = file_info['file']
                self._add_item_to_tree(modified_tree, file_path, 'modified', is_directory=False, 
                                     extra_info=file_info)
            
            self.log_message("\n📋 FICHIERS MODIFIÉS", 'modified')
            self.log_message("─" * 50)
            if modified_tree:
                self._display_tree(modified_tree, "", "")
            else:
                self.log_message("  (Aucun fichier modifié)", 'success')
        
        # Message final du résultat
        if not (enhanced_report['missing_files'] or enhanced_report['extra_files'] or 
                enhanced_report.get('missing_directories', []) or enhanced_report.get('extra_directories', []) or
                enhanced_report.get('modified_files', [])):
            self.log_message("\n✨ CORRESPONDANCE PARFAITE! Les archives sont identiques! ✨", 'success')
        else:
            total_issues = (len(enhanced_report['missing_files']) + 
                          len(enhanced_report['extra_files']) + 
                          len(enhanced_report.get('modified_files', [])))
            self.log_message(f"\n⚠️ Trouvé {total_issues} différences qui nécessitent une attention", 'warning')
        
        self.log_message("═══════════════════════════════════════════════════════")
        self.log_message("📊 FIN DES RÉSULTATS DE COMPARAISON", 'info')
        self.log_message("═══════════════════════════════════════════════════════\n")
    
    def _enhance_report_with_directories(self, report):
        """
        Améliorer le rapport pour inclure les dossiers manquants et supplémentaires.
        """
        # Obtenir tous les chemins de dossiers depuis les chemins de fichiers
        missing_dirs = set()
        extra_dirs = set()
        
        # Extraire les dossiers des fichiers manquants
        for file_path in report['missing_files']:
            parts = file_path.replace('\\', '/').split('/')
            for i in range(len(parts) - 1):  # Exclure le fichier lui-même
                dir_path = '/'.join(parts[:i + 1])
                missing_dirs.add(dir_path)
        
        # Extract directories from extra files
        for file_path in report['extra_files']:
            parts = file_path.replace('\\', '/').split('/')
            for i in range(len(parts) - 1):  # Exclude the file itself
                dir_path = '/'.join(parts[:i + 1])
                extra_dirs.add(dir_path)
        
        # Remove directories that exist in both (they're not truly missing/extra)
        common_dirs = missing_dirs & extra_dirs
        missing_dirs -= common_dirs
        extra_dirs -= common_dirs
        
        # Filter out parent directories if child directories are already listed
        missing_dirs = self._filter_parent_directories(missing_dirs)
        extra_dirs = self._filter_parent_directories(extra_dirs)
        
        return {
            'missing_files': report['missing_files'],
            'extra_files': report['extra_files'],
            'missing_directories': sorted(missing_dirs),
            'extra_directories': sorted(extra_dirs),
            'num_missing': report['num_missing'],
            'num_extra': report['num_extra']
        }
    
    def _filter_parent_directories(self, directories):
        """
        Remove parent directories if their child directories are already in the set.
        """
        sorted_dirs = sorted(directories, key=lambda x: x.count('/'))
        filtered_dirs = set()
        
        for directory in sorted_dirs:
            # Check if any directory in filtered_dirs is a parent of this directory
            is_child = False
            for existing_dir in filtered_dirs:
                if directory.startswith(existing_dir + '/'):
                    is_child = True
                    break
            
            if not is_child:
                # Remove any existing directories that are children of this directory
                filtered_dirs = {d for d in filtered_dirs if not d.startswith(directory + '/')}
                filtered_dirs.add(directory)
        
        return filtered_dirs
    
    def _add_item_to_tree(self, tree, item_path, status, is_directory, extra_info=None):
        """
        Add a file or directory to the tree structure with its status.
        """
        parts = item_path.replace('\\', '/').split('/')
        current_level = tree
        
        # Navigate/create the directory structure
        for i, part in enumerate(parts):
            if part not in current_level:
                current_level[part] = {}
            
            # If this is the last part, mark its status and type
            if i == len(parts) - 1:
                current_level[part]['_status'] = status
                current_level[part]['_is_file'] = not is_directory
                current_level[part]['_is_target'] = True  # This is the actual missing/extra item
                if extra_info:
                    current_level[part]['_extra_info'] = extra_info
            else:
                # It's an intermediate directory, ensure it has the proper structure
                if '_is_file' not in current_level[part]:
                    current_level[part]['_is_file'] = False
                current_level = current_level[part]
    
    def _display_tree(self, tree, prefix, current_prefix):
        """
        Display the tree structure in file explorer format.
        """
        items = [(name, data) for name, data in tree.items() if not name.startswith('_')]
        items.sort(key=lambda x: (x[1].get('_is_file', False), x[0].lower()))
        
        for i, (name, data) in enumerate(items):
            is_last = i == len(items) - 1
            
            # Choose the appropriate tree characters
            if is_last:
                current_connector = "└── "
                next_prefix = current_prefix + "    "
            else:
                current_connector = "├── "
                next_prefix = current_prefix + "│   "
            
            # Determine the display format based on file status
            if data.get('_is_file', False):
                # It's a file
                status = data.get('_status', '')
                is_target = data.get('_is_target', False)
                extra_info = data.get('_extra_info', {})
                
                if is_target:
                    if status == 'missing':
                        display_name = f"❌ {name} (MISSING FILE)"
                    elif status == 'extra':
                        display_name = f"➕ {name} (EXTRA FILE)"
                    elif status == 'modified':
                        size_ref = extra_info.get('size_ref', 0)
                        size_ext = extra_info.get('size_ext', 0)
                        display_name = f"🔄 {name} (MODIFIED - Ref:{size_ref}B, Ext:{size_ext}B)"
                    else:
                        display_name = f"📄 {name}"
                else:
                    display_name = f"📄 {name}"
            else:
                # It's a directory
                status = data.get('_status', '')
                is_target = data.get('_is_target', False)
                
                if is_target:
                    if status == 'missing':
                        display_name = f"❌ {name}/ (MISSING DIRECTORY)"
                    elif status == 'extra':
                        display_name = f"➕ {name}/ (EXTRA DIRECTORY)"
                    else:
                        display_name = f"📁 {name}/"
                else:
                    display_name = f"📁 {name}/"
            
            self.log_message(f"{current_prefix}{current_connector}{display_name}")
            
            # Show additional details for modified files
            if data.get('_status') == 'modified' and data.get('_extra_info'):
                info = data.get('_extra_info', {})
                if 'hash_ref' in info and 'hash_ext' in info:
                    self.log_message(f"{current_prefix}{'    ' if is_last else '│   '}    Ref hash: {info['hash_ref'][:16]}...")
                    self.log_message(f"{current_prefix}{'    ' if is_last else '│   '}    Ext hash: {info['hash_ext'][:16]}...")
            
            # Recursively display subdirectories/files
            if not data.get('_is_file', False):
                self._display_tree(data, next_prefix, next_prefix)
    
    def export_result(self):
        """
        Exporter le résultat de comparaison vers un fichier avec de beaux commentaires.
        """
        if self.current_report is None:
            messagebox.showwarning("⚠️ Aucun Résultat", 
                                 "Aucun résultat de comparaison à exporter.\nVeuillez d'abord effectuer une comparaison.")
            return
        
        output_path = self.output_file_var.get().strip()
        if not output_path:
            output_path = filedialog.asksaveasfilename(
                title="📤 Exporter les Résultats Sous",
                defaultextension=".json",
                filetypes=[("Fichiers JSON", "*.json"), ("Tous les fichiers", "*.*")]
            )
        
        if output_path:
            try:
                self.update_status("Export des résultats...", "📤")
                
                # Ajouter de belles métadonnées à l'export
                export_data = {
                    "metadata": {
                        "timestamp": str(datetime.datetime.now()),
                        "reference_path": self.ref_path_var.get(),
                        "extracted_path": self.extract_path_var.get(),
                        "application": "Comparateur d'Archives v2.0 - APST2607",
                        "total_differences": (self.current_report.get('num_missing', 0) + 
                                            self.current_report.get('num_extra', 0) + 
                                            self.current_report.get('num_modified', 0))
                    },
                    "results": self.current_report
                }
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                
                self.log_message(f"📤 Résultats exportés avec succès vers: {output_path}")
                self.update_status("Export terminé avec succès", "✅")
                messagebox.showinfo("✅ Export Réussi", 
                                  f"Résultats exportés avec succès vers:\n{output_path}")
                
            except Exception as e:
                error_msg = f"❌ Erreur lors de l'export: {str(e)}"
                self.log_message(error_msg)
                messagebox.showerror("❌ Erreur d'Export", str(e))
                self.update_status("Échec de l'export", "❌")
    
    def import_result(self):
        """
        Importer et afficher des résultats de comparaison précédemment sauvegardés avec de beaux commentaires.
        """
        file_path = filedialog.askopenfilename(
            title="📥 Importer les Résultats",
            filetypes=[("Fichiers JSON", "*.json"), ("Tous les fichiers", "*.*")]
        )
        
        if file_path:
            try:
                self.update_status("Importing results...", "📥")
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Gérer l'ancien format (résultats directs) et le nouveau format (avec métadonnées)
                if 'results' in data:
                    report = data['results']
                    metadata = data.get('metadata', {})
                    
                    self.log_message(f"📥 Résultats importés avec succès depuis: {file_path}")
                    if 'timestamp' in metadata:
                        self.log_message(f"🕒 Horodatage de comparaison original: {metadata['timestamp']}")
                    if 'reference_path' in metadata:
                        self.log_message(f"📚 Chemin de référence original: {metadata['reference_path']}")
                    if 'extracted_path' in metadata:
                        self.log_message(f"📦 Chemin d'extraction original: {metadata['extracted_path']}")
                    if 'total_differences' in metadata:
                        self.log_message(f"📊 Total des différences trouvées: {metadata['total_differences']}")
                else:
                    # Ancien format - résultats directs
                    report = data
                    self.log_message(f"📥 Résultats legacy importés depuis: {file_path}")
                
                # Valider les données importées
                required_keys = ['missing_files', 'extra_files', 'num_missing', 'num_extra']
                if all(key in report for key in required_keys):
                    self.current_report = report
                    self.display_comparison_results(report)
                    self.update_status("Import terminé avec succès", "✅")
                else:
                    raise ValueError("Format de fichier invalide - champs requis manquants")
                    
            except Exception as e:
                error_msg = f"❌ Erreur lors de l'import: {str(e)}"
                self.log_message(error_msg)
                messagebox.showerror("❌ Erreur d'Import", str(e))
                self.update_status("Échec de l'import", "❌")

    def detect_duplicates(self):
        """
        Détecter les fichiers en double dans un répertoire en utilisant des hachages SHA-256.
        """
        # Demander à l'utilisateur de sélectionner un répertoire
        directory = filedialog.askdirectory(
            title="🔍 Sélectionner le Répertoire pour Détecter les Doublons",
        )
        
        if not directory:
            return
        
        if not os.path.exists(directory):
            messagebox.showerror("❌ Erreur", f"Le répertoire n'existe pas: {directory}")
            return
        
        try:
            # Afficher la barre de progression
            self.show_progress_bar(100)
            
            self.update_status("Détection des doublons en cours...", "🔍")
            self.log_message("🚀 Démarrage de la détection des fichiers en double...")
            self.log_message(f"📁 Répertoire analysé: {directory}")
            self.log_message("🔧 Filtres appliqués: fichiers entre 1KB et 2GB, exclusion des fichiers système", 'info')
            
            # Effectuer la détection des doublons
            duplicates_report = self._scan_for_duplicates(directory)
            
            # Afficher les résultats
            self.display_duplicates_results(duplicates_report)
            
            # Mettre à jour le statut
            total_duplicates = sum(len(group) for group in duplicates_report['duplicate_groups'].values())
            if total_duplicates == 0:
                self.update_status("✨ Aucun doublon trouvé!", "✨")
            else:
                self.update_status(f"⚠️ Trouvé {len(duplicates_report['duplicate_groups'])} groupes de doublons", "⚠️")
                
        except KeyboardInterrupt:
            self.log_message("⚠️ Opération interrompue par l'utilisateur", 'warning')
            self.update_status("Opération annulée", "⚠️")
        except Exception as e:
            error_msg = f"❌ Erreur lors de la détection des doublons: {str(e)}"
            self.log_message(error_msg)
            messagebox.showerror("❌ Erreur de Détection", str(e))
            self.update_status("Échec de la détection", "❌")
        finally:
            # Cacher la barre de progression
            self.hide_progress_bar()

    def _scan_for_duplicates(self, directory):
        """
        Scanner le répertoire pour identifier les fichiers en double avec optimisations pour gros volumes.
        """
        file_hashes = {}  # hash -> [list of file paths]
        total_files = 0
        processed_files = 0
        skipped_files = 0
        error_files = 0
        
        # Compter le nombre total de fichiers avec filtrage
        self.log_message("🔍 Comptage des fichiers à analyser...")
        for root, dirs, files in os.walk(directory):
            # Ignorer les dossiers système et cachés
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['System Volume Information', '$RECYCLE.BIN', 'hiberfil.sys', 'pagefile.sys']]
            
            for file in files:
                # Ignorer les fichiers système, temporaires et très petits
                if not file.startswith('.') and not file.lower().endswith(('.tmp', '.temp', '.log')):
                    file_path = os.path.join(root, file)
                    try:
                        # Ignorer les fichiers très petits (< 1KB) et très gros (> 2GB pour éviter la saturation mémoire)
                        file_size = os.path.getsize(file_path)
                        if 1024 <= file_size <= 2 * 1024 * 1024 * 1024:  # Entre 1KB et 2GB
                            total_files += 1
                        else:
                            skipped_files += 1
                    except (OSError, PermissionError):
                        skipped_files += 1
        
        if skipped_files > 0:
            self.log_message(f"⚠️ {skipped_files} fichiers ignorés (système, trop petits/gros, ou inaccessibles)", 'warning')
        
        self.log_message(f"📊 Analyse de {total_files} fichiers pour détecter les doublons...")
        
        if total_files == 0:
            self.log_message("⚠️ Aucun fichier valide à analyser", 'warning')
            return {
                'total_files': 0,
                'unique_files': 0,
                'duplicate_groups': {},
                'total_duplicate_files': 0
            }
        
        # Initialiser la barre de progression
        self.update_progress_bar(0)
        
        # Scanner tous les fichiers et calculer leurs hachages avec gestion d'erreurs robuste
        for root, dirs, files in os.walk(directory):
            # Ignorer les dossiers système et cachés
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['System Volume Information', '$RECYCLE.BIN', 'hiberfil.sys', 'pagefile.sys']]
            
            for file in files:
                if not file.startswith('.') and not file.lower().endswith(('.tmp', '.temp', '.log')):
                    file_path = os.path.join(root, file)
                    try:
                        # Vérifier la taille du fichier
                        file_size = os.path.getsize(file_path)
                        if not (1024 <= file_size <= 2 * 1024 * 1024 * 1024):
                            continue
                        
                        # Calculer le hachage SHA-256 avec gestion d'erreurs
                        file_hash = self._calculate_file_hash_safe(file_path)
                        
                        if file_hash:  # Seulement si le hachage a réussi
                            if file_hash not in file_hashes:
                                file_hashes[file_hash] = []
                            file_hashes[file_hash].append(file_path)
                        else:
                            error_files += 1
                        
                        processed_files += 1
                        
                        # Mise à jour de progression avec libération périodique de mémoire
                        progress_percent = min(int((processed_files / total_files) * 90), 90)
                        self.update_progress_bar(progress_percent)
                        
                        # Mise à jour de progression et nettoyage mémoire tous les 100 fichiers
                        if processed_files % 100 == 0:
                            progress_msg = f"Traitement: {processed_files}/{total_files} fichiers"
                            if error_files > 0:
                                progress_msg += f" ({error_files} erreurs)"
                            self.log_message(f"🔄 {progress_msg}")
                            self.root.update_idletasks()
                            
                            # Forcer le garbage collection pour libérer la mémoire
                            import gc
                            gc.collect()
                        
                        # Pause périodique pour éviter de bloquer l'interface
                        if processed_files % 50 == 0:
                            self.root.update()
                            
                    except (OSError, PermissionError, FileNotFoundError) as e:
                        error_files += 1
                        if error_files <= 10:  # Limiter les messages d'erreur
                            self.log_message(f"⚠️ Accès refusé: {os.path.basename(file_path)}", 'warning')
                        elif error_files == 11:
                            self.log_message("⚠️ Plus de 10 erreurs d'accès, les suivantes seront comptées silencieusement", 'warning')
                    except KeyboardInterrupt:
                        self.log_message("⚠️ Opération interrompue par l'utilisateur", 'warning')
                        raise
                    except Exception as e:
                        error_files += 1
                        if error_files <= 5:  # Limiter les messages d'erreur détaillés
                            self.log_message(f"⚠️ Erreur inattendue pour {os.path.basename(file_path)}: {str(e)[:100]}", 'warning')
        
        # Phase finale : identification des doublons (10% restants)
        self.update_progress_bar(90)
        self.log_message("🔄 Identification des groupes de doublons...")
        
        # Identifier les doublons (hachages avec plus d'un fichier)
        duplicate_groups = {}
        unique_files = 0
        
        for file_hash, file_paths in file_hashes.items():
            if len(file_paths) > 1:
                # Créer un nom de groupe basé sur le premier fichier
                group_name = os.path.basename(file_paths[0])
                duplicate_groups[group_name] = file_paths
            else:
                unique_files += 1
        
        # Finaliser la barre de progression
        self.update_progress_bar(100)
        
        if error_files > 0:
            self.log_message(f"⚠️ Total: {error_files} fichiers non traités à cause d'erreurs", 'warning')
        
        return {
            'total_files': processed_files,
            'unique_files': unique_files,
            'duplicate_groups': duplicate_groups,
            'total_duplicate_files': sum(len(group) for group in duplicate_groups.values()),
            'error_files': error_files,
            'skipped_files': skipped_files
        }

    def _calculate_file_hash(self, file_path):
        """
        Calculer le hachage SHA-256 d'un fichier.
        """
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                # Lire le fichier par blocs pour économiser la mémoire
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
        except Exception as e:
            raise Exception(f"Erreur lors du calcul du hachage pour {file_path}: {str(e)}")
        return hash_sha256.hexdigest()

    def _calculate_file_hash_safe(self, file_path):
        """
        Calculer le hachage SHA-256 d'un fichier avec gestion d'erreurs robuste pour gros volumes.
        """
        hash_sha256 = hashlib.sha256()
        try:
            # Vérifier l'accès au fichier avant de l'ouvrir
            if not os.access(file_path, os.R_OK):
                return None
            
            # Vérifier que le fichier n'est pas un lien symbolique brisé
            if os.path.islink(file_path) and not os.path.exists(file_path):
                return None
            
            with open(file_path, "rb") as f:
                # Lire le fichier par blocs plus petits pour les gros fichiers
                chunk_size = 8192  # 8KB chunks
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    hash_sha256.update(chunk)
                    
                    # Permettre l'interruption pour les très gros fichiers
                    self.root.update_idletasks()
            
            return hash_sha256.hexdigest()
            
        except (PermissionError, OSError, FileNotFoundError):
            # Fichier inaccessible, verrouillé ou supprimé pendant le traitement
            return None
        except MemoryError:
            # Fichier trop gros pour la mémoire disponible
            self.log_message(f"⚠️ Fichier trop volumineux pour la mémoire: {os.path.basename(file_path)}", 'warning')
            return None
        except KeyboardInterrupt:
            # Permettre l'interruption utilisateur
            raise
        except Exception as e:
            # Toute autre erreur inattendue
            return None

    def display_duplicates_results(self, report):
        """
        Afficher les résultats de détection des doublons dans un format d'arbre magnifiquement formaté.
        """
        self.log_message("═══════════════════════════════════════════════════════")
        self.log_message("🔍 RÉSULTATS DE DÉTECTION DES DOUBLONS", 'info')
        self.log_message("═══════════════════════════════════════════════════════")
        
        # Statistiques magnifiques
        stats = [
            ("📄 Fichiers analysés", report['total_files'], 'info'),
            ("✅ Fichiers uniques", report['unique_files'], 'success'),
            ("🔄 Groupes de doublons", len(report['duplicate_groups']), 'modified'),
            ("📄 Total fichiers en double", report['total_duplicate_files'], 'missing')
        ]
        
        # Ajouter les statistiques d'erreurs si présentes
        if report.get('error_files', 0) > 0:
            stats.append(("⚠️ Fichiers avec erreurs", report['error_files'], 'warning'))
        if report.get('skipped_files', 0) > 0:
            stats.append(("⏩ Fichiers ignorés", report['skipped_files'], 'warning'))
        
        for label, count, tag in stats:
            self.log_message(f"{label}: {count}", tag)
        
        # Afficher les groupes de doublons
        if report['duplicate_groups']:
            self.log_message("\n📋 FICHIERS EN DOUBLE DÉTECTÉS", 'missing')
            self.log_message("─" * 50)
            
            for group_name, file_paths in report['duplicate_groups'].items():
                self.log_message(f"\n🔄 Groupe: {group_name} ({len(file_paths)} copies)", 'modified')
                for i, file_path in enumerate(file_paths, 1):
                    # Afficher le chemin de façon sécurisée pour tous les disques
                    display_path = self._get_display_path(file_path)
                    self.log_message(f"  {i}. {display_path}", 'warning')
        else:
            self.log_message("\n✨ AUCUN DOUBLON DÉTECTÉ! Tous les fichiers sont uniques! ✨", 'success')
        
        # Calcul de l'espace potentiellement économisable
        if report['duplicate_groups']:
            total_wasted_space = 0
            for file_paths in report['duplicate_groups'].values():
                if file_paths:
                    try:
                        file_size = os.path.getsize(file_paths[0])
                        # Espace gaspillé = taille du fichier * (nombre de copies - 1)
                        total_wasted_space += file_size * (len(file_paths) - 1)
                    except:
                        pass
            
            if total_wasted_space > 0:
                # Convertir en unités lisibles
                if total_wasted_space < 1024:
                    size_str = f"{total_wasted_space} bytes"
                elif total_wasted_space < 1024 * 1024:
                    size_str = f"{total_wasted_space / 1024:.2f} KB"
                elif total_wasted_space < 1024 * 1024 * 1024:
                    size_str = f"{total_wasted_space / (1024 * 1024):.2f} MB"
                else:
                    size_str = f"{total_wasted_space / (1024 * 1024 * 1024):.2f} GB"
                
                self.log_message(f"\n💾 Espace potentiellement économisable: {size_str}", 'info')
        
        self.log_message("═══════════════════════════════════════════════════════")
        self.log_message("🔍 FIN DE LA DÉTECTION DES DOUBLONS", 'info')
        self.log_message("═══════════════════════════════════════════════════════\n")

    def _get_display_path(self, file_path, base_directory=None):
        """
        Obtenir un chemin d'affichage lisible, gérant les disques différents sur Windows.
        """
        try:
            if base_directory:
                # Essayer d'obtenir le chemin relatif par rapport au répertoire de base
                relative_path = os.path.relpath(file_path, base_directory)
                # Si le chemin relatif commence par '..\\..\\..' c'est probablement sur un autre disque
                if not relative_path.startswith('..\\..\\..'):
                    return relative_path
            else:
                # Essayer d'obtenir le chemin relatif par rapport au répertoire courant
                relative_path = os.path.relpath(file_path)
                # Si le chemin relatif ne commence pas par de multiples '..' c'est OK
                if not relative_path.startswith('..\\..\\..'):
                    return relative_path
        except ValueError:
            # ValueError est levée quand les chemins sont sur des disques différents
            pass
        
        # Si on ne peut pas faire de chemin relatif, afficher juste le nom du fichier et son dossier parent
        try:
            parent_dir = os.path.basename(os.path.dirname(file_path))
            file_name = os.path.basename(file_path)
            drive = os.path.splitdrive(file_path)[0]
            if parent_dir:
                return f"{drive}\\...\\{parent_dir}\\{file_name}"
            else:
                return f"{drive}\\{file_name}"
        except:
            # En dernier recours, afficher le chemin complet
            return file_path


#### functions
def main():
    """ 
        main function - launches GUI
    """
    root = tk.Tk()
    app = ArchiveComparerGUI(root)
    root.mainloop()

def compare_archives_with_progress(extracted_path, reference_path, progress_callback=None):
    """
        Compare the contents of an archive with a reference directory with progress updates.
        
        Parameters:
        - extracted_path: Path to the extracted archive directory.
        - reference_path: Path to the reference directory.
        - progress_callback: Function to call for progress updates.
        
        Returns:
        - A report of missing, extra, and modified files along with directories.
    """
    def update_progress(message):
        if progress_callback:
            progress_callback(message)
    
    # Get the list of files and directories in the extracted archive and reference directory
    update_progress("Scanning reference directory...")
    reference_files = get_file_list(reference_path)
    reference_dirs = get_directory_list(reference_path)
    
    update_progress("Scanning extracted directory...")
    extracted_files = get_file_list(extracted_path)
    extracted_dirs = get_directory_list(extracted_path)

    # Compare the file lists
    update_progress("Comparing file lists...")
    missing_files = reference_files - extracted_files
    extra_files = extracted_files - reference_files
    common_files = reference_files & extracted_files
    
    # Compare the directory lists
    missing_dirs = reference_dirs - extracted_dirs
    extra_dirs = extracted_dirs - reference_dirs
    
    # Check integrity of common files
    update_progress(f"🔐 Checking integrity of {len(common_files)} common files...")
    modified_files = []
    
    # Batch progress updates for better performance with large datasets
    batch_size = max(1, len(common_files) // 100)  # Update progress every 1% of files
    if batch_size < 50:
        batch_size = 50  # Minimum batch size for performance
    
    for i, file_path in enumerate(common_files):
        if i % batch_size == 0:  # Update progress in batches
            progress_pct = int((i / len(common_files)) * 100)
            update_progress(f"🔐 Checking file integrity... {i + 1:,}/{len(common_files):,} ({progress_pct}%)")
        
        ref_file_path = os.path.join(reference_path, file_path.replace('/', os.sep))
        ext_file_path = os.path.join(extracted_path, file_path.replace('/', os.sep))
        
        try:
            ref_hash = calculate_file_hash(ref_file_path)
            ext_hash = calculate_file_hash(ext_file_path)
            
            if ref_hash != ext_hash:
                # Files are different
                ref_size = os.path.getsize(ref_file_path)
                ext_size = os.path.getsize(ext_file_path)
                
                modified_files.append({
                    'file': file_path,
                    'hash_ref': ref_hash,
                    'hash_ext': ext_hash,
                    'size_ref': ref_size,
                    'size_ext': ext_size
                })
        except (OSError, IOError) as e:
            # Handle file access errors
            modified_files.append({
                'file': file_path,
                'error': str(e),
                'hash_ref': 'ERROR',
                'hash_ext': 'ERROR',
                'size_ref': 0,
                'size_ext': 0
            })
    
    update_progress("Generating final report...")
    
    # Generate report
    report = {
        "missing_files": list(missing_files),
        "extra_files": list(extra_files),
        "modified_files": modified_files,
        "missing_directories": list(missing_dirs),
        "extra_directories": list(extra_dirs),
        "num_missing": len(missing_files),
        "num_extra": len(extra_files),
        "num_modified": len(modified_files),
        "num_missing_dirs": len(missing_dirs),
        "num_extra_dirs": len(extra_dirs),
        "num_common": len(common_files) - len(modified_files)  # Files that are identical
    }
    
    return report

def compare_archives(extracted_path, reference_path):
    """
        Compare the contents of an archive with a reference directory.
        
        Parameters:
        - extracted_path: Path to the extracted archive directory.
        - reference_path: Path to the reference directory.

        Returns:
        - A report of missing, extra, and modified files along with directories.
    """
    return compare_archives_with_progress(extracted_path, reference_path)

def calculate_file_hash(file_path, hash_algorithm='sha256'):
    """
        Calculate the hash of a file.
        
        Parameters:
        - file_path: Path to the file.
        - hash_algorithm: Hash algorithm to use (default: sha256).
        
        Returns:
        - The hexadecimal hash string of the file.
    """
    hash_obj = hashlib.new(hash_algorithm)
    
    try:
        with open(file_path, 'rb') as f:
            # Read file in chunks to handle large files efficiently
            for chunk in iter(lambda: f.read(8192), b""):
                hash_obj.update(chunk)
    except (OSError, IOError):
        # Return a special hash for files that can't be read
        return "ERROR_READING_FILE"
    
    return hash_obj.hexdigest()

def get_directory_list(directory):
    """
        Get a set of all directory paths in the given directory and its subdirectories.
        
        Parameters:
        - directory: Path to the directory.

        Returns:
        - A set of directory paths relative to the given directory.
    """
    dir_set = set()
    for root, dirs, _ in os.walk(directory):
        for dir_name in dirs:
            try:
                relative_path = os.path.relpath(os.path.join(root, dir_name), directory)
                # Normalize path separators
                relative_path = relative_path.replace('\\', '/')
                dir_set.add(relative_path)
            except ValueError:
                # Handle different drives on Windows
                full_path = os.path.join(root, dir_name)
                # Use path relative to the directory's drive
                try:
                    # Remove the directory prefix manually if on same drive
                    if full_path.startswith(directory):
                        relative_path = full_path[len(directory):].lstrip('\\/')
                        relative_path = relative_path.replace('\\', '/')
                        dir_set.add(relative_path)
                except:
                    # If all else fails, use basename
                    dir_set.add(os.path.basename(full_path))
    return dir_set

def get_file_list(directory):
    """
        Get a set of all file paths in the given directory and its subdirectories.
        
        Parameters:
        - directory: Path to the directory.

        Returns:
        - A set of file paths relative to the given directory.
    """
    file_set = set()
    for root, _, files in os.walk(directory):
        for file in files:
            try:
                relative_path = os.path.relpath(os.path.join(root, file), directory)
                # Normalize path separators
                relative_path = relative_path.replace('\\', '/')
                file_set.add(relative_path)
            except ValueError:
                # Handle different drives on Windows
                full_path = os.path.join(root, file)
                # Use path relative to the directory's drive
                try:
                    # Remove the directory prefix manually if on same drive
                    if full_path.startswith(directory):
                        relative_path = full_path[len(directory):].lstrip('\\/')
                        relative_path = relative_path.replace('\\', '/')
                        file_set.add(relative_path)
                except:
                    # If all else fails, use basename
                    file_set.add(os.path.basename(full_path))
    return file_set

#### main

if __name__ == "__main__":
    main()