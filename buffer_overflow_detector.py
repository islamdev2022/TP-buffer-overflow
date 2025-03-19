import sys
import time
import customtkinter as ctk
from tkinter import messagebox
import platform
from colorama import Fore, Style,init
import psutil
from typing import Dict, Any, List, Union

# Set appearance mode and theme
ctk.set_appearance_mode("System")  # Modes: System, Dark, Light
ctk.set_default_color_theme("blue")  # Themes: blue, green, dark-blue

# Initialize colorama for colored terminal output
init()

class BufferOverflowDetector:
    def __init__(self):
        """Initialize the detector with system limits and thresholds"""
        self.max_string_length = 255  # Default max string length
        self.max_int_value = sys.maxsize
        self.min_int_value = -sys.maxsize - 1
        self.max_float_value = sys.float_info.max
        self.min_float_value = -sys.float_info.max
        self.memory_threshold = 90  # Memory usage threshold (%)
        self.disk_threshold = 90    # Disk usage threshold (%)
        
    def check_string(self, input_str: str, max_length: int = None) -> Dict[str, Any]:
        """
        Checks if a string exceeds the maximum allowed length.
        
        Args:
            input_str: The string to check
            max_length: Maximum allowed length (uses default if None)
            
        Returns:
            Dictionary with overflow status and details
        """
        if max_length is None:
            max_length = self.max_string_length
            
        result = {
            "overflow": False,
            "message": "",
            "value": input_str,
            "max_allowed": max_length
        }
        
        try:
            if len(input_str) > max_length:
                result["overflow"] = True
                result["message"] = f"Dépassement de tampon détecté: {len(input_str)} caractères > maximum {max_length}"
        except Exception as e:
            result["overflow"] = True
            result["message"] = f"Erreur lors de la vérification de la chaîne: {str(e)}"
            
        return result

    def check_character(self, char: str) -> Dict[str, Any]:
        """
        Checks if a character is valid (single character)
        
        Args:
            char: The character to check
            
        Returns:
            Dictionary with overflow status and details
        """
        result = {
            "overflow": False,
            "message": "",
            "value": char
        }
        
        try:
            if len(char) > 1:
                result["overflow"] = True
                result["message"] = f"Dépassement de caractère détecté: '{char}' contient {len(char)} caractères"
        except Exception as e:
            result["overflow"] = True
            result["message"] = f"Erreur lors de la vérification du caractère: {str(e)}"
            
        return result

    def check_number(self, value: Union[int, float], is_integer: bool = True) -> Dict[str, Any]:
        """
        Checks if a number exceeds system limits.
        
        Args:
            value: The number to check
            is_integer: Whether the number is an integer (True) or float (False)
            
        Returns:
            Dictionary with overflow status and details
        """
        result = {
            "overflow": False,
            "message": "",
            "value": value,
            "type": "integer" if is_integer else "float/double"
        }
        
        try:
            if is_integer:
                if value > self.max_int_value or value < self.min_int_value:
                    result["overflow"] = True
                    result["message"] = f"Dépassement d'entier détecté: {value}"
                    result["limits"] = {"max": self.max_int_value, "min": self.min_int_value}
            else:
                if value > self.max_float_value or value < self.min_float_value:
                    result["overflow"] = True
                    result["message"] = f"Dépassement de flottant détecté: {value}"
                    result["limits"] = {"max": self.max_float_value, "min": self.min_float_value}
        except Exception as e:
            result["overflow"] = True
            result["message"] = f"Erreur lors de la vérification du nombre: {str(e)}"
                
        return result

    def check_array(self, array: List[Any], max_size: int) -> Dict[str, Any]:
        """
        Checks if an array exceeds the maximum allowed size.
        
        Args:
            array: The array to check
            max_size: Maximum allowed size
            
        Returns:
            Dictionary with overflow status and details
        """
        result = {
            "overflow": False,
            "message": "",
            "size": len(array),
            "max_allowed": max_size
        }
        
        try:
            if len(array) > max_size:
                result["overflow"] = True
                result["message"] = f"Dépassement de tableau détecté: taille {len(array)} > maximum {max_size}"
        except Exception as e:
            result["overflow"] = True
            result["message"] = f"Erreur lors de la vérification du tableau: {str(e)}"
            
        return result

    def check_matrix(self, matrix: List[List[Any]], max_rows: int, max_cols: int) -> Dict[str, Any]:
        """
        Checks if a matrix exceeds the maximum allowed dimensions.
        
        Args:
            matrix: The 2D matrix to check
            max_rows: Maximum allowed rows
            max_cols: Maximum allowed columns
            
        Returns:
            Dictionary with overflow status and details
        """
        result = {
            "overflow": False,
            "message": "",
            "dimensions": {"rows": 0, "cols": 0},
            "max_allowed": {"rows": max_rows, "cols": max_cols}
        }
        
        try:
            rows = len(matrix)
            cols = max(len(row) for row in matrix) if rows > 0 else 0
            
            result["dimensions"]["rows"] = rows
            result["dimensions"]["cols"] = cols
            
            if rows > max_rows:
                result["overflow"] = True
                result["message"] = f"Dépassement de matrice détecté: {rows} lignes > maximum {max_rows}"
            
            if cols > max_cols:
                result["overflow"] = True
                message = f"Dépassement de matrice détecté: {cols} colonnes > maximum {max_cols}"
                result["message"] = message if not result["overflow"] else result["message"] + f" et {message}"
                
        except Exception as e:
            result["overflow"] = True
            result["message"] = f"Erreur lors de la vérification de la matrice: {str(e)}"
            
        return result

    def check_stack(self, stack: List[Any], max_size: int) -> Dict[str, Any]:
        """
        Checks if a stack exceeds the maximum allowed size.
        
        Args:
            stack: The stack to check
            max_size: Maximum allowed size
            
        Returns:
            Dictionary with overflow status and details
        """
        result = self.check_array(stack, max_size)
        result["type"] = "stack"
        return result
        
    def check_list(self, lst: List[Any], max_size: int) -> Dict[str, Any]:
        """
        Checks if a list exceeds the maximum allowed size.
        
        Args:
            lst: The list to check
            max_size: Maximum allowed size
            
        Returns:
            Dictionary with overflow status and details
        """
        result = self.check_array(lst, max_size)
        result["type"] = "list"
        return result

    def check_memory_usage(self) -> Dict[str, Any]:
        """
        Checks system memory usage.
        
        Returns:
            Dictionary with overflow status and details about memory usage
        """
        result = {
            "overflow": False,
            "message": "",
            "memory_info": {}
        }
        
        try:
            # Get memory information
            memory = psutil.virtual_memory()
            
            result["memory_info"] = {
                "total": memory.total,
                "available": memory.available,
                "used": memory.used,
                "percent": memory.percent,
                "total_gb": memory.total / (1024**3),
                "available_gb": memory.available / (1024**3),
                "used_gb": memory.used / (1024**3)
            }
            
            # Consider overflow if usage > threshold
            if memory.percent > self.memory_threshold:
                result["overflow"] = True
                result["message"] = f"Attention: Utilisation élevée de la mémoire ({memory.percent:.1f}%)"
        except Exception as e:
            result["overflow"] = True
            result["message"] = f"Erreur lors de la vérification de la mémoire: {str(e)}"
            
        return result
        
    def check_disk_usage(self, path: str = "/") -> Dict[str, Any]:
        """
        Checks disk usage for the specified path.
        
        Args:
            path: The disk path to check (default: root directory)
            
        Returns:
            Dictionary with overflow status and details about disk usage
        """
        result = {
            "overflow": False,
            "message": "",
            "disk_info": {}
        }
        
        try:
            # Get disk information
            disk = psutil.disk_usage(path)
            
            result["disk_info"] = {
                "path": path,
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": disk.percent,
                "total_gb": disk.total / (1024**3),
                "used_gb": disk.used / (1024**3),
                "free_gb": disk.free / (1024**3)
            }
            
            # Consider overflow if usage > threshold
            if disk.percent > self.disk_threshold:
                result["overflow"] = True
                result["message"] = f"Attention: Utilisation élevée du disque ({disk.percent:.1f}%) pour {path}"
        except Exception as e:
            result["overflow"] = True
            result["message"] = f"Erreur lors de la vérification du disque: {str(e)}"
            
        return result
        
    def check_removable_drives(self) -> Dict[str, Any]:
        """
        Checks usage of removable drives (flash drives, etc.).
        
        Returns:
            Dictionary with overflow status and details about removable drives
        """
        result = {
            "overflow": False,
            "message": "",
            "drives": []
        }
        
        try:
            # Get all partitions
            partitions = psutil.disk_partitions(all=True)
            
            # Check each partition
            for partition in partitions:
                # Check if it might be a removable drive
                if partition.device and "removable" in partition.opts.lower() or (
                    platform.system() == "Windows" and partition.device.startswith(("E:", "F:", "G:", "H:"))
                ):
                    try:
                        usage = psutil.disk_usage(partition.mountpoint)
                        drive_info = {
                            "device": partition.device,
                            "mountpoint": partition.mountpoint,
                            "fstype": partition.fstype,
                            "total_gb": usage.total / (1024**3),
                            "used_gb": usage.used / (1024**3),
                            "free_gb": usage.free / (1024**3),
                            "percent": usage.percent
                        }
                        
                        result["drives"].append(drive_info)
                        
                        if usage.percent > self.disk_threshold:
                            result["overflow"] = True
                            message = f"Attention: Utilisation élevée du disque amovible ({usage.percent:.1f}%) pour {partition.device}"
                            result["message"] = message if not result["message"] else result["message"] + f"\n{message}"
                    except:
                        # Skip drives that can't be accessed
                        pass
        except Exception as e:
            result["overflow"] = True
            result["message"] = f"Erreur lors de la vérification des disques amovibles: {str(e)}"
            
        return result

    def simulate_buffer_overflow(self, size: int) -> Dict[str, Any]:
        """
        Simulates a buffer overflow by attempting to allocate a large array.
        This demonstrates how programs might crash due to buffer overflows.
        
        Args:
            size: Size of the array to allocate
            
        Returns:
            Dictionary with simulation results
        """
        result = {
            "overflow": False,
            "message": "",
            "simulation": "buffer_overflow"
        }
        
        try:
            start_time = time.time()
            # Try to allocate a large array
            large_array = [0] * size
            end_time = time.time()
            
            result["allocated_size"] = size
            result["allocation_time"] = end_time - start_time
            result["message"] = f"Allocation réussie de {size} éléments en {result['allocation_time']:.4f} secondes"
        except MemoryError:
            result["overflow"] = True
            result["message"] = f"Dépassement de mémoire détecté: impossible d'allouer {size} éléments"
        except Exception as e:
            result["overflow"] = True
            result["message"] = f"Erreur lors de la simulation: {str(e)}"
            
        return result


class BufferOverflowDetectorGUI(ctk.CTk):
    def __init__(self, detector):
        super().__init__()
        
        # Store the detector instance
        self.detector = detector
        
        # Configure window
        self.title("Détecteur de Dépassement de Tampon")
        self.geometry("900x600")
        
        # Create sidebar frame
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.pack(side="left", fill="y", padx=0, pady=0)
        
        # Create main content frame
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.pack(side="right", fill="both", expand=True, padx=0, pady=0)
        
        # Create title label
        self.title_label = ctk.CTkLabel(self.sidebar_frame, text="Options de test", font=ctk.CTkFont(size=16, weight="bold"))
        self.title_label.pack(padx=20, pady=(20, 10))
        
        # Create sidebar buttons
        self.sidebar_buttons = []
        
        # Add buttons for each test type
        test_options = [
            ("Caractère et chaîne", self.show_character_string_test),
            ("Entiers et réels", self.show_numbers_test),
            ("Tableaux et matrices", self.show_arrays_matrices_test),
            ("Listes et piles", self.show_lists_stacks_test),
            ("Mémoire", self.show_memory_test),
            ("Simulation dépassement", self.show_buffer_overflow_simulation)
        ]
        
        for text, command in test_options:
            button = ctk.CTkButton(self.sidebar_frame, text=text, command=command)
            button.pack(padx=20, pady=10, fill="x")
            self.sidebar_buttons.append(button)
        
        # Create appearance mode selector
        self.appearance_label = ctk.CTkLabel(self.sidebar_frame, text="Apparence:", anchor="w")
        self.appearance_label.pack(padx=20, pady=(20, 0))
        self.appearance_option = ctk.CTkOptionMenu(self.sidebar_frame, values=["System", "Dark", "Light"],
                                                   command=self.change_appearance_mode)
        self.appearance_option.pack(padx=20, pady=(10, 20))
        
        # Create results text area
        self.result_frame = ctk.CTkFrame(self.main_frame)
        self.result_frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        self.result_label = ctk.CTkLabel(self.result_frame, text="Résultats", font=ctk.CTkFont(size=16, weight="bold"))
        self.result_label.pack(padx=10, pady=10)
        
        self.results_text = ctk.CTkTextbox(self.result_frame, wrap="word", font=ctk.CTkFont(size=12))
        self.results_text.pack(padx=10, pady=10, fill="both", expand=True)
        
        # Create content frames for each test (initially hidden)
        self.character_string_frame = self.create_character_string_frame()
        self.numbers_frame = self.create_numbers_frame()
        self.arrays_matrices_frame = self.create_arrays_matrices_frame()
        self.lists_stacks_frame = self.create_lists_stacks_frame()
        self.memory_frame = self.create_memory_frame()
        self.buffer_overflow_frame = self.create_buffer_overflow_frame()
        
        # Show the first test by default
        self.show_character_string_test()
    
    def change_appearance_mode(self, new_appearance_mode):
        ctk.set_appearance_mode(new_appearance_mode)
    
    def hide_all_content_frames(self):
        for frame in [self.character_string_frame, self.numbers_frame, self.arrays_matrices_frame,
                      self.lists_stacks_frame, self.memory_frame, self.buffer_overflow_frame]:
            frame.pack_forget()
    
    def show_character_string_test(self):
        self.hide_all_content_frames()
        self.character_string_frame.pack(padx=20, pady=20, fill="both", expand=True)
    
    def show_numbers_test(self):
        self.hide_all_content_frames()
        self.numbers_frame.pack(padx=20, pady=20, fill="both", expand=True)
    
    def show_arrays_matrices_test(self):
        self.hide_all_content_frames()
        self.arrays_matrices_frame.pack(padx=20, pady=20, fill="both", expand=True)
    
    def show_lists_stacks_test(self):
        self.hide_all_content_frames()
        self.lists_stacks_frame.pack(padx=20, pady=20, fill="both", expand=True)
    
    def show_memory_test(self):
        self.hide_all_content_frames()
        self.memory_frame.pack(padx=20, pady=20, fill="both", expand=True)
    
    def show_buffer_overflow_simulation(self):
        self.hide_all_content_frames()
        self.buffer_overflow_frame.pack(padx=20, pady=20, fill="both", expand=True)
    
    def append_result(self, text):
        self.results_text.insert("end", text + "\n\n")
        self.results_text.see("end")
    
    def format_result_gui(self, result):
        """Format result for GUI display"""
        output = ""
        
        if result["overflow"]:
            output += "[OVERFLOW DÉTECTÉ] "
            output += result["message"]
        else:
            output += "[OK] "
            
            if "value" in result:
                output += f"Valeur: {result['value']}"
            elif "size" in result:
                output += f"Taille: {result['size']}/{result['max_allowed']}"
            elif "dimensions" in result:
                dims = result["dimensions"]
                max_dims = result["max_allowed"]
                output += f"Dimensions: {dims['rows']}x{dims['cols']} (max: {max_dims['rows']}x{max_dims['cols']})"
            elif "memory_info" in result:
                mem = result["memory_info"]
                output += f"Mémoire: {mem['percent']:.1f}% utilisée ({mem['used_gb']:.2f}/{mem['total_gb']:.2f} GB)"
            elif "disk_info" in result:
                disk = result["disk_info"]
                output += f"Disque ({disk['path']}): {disk['percent']:.1f}% utilisé ({disk['used_gb']:.2f}/{disk['total_gb']:.2f} GB)"
        
        return output
    
    def create_character_string_frame(self):
        frame = ctk.CTkFrame(self.main_frame)
        
        # Character test
        char_label = ctk.CTkLabel(frame, text="Test de caractère", font=ctk.CTkFont(size=14, weight="bold"))
        char_label.pack(padx=10, pady=10, anchor="w")
        
        char_input_frame = ctk.CTkFrame(frame)
        char_input_frame.pack(padx=10, pady=5, fill="x")
        
        char_input_label = ctk.CTkLabel(char_input_frame, text="Entrez un caractère:")
        char_input_label.pack(side="left", padx=10)
        
        self.char_input = ctk.CTkEntry(char_input_frame, width=100)
        self.char_input.pack(side="left", padx=10)
        
        char_test_button = ctk.CTkButton(char_input_frame, text="Tester", command=self.test_character)
        char_test_button.pack(side="left", padx=10)
        
        # String test
        string_label = ctk.CTkLabel(frame, text="Test de chaîne de caractères", font=ctk.CTkFont(size=14, weight="bold"))
        string_label.pack(padx=10, pady=(20, 10), anchor="w")
        
        string_max_frame = ctk.CTkFrame(frame)
        string_max_frame.pack(padx=10, pady=5, fill="x")
        
        string_max_label = ctk.CTkLabel(string_max_frame, text="Longueur maximale:")
        string_max_label.pack(side="left", padx=10)
        
        self.string_max_input = ctk.CTkEntry(string_max_frame, width=100)
        self.string_max_input.pack(side="left", padx=10)
        self.string_max_input.insert(0, "255")
        
        string_input_frame = ctk.CTkFrame(frame)
        string_input_frame.pack(padx=10, pady=5, fill="x")
        
        string_input_label = ctk.CTkLabel(string_input_frame, text="Entrez une chaîne:")
        string_input_label.pack(side="left", padx=10)
        
        self.string_input = ctk.CTkEntry(string_input_frame, width=300)
        self.string_input.pack(side="left", padx=10)
        
        string_test_button = ctk.CTkButton(string_input_frame, text="Tester", command=self.test_string)
        string_test_button.pack(side="left", padx=10)
        
        return frame
    
    def create_numbers_frame(self):
        frame = ctk.CTkFrame(self.main_frame)
        
        # Integer test
        int_label = ctk.CTkLabel(frame, text="Test d'entier", font=ctk.CTkFont(size=14, weight="bold"))
        int_label.pack(padx=10, pady=10, anchor="w")
        
        int_input_frame = ctk.CTkFrame(frame)
        int_input_frame.pack(padx=10, pady=5, fill="x")
        
        int_input_label = ctk.CTkLabel(int_input_frame, text="Entrez un entier:")
        int_input_label.pack(side="left", padx=10)
        
        self.int_input = ctk.CTkEntry(int_input_frame, width=200)
        self.int_input.pack(side="left", padx=10)
        
        int_test_button = ctk.CTkButton(int_input_frame, text="Tester", command=self.test_integer)
        int_test_button.pack(side="left", padx=10)
        
        # Float test
        float_label = ctk.CTkLabel(frame, text="Test de nombre réel/double", font=ctk.CTkFont(size=14, weight="bold"))
        float_label.pack(padx=10, pady=(20, 10), anchor="w")
        
        float_input_frame = ctk.CTkFrame(frame)
        float_input_frame.pack(padx=10, pady=5, fill="x")
        
        float_input_label = ctk.CTkLabel(float_input_frame, text="Entrez un nombre réel:")
        float_input_label.pack(side="left", padx=10)
        
        self.float_input = ctk.CTkEntry(float_input_frame, width=200)
        self.float_input.pack(side="left", padx=10)
        
        float_test_button = ctk.CTkButton(float_input_frame, text="Tester", command=self.test_float)
        float_test_button.pack(side="left", padx=10)
        
        return frame
    
    def create_arrays_matrices_frame(self):
        frame = ctk.CTkFrame(self.main_frame)
        
        # Array test
        array_label = ctk.CTkLabel(frame, text="Test de tableau", font=ctk.CTkFont(size=14, weight="bold"))
        array_label.pack(padx=10, pady=10, anchor="w")
        
        array_max_frame = ctk.CTkFrame(frame)
        array_max_frame.pack(padx=10, pady=5, fill="x")
        
        array_max_label = ctk.CTkLabel(array_max_frame, text="Taille maximale:")
        array_max_label.pack(side="left", padx=10)
        
        self.array_max_input = ctk.CTkEntry(array_max_frame, width=100)
        self.array_max_input.pack(side="left", padx=10)
        self.array_max_input.insert(0, "10")
        
        array_size_frame = ctk.CTkFrame(frame)
        array_size_frame.pack(padx=10, pady=5, fill="x")
        
        array_size_label = ctk.CTkLabel(array_size_frame, text="Taille du tableau à tester:")
        array_size_label.pack(side="left", padx=10)
        
        self.array_size_input = ctk.CTkEntry(array_size_frame, width=100)
        self.array_size_input.pack(side="left", padx=10)
        
        array_test_button = ctk.CTkButton(array_size_frame, text="Tester", command=self.test_array)
        array_test_button.pack(side="left", padx=10)
        
        # Matrix test
        matrix_label = ctk.CTkLabel(frame, text="Test de matrice", font=ctk.CTkFont(size=14, weight="bold"))
        matrix_label.pack(padx=10, pady=(20, 10), anchor="w")
        
        matrix_max_frame = ctk.CTkFrame(frame)
        matrix_max_frame.pack(padx=10, pady=5, fill="x")
        
        matrix_max_rows_label = ctk.CTkLabel(matrix_max_frame, text="Nombre max de lignes:")
        matrix_max_rows_label.pack(side="left", padx=10)
        
        self.matrix_max_rows_input = ctk.CTkEntry(matrix_max_frame, width=80)
        self.matrix_max_rows_input.pack(side="left", padx=10)
        self.matrix_max_rows_input.insert(0, "5")
        
        matrix_max_cols_label = ctk.CTkLabel(matrix_max_frame, text="Nombre max de colonnes:")
        matrix_max_cols_label.pack(side="left", padx=10)
        
        self.matrix_max_cols_input = ctk.CTkEntry(matrix_max_frame, width=80)
        self.matrix_max_cols_input.pack(side="left", padx=10)
        self.matrix_max_cols_input.insert(0, "5")
        
        matrix_size_frame = ctk.CTkFrame(frame)
        matrix_size_frame.pack(padx=10, pady=5, fill="x")
        
        matrix_rows_label = ctk.CTkLabel(matrix_size_frame, text="Nombre de lignes à tester:")
        matrix_rows_label.pack(side="left", padx=10)
        
        self.matrix_rows_input = ctk.CTkEntry(matrix_size_frame, width=80)
        self.matrix_rows_input.pack(side="left", padx=10)
        
        matrix_cols_label = ctk.CTkLabel(matrix_size_frame, text="Nombre de colonnes à tester:")
        matrix_cols_label.pack(side="left", padx=10)
        
        self.matrix_cols_input = ctk.CTkEntry(matrix_size_frame, width=80)
        self.matrix_cols_input.pack(side="left", padx=10)
        
        matrix_test_button = ctk.CTkButton(matrix_size_frame, text="Tester", command=self.test_matrix)
        matrix_test_button.pack(side="left", padx=10)
        
        return frame
    
    def create_lists_stacks_frame(self):
        frame = ctk.CTkFrame(self.main_frame)
        
        # List test
        list_label = ctk.CTkLabel(frame, text="Test de liste", font=ctk.CTkFont(size=14, weight="bold"))
        list_label.pack(padx=10, pady=10, anchor="w")
        
        list_max_frame = ctk.CTkFrame(frame)
        list_max_frame.pack(padx=10, pady=5, fill="x")
        
        list_max_label = ctk.CTkLabel(list_max_frame, text="Taille maximale:")
        list_max_label.pack(side="left", padx=10)
        
        self.list_max_input = ctk.CTkEntry(list_max_frame, width=100)
        self.list_max_input.pack(side="left", padx=10)
        self.list_max_input.insert(0, "10")
        
        list_size_frame = ctk.CTkFrame(frame)
        list_size_frame.pack(padx=10, pady=5, fill="x")
        
        list_size_label = ctk.CTkLabel(list_size_frame, text="Taille de la liste à tester:")
        list_size_label.pack(side="left", padx=10)
        
        self.list_size_input = ctk.CTkEntry(list_size_frame, width=100)
        self.list_size_input.pack(side="left", padx=10)
        
        list_test_button = ctk.CTkButton(list_size_frame, text="Tester", command=self.test_list)
        list_test_button.pack(side="left", padx=10)
        
        # Stack test
        stack_label = ctk.CTkLabel(frame, text="Test de pile", font=ctk.CTkFont(size=14, weight="bold"))
        stack_label.pack(padx=10, pady=(20, 10), anchor="w")
        
        stack_max_frame = ctk.CTkFrame(frame)
        stack_max_frame.pack(padx=10, pady=5, fill="x")
        
        stack_max_label = ctk.CTkLabel(stack_max_frame, text="Taille maximale:")
        stack_max_label.pack(side="left", padx=10)
        
        self.stack_max_input = ctk.CTkEntry(stack_max_frame, width=100)
        self.stack_max_input.pack(side="left", padx=10)
        self.stack_max_input.insert(0, "10")
        
        stack_size_frame = ctk.CTkFrame(frame)
        stack_size_frame.pack(padx=10, pady=5, fill="x")
        
        stack_size_label = ctk.CTkLabel(stack_size_frame, text="Taille de la pile à tester:")
        stack_size_label.pack(side="left", padx=10)
        
        self.stack_size_input = ctk.CTkEntry(stack_size_frame, width=100)
        self.stack_size_input.pack(side="left", padx=10)
        
        stack_test_button = ctk.CTkButton(stack_size_frame, text="Tester", command=self.test_stack)
        stack_test_button.pack(side="left", padx=10)
        
        return frame
    
    def create_memory_frame(self):
        frame = ctk.CTkFrame(self.main_frame)
        
        # Memory test
        memory_label = ctk.CTkLabel(frame, text="Test de mémoire", font=ctk.CTkFont(size=14, weight="bold"))
        memory_label.pack(padx=10, pady=10, anchor="w")
        
        memory_test_button = ctk.CTkButton(frame, text="Tester la mémoire RAM", command=self.test_memory)
        memory_test_button.pack(padx=10, pady=10)
        
        # Disk test
        disk_label = ctk.CTkLabel(frame, text="Test de disque dur", font=ctk.CTkFont(size=14, weight="bold"))
        disk_label.pack(padx=10, pady=(20, 10), anchor="w")
        
        disk_frame = ctk.CTkFrame(frame)
        disk_frame.pack(padx=10, pady=5, fill="x")
        
        disk_path_label = ctk.CTkLabel(disk_frame, text="Chemin du disque:")
        disk_path_label.pack(side="left", padx=10)
        
        self.disk_path_input = ctk.CTkEntry(disk_frame, width=200)
        self.disk_path_input.pack(side="left", padx=10)
        # Set appropriate root directory based on OS
        root_dir = "C:\\" if platform.system() == "Windows" else "/"
        self.disk_path_input.insert(0, root_dir)
        
        disk_test_button = ctk.CTkButton(disk_frame, text="Tester", command=self.test_disk)
        disk_test_button.pack(side="left", padx=10)
        
        # Removable drives test
        removable_label = ctk.CTkLabel(frame, text="Test de disques amovibles", font=ctk.CTkFont(size=14, weight="bold"))
        removable_label.pack(padx=10, pady=(20, 10), anchor="w")
        
        removable_test_button = ctk.CTkButton(frame, text="Tester les disques amovibles", command=self.test_removable_drives)
        removable_test_button.pack(padx=10, pady=10)
        
        return frame
    
    def create_buffer_overflow_frame(self):
        frame = ctk.CTkFrame(self.main_frame)
        
        # Buffer overflow simulation
        buffer_label = ctk.CTkLabel(frame, text="Simulation de dépassement de tampon", 
                                    font=ctk.CTkFont(size=14, weight="bold"))
        buffer_label.pack(padx=10, pady=10, anchor="w")
        
        buffer_info = ctk.CTkLabel(frame, text="Cette simulation va tenter d'allouer un tableau de grande taille en mémoire.\n"
                                              "Un dépassement se produira si la mémoire est insuffisante.")
        buffer_info.pack(padx=10, pady=10)
        
        buffer_frame = ctk.CTkFrame(frame)
        buffer_frame.pack(padx=10, pady=5, fill="x")
        
        buffer_size_label = ctk.CTkLabel(buffer_frame, text="Taille du tableau à allouer:")
        buffer_size_label.pack(side="left", padx=10)
        
        self.buffer_size_input = ctk.CTkEntry(buffer_frame, width=200)
        self.buffer_size_input.pack(side="left", padx=10)
        self.buffer_size_input.insert(0, "100000000")
        
        buffer_test_button = ctk.CTkButton(buffer_frame, text="Tester", command=self.test_buffer_overflow)
        buffer_test_button.pack(side="left", padx=10)
        
        return frame
    
    # Test methods
    def test_character(self):
        try:
            char = self.char_input.get()
            result = self.detector.check_character(char)
            self.append_result(f"Test de caractère: {self.format_result_gui(result)}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du test de caractère: {str(e)}")
    
    def test_string(self):
        try:
            string = self.string_input.get()
            max_length = int(self.string_max_input.get())
            result = self.detector.check_string(string, max_length)
            self.append_result(f"Test de chaîne: {self.format_result_gui(result)}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du test de chaîne: {str(e)}")
    
    def test_integer(self):
        try:
            value = int(self.int_input.get())
            result = self.detector.check_number(value, is_integer=True)
            self.append_result(f"Test d'entier: {self.format_result_gui(result)}")
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer un entier valide.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du test d'entier: {str(e)}")
    
    def test_float(self):
        try:
            value = float(self.float_input.get())
            result = self.detector.check_number(value, is_integer=False)
            self.append_result(f"Test de nombre réel: {self.format_result_gui(result)}")
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer un nombre réel valide.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du test de nombre réel: {str(e)}")
    
    def test_array(self):
        try:
            size = int(self.array_max_input.get())
            test_size = int(self.array_size_input.get())
            test_array = [0] * test_size
            result = self.detector.check_array(test_array, size)
            self.append_result(f"Test de tableau: {self.format_result_gui(result)}")
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer des tailles valides.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du test de tableau: {str(e)}")
    
    def test_matrix(self):
        try:
            max_rows = int(self.matrix_max_rows_input.get())
            max_cols = int(self.matrix_max_cols_input.get())
            test_rows = int(self.matrix_rows_input.get())
            test_cols = int(self.matrix_cols_input.get())
            test_matrix = [[0 for _ in range(test_cols)] for _ in range(test_rows)]
            result = self.detector.check_matrix(test_matrix, max_rows, max_cols)
            self.append_result(f"Test de matrice: {self.format_result_gui(result)}")
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer des dimensions valides.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du test de matrice: {str(e)}")
    
    def test_list(self):
        try:
            max_size = int(self.list_max_input.get())
            test_size = int(self.list_size_input.get())
            test_list = [0] * test_size
            result = self.detector.check_list(test_list, max_size)
            self.append_result(f"Test de liste: {self.format_result_gui(result)}")
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer des tailles valides.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du test de liste: {str(e)}")
    
    def test_stack(self):
        try:
            max_size = int(self.stack_max_input.get())
            test_size = int(self.stack_size_input.get())
            test_stack = [0] * test_size
            result = self.detector.check_stack(test_stack, max_size)
            self.append_result(f"Test de pile: {self.format_result_gui(result)}")
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer des tailles valides.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du test de pile: {str(e)}")
    
    def test_memory(self):
        try:
            result = self.detector.check_memory_usage()
            self.append_result(f"Test de mémoire RAM: {self.format_result_gui(result)}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du test de mémoire: {str(e)}")
    
    def test_disk(self):
        try:
            path = self.disk_path_input.get()
            result = self.detector.check_disk_usage(path)
            self.append_result(f"Test de disque: {self.format_result_gui(result)}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du test de disque: {str(e)}")
    
    def test_removable_drives(self):
        try:
            result = self.detector.check_removable_drives()
            self.append_result(f"Test de disques amovibles: {len(result['drives'])} disque(s) détecté(s)")
            if result["drives"]:
                for drive in result["drives"]:
                    self.append_result(f"- {drive['device']}: {drive['percent']:.1f}% utilisé, {drive['free_gb']:.2f} GB libre")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du test de disques amovibles: {str(e)}")
    
    def test_buffer_overflow(self):
        try:
            size = int(self.buffer_size_input.get())
            result = self.detector.simulate_buffer_overflow(size)
            self.append_result(f"Simulation de dépassement: {self.format_result_gui(result)}")
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer une taille valide.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la simulation: {str(e)}")


def main():
    """Main function to run the GUI application"""
    detector = BufferOverflowDetector()
    gui = BufferOverflowDetectorGUI(detector)
    gui.mainloop()


if __name__ == "__main__":
    main()