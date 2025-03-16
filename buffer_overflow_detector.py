import sys
import platform
import psutil
import time
from typing import Any, List, Dict, Union
from colorama import init, Fore, Style

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

def format_result(result: Dict[str, Any]) -> str:
    """
    Formats a result dictionary into a readable string with color.
    
    Args:
        result: The result dictionary from a check method
        
    Returns:
        Formatted string with color-coded status
    """
    output = ""
    
    if result["overflow"]:
        output += f"{Fore.RED}[OVERFLOW DÉTECTÉ]{Style.RESET_ALL} "
        output += result["message"]
    else:
        output += f"{Fore.GREEN}[OK]{Style.RESET_ALL} "
        
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

def get_user_input():
    """Gets user input for testing different overflow scenarios"""
    print(f"\n{Fore.CYAN}=== Détecteur de Dépassement de Tampon ===={Style.RESET_ALL}")
    print("Choisissez une option à tester:")
    print("1. Caractère et chaîne de caractères")
    print("2. Entiers, réels et doubles")
    print("3. Tableaux et matrices")
    print("4. Listes et piles")
    print("5. Mémoire (RAM, disque dur, disque amovible)")
    print("6. Simulation de dépassement de tampon")
    print("7. Quitter")
    
    choice = input("Entrez le numéro de l'option: ")
    
    try:
        return int(choice)
    except ValueError:
        print(f"{Fore.RED}Entrée invalide. Veuillez entrer un nombre entre 1 et 7.{Style.RESET_ALL}")
        return 0

def test_character_and_string(detector):
    """Tests character and string overflow detection"""
    print(f"\n{Fore.YELLOW}=== Test de caractère et chaîne de caractères ==={Style.RESET_ALL}")
    
    # Test character
    char = input("Entrez un caractère: ")
    result = detector.check_character(char)
    print(format_result(result))
    
    # Test string
    max_length = input("Entrez la longueur maximale pour la chaîne (ou appuyez sur Entrée pour la valeur par défaut 255): ")
    max_length = int(max_length) if max_length.strip() else 255
    
    string = input(f"Entrez une chaîne de caractères (max suggéré: {max_length}): ")
    result = detector.check_string(string, max_length)
    print(format_result(result))

def test_numbers(detector):
    """Tests number overflow detection"""
    print(f"\n{Fore.YELLOW}=== Test d'entiers, réels et doubles ==={Style.RESET_ALL}")
    
    print("\nTest d'entier:")
    try:
        value = int(input("Entrez un entier (essayez une très grande valeur): "))
        result = detector.check_number(value, is_integer=True)
        print(format_result(result))
    except ValueError:
        print(f"{Fore.RED}Entrée invalide pour un entier.{Style.RESET_ALL}")
    
    print("\nTest de nombre réel/double:")
    try:
        value = float(input("Entrez un nombre réel/double (essayez une très grande valeur): "))
        result = detector.check_number(value, is_integer=False)
        print(format_result(result))
    except ValueError:
        print(f"{Fore.RED}Entrée invalide pour un nombre réel.{Style.RESET_ALL}")

def test_arrays_and_matrices(detector):
    """Tests array and matrix overflow detection"""
    print(f"\n{Fore.YELLOW}=== Test de tableaux et matrices ==={Style.RESET_ALL}")
    
    # Test array
    print("\nTest de tableau:")
    try:
        size = int(input("Entrez la taille maximale du tableau: "))
        test_size = int(input(f"Entrez la taille du tableau à tester (essayez > {size}): "))
        
        # Create an array of the specified size
        test_array = [0] * test_size
        
        result = detector.check_array(test_array, size)
        print(format_result(result))
    except ValueError:
        print(f"{Fore.RED}Entrée invalide pour la taille du tableau.{Style.RESET_ALL}")
    
    # Test matrix
    print("\nTest de matrice:")
    try:
        max_rows = int(input("Entrez le nombre maximum de lignes: "))
        max_cols = int(input("Entrez le nombre maximum de colonnes: "))
        
        test_rows = int(input(f"Entrez le nombre de lignes à tester (essayez > {max_rows}): "))
        test_cols = int(input(f"Entrez le nombre de colonnes à tester (essayez > {max_cols}): "))
        
        # Create a matrix of the specified dimensions
        test_matrix = [[0 for _ in range(test_cols)] for _ in range(test_rows)]
        
        result = detector.check_matrix(test_matrix, max_rows, max_cols)
        print(format_result(result))
    except ValueError:
        print(f"{Fore.RED}Entrée invalide pour les dimensions de la matrice.{Style.RESET_ALL}")

def test_lists_and_stacks(detector):
    """Tests list and stack overflow detection"""
    print(f"\n{Fore.YELLOW}=== Test de listes et piles ==={Style.RESET_ALL}")
    
    # Test list
    print("\nTest de liste:")
    try:
        max_size = int(input("Entrez la taille maximale de la liste: "))
        test_size = int(input(f"Entrez la taille de la liste à tester (essayez > {max_size}): "))
        
        # Create a list of the specified size
        test_list = [0] * test_size
        
        result = detector.check_list(test_list, max_size)
        print(format_result(result))
    except ValueError:
        print(f"{Fore.RED}Entrée invalide pour la taille de la liste.{Style.RESET_ALL}")
    
    # Test stack
    print("\nTest de pile:")
    try:
        max_size = int(input("Entrez la taille maximale de la pile: "))
        test_size = int(input(f"Entrez la taille de la pile à tester (essayez > {max_size}): "))
        
        # Create a stack of the specified size
        test_stack = [0] * test_size
        
        result = detector.check_stack(test_stack, max_size)
        print(format_result(result))
    except ValueError:
        print(f"{Fore.RED}Entrée invalide pour la taille de la pile.{Style.RESET_ALL}")

def test_memory(detector):
    """Tests memory usage detection"""
    print(f"\n{Fore.YELLOW}=== Test de mémoire (RAM, disque dur, disque amovible) ==={Style.RESET_ALL}")
    
    # Check RAM
    print("\nTest de la mémoire RAM:")
    result = detector.check_memory_usage()
    print(format_result(result))
    
    # Check disk
    print("\nTest du disque dur:")
    # Get appropriate root directory based on OS
    root_dir = "C:\\" if platform.system() == "Windows" else "/"
    result = detector.check_disk_usage(root_dir)
    print(format_result(result))
    
    # Check removable drives
    print("\nTest des disques amovibles:")
    result = detector.check_removable_drives()
    if result["drives"]:
        print(format_result(result))
        print("\nDisques amovibles détectés:")
        for i, drive in enumerate(result["drives"]):
            print(f"{i+1}. {drive['device']} ({drive['percent']:.1f}% utilisé, {drive['free_gb']:.2f} GB libre)")
    else:
        print(f"{Fore.YELLOW}Aucun disque amovible détecté ou accessible.{Style.RESET_ALL}")

def test_buffer_overflow_simulation(detector):
    """Tests buffer overflow simulation"""
    print(f"\n{Fore.YELLOW}=== Simulation de dépassement de tampon ==={Style.RESET_ALL}")
    print("Cette simulation va tenter d'allouer un tableau de grande taille en mémoire.")
    print("Un dépassement se produira si la mémoire est insuffisante.")
    
    try:
        size = int(input("Entrez la taille du tableau à allouer (essayez une grande valeur comme 100000000): "))
        result = detector.simulate_buffer_overflow(size)
        print(format_result(result))
    except ValueError:
        print(f"{Fore.RED}Entrée invalide pour la taille du tableau.{Style.RESET_ALL}")

def main():
    """Main function"""
    detector = BufferOverflowDetector()
    
    while True:
        choice = get_user_input()
        
        if choice == 1:
            test_character_and_string(detector)
        elif choice == 2:
            test_numbers(detector)
        elif choice == 3:
            test_arrays_and_matrices(detector)
        elif choice == 4:
            test_lists_and_stacks(detector)
        elif choice == 5:
            test_memory(detector)
        elif choice == 6:
            test_buffer_overflow_simulation(detector)
        elif choice == 7:
            print(f"\n{Fore.CYAN}Au revoir!{Style.RESET_ALL}")
            break
        else:
            print(f"{Fore.RED}Option invalide. Veuillez entrer un nombre entre 1 et 7.{Style.RESET_ALL}")
        
        input("\nAppuyez sur Entrée pour continuer...")

if __name__ == "__main__":
    main()