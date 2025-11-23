import os,re
from typing import *
import xml.etree.ElementTree as ET
from datetime import datetime

class Debugger:
    """
    Debugger is a professional utility class for printing structured and color-coded debug messages
    to the terminal. It supports multiple message levels, ANSI color coding, custom colors, and
    indentation levels for hierarchical debug output.

    Features:
    - Multiple message types: INFO, DEBUG, SUCCESS, WARNING, ERROR, CRITICAL, CUSTOM
    - ANSI color-coded output if supported; automatically enabled on Windows
    - Custom colors for user-defined messages
    - Indentation based on debug level for hierarchical debugging
    - Simple API for professional logging in CLI applications
    """

    # Default ANSI color codes and symbols for each message type
    COLORS = {
        "RESET": "\033[0m",
        "BRIGHT": "\033[1m",
        "INFO": "\033[1;94m",      # Bright Blue
        "DEBUG": "\033[1;36m",     # Cyan
        "SUCCESS": "\033[1;92m",   # Bright Green
        "WARNING": "\033[1;93m",   # Yellow
        "ERROR": "\033[1;91m",     # Bright Red
        "CRITICAL": "\033[1;41m",  # White text on Red background
        "CUSTOM": "\033[1;95m",    # Magenta default
    }

    SYMBOLS = {
        "INFO": "ℹ",
        "DEBUG": "🐞",
        "SUCCESS": "✔",
        "WARNING": "⚠",
        "ERROR": "✖",
        "CRITICAL": "‼",
        "CUSTOM": "*",
    }

    def __init__(self, level: Optional[int] = 0, DefaultSymbol:Optional[bool] = False):
        """
        Initialize the Debugger.

        :param level: Optional integer debug level. Each level adds a tab '\t' indentation to messages.
        :param DefaultSymbol: Optional default symbol usage. Default symbols are automatically used in debug messages.
        """
        self.level = level
        self.DefaultSymbol = DefaultSymbol
        self.ansi = self._enable_ansi()

    def _enable_ansi(self) -> bool:
        """
        Enable ANSI escape sequences if supported by the terminal.

        Windows: Uses Windows API to enable virtual terminal processing.
        Linux/MacOS: Checks if stdout is a terminal (isatty).

        :return: True if ANSI codes can be used, False otherwise
        """
        try:
            if os.name == "nt":
                import ctypes
                kernel32 = ctypes.windll.kernel32
                handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
                mode = ctypes.c_uint()
                if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                    # ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
                    kernel32.SetConsoleMode(handle, mode.value | 0x0004)
                    return True
                return False
            else:
                return sys.stdout.isatty()
        except Exception:
            return False

    def _print(self, message_type: str, message: str, color: Optional[str] = None, symbol: Optional[str] = None):
        """
        Internal method to print a message with optional color, symbol, and indentation.

        :param message_type: The type of message, e.g., INFO, DEBUG, ERROR
        :param message: The message string to print
        :param color: Optional custom ANSI color code (overrides default)
        :param symbol: Optional symbol to display before the message type
        """
        indent = '\t' * self.level
        ansi_color = color if color else self.COLORS.get(message_type.upper(), "")
        reset_color = self.COLORS["RESET"]
        sym = symbol if symbol else (self.SYMBOLS.get(message_type.upper(), "") if self.DefaultSymbol else "")
        if self.ansi and ansi_color:
            print(f"{indent}[{ansi_color}{sym}{message_type.upper()}{reset_color}]\t{message}")
        else:
            print(f"{indent}[{message_type.upper()}]\t{message}")

    # -------------------- Standard Debug Levels --------------------

    def info(self, message: str):
        """
        Print an informational message in bright blue.

        :param message: The message string to print
        """
        self._print("INFO", message)

    def debug(self, message: str):
        """
        Print a debug message in cyan, for development diagnostics.

        :param message: The message string to print
        """
        self._print("DEBUG", message)

    def success(self, message: str):
        """
        Print a success message in bright green, indicating a successful operation.

        :param message: The message string to print
        """
        self._print("SUCCESS", message)

    def warning(self, message: str):
        """
        Print a warning message in yellow, highlighting potential issues.

        :param message: The message string to print
        """
        self._print("WARNING", message)

    def error(self, message: str):
        """
        Print an error message in bright red, indicating a recoverable failure.

        :param message: The message string to print
        """
        self._print("ERROR", message)

    def critical(self, message: str):
        """
        Print a critical message in white text on red background, for severe failures.

        :param message: The message string to print
        """
        self._print("CRITICAL", message)

    def custom(self, message: str, color_code: str = "\033[1;95m", symbol: str = "*"):
        """
        Print a custom message with a user-defined color and symbol.

        :param message: The message string to print
        :param color_code: ANSI escape code string for custom color (default is bright magenta)
        :param symbol: Optional symbol to display before the message type
        """
        self._print("CUSTOM", message, color=color_code, symbol=symbol)

    def set_level(self, level: int):
        """
        Set the debug level dynamically.

        :param level: New debug level. Each level adds a tab '\t' indentation.
        """
        self.level = level

        

class File:
    """
    A comprehensive file processing class that supports various operations on 
    JSON, TXT, CSV, LOG, INI, YML and other files with advanced error handling,
    directory management and flexible path processing features based on file-folder configuration.
    """

    SUPPORTED_FORMATS = ['.json', '.txt', '.log', '.pdf', '.xml', '.csv', '.yml', '.yaml', '.ini', '.properties', '.md', '.rtf', '.html', '.css', '.js','.tex','.py']  # Supported file formats

    def __init__(self, filefolder: Optional[str] = None, debug:bool=False,debugger:Optional[Debugger]=None):
        """
        Initializes the File object with an optional filefolder for default file path handling.

        :param filefolder: Optional root directory for file operations, if specified.
        :param debug: Optional flag to enable debug mode for detailed error or function messages.
        """
        self.filefolder = filefolder
        self.debug = debug
        self.debugger = Debugger() if debugger==None else debugger

    def _default_dict(self):
        """
        Generates a nested defaultdict structure to allow safe access to deeply nested keys without risk of KeyError.
        """
        from collections import defaultdict
        return defaultdict(self._default_dict)

    def _recursive_update(self, target, default):
        """
        Recursively updates a target dictionary by filling in missing keys from a default dictionary.

        :param target: The dictionary to be updated.
        :param default: The dictionary containing default keys and values.
        :return: The updated target dictionary with all keys from the default dictionary.
        """
        for key, value in default.items():
            if isinstance(value, dict):
                target[key] = self._recursive_update(target.get(key, {}), value)
            else:
                target.setdefault(key, value)
        return target

    def _validate_and_prepare_path(self, path: str):
        """
        Converts a file path to an absolute path, optionally prepends filefolder, and ensures directory existence.

        :param path: The file path to validate and prepare.
        :return: An absolute file path, creating any required directories.
        """
        # If the path is relative and filefolder is provided, prepend filefolder to the path
        if not os.path.isabs(path) and self.filefolder and not (path.startswith("./") or path.startswith("../")):
            path = os.path.join(self.filefolder, path)
        
        absolute_path = os.path.abspath(path)
        os.makedirs(os.path.dirname(absolute_path), exist_ok=True)  # Create required directories if missing
        return absolute_path
    
    def get_info(self, path: str) -> dict:
        """
        Retrieves detailed information about a file or folder.

        :param path: Path to the file or directory.
        :return: A dictionary containing size, type, extension (if file), mode, and last write time.
        """
        import stat
        import time
        file_path = self._validate_and_prepare_path(path)

        if not os.path.exists(file_path):
            if self.debug:
                self.debugger.error(f"Path does not exist: {file_path}")
            return {}

        info = {
            "path": file_path,
            "is_file": os.path.isfile(file_path),
            "is_directory": os.path.isdir(file_path),
            "size": os.path.getsize(file_path) if os.path.isfile(file_path) else None,
            "extension": os.path.splitext(file_path)[1] if os.path.isfile(file_path) else None,
            "mode": stat.filemode(os.stat(file_path).st_mode),
            "last_modified": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(file_path)))
        }

        if self.debug:
            self.debugger.info(f"Retrieved info: {info}")
        return info
    
    def rename_file(self, old_path: str, new_name: str) -> bool:
        """
        Renames a file to a new name in the same directory.

        :param old_path: The current file path.
        :param new_name: The new file name.
        :return: True if renamed successfully, otherwise False.
        """
        file_path = self._validate_and_prepare_path(old_path)

        if not os.path.isfile(file_path):
            if self.debug:
                self.debugger.error(f"File not found: {file_path}")
            return False

        directory = os.path.dirname(file_path)
        new_path = os.path.join(directory, new_name)

        try:
            os.rename(file_path, new_path)
            if self.debug:
                self.debugger.success(f"Renamed file: {file_path} -> {new_path}")
            return True
        except Exception as e:
            if self.debug:
                self.debugger.error(f"Rename failed: {e}")
            return False

    def rename_folder(self, old_path: str, new_name: str) -> bool:
        """
        Renames a folder to a new name in the same directory.

        :param old_path: The current folder path.
        :param new_name: The new folder name.
        :return: True if renamed successfully, otherwise False.
        """
        folder_path = self._validate_and_prepare_path(old_path)

        if not os.path.isdir(folder_path):
            if self.debug:
                self.debugger.error(f"Folder not found: {folder_path}")
            return False

        parent_directory = os.path.dirname(folder_path)
        new_path = os.path.join(parent_directory, new_name)

        try:
            os.rename(folder_path, new_path)
            if self.debug:
                self.debugger.success(f"Renamed folder: {folder_path} -> {new_path}")
            return True
        except Exception as e:
            if self.debug:
                self.debugger.error(f"Rename failed: {e}")
            return False

    def create_shortcut(self, target_path: str, shortcut_path: str, description: str = "") -> bool:
        """
        Creates a Windows shortcut (.lnk) to the specified target file or folder.

        :param target_path: The file or folder path to which the shortcut points.
        :param shortcut_path: The full path where the shortcut should be created (including .lnk extension).
        :param description: Optional description for the shortcut.
        :return: True if the shortcut is created successfully, otherwise False.
        """
        import win32com.client
        try:
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortcut(shortcut_path)
            shortcut.TargetPath = target_path
            shortcut.Description = description
            shortcut.Save()
            
            if self.debug:
                self.debugger.success(f"Created shortcut: {shortcut_path} -> {target_path}")
            return True
        except Exception as e:
            if self.debug:
                self.debugger.error(f"Failed to create shortcut: {e}")
            return False

    def list_files_and_folders(self, path: Optional[str] = None) -> list:
        """
        Lists all files and folders in the specified directory.
        If no path is specified, the default filefolder is used.

        :param path: Optional path to the directory to list files and folders from.
        :return: A list of file and folder names in the specified directory.
        """
        directory = path or self.filefolder
        
        if not directory:
            raise ValueError("\033[31;1mPath or default filefolder must be specified.\033[0m")
        
        absolute_path = self._validate_and_prepare_path(directory)
        
        try:
            return os.listdir(absolute_path)  
        except FileNotFoundError:
            if self.debug:
                self.debugger.error(f"Directory not found: {absolute_path}")
            return []
        except PermissionError:
            if self.debug:
                self.debugger.error(f"Permission denied: {absolute_path}")
            return []
    def create_folder(self, folder_path: str) -> bool:
        """
        Creates a new folder at the specified path. If the folder already exists, no action is taken.

        :param folder_path: The path to the folder to be created.
        :return: True if the folder was created successfully or already exists, False if an error occurred.
        """
        absolute_path = self._validate_and_prepare_path(folder_path)
        try:
            os.makedirs(absolute_path, exist_ok=True)
            if self.debug:
                self.debugger.success(f"Folder created or already exists: {absolute_path}")
            return True
        except Exception as e:
            if self.debug:
                self.debugger.error(f"Error creating folder: {absolute_path} - {e}")
            return False

    def copy_file(self, source: str, destination: str) -> bool:
        """
        Copies a file from the source path to the destination path.

        :param source: The source file path.
        :param destination: The destination file path.
        :return: True if the file was copied successfully, False if an error occurred.
        """
        source_path = self._validate_and_prepare_path(source)
        destination_path = self._validate_and_prepare_path(destination)

        try:
            import shutil
            shutil.copy2(source_path, destination_path)  # Copy with metadata
            if self.debug:
                self.debugger.success(f"File copied from: {source_path} to: {destination_path}")
            return True
        except FileNotFoundError:
            if self.debug:
                self.debugger.error(f"Source file not found: {source_path}")
            return False
        except PermissionError:
            if self.debug:
                self.debugger.error(f"Permission denied: {destination_path}")
            return False
        except Exception as e:
            if self.debug:
                self.debugger.error(f"Error copying file: {source_path} - {e}")
            return False

    def move_file(self, source: str, destination: str) -> bool:
        """
        Moves a file from the source path to the destination path.

        :param source: The source file path.
        :param destination: The destination file path.
        :return: True if the file was moved successfully, False if an error occurred.
        """
        source_path = self._validate_and_prepare_path(source)
        destination_path = self._validate_and_prepare_path(destination)

        try:
            import shutil
            shutil.move(source_path, destination_path)
            if self.debug:
                self.debugger.success(f"File moved from: {source_path} to: {destination_path}")
            return True
        except FileNotFoundError:
            if self.debug:
                self.debugger.error(f"Source file not found: {source_path}")
            return False
        except PermissionError:
            if self.debug:
                self.debugger.error(f"Permission denied: {destination_path}")
            return False
        except Exception as e:
            if self.debug:
                self.debugger.error(f"Error moving file: {source_path} - {e}")
            return False

    def move_folder(self, source: str, destination: str) -> bool:
        """
        Moves a folder and its contents from the source path to the destination path.

        :param source: The source folder path.
        :param destination: The destination folder path.
        :return: True if the folder was moved successfully, False if an error occurred.
        """
        source_path = self._validate_and_prepare_path(source)
        destination_path = self._validate_and_prepare_path(destination)

        try:
            import shutil
            shutil.move(source_path, destination_path)
            if self.debug:
                self.debugger.success(f"Folder moved from: {source_path} to: {destination_path}")
            return True
        except FileNotFoundError:
            if self.debug:
                self.debugger.error(f"Source folder not found: {source_path}")
            return False
        except PermissionError:
            if self.debug:
                self.debugger.error(f"Permission denied: {destination_path}")
            return False
        except Exception as e:
            if self.debug:
                self.debugger.error(f"Error moving folder: {source_path} - {e}")
            return False


    # JSON File Operations

    def json_read(self, path: str, default: Optional[Union[dict, list]] = None) -> Union[dict, list]:
        """
        Reads data from a JSON file and returns it as a dictionary or list.
        If the file does not exist, creates an empty JSON file and returns the default value if provided.

        :param path: Path to the JSON file.
        :param default: Optional default dictionary or list structure.
        :return: A dictionary or list containing JSON data or default values if the file is missing.
        """
        import json
        from collections import defaultdict
        file_path = self._validate_and_prepare_path(path)
        
        if not os.path.exists(file_path):
            # If the file does not exist, create an empty JSON file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(default if default is not None else {}, f)
            data = default if default is not None else {}
            
            if self.debug:
                self.debugger.success(f"Created empty JSON file: {file_path}")
        else:
            try:
                # Open and read the JSON file
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f, object_hook=lambda d: defaultdict(self._default_dict, d) if isinstance(d, dict) else d)
                    
                if self.debug:
                    self.debugger.success(f"Successfully loaded JSON file: {file_path}")
            except json.JSONDecodeError as e:
                # Handle JSON decoding errors
                print(f"\033[31mJSON decoding error while reading \033[35m{path}\033[0m: \033[36m{e}\033[0m")
                data = default if default is not None else {}
        
        # Ensure the returned type matches the default type if provided
        if isinstance(default, dict) and not isinstance(data, dict):
            data = {}
        elif isinstance(default, list) and not isinstance(data, list):
            data = []
        
        # If default is provided, update the data structure accordingly
        if default and isinstance(data, dict):
            data = self._recursive_update(data, default)
        
        return data

    def json_write(self, path: str, data: dict|list):
        """
        Writes a dictionary to a JSON file, ensuring directory structure exists.

        :param path: Path to the JSON file.
        :param data: A dictionary containing data to write.
        :raises TypeError: If data is not a dictionary.
        """
        import json
        from collections import defaultdict
        if not isinstance(data, dict) and not isinstance(data, list):
            raise TypeError("Data to be written must be a dictionary.")
        
        file_path = self._validate_and_prepare_path(path)

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
                if self.debug:
                    self.debugger.success(f"Wrote JSON data to: {file_path}")
        except IOError as e:
            print(f"\033[31mAn error occurred while writing to JSON file \033[35m{path}\033[0m: \033[36m{e}\033[0m")

    # TXT File Operations

    def txt_read_str(self, path: str) -> str:
        """
        Reads a text file and returns its entire content as a single string.

        :param path: Path to the text file.
        :return: A string containing the file's content.
        """
        file_path = self._validate_and_prepare_path(path)
        
        if not os.path.exists(file_path):
            open(file_path, 'w').close()  # Create an empty file if it does not exist
            if self.debug:
                self.debugger.success(f"Created empty TXT file: {file_path}")
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return content

    def txt_read_linear(self, path: str) -> Dict[str, str]:
        """
        Reads a text file line by line, returning a dictionary with line numbers as keys.

        :param path: Path to the text file.
        :return: A dictionary where each line is mapped by line numbers.
        """
        file_path = self._validate_and_prepare_path(path)
        
        if not os.path.exists(file_path):
            open(file_path, 'w').close()  # Create an empty file if it does not exist
            if self.debug:
                self.debugger.success(f"Created empty TXT file: {file_path}")
            
        lines = {}
        with open(file_path, 'r', encoding='utf-8') as f:
            for idx, line in enumerate(f, 1):
                lines[str(idx)] = line.strip()
        
        return lines

    def txt_write_str(self, path: str, content: str):
        """
        Writes a single string content to a text file, overwriting any existing data.

        :param path: Path to the text file.
        :param content: The content to be written to the file.
        """
        file_path = self._validate_and_prepare_path(path)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def txt_write_linear(self, path: str, data: Dict[int, str]):
        """
        Writes dictionary entries to a text file where keys are line numbers and values are line content.

        :param path: Path to the text file.
        :param data: Dictionary where each key represents a line number and value represents content.
        """
        file_path = self._validate_and_prepare_path(path)
        max_line = max(data.keys())
        
        with open(file_path, 'w', encoding='utf-8') as file:
            for line_num in range(1, max_line + 1):
                line_content = data.get(line_num, "")
                file.write(line_content + '\n')

    # LOG File Operations

    def log_read(self, path: str) -> Dict[str, str]:
        """
        Reads a log file line by line, returning each line as an entry in a dictionary with line numbers as keys.

        :param path: Path to the log file.
        :return: Dictionary where each key is a line number and value is the line content.
        """
        return self.txt_read_linear(path)

    def log_write(self, path: str, content: str):
        """
        Writes a single log entry to a log file, appending it to the end of the file.

        :param path: Path to the log file.
        :param content: Log entry to append to the file.
        """
        file_path = self._validate_and_prepare_path(path)
        
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(content + '\n')
            if self.debug:
                self.debugger.success(f"Wrote LOG to: {file_path}")

    def log_write_entry(self, path: str, entry: str):
        """
        Writes a log entry with a timestamp to the log file, appending it to the end of the file.

        :param path: Path to the log file.
        :param entry: The log entry text.
        """
        from datetime import datetime

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"{timestamp} - {entry}"
        
        self.log_write(path, log_entry)

    # PDF File Operations

    def pdf_read(self, path: str) -> str:
        """
        Reads a PDF file and returns its text content as a single string.

        :param path: Path to the PDF file.
        :return: A string containing the text content of the PDF.
        :raises FileNotFoundError: If the PDF file does not exist.
        """
        file_path = self._validate_and_prepare_path(path)
        content = []
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {path} does not exist.")
        from PyPDF2 import PdfReader, PdfWriter
        reader = PdfReader(file_path)
        for page in reader.pages:
            content.append(page.extract_text())
        
        return "\n".join(content)

    def pdf_write(self, path: str, content: str):
        """
        Writes text content to a PDF file, creating a new file or overwriting an existing one.

        :param path: Path to the PDF file.
        :param content: The text content to write to the PDF.
        """
        file_path = self._validate_and_prepare_path(path)
        from reportlab.pdfgen import canvas
        # Set up a canvas to write text content to a new PDF
        c = canvas.Canvas(file_path)
        text_obj = c.beginText(40, 800)  # Position the text object at an initial Y-position
        
        # Write each line of content to the PDF
        for line in content.splitlines():
            text_obj.textLine(line)
        
        c.drawText(text_obj)
        c.save()
    def xml_read(self, path: str) -> Optional[Dict[str, Any]]:
        """
        Reads an XML file and parses it into a Python dictionary.

        :param path: Path to the XML file.
        :return: A dictionary representing the XML structure, or None if the file doesn't exist or is invalid.
        :raises FileNotFoundError: If the XML file does not exist.
        :raises ET.ParseError: If there is an error parsing the XML file.
        """
        file_path = self._validate_and_prepare_path(path)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {path} does not exist.")
        
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Convert XML tree to a nested dictionary
            return self._xml_to_dict(root)
        except ET.ParseError as e:
            print(f"\033[31mError parsing the XML file \033[35m{path}\033[0m: \033[36m{e}\033[0m")
            return None
    def _xml_to_dict(self, element: ET.Element) -> Dict[str, Any]:
        """
        Converts an XML Element to a dictionary. Recursively processes child elements.

        :param element: The XML Element to convert.
        :return: A dictionary representation of the XML element.
        """
        if element.attrib.get("xsi:nil") == "true":
            return None
        text = element.text.strip() if element.text and element.text.strip() else ""

        if len(element) == 0:
            if element.attrib:
                out = {"@attributes": element.attrib}
                if text:
                    out["#text"] = text
                return out if out else None
            else:
                return text if text != "" else None
            
        result = {}

        if element.attrib:
            result["@attributes"] = dict(element.attrib)

        if text:
            result["#text"] = text

        for child in element:
            child_value = self._xml_to_dict(child)
            tag = child.tag

            if tag in result:
                if not isinstance(result[tag], list):
                    result[tag] = [result[tag]]
                result[tag].append(child_value)
            else:
                result[tag] = child_value

        return result

    def xml_write(self, path: str, data: Dict[str, Any], root_element: Optional[str] = 'root'):
        """
        Writes a dictionary to an XML file.

        :param path: Path to the XML file.
        :param data: The data to be written as an XML structure.
        :param root_element: The name of the root element for the XML structure.
        :raises ValueError: If data is not a dictionary or cannot be converted to XML.
        """
        if not isinstance(data, dict):
            raise ValueError("Data to be written must be a dictionary.")
        file_path = self._validate_and_prepare_path(path)
        
        # Convert the dictionary to an XML tree
        root = self._dict_to_xml(data, root_element)
        tree = ET.ElementTree(root)
        
        # Write the tree to the file
        tree.write(file_path, encoding='utf-8', xml_declaration=True)

    def _dict_to_xml(self, data: Dict[str, Any], root_element: str) -> ET.Element:
        """
        Converts a dictionary to an XML Element, recursively processing nested structures.

        :param data: The dictionary containing data to convert.
        :param root_element: The name of the root element.
        :return: The corresponding XML Element object.
        """
        if not isinstance(data, dict) and not isinstance(data, list):
            elem = ET.Element(root_element)
            if data is None:
                elem.set("xsi:nil", "true")
            else:
                elem.text = str(data)
            return elem

        if isinstance(data, list):
            wrapper = ET.Element(root_element)
            for item in data:
                sub_elem = self._dict_to_xml(item, root_element)
                wrapper.append(sub_elem)
            return wrapper

        elem = ET.Element(root_element)

        attributes = data.get("@attributes", {})
        for k, v in attributes.items():
            elem.set(k, v)

        if "#text" in data:
            elem.text = str(data["#text"])

        for key, value in data.items():
            if key in ("@attributes", "#text"):
                continue

            if isinstance(value, list):
                for item in value:
                    elem.append(self._dict_to_xml(item, key))
            else:
                elem.append(self._dict_to_xml(value, key))

        return elem

    def xml_append(self, path: str, data: Dict[str, Any], root_element: Optional[str] = 'root'):
        """
        Appends data to an existing XML file.

        :param path: Path to the XML file.
        :param data: Data to append to the XML file.
        :param root_element: The root element to use for appending.
        :raises ValueError: If data is not a dictionary.
        """
        if not isinstance(data, dict):
            raise ValueError("Data to be appended must be a dictionary.")

        file_path = self._validate_and_prepare_path(path)

        # Check if the file exists and read the existing data
        if os.path.exists(file_path):
            tree = ET.parse(file_path)
            root = tree.getroot()
        else:
            root = ET.Element(root_element)
        
        # Convert the dictionary to XML and append it to the root element
        new_elements = self._dict_to_xml(data, root_element)
        root.append(new_elements)

        # Write the updated XML tree back to the file
        tree = ET.ElementTree(root)
        tree.write(file_path, encoding='utf-8', xml_declaration=True)

    def xml_find(self, path: str, query: str) -> Optional[Dict[str, Any]]:
        """
        Finds and returns the first matching element based on the provided query.

        :param path: Path to the XML file.
        :param query: Query string to find the element (XPath).
        :return: A dictionary representing the matching XML element, or None if not found.
        :raises FileNotFoundError: If the XML file does not exist.
        :raises ET.ParseError: If there is an error parsing the XML file.
        """
        file_path = self._validate_and_prepare_path(path)
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {path} does not exist.")
        
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Find the element using XPath query
            element = root.find(query)
            if element is not None:
                return self._xml_to_dict(element)
            else:
                return None
        except ET.ParseError as e:
            print(f"\033[31mError parsing the XML file \033[35m{path}\033[0m: \033[36m{e}\033[0m")
            return None
    def csv_read(self, path: str, delimiter: str = ',', quotechar: str = '"') -> List[Dict[str, str]]:
        """
        Reads a CSV file and returns its contents as a list of dictionaries.
        Each row is represented as a dictionary where the keys are column headers.
        
        If the file does not exist, it creates an empty CSV file with headers.
        
        Parameters:
            path (str): Path to the CSV file.
            delimiter (str): Character used to separate values. Defaults to ','.
            quotechar (str): Character used to quote fields. Defaults to '"'.
        
        Returns:
            List[Dict[str, str]]: A list of dictionaries where each dictionary corresponds to a row.
        """
        import csv
        file_path = self._validate_and_prepare_path(path)
        
        # If the file doesn't exist, create an empty CSV with headers
        if not os.path.exists(file_path):
            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=[], delimiter=delimiter, quotechar=quotechar)
                writer.writeheader()  # Write an empty header
                if self.debug:
                    self.debugger.success(f"Created empty CSV file: {file_path}")
            return []

        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=delimiter, quotechar=quotechar)
            return [row for row in reader]

    def csv_write(self, path: str, data: List[Dict[str, str]], fieldnames: Optional[List[str]] = None, delimiter: str = ',', quotechar: str = '"'):
        """
        Writes a list of dictionaries to a CSV file. The keys of the dictionary represent the column headers.
        
        Parameters:
            path (str): Path to the CSV file.
            data (List[Dict[str, str]]): List of dictionaries to be written to the CSV.
            fieldnames (List[str], optional): List of fieldnames (headers) for the CSV file. Defaults to None, which uses the keys of the first dictionary.
            delimiter (str): Character used to separate values. Defaults to ','.
            quotechar (str): Character used to quote fields. Defaults to '"'.
        """
        import csv
        if not data:
            raise ValueError("Data cannot be empty.")
        
        # If fieldnames are not provided, use the keys from the first dictionary
        if not fieldnames:
            fieldnames = data[0].keys()

        file_path = self._validate_and_prepare_path(path)
        
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=delimiter, quotechar=quotechar)
            writer.writeheader()
            writer.writerows(data)

    def csv_append(self, path: str, data: List[Dict[str, str]], fieldnames: Optional[List[str]] = None, delimiter: str = ',', quotechar: str = '"'):
        """
        Appends a list of dictionaries to an existing CSV file. The keys of the dictionary represent the column headers.
        
        Parameters:
            path (str): Path to the CSV file.
            data (List[Dict[str, str]]): List of dictionaries to be appended to the CSV.
            fieldnames (List[str], optional): List of fieldnames (headers) for the CSV file. Defaults to None, which uses the keys of the first dictionary.
            delimiter (str): Character used to separate values. Defaults to ','.
            quotechar (str): Character used to quote fields. Defaults to '"'.
        """
        import csv
        if not data:
            raise ValueError("Data cannot be empty.")
        
        # If fieldnames are not provided, use the keys from the first dictionary
        if not fieldnames:
            fieldnames = data[0].keys()

        file_path = self._validate_and_prepare_path(path)
        
        # Append to the file, if it exists; otherwise, create a new file with headers
        with open(file_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=delimiter, quotechar=quotechar)
            if file.tell() == 0:  # If file is empty, write header first
                writer.writeheader()
            writer.writerows(data)

    def csv_update(self, path: str, data: List[Dict[str, str]], identifier: str, delimiter: str = ',', quotechar: str = '"'):
        """
        Updates specific rows in a CSV file. Identifies rows using a unique identifier (fieldname).
        
        Parameters:
            path (str): Path to the CSV file.
            data (List[Dict[str, str]]): List of dictionaries to update.
            identifier (str): The column name used to identify rows that need to be updated.
            delimiter (str): Character used to separate values. Defaults to ','.
            quotechar (str): Character used to quote fields. Defaults to '"'.
        """
        import csv
        file_path = self._validate_and_prepare_path(path)
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {path} does not exist.")
        
        # Read the existing content from the CSV file
        existing_data = self.csv_read(path, delimiter, quotechar)
        
        # Update the data
        updated_data = []
        for row in existing_data:
            for new_row in data:
                if row[identifier] == new_row[identifier]:
                    row.update(new_row)
            updated_data.append(row)
        
        # Write the updated data back to the CSV file
        self.csv_write(path, updated_data, fieldnames=existing_data[0].keys(), delimiter=delimiter, quotechar=quotechar)
    def yaml_read(self, path: str, default: Optional[dict] = None) -> dict:
        """
        Reads a YAML file and returns its contents as a dictionary. 
        If the file does not exist, it creates an empty YAML file with the default content.

        :param path: Path to the YAML file.
        :param default: Optional dictionary to provide default values if the file is missing.
        :return: A dictionary representing the YAML data.
        """
        file_path = self._validate_and_prepare_path(path)
        import yaml
        # If file does not exist, create an empty YAML file
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as file:
                yaml.dump(default or {}, file, default_flow_style=False)
            if self.debug:
                self.debugger.success(f"Created empty YAML file: {file_path}")
            return default or {}

        # Read existing YAML file
        with open(file_path, 'r', encoding='utf-8') as file:
            try:
                data = yaml.safe_load(file)
            except yaml.YAMLError as e:
                print(f"\033[31mError reading YAML file \033[35m{path}\033[0m: \033[36m{e}\033[0m")
                data = default or {}

        return data

    def yaml_write(self, path: str, data: dict):
        """
        Writes a dictionary to a YAML file. If the file exists, it will be overwritten.
        
        :param path: Path to the YAML file.
        :param data: A dictionary representing the data to be written.
        """
        file_path = self._validate_and_prepare_path(path)
        import yaml
        # Write to the YAML file
        with open(file_path, 'w', encoding='utf-8') as file:
            try:
                yaml.dump(data, file, default_flow_style=False)
            except yaml.YAMLError as e:
                print(f"Error writing to YAML file {path}: {e}")
    
    def ini_read(self, path: str, default: Optional[Dict[str, Dict[str, str]]] = None) -> Dict[str, Dict[str, str]]:
        """
        Reads an INI file and returns its contents as a dictionary.
        If the file does not exist, it creates an empty INI file with the default content.

        :param path: Path to the INI file.
        :param default: Optional dictionary to provide default values if the file is missing.
        :return: A dictionary representing the INI data.
        """
        file_path = self._validate_and_prepare_path(path)
        import configparser
        # If file does not exist, create an empty INI file with default content
        if not os.path.exists(file_path):
            config = configparser.ConfigParser()
            if default:
                for section, values in default.items():
                    config[section] = values
            with open(file_path, 'w', encoding='utf-8') as file:
                config.write(file)
            if self.debug:
                self.debugger.success(f"Created empty INI file: {file_path}")
            return default or {}

        # Read the existing INI file
        config = configparser.ConfigParser()
        config.read(file_path, encoding='utf-8')

        # Convert to a dictionary
        data = {section: dict(config.items(section)) for section in config.sections()}

        return data

    def ini_write(self, path: str, data: Dict[str, Dict[str, str]], append: bool = False):
        """
        Writes a dictionary to an INI file. If the file exists, it can be either overwritten or appended.
        
        :param path: Path to the INI file.
        :param data: A dictionary representing the data to be written to the INI file.
        :param append: If True, the data will be appended to the file; if False, the file will be overwritten.
        """
        file_path = self._validate_and_prepare_path(path)
        import configparser
        config = configparser.ConfigParser()

        # If appending, read the existing file and add new sections/values
        if append:
            config.read(file_path, encoding='utf-8')

        for section, values in data.items():
            if not config.has_section(section):
                config.add_section(section)
            for key, value in values.items():
                config.set(section, key, value)

        with open(file_path, 'w', encoding='utf-8') as file:
            config.write(file)
    def properties_read(self, path: str) -> Dict[str, str]:
        """
        Reads a .properties file and returns the data as a dictionary.
        
        Each line in the .properties file should follow the format `key=value`.
        Lines that start with `#` or `!` are considered comments and ignored.

        :param path: Path to the .properties file.
        :return: A dictionary of key-value pairs read from the file.
        """
        file_path = self._validate_and_prepare_path(path)
        properties = {}

        if not os.path.exists(file_path):
            open(file_path, 'w').close()  # Create empty file if not exists
            if self.debug:
                self.debugger.success(f"Created empty PROPERTIES file: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith(('#', '!')) and '=' in line:
                    key, value = line.split('=', 1)
                    properties[key.strip()] = value.strip()

        return properties

    def properties_write(self, path: str, data: Dict[str, str], append: bool = False):
        """
        Writes a dictionary to a .properties file. Supports appending or overwriting.

        :param path: Path to the .properties file.
        :param data: A dictionary where each key-value pair is written as `key=value`.
        :param append: If True, appends data to the file. If False, overwrites the file.
        """
        file_path = self._validate_and_prepare_path(path)
        mode = 'a' if append else 'w'

        with open(file_path, mode, encoding='utf-8') as f:
            for key, value in data.items():
                f.write(f"{key} = {value}\n")

    def md_read(self, path: str) -> str:
        """
        Reads a .md file and returns its content as a string.

        :param path: Path to the .md file.
        :return: A string containing the Markdown content.
        """
        file_path = self._validate_and_prepare_path(path)

        if not os.path.exists(file_path):
            open(file_path, 'w').close()  # Create empty file if not exists
            if self.debug:
                self.debugger.success(f"Created empty MD file: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return content

    def md_write(self, path: str, content: str, append: bool = False):
        """
        Writes a string to a .md file. Supports appending or overwriting.

        :param path: Path to the .md file.
        :param content: Markdown content to write.
        :param append: If True, appends content to the file. If False, overwrites the file.
        """
        file_path = self._validate_and_prepare_path(path)
        mode = 'a' if append else 'w'

        with open(file_path, mode, encoding='utf-8') as f:
            f.write(content)

    def rtf_read(self, path: str) -> str:
        """
        Reads an RTF (.rtf) file and returns its content as a string.

        :param path: Path to the .rtf file.
        :return: A string containing the RTF content.
        """
        file_path = self._validate_and_prepare_path(path)
        
        if not os.path.exists(file_path):
            open(file_path, 'w').close()  # Create empty file if not exists
            if self.debug:
                self.debugger.success(f"Created empty file: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return content

    def rtf_write(self, path: str, content: str, append: bool = False):
        """
        Writes a string to an RTF (.rtf) file. Supports appending or overwriting.

        :param path: Path to the .rtf file.
        :param content: Text content to write to the RTF file.
        :param append: If True, appends content to the file. If False, overwrites the file.
        """
        file_path = self._validate_and_prepare_path(path)
        mode = 'a' if append else 'w'

        with open(file_path, mode, encoding='utf-8') as f:
            f.write(content)
        if self.debug:
            self.debugger.success(f"Wrote to file: {file_path}")

    def html_read(self, path: str) -> str:
        """
        Reads an HTML (.html, .htm) file and returns its content as a string.

        :param path: Path to the .html or .htm file.
        :return: A string containing the HTML content.
        """
        return self.rtf_read(path)

    def html_write(self, path: str, content: str, append: bool = False):
        """
        Writes a string to an HTML (.html, .htm) file. Supports appending or overwriting.

        :param path: Path to the .html or .htm file.
        :param content: HTML content to write to the file.
        :param append: If True, appends content to the file. If False, overwrites the file.
        """
        self.rtf_write(path, content, append)

    def css_read(self, path: str) -> str:
        """
        Reads a CSS (.css) file and returns its content as a string.

        :param path: Path to the .css file.
        :return: A string containing the CSS rules.
        """
        return self.rtf_read(path)

    def css_write(self, path: str, content: str, append: bool = False):
        """
        Writes a string to a CSS (.css) file. Supports appending or overwriting.

        :param path: Path to the .css file.
        :param content: CSS rules to write to the file.
        :param append: If True, appends content to the file. If False, overwrites the file.
        """
        self.rtf_write(path, content, append)

    def js_read(self, path: str) -> str:
        """
        Reads a JavaScript (.js) file and returns its content as a string.

        :param path: Path to the .js file.
        :return: A string containing the JavaScript code.
        """
        return self.rtf_read(path)

    def js_write(self, path: str, content: str, append: bool = False):
        """
        Writes a string to a JavaScript (.js) file. Supports appending or overwriting.

        :param path: Path to the .js file.
        :param content: JavaScript code to write to the file.
        :param append: If True, appends content to the file. If False, overwrites the file.
        """
        self.rtf_write(path, content, append)

    def js_run(self, path: str, terminal: bool = False, inputs: Optional[Union[List[str], str]] = None, output: bool = True) -> Optional[str]:
        """
        Executes a JavaScript (.js) file using Node.js with additional options for terminal execution, 
        input handling, and optional output return.

        :param path: Path to the .js file to execute.
        :param terminal: If True, runs the script in a terminal window; otherwise, runs it in the background.
        :param inputs: Input(s) to pass to the JavaScript file, as a single string or a list of strings.
        :param output: If True, returns the output of the executed JavaScript code.
        :return: The output of the executed JavaScript code if output is True; otherwise, None.
        :raises FileNotFoundError: If the file does not exist.
        :raises RuntimeError: If Node.js is not installed or an error occurs during execution.
        """
        file_path = self._validate_and_prepare_path(path)
        import subprocess
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {path} does not exist.")
        
        # Convert inputs into a space-separated string if they are provided
        input_data = ""
        if inputs:
            if isinstance(inputs, list):
                input_data = " ".join(map(str, inputs))
            elif isinstance(inputs, str):
                input_data = inputs
            else:
                raise ValueError("Inputs must be a string or a list of strings.")

        try:
            if terminal:
                # Run the script in a terminal
                if os.name == 'nt':  # Windows
                    subprocess.run(["start", "cmd", "/k", f"node {file_path} {input_data}"], shell=True)
                elif os.name == 'posix':  # macOS/Linux
                    subprocess.run(["xterm", "-e", f"node {file_path} {input_data}"], shell=True)
                else:
                    raise RuntimeError("Terminal emulator not found on your system.")
                return None if not output else "Executed in terminal, output not captured."
            else:
                # Run the script in the background
                result = subprocess.run(['node', file_path] + input_data.split(), capture_output=True, text=True, check=True)
                return result.stdout if output else None
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error running JavaScript file {path}: {e.stderr}")
        
    def py_read(self, path: str) -> str:
        """
        Reads a Python (.py) file and returns its content as a string.
        
        :param path: Path to the .py file.
        :return: A string containing the Python code.
        """
        path=self._validate_and_prepare_path(path)
        
        return self.rtf_read(path)

    def py_write(self, path: str, content: str, append: bool = False):
        """
        Writes a string to a Python (.py) file. Supports appending or overwriting.
        
        :param path: Path to the .py file.
        :param content: Python code to write to the file.
        :param append: If True, appends content to the file. If False, overwrites the file.
        """
        path=self._validate_and_prepare_path(path)
        mode = 'a' if append else 'w'
        with open(path, mode, encoding='utf-8') as file:
            file.write(content)
        print(f"\033[32mPython file \033[33m{'appended' if append else 'written'}\033[32m at \033[35m{path}\033[0m")

    def py_run(self, path: str, terminal: bool = False, inputs: Optional[Union[List[str], str]] = None, output: bool = True) -> Optional[str]:
        """
        Executes a Python (.py) file using the Python interpreter with additional options for terminal execution, 
        input handling, and optional output return.

        :param path: Path to the .py file to execute.
        :param terminal: If True, runs the script in a terminal window; otherwise, runs it in the background.
        :param inputs: Input(s) to pass to the Python file, as a single string or a list of strings.
        :param output: If True, returns the output of the executed Python code.
        :return: The output of the executed Python code if output is True; otherwise, None.
        :raises FileNotFoundError: If the file does not exist.
        :raises RuntimeError: If Python is not properly installed or an error occurs during execution.
        """
        # Validate the file path
        path=self._validate_and_prepare_path(path)
        import subprocess
        # Convert inputs into a space-separated string if they are provided
        input_data = ""
        if inputs:
            if isinstance(inputs, list):
                input_data = " ".join(map(str, inputs))
            elif isinstance(inputs, str):
                input_data = inputs
            else:
                raise ValueError("\033[32mInputs must be a string or a list of strings.\033[0m")

        try:
            if terminal:
                # Run the script in a terminal
                if os.name == 'nt':  # Windows
                    subprocess.run(["start", "cmd", "/k", f"python {path} {input_data}"], shell=True)
                elif os.name == 'posix':  # macOS/Linux
                    subprocess.run(["xterm", "-e", f"python {path} {input_data}"], shell=True)
                else:
                    raise RuntimeError("Terminal emulator not found on your system.")
                return None if not output else "Executed in terminal, output not captured."
            else:
                # Run the script in the background
                command = ['python', path] + input_data.split()
                result = subprocess.run(command, capture_output=True, text=True, check=True)
                return result.stdout if output else None
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error running Python file {path}: {e.stderr.strip()}")


    def py_add_code(self, path: str, code: str, position: str = "end"):
        """
        Adds a Python code block to a specified Python file at a given position.

        :param path: Path to the Python (.py) file where the code will be added.
        :param code: The Python code block to add.
        :param position: The position to add the code ('start', 'end', or a specific line number).
                        - 'start': Adds the code after imports and global variables.
                        - 'end': Adds the code before the __main__ block or at the end if no __main__ block exists.
                        - A line number can be specified to add the code at that exact position.
        :raises FileNotFoundError: If the file does not exist.
        """
        # Validate and prepare the file path
        path = self._validate_and_prepare_path(path)

        if not os.path.exists(path):
            raise FileNotFoundError(f"The file {path} does not exist.")

        # Read the existing content of the file
        with open(path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # Process the position
        if position == "start":
            # Find the position after imports and global variables
            insert_index = 0
            for i, line in enumerate(lines):
                if not line.strip() or line.strip().startswith("#") or "import" in line:
                    insert_index = i + 1
                else:
                    break
            lines.insert(insert_index, f"\n{code.strip()}\n")
        elif position == "end":
            # Insert before the `if __name__ == "__main__":` block if it exists
            insert_index = len(lines)
            for i, line in reversed(list(enumerate(lines))):
                if line.strip() == "if __name__ == \"__main__\":":
                    insert_index = i
                    break
            lines.insert(insert_index, f"\n{code.strip()}\n")
        elif position.isdigit():
            # Insert at a specific line number
            insert_index = int(position) - 1
            lines.insert(insert_index, f"\n{code.strip()}\n")
        else:
            raise ValueError("Invalid position. Use 'start', 'end', or a specific line number.")

        # Write the modified content back to the file
        with open(path, 'w', encoding='utf-8') as file:
            file.writelines(lines)


    def open_html(self, path: str, browser_name: Optional[str] = None):
        """
        Opens an HTML file in a specified or default web browser.
        
        :param path: Path to the HTML file.
        :param browser_name: Name of the web browser to use (e.g., 'chrome', 'firefox').
                            If None, opens in the default browser.
        """
        import webbrowser
        # Ensure the file exists
        file_path = self._validate_and_prepare_path(path)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {path} does not exist.")
        
        # Convert path to URL format
        file_url = f"file://{file_path}"

        # Open in specified browser, or fallback to default if not available
        try:
            if browser_name:
                browser = webbrowser.get(browser_name)
                browser.open(file_url)
            else:
                webbrowser.open(file_url)
        except webbrowser.Error:
            print(f"\033[32mCould not open the browser \033[35m'{browser_name}'\033[0m. Opening with the default browser instead.\033[0m")
            webbrowser.open(file_url)

    def sql_execute(self, path: str, query: str, params: tuple = ()):
        """
        Executes an SQL query on a database file.
        
        :param path: Path to the .sql database file.
        :param query: SQL query to execute.
        :param params: Tuple of parameters for the query.
        :return: Query result for SELECT queries or confirmation of execution for other queries.
        """
        file_path = self._validate_and_prepare_path(path)
        import sqlite3
        with sqlite3.connect(file_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            if query.strip().upper().startswith("SELECT"):
                return cursor.fetchall()
            else:
                return f"Query executed successfully: {query}"

    def sql_create_table(self, path: str, table_name: str, columns: Dict[str, str]):
        """
        Creates a table in an SQL database.
        
        :param path: Path to the .sql database file.
        :param table_name: Name of the table to create.
        :param columns: Dictionary of column names and types.
        """
        cols = ", ".join([f"{col} {type_}" for col, type_ in columns.items()])
        self.sql_execute(path, f"CREATE TABLE IF NOT EXISTS {table_name} ({cols})")

    def sql_insert(self, path: str, table_name: str, data: Dict[str, Any]):
        """
        Inserts data into an SQL table.
        
        :param path: Path to the .sql database file.
        :param table_name: Name of the table to insert data into.
        :param data: Dictionary where keys are column names and values are data.
        """
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        values = tuple(data.values())
        self.sql_execute(path, f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})", values)

    def sql_query(self, path: str, query: str, params: tuple = ()):
        """
        Executes an SQL SELECT query and returns the results.
        
        :param path: Path to the .sql database file.
        :param query: SQL SELECT query to execute.
        :param params: Tuple of parameters for the query.
        :return: Results of the SELECT query.
        """
        return self.sql_execute(path, query, params)

    def handle_compressed(self, path: str, action: str, target: Optional[str] = None):
        """
        Handles compression and extraction of files in .zip, .rar, and similar formats.
        
        :param path: Path to the compressed file or directory.
        :param action: Either 'compress' to create an archive or 'extract' to extract files.
        :param target: Directory to extract files into, or name of the new archive.
        """
        file_path = self._validate_and_prepare_path(path)
        import zipfile
        if action == 'compress':
            if not os.path.isdir(file_path):
                raise ValueError(f"The path {path} is not a directory.")
            archive_path = target if target else f"{file_path}.zip"
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as archive:
                for root, dirs, files in os.walk(file_path):
                    for file in files:
                        full_path = os.path.join(root, file)
                        archive.write(full_path, arcname=os.path.relpath(full_path, file_path))
            print(f"\033[32mCompressed to {archive_path}\033[0m")

        elif action == 'extract':
            if not zipfile.is_zipfile(file_path):
                raise ValueError(f"\033[31mThe file \033[35m{path}\033[31m is not a valid compressed file.\033[0m")
            target_dir = target if target else os.path.splitext(file_path)[0]
            with zipfile.ZipFile(file_path, 'r') as archive:
                archive.extractall(target_dir)
            print(f"\033[32mExtracted to {target_dir}\033[0m")
        else:
            raise ValueError("\033[31mInvalid action. Choose either 'compress' or 'extract'.\033[0m")
    # LaTeX Processing Methods

    def markdown_to_latex(self, markdown_text: str) -> str:
        """
        Converts a Markdown text into LaTeX format.
        
        :param markdown_text: The Markdown text to convert.
        :return: The corresponding LaTeX formatted string.
        """
        import markdown2
        from pylatexenc.latexencode import unicode_to_latex
        latex_text = markdown2.markdown(markdown_text)
        latex_text = unicode_to_latex(latex_text)
        return latex_text

    def tex_read(self, path: str) -> str:
        """
        Reads a .tex file and returns its content as a string.
        
        :param path: The path to the .tex file.
        :return: The content of the .tex file.
        """
        file_path = self._validate_and_prepare_path(path)
        return self.rtf_read(file_path)

    def tex_write(self, path: str, content: str):
        """
        Writes the given content to a .tex file.
        
        :param path: The path to the .tex file.
        :param content: The content to write to the file.
        """
        file_path = self._validate_and_prepare_path(path)
        self.rtf_write(file_path,content)

    def latex_compile(self, latex_formula: str) -> str:
        """
        Compiles a LaTeX formula into plain text by handling special characters properly.
        
        :param latex_formula: The LaTeX formula to compile.
        :return: The compiled plain text representation of the formula.
        """
        from pylatexenc.latex2text import LatexNodes2Text
        # Remove escape sequences and fix invalid LaTeX syntax if necessary
        latex_formula = re.sub(r"\\\((.*?)\\\)", r"\1", latex_formula)  # Remove \( \) delimiters
        latex_formula = re.sub(r"\\\[|\[", "", latex_formula)  # Remove other delimiters
        plain_text = LatexNodes2Text().latex_to_text(latex_formula)
        return plain_text

    def tex_to_markdown(self, tex_content: str) -> str:
        """
        Converts LaTeX content to plain Markdown without adding HTML elements.
        
        :param tex_content: The LaTeX content to convert.
        :return: Plain Markdown text.
        """
        from pylatexenc.latex2text import LatexNodes2Text
        # Remove LaTeX commands
        plain_text = LatexNodes2Text().latex_to_text(tex_content)
        # Clean remaining symbols if needed
        plain_text = re.sub(r"\\[a-z]+", "", plain_text)  # Remove unknown LaTeX commands
        return plain_text

    def tex_append(self, path: str, content: str):
        """
        Appends content to an existing .tex file. Creates the file if it does not exist.
        
        :param path: The path to the .tex file.
        :param content: The content to append.
        """
        file_path = self._validate_and_prepare_path(path)
        self.rtf_write(file_path,content,True)
    def latex_to_html(self, latex_formula: str, output_file: Optional[str] = None) -> str:
        """
        Converts a LaTeX formula into an HTML file with MathJax support.
        If output_file is None, returns the HTML as a string. Otherwise, writes it to a file as well.

        :param latex_formula: The LaTeX formula to include in the HTML.
        :param output_file: The path of the HTML file to create (optional).
        :return: The HTML content as a string.
        """
        # Static file location relative to this script
        static_dir = os.path.join(os.path.dirname(__file__), "static")
        mathjax_path = os.path.join(static_dir, "tex-mml-chtml.js")

        # Check if the MathJax file exists
        if not os.path.exists(mathjax_path):
            raise FileNotFoundError(f"MathJax file not found at {mathjax_path}. Ensure it's placed in the static directory.")

        # Use relative path for the script in the HTML
        relative_path = os.path.relpath(mathjax_path, os.getcwd())
        js_codes=self.js_read(relative_path)
        
        html_template = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>LaTeX to HTML</title>
            <script id="MathJax-script">{js_codes}</script>
        </head>
        <body>
            <p>\\({latex_formula}\\)</p>
        </body>
        </html>
        """

        # Write to file if output_file is provided
        if output_file:
            with open(output_file, "w", encoding="utf-8") as file:
                file.write(html_template)
            print(f"\033[32mHTML file created at \033[35m{output_file}\033[0m")

        # Return the HTML as a string
        return html_template
    def latex_to_image(self, latex_formula: str, 
                   output_file: Optional[str] = None, 
                   bg_color: str = "white", 
                   text_color: str = "black", 
                   figsize: Tuple[float, float] = (8, 4)) -> bytes:
        """
        Converts a LaTeX formula to an image using MathText from Matplo
        tlib.

        :param latex_formula: The LaTeX formula to render.
        :param output_file: The path of the output image file (optional).
        :param bg_color: Background color of the image (default is white).
        :param text_color: Text color of the LaTeX formula (default is black).
        :param figsize: Size of the figure as a tuple (width, height), default is (8, 4).
        :return: Binary content of the image.
        """
        import matplotlib.pyplot as plt
        from io import BytesIO
        # Remove dollar signs if present
        if latex_formula.startswith("$") and latex_formula.endswith("$"):
            latex_formula = latex_formula[1:-1]

        # Wrap the formula with math mode symbols
        latex_formula = f"${latex_formula}$"

        # Create a figure
        fig, ax = plt.subplots(figsize=figsize)
        fig.patch.set_facecolor(bg_color)  # Set background color
        ax.text(0.5, 0.5, latex_formula, fontsize=20, ha='center', va='center', 
                color=text_color, usetex=False)
        ax.axis('off')

        # Save the figure to a buffer
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', pad_inches=0, facecolor=fig.get_facecolor())
        plt.close(fig)

        # Save to file if output path is provided
        if output_file:
            # Ensure the directory exists
            output_dir = os.path.dirname(output_file)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                print(f"\033[34m Created directory: \033[35m{output_dir} \033[0m")
            # Write the image to the file
            with open(output_file, "wb") as f:
                f.write(buffer.getvalue())
            print(f"\033[32m Image saved to \033[35m{output_file} \033[0m")

        # Return binary image data
        buffer.seek(0)
        return buffer.getvalue()
        
class ScriptRunner:
    """
    A class for running scripts in Node.js and other environments, with support for input handling,
    terminal execution, and capturing output.
    """
    def __init__(self, default_interpreter: str = "node"):
        """
        Initializes the ScriptRunner with a default interpreter.

        :param default_interpreter: Default interpreter to use (e.g., 'node', 'python', etc.).
        """
        self.default_interpreter = default_interpreter

    def _validate_path(self, path: str) -> str:
        """
        Validates the script file path and converts it to an absolute path.

        :param path: Path to the script file.
        :return: Absolute file path.
        :raises FileNotFoundError: If the file does not exist.
        """
        absolute_path = os.path.abspath(path)
        if not os.path.exists(absolute_path):
            raise FileNotFoundError(f"The file {path} does not exist.")
        return absolute_path

    def run_script(
        self,
        path: str,
        interpreter: Optional[str] = None,
        terminal: bool = False,
        inputs: Optional[Union[List[str], str]] = None,
        output: bool = True
    ) -> Optional[str]:
        """
        Executes a script file using a specified interpreter and additional options for terminal execution,
        input handling, and optional output return.

        :param path: Path to the script file to execute.
        :param interpreter: Interpreter to use (e.g., 'node', 'python'). Defaults to the class interpreter.
        :param terminal: If True, runs the script in a terminal window; otherwise, runs it in the background.
        :param inputs: Input(s) to pass to the script, as a single string or a list of strings.
        :param output: If True, returns the output of the executed script.
        :return: The output of the executed script if output is True; otherwise, None.
        :raises FileNotFoundError: If the file does not exist.
        :raises RuntimeError: If the interpreter is not found or an error occurs during execution.
        """
        import subprocess
        interpreter = interpreter or self.default_interpreter
        file_path = self._validate_path(path)

        # Prepare inputs
        input_data = ""
        if inputs:
            if isinstance(inputs, list):
                input_data = " ".join(map(str, inputs))
            elif isinstance(inputs, str):
                input_data = inputs
            else:
                raise ValueError("Inputs must be a string or a list of strings.")

        try:
            if terminal:
                # Run the script in a terminal
                if os.name == 'nt':  # Windows
                    subprocess.run(["start", "cmd", "/k", f"{interpreter} {file_path} {input_data}"], shell=True)
                elif os.name == 'posix':  # macOS/Linux
                    subprocess.run(["xterm", "-e", f"{interpreter} {file_path} {input_data}"], shell=True)
                else:
                    raise RuntimeError("Terminal emulator not found on your system.")
                return None if not output else "Executed in terminal, output not captured."
            else:
                # Run the script in the background
                result = subprocess.run(
                    [interpreter, file_path] + input_data.split(),
                    capture_output=True,
                    text=True,
                    check=True
                )
                return result.stdout if output else None
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error running script {path}: {e.stderr}")
        except FileNotFoundError as e:
            if terminal:
                raise RuntimeError("Terminal emulator not found on your system.")
            else:
                raise e

    def set_default_interpreter(self, interpreter: str):
        """
        Sets the default interpreter for the ScriptRunner.

        :param interpreter: Interpreter to set (e.g., 'node', 'python').
        """
        self.default_interpreter = interpreter



class TaskScheduler:
    """
    A comprehensive task scheduler that supports task pausing/resuming,
    one-time and repeating tasks, priority-based execution, and CLI-based task listing.
    """

    def __init__(self):
        """
        Initializes the TaskScheduler with necessary attributes and structures for managing tasks.
        """
        import threading
        from queue import PriorityQueue
        self.tasks = {}  # Maps task_id to thread or task details
        self.task_status = {}  # Tracks the status of each task ('running', 'paused', 'cancelled', etc.)
        self.priority_queue = PriorityQueue()  # Manages priority-based task execution
        self.lock = threading.Lock()  # Ensures thread safety

    def schedule_task(
        self,
        task: Callable,
        interval: Optional[int] = None,
        repeat: bool = True,
        priority: int = 5,
    ) -> str:
        """
        Schedules a task for execution with optional repeat and priority control.

        :param task: The callable function to execute.
        :param interval: Time interval (in seconds) for repeating tasks. None for one-time tasks.
        :param repeat: Whether the task repeats (True) or runs once (False).
        :param priority: Priority of the task (lower values indicate higher priority).
        :return: A unique ID for the scheduled task.
        """
        import uuid
        import time
        import threading
        task_id = str(uuid.uuid4())

        def task_wrapper():
            """
            Wraps the task execution logic with repeat or one-time behavior.
            """
            while self.task_status.get(task_id) == "running":
                try:
                    task()
                    if not repeat:
                        break
                except Exception as e:
                    print(f"\033[31mTask \033[35m{task_id}\033[31m encountered an error: \033[36m{e}\033[0m")
                if interval:
                    time.sleep(interval)
            self.task_status[task_id] = "completed"

        thread = threading.Thread(target=task_wrapper, daemon=True)
        self.tasks[task_id] = {
            "thread": thread,
            "task": task,
            "interval": interval,
            "repeat": repeat,
            "priority": priority,
        }
        self.task_status[task_id] = "queued"
        self.priority_queue.put((priority, task_id))  # Add to the priority queue
        self._start_queued_task(task_id)
        return task_id

    def _start_queued_task(self, task_id: str):
        """
        Starts the next task in the priority queue.
        """
        with self.lock:
            if task_id in self.tasks and self.task_status[task_id] == "queued":
                self.task_status[task_id] = "running"
                self.tasks[task_id]["thread"].start()

    def pause_task(self, task_id: str):
        """
        Pauses a running task by changing its status to 'paused'.

        :param task_id: The unique ID of the task to pause.
        """
        with self.lock:
            if self.task_status.get(task_id) == "running":
                self.task_status[task_id] = "paused"
                print(f"\033[32mTask \033[35m{task_id} \033[32mhas been paused.\033[0m")
            else:
                print(f"\033[31mCannot pause task \033[35m{task_id}\033[36m. Current status: \033[32m{self.task_status.get(task_id)}\033[0m")

    def resume_task(self, task_id: str):
        """
        Resumes a paused task.

        :param task_id: The unique ID of the task to resume.
        """
        with self.lock:
            if self.task_status.get(task_id) == "paused":
                self.task_status[task_id] = "running"
                self._start_queued_task(task_id)
                print(f"\033[32mTask \033[35m{task_id} \033[32mhas been resumed.\033[0m")
            else:
                print(f"\033[31mCannot resume task \033[35m{task_id}\033[36m. Current status: \033[32m{self.task_status.get(task_id)}\033[0m")

    def cancel_task(self, task_id: str):
        """
        Cancels a scheduled or running task.

        :param task_id: The unique ID of the task to cancel.
        """
        with self.lock:
            if task_id in self.tasks:
                self.task_status[task_id] = "cancelled"
                print(f"Task {task_id} has been cancelled.")
            else:
                print(f"No task found with ID: {task_id}")

    def list_tasks(self):
        """
        Lists all tasks with their status, priority, and repeat status.

        :return: None. Prints task details to the console.
        """
        print("Scheduled Tasks:")
        for task_id, details in self.tasks.items():
            status = self.task_status.get(task_id, "unknown")
            print(
                f"ID: {task_id}, Status: {status}, Priority: {details['priority']}, Repeat: {details['repeat']}"
            )

class Logger:
    """
    A versatile logging class to handle application-level logging with support for
    different log levels and formatted outputs.
    """

    def __init__(self, log_file: str = "app.log", log_level: str = "INFO"):
        """
        Initializes the Logger instance with a log file and default log level.

        :param log_file: Path to the log file. Default is 'app.log'.
        :param log_level: Default logging level. Default is 'INFO'.
        """
        import logging
        self.logger = logging.getLogger("ApplicationLogger")
        self.set_log_level(log_level)
        self._configure_logger(log_file)

    def _configure_logger(self, log_file: str):
        """
        Configures the logger with file and console handlers.

        :param log_file: Path to the log file.
        """
        import logging
        # Prevent duplicate logs if logger is already configured
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        # Create handlers
        file_handler = logging.FileHandler(log_file)
        console_handler = logging.StreamHandler()

        # Define log format
        log_format = logging.Formatter(
            "[%(asctime)s] [%(levelname)s]: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Apply format to handlers
        file_handler.setFormatter(log_format)
        console_handler.setFormatter(log_format)

        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        # Avoid duplicate logging from root logger
        self.logger.propagate = False

    def set_log_level(self, level: str):
        """
        Sets the logging level for the logger.

        :param level: Log level as a string (e.g., 'INFO', 'WARNING', 'ERROR').
        """
        import logging
        level = level.upper()
        level_mapping = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        if level in level_mapping:
            self.logger.setLevel(level_mapping[level])
            print(f"\033[32mLog level set to \033[35m{level}.\033[0m")
        else:
            raise ValueError(f"\033[31mInvalid log level: \033[35m{level}\033[0m")

    def log_info(self, message: str):
        """
        Logs an informational message.

        :param message: The message to log.
        """
        self.logger.info(message)

    def log_warning(self, message: str):
        """
        Logs a warning message.

        :param message: The message to log.
        """
        self.logger.warning(message)

    def log_error(self, message: str):
        """
        Logs an error message.

        :param message: The message to log.
        """
        self.logger.error(message)

class EmailManager:
    """
    A comprehensive email management class that supports sending, scheduling emails,
    and checking the inbox.
    """

    def __init__(self, smtp_server: str, smtp_port: int, email_address: str, email_password: str):
        """
        Initializes the EmailManager with SMTP server details and login credentials.

        :param smtp_server: The SMTP server address (e.g., 'smtp.gmail.com').
        :param smtp_port: The SMTP server port (e.g., 587 for TLS).
        :param email_address: The sender's email address.
        :param email_password: The sender's email password.
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email_address = email_address
        self.email_password = email_password

    def send_email(self, to: str, subject: str, body: str):
        """
        Sends an email immediately.

        :param to: Recipient's email address.
        :param subject: Email subject.
        :param body: Email body content.
        """
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        from email.utils import formataddr
        import smtplib

        try:
            msg = MIMEMultipart()
            msg['From'] = formataddr(("Email Manager", self.email_address))
            msg['To'] = to
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_address, self.email_password)
                server.send_message(msg)

            print(f"\033[32mEmail sent successfully to \033[35m{to}.\033[0m")

        except Exception as e:
            print(f"\033[31mFailed to send email to \033[35m{to}. \033[32mError: \033[36m{str(e)}\033[0m")

    def schedule_email(self, to: str, subject: str, body: str, send_time: datetime):
        """
        Schedules an email to be sent at a specific time.

        :param to: Recipient's email address.
        :param subject: Email subject.
        :param body: Email body content.
        :param send_time: Datetime object specifying when to send the email.
        """
        from threading import Timer
        delay = (send_time - datetime.now()).total_seconds()
        if delay < 0:
            print("\033[31mCannot schedule an email in the past.\033[0m")
            return

        print(f"\033[32mEmail scheduled to \033[35m{to}\033[35m at \033[36m{send_time}.\033[0m")
        Timer(delay, self.send_email, args=(to, subject, body)).start()

    def check_inbox(self, user: str):
        """
        Checks the inbox of the specified email account.

        :param user: The email account username to check.
        :return: A list of email subjects and senders.
        """
        import imaplib
        import email
        try:
            with imaplib.IMAP4_SSL('imap.gmail.com') as mail:
                mail.login(user, self.email_password)
                mail.select('inbox')

                _, data = mail.search(None, 'ALL')
                mail_ids = data[0].split()

                emails = []
                for mail_id in mail_ids[-10:]:  # Fetch the last 10 emails
                    _, msg_data = mail.fetch(mail_id, '(RFC822)')
                    for response_part in msg_data:
                        if isinstance(response_part, tuple):
                            msg = email.message_from_bytes(response_part[1])
                            subject = msg["subject"]
                            sender = msg["from"]
                            emails.append((subject, sender))

                print("Last 10 emails:")
                for subject, sender in emails:
                    print(f"From: {sender}, Subject: {subject}")

                return emails

        except Exception as e:
            print(f"Failed to check inbox. Error: {str(e)}")
            return []

class FileTransferManager:
    """
    A comprehensive file transfer manager that supports FTP and SFTP protocols 
    for file uploads, downloads, and transfer status tracking.
    """
    
    def __init__(self):
        """
        Initializes the FileTransferManager with a transfer status dictionary.
        """
        self.transfers: Dict[str, Dict[str, str]] = {}  # Stores transfer statuses
    
    def _generate_transfer_id(self) -> str:
        """
        Generates a unique transfer ID.
        
        :return: A unique string representing the transfer ID.
        """
        import uuid
        return str(uuid.uuid4())

    def upload(self, file_path: str, destination: str, protocol: str = "ftp", **kwargs):
        """
        Uploads a file to a remote server using the specified protocol.
        
        :param file_path: Path to the local file to be uploaded.
        :param destination: The destination path on the remote server.
        :param protocol: The protocol to use ('ftp' or 'sftp'). Defaults to 'ftp'.
        :param kwargs: Additional arguments for FTP/SFTP configuration.
        :return: The transfer ID for the initiated upload.
        """
        transfer_id = self._generate_transfer_id()
        self.transfers[transfer_id] = {"status": "in_progress", "type": "upload", "protocol": protocol}
        
        try:
            if protocol == "ftp":
                self._ftp_upload(file_path, destination, **kwargs)
            elif protocol == "sftp":
                self._sftp_upload(file_path, destination, **kwargs)
            else:
                raise ValueError("Unsupported protocol. Use 'ftp' or 'sftp'.")
            self.transfers[transfer_id]["status"] = "completed"
        except Exception as e:
            self.transfers[transfer_id]["status"] = f"failed: {str(e)}"
            print(f"Failed to upload file: {e}")
        
        return transfer_id

    def download(self, remote_path: str, local_path: str, protocol: str = "ftp", **kwargs):
        """
        Downloads a file from a remote server using the specified protocol.
        
        :param remote_path: Path to the remote file to be downloaded.
        :param local_path: Path to save the downloaded file locally.
        :param protocol: The protocol to use ('ftp' or 'sftp'). Defaults to 'ftp'.
        :param kwargs: Additional arguments for FTP/SFTP configuration.
        :return: The transfer ID for the initiated download.
        """
        transfer_id = self._generate_transfer_id()
        self.transfers[transfer_id] = {"status": "in_progress", "type": "download", "protocol": protocol}
        
        try:
            if protocol == "ftp":
                self._ftp_download(remote_path, local_path, **kwargs)
            elif protocol == "sftp":
                self._sftp_download(remote_path, local_path, **kwargs)
            else:
                raise ValueError("Unsupported protocol. Use 'ftp' or 'sftp'.")
            self.transfers[transfer_id]["status"] = "completed"
        except Exception as e:
            self.transfers[transfer_id]["status"] = f"failed: {str(e)}"
            print(f"Failed to download file: {e}")
        
        return transfer_id

    def check_transfer_status(self, transfer_id: str) -> Optional[str]:
        """
        Checks the status of a file transfer.
        
        :param transfer_id: The unique ID of the transfer to check.
        :return: The status of the transfer ('in_progress', 'completed', 'failed', or None if not found).
        """
        return self.transfers.get(transfer_id, {}).get("status")

    def _ftp_upload(self, file_path: str, destination: str, **kwargs):
        """
        Performs file upload via FTP.
        
        :param file_path: Path to the local file to be uploaded.
        :param destination: The destination path on the remote server.
        :param kwargs: FTP configuration such as host, username, and password.
        """
        import ftplib
        with ftplib.FTP(kwargs["host"]) as ftp:
            ftp.login(kwargs["username"], kwargs["password"])
            with open(file_path, "rb") as file:
                ftp.storbinary(f"STOR {destination}", file)

    def _ftp_download(self, remote_path: str, local_path: str, **kwargs):
        """
        Performs file download via FTP.
        
        :param remote_path: Path to the remote file to be downloaded.
        :param local_path: Path to save the downloaded file locally.
        :param kwargs: FTP configuration such as host, username, and password.
        """
        import ftplib
        with ftplib.FTP(kwargs["host"]) as ftp:
            ftp.login(kwargs["username"], kwargs["password"])
            with open(local_path, "wb") as file:
                ftp.retrbinary(f"RETR {remote_path}", file.write)

    def _sftp_upload(self, file_path: str, destination: str, **kwargs):
        """
        Performs file upload via SFTP.
        
        :param file_path: Path to the local file to be uploaded.
        :param destination: The destination path on the remote server.
        :param kwargs: SFTP configuration such as host, username, password, and port.
        """
        import paramiko
        transport = paramiko.Transport((kwargs["host"], kwargs.get("port", 22)))
        transport.connect(username=kwargs["username"], password=kwargs["password"])
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.put(file_path, destination)
        sftp.close()
        transport.close()

    def _sftp_download(self, remote_path: str, local_path: str, **kwargs):
        """
        Performs file download via SFTP.
        
        :param remote_path: Path to the remote file to be downloaded.
        :param local_path: Path to save the downloaded file locally.
        :param kwargs: SFTP configuration such as host, username, password, and port.
        """
        import paramiko
        transport = paramiko.Transport((kwargs["host"], kwargs.get("port", 22)))
        transport.connect(username=kwargs["username"], password=kwargs["password"])
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.get(remote_path, local_path)
        sftp.close()
        transport.close()
class TextProcessor:
    """
    A class for processing, editing, and analyzing text. 
    Supports word counting, keyword searching, text replacement, and additional text manipulation features.
    """

    def word_count(self, text: str) -> int:
        """
        Counts the number of words in a given text.
        
        :param text: The input text.
        :return: The number of words in the text.
        """
        words = text.split()
        return len(words)

    def find_keywords(self, text: str, keywords: List[str]) -> Dict[str, int]:
        """
        Searches for specific keywords in the text and returns their occurrence count.
        
        :param text: The input text.
        :param keywords: A list of keywords to search for.
        :return: A dictionary with keywords as keys and their counts as values.
        """
        text_lower = text.lower()
        return {keyword: text_lower.count(keyword.lower()) for keyword in keywords}

    def replace_text(self, text: str, old: str, new: str) -> str:
        """
        Replaces all occurrences of a substring with a new string in the text.
        
        :param text: The input text.
        :param old: The substring to be replaced.
        :param new: The new substring to replace with.
        :return: The modified text with replacements.
        """
        return text.replace(old, new)

    def sentence_count(self, text: str) -> int:
        """
        Counts the number of sentences in a given text.
        
        :param text: The input text.
        :return: The number of sentences in the text.
        """
        sentences = re.split(r'[.!?]', text)
        return len([s for s in sentences if s.strip()])

    def character_count(self, text: str, include_spaces: bool = True) -> int:
        """
        Counts the number of characters in the text.
        
        :param text: The input text.
        :param include_spaces: Whether to include spaces in the count.
        :return: The number of characters in the text.
        """
        if not include_spaces:
            text = text.replace(" ", "")
        return len(text)

    def most_frequent_words(self, text: str, top_n: int = 5) -> List[Tuple[str, int]]:
        """
        Finds the most frequent words in the text.
        
        :param text: The input text.
        :param top_n: The number of most frequent words to return.
        :return: A list of tuples with words and their frequencies.
        """
        words = re.findall(r'\w+', text.lower())
        word_counts = {}
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_words[:top_n]

    def remove_stopwords(self, text: str, stopwords: List[str]) -> str:
        """
        Removes common stopwords from the text.
        
        :param text: The input text.
        :param stopwords: A list of stopwords to remove.
        :return: The text with stopwords removed.
        """
        words = text.split()
        filtered_words = [word for word in words if word.lower() not in stopwords]
        return " ".join(filtered_words)

    def unique_words(self, text: str) -> List[str]:
        """
        Finds unique words in the text.
        
        :param text: The input text.
        :return: A list of unique words in the text.
        """
        words = set(re.findall(r'\w+', text.lower()))
        return sorted(words)

    def text_summary(self, text: str, max_sentences: int = 3) -> str:
        """
        Generates a summary of the text by selecting the first few sentences.
        
        :param text: The input text.
        :param max_sentences: The maximum number of sentences in the summary.
        :return: A summary of the text.
        """
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
        return " ".join(sentences[:max_sentences])

    def find_longest_word(self, text: str) -> str:
        """
        Finds the longest word in the text.
        
        :param text: The input text.
        :return: The longest word in the text.
        """
        words = re.findall(r'\w+', text)
        return max(words, key=len) if words else ""

    def calculate_readability(self, text: str) -> float:
        """
        Calculates the readability score (Flesch Reading Ease) for the text.
        
        :param text: The input text.
        :return: The readability score.
        """
        words = text.split()
        sentences = len(re.split(r'[.!?]', text))
        syllables = sum(self._count_syllables(word) for word in words)
        if sentences == 0 or len(words) == 0:
            return 0
        return 206.835 - 1.015 * (len(words) / sentences) - 84.6 * (syllables / len(words))

    def _count_syllables(self, word: str) -> int:
        """
        Counts the number of syllables in a word.
        
        :param word: The input word.
        :return: The number of syllables in the word.
        """
        word = word.lower()
        vowels = "aeiouy"
        syllables = 0
        if word[0] in vowels:
            syllables += 1
        for i in range(1, len(word)):
            if word[i] in vowels and word[i - 1] not in vowels:
                syllables += 1
        if word.endswith("e"):
            syllables = max(1, syllables - 1)
        return syllables
