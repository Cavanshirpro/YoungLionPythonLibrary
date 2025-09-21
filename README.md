# Young Lion Python Library

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)

The **Young Lion Python Library** is designed to simplify the work of developers, especially *Young Lion Developers*. This library provides a wide range of functionalities for handling various file formats, managing directories, and executing file-related operations efficiently.

This library is under development and will be expanded with more features in the future.

---

## Unlike 0.0.7:
We fixed some minor bugs in VISTA in version 0.0.7.1. We did not make the version 0.0.8 because there were no major changes. (0.0.7.2, 0.0.7.3)
In 0.0.7.4 we colored some terminal text.
In 0.0.7.6 New functions have been added to the File class. move_folder move_file copy_file create_folder
In 0.0.7.8 We optimized functions
## Unlike 0.0.8:
0.0.8 We add new search module
0.0.8.2 Added some small functions to File class
## Unlike 0.0.9:
0.0.9 We add minigames in library
0.0.9.1 Some bugs have been fixed and hangman word data has been improved.
0.0.9.2 A custom feature has arrived for you to integrate XOX and Hangman games into your own interface and applications.
0.0.9.4 We add Terminal Module in library
0.0.9.6 We added ANCI and untils to the terminal module.
0.0.9.7 I came to the decision to divide the library into categories

---

## Table of Contents

- [Installation](#installation)
- [Modules](#modules)
  - [Functions](#functions)
  - [Search](#search)
- [Usage Examples](#usage-examples)
  - [File Module Example](#file-module-example)
  - [Search Module Example](#search-module-example)
- [Changelog](#changelog)
- [License](#license)
- [Contributing](#contributing) (Optional: Add details if applicable)

---

## Installation

To install the Young Lion library, run the following command:

```bash
pip install YoungLion
```

**Attention!** If an error or problem occurs during the installation, you may need to run these commands in the terminal:

```bash
pip cache purge
python -m pip install --upgrade pip
pip install YoungLion --no-cache-dir
```

---

## Modules

The library is organized into the following modules:

- ### Functions
- ### Search
---

## Functions Features and Overview

This module contains a very comprehensive set of Python classes that perform various functions. Below is a general summary of these classes and the main features they offer:

---

#### **1. `File` Class**
- **Purpose**: File processing (JSON, TXT, CSV, LOG, PDF, XML, YAML, INI, etc.) and directory management.
- **Supported Operations**:
  - Reading and writing JSON, TXT, LOG files.
  - Reading, writing, adding and updating CSV files.
  - Reading, writing, and creating PDF content.
  - Read, write and edit XML files.
  - Compressing and extracting compressed files (`.zip`).
  - Read/write HTML, CSS, and JS files.
  - **Python File Management**:
    - Executing Python files with argument and terminal options.
    - Adding code blocks to Python files (start, end, or specific line).
    - Validating and preparing Python file paths.
  - Executing SQL queries and creating tables.
  - **JavaScript File Management**:
    - Reading, writing, and executing JavaScript files.
    - Terminal-based or background execution.
  - **LaTeX Processing**:
    - Converting Markdown to LaTeX.
    - Reading and writing `.tex` files.
    - Compiling LaTeX to plain text.
    - Converting LaTeX to Markdown.
    - Appending content to `.tex` files.
    - Converting LaTeX to HTML with MathJax support.
    - Rendering LaTeX as images.
  - **Directory & File Operations**: (Added in 0.0.7.6)
    - `move_folder`, `move_file`, `copy_file`, `create_folder`, `delete_file`, `delete_folder` (Added in 0.0.8.2)

---

#### **2. `ScriptRunner` Class**
- **Objective**: Execute scripts in Node.js or a specified interpreter.
- **Key Features**:
  - Run a script in the terminal or in the background.
  - Providing input data for the script.
  - Capture and process outputs.

---

#### **3. `TaskScheduler` Class
- **Purpose**: Schedule, pause, resume and cancel tasks.
- **Supported Functions**:
  - Create one-off or repetitive tasks.
  - Prioritizing tasks.
  - CLI-based task listing.

---

#### **4. `Logger` Class**
- Purpose**: Flexible logging at the application level.
- **Features**:
  - Write information, error and warning messages to log file.
  - Support for different log levels (INFO, DEBUG, ERROR, etc.).
  - Console and file logging support.

---

#### **5. `EmailManager` Class**
- **Purpose**: Email sending and management.
- **Basic Functions**:
  - Sending email instantly.
  - Scheduling email based on a specific time.
  - Check the last messages in your inbox.

---

#### **6. `FileTransferManager` Class**
- **Purpose**: Uploading and downloading files using FTP and SFTP.
- **Features**:
  - File upload and download.
  - Track transfer status.
  - Supported protocols: FTP and SFTP.

---

#### **7. `TextProcessor` Class**
- **Purpose**: Text analysis and editing.
- **Key Features**:
  - Word and character counting.
  - Keyword search.
  - Text replacement and summarization.
  - Finding the most frequently used words.
  - Readability score calculation.

---

With their modular structure and rich feature set, these classes provide powerful tools for many application development processes. Each one is optimized for a specific type of data processing or management operations.

---
## Search Features and Overview

The **Search** module provides an advanced and efficient way to search through structured data using keyword-based matching. This module offers:

- **Tag Generation (`GenerateTags` class)**:
  - Automatically generates keyword tags from input text.
  - Supports custom replacements (e.g., "Minecraft" → "MC").
  - Removes unnecessary stopwords for better efficiency.
  - Supports case normalization and special character cleaning.
  - Generates keyword combinations and permutations.

- **Data Organization (`SearchData` class)**:
  - Stores searchable data with keyword-based mapping.
  - Allows quick retrieval of associated data.

- **Advanced Search System (`Search` class)**:
  - Finds relevant search results based on keywords.
  - Uses fuzzy matching to suggest close alternatives.
  - Supports exact-match searching if required.

### **Usage Example**

```python
from YoungLion import Search, SearchData, GenerateTags

# Create structured search data
search_entries = [
    {"tags": ["Science", "Physics", "Quantum Mechanics"], "return": {"title": "Quantum Theory", "link": "example.com/qm"}},
    {"tags": ["Programming", "Python", "Machine Learning"], "return": "Learn Python for ML"}
]

sdata = SearchData(search_entries)
search_engine = Search(sdata)

# Perform a search
results = search_engine.search("Physics")
print(results)  # Output: [{'title': 'Quantum Theory', 'link': 'example.com/qm'}]
```

With the **Search** module, you can implement a high-performance keyword search engine with minimal effort.

# Terminal Feature and Overview

We created this module to make some of your operations easier in the programs you will perform via the terminal.

- ## Terminal Loader
### Overview
With this feature, you will be able to create a loading bar in the terminal very easily in your own codes.

### **Usage Example**

```python
import time
from YoungLion.terminal import TerminalBar # Corrected import path if necessary

print("Test Starting:\n\n")
total_size = 1024*1024
bar = TerminalBar(total_size, 0, 100) # Initialize bar

# Simulate progress
for i in range(0, total_size + 1, total_size // 10):
    bar.update(i)
    time.sleep(0.1)
print("\nLoading Complete!")
```

---

# Usage/Examples

### **Comprehensive Guide to Using the `File` Class**

The `File` class is a robust utility for managing and processing various file types such as JSON, TXT, CSV, PDF, XML, YAML, and more. With built-in error handling and directory management, it simplifies complex file operations for developers. Below is a detailed guide on its usage and capabilities.

---

### **Initialization**
The `File` class can optionally be initialized with a `filefolder` parameter, which sets a default directory for file operations.

```python
import YoungLion

# Initialize with a default directory
file_manager = YoungLion.File(filefolder="/path/to/default/directory")
```

---

### **Supported File Operations**

#### **1. Directory Management**
The `list_files_and_folders` method lists all files and folders in a given directory.

```python
# List files and folders in the default directory
items = file_manager.list_files_and_folders()

# List files and folders in a specific directory
items = file_manager.list_files_and_folders(path="/path/to/directory")
```

---

#### **2. JSON File Handling**
**Reading JSON Files**: Reads data from a JSON file, with optional defaults and automatic creation of empty files if missing.

```python
# Reading a JSON file
data = file_manager.json_read("data.json", default={"key": "value"})

# Access nested data safely
value = data["key"]["nested_key"]
```

**Writing JSON Files**: Writes a dictionary to a JSON file.

```python
# Writing data to a JSON file
file_manager.json_write("data.json", {"name": "John", "age": 30})
```

---

#### **3. TXT File Handling**
**Reading Text Files**: Read an entire text file or process it line-by-line.

```python
# Read the whole file as a string
content = file_manager.txt_read_str("notes.txt")

# Read line-by-line into a dictionary with line numbers as keys
lines = file_manager.txt_read_linear("notes.txt")
```

**Writing Text Files**: Write strings or line-based dictionaries to a text file.

```python
# Write a string to a file
file_manager.txt_write_str("output.txt", "This is a sample text.")

# Write lines to a file with line numbers
lines_to_write = {1: "First line", 2: "Second line"}
file_manager.txt_write_linear("output.txt", lines_to_write)
```

---

#### **4. CSV File Handling**
**Reading CSV Files**: Reads a CSV file into a list of dictionaries.

```python
# Read CSV file
rows = file_manager.csv_read("data.csv")
```

**Writing CSV Files**: Writes a list of dictionaries to a CSV file.

```python
# Write rows to a CSV file
file_manager.csv_write("output.csv", [{"Name": "Alice", "Age": 25}, {"Name": "Bob", "Age": 30}])
```

**Appending and Updating CSV Data**: Append new rows or update existing ones based on unique identifiers.

```python
# Append rows to an existing CSV
file_manager.csv_append("data.csv", [{"Name": "Charlie", "Age": 35}])

# Update rows in a CSV
file_manager.csv_update("data.csv", [{"Name": "Alice", "Age": 26}], identifier="Name")
```

---

#### **5. PDF File Handling**
**Reading PDF Files**: Extracts text content from a PDF file.

```python
# Extract text from a PDF
text = file_manager.pdf_read("document.pdf")
```

**Writing PDF Files**: Writes text content to a PDF.

```python
# Write text to a PDF
file_manager.pdf_write("output.pdf", "This is a sample PDF content.")
```

---

#### **6. XML File Handling**
**Reading XML Files**: Parses XML files into dictionaries.

```python
# Read an XML file
xml_data = file_manager.xml_read("data.xml")
```

**Writing and Appending XML Files**: Writes or appends dictionaries to XML files.

```python
# Write XML data
file_manager.xml_write("output.xml", {"root": {"child": "value"}})

# Append XML data
file_manager.xml_append("data.xml", {"additional": "value"})
```

---

#### **7. YAML and INI File Handling**
**YAML Operations**: Read and write YAML files.

```python
# Read YAML file
yaml_data = file_manager.yaml_read("config.yml", default={"setting": "default"})

# Write YAML data
file_manager.yaml_write("config.yml", {"setting": "custom"})
```

**INI Operations**: Read and write INI configuration files.

```python
# Read INI file
ini_data = file_manager.ini_read("config.ini")

# Write INI data
file_manager.ini_write("config.ini", {"Section": {"Key": "Value"}})
```

---

#### **8. Properties File Handling**
Reads and writes `.properties` files, commonly used for configuration.

```python
# Read properties file
props = file_manager.properties_read("config.properties")

# Write to properties file
file_manager.properties_write("config.properties", {"key": "value"}, append=True)
```

---

#### **9. HTML, CSS, and JavaScript**
Handles web-related file types like HTML, CSS, and JS.

```python
# Read an HTML file
html_content = file_manager.html_read("index.html")

# Write to an HTML file
file_manager.html_write("index.html", "<h1>Hello World</h1>")
```

---

#### **10. Compressed Files**
Compress or extract files and folders.

```python
# Compress a folder
file_manager.handle_compressed("folder_path", action="compress", target="archive.zip")

# Extract a zip file
file_manager.handle_compressed("archive.zip", action="extract", target="output_folder")
```

---

#### **11. LaTeX Processing**
The `File` class includes comprehensive support for LaTeX operations.

**Converting Markdown to LaTeX**: Converts a Markdown string to a LaTeX-formatted string.

```python
# Convert Markdown to LaTeX
latex_content = file.markdown_to_latex("# Heading\nThis is a paragraph.")
```

**Reading and Writing `.tex` Files**: Provides utilities to read, write, and append `.tex` files.

```python
# Read a .tex file
content = file.tex_read("document.tex")

# Write content to a .tex file
file.tex_write("output.tex", "\\section{Introduction}\nThis is a LaTeX document.")

# Append content to a .tex file
file.tex_append("document.tex", "\\subsection{Conclusion}\nThank you!")
```

**Compiling LaTeX to Plain Text**: Converts LaTeX-formatted content to plain text, stripping out special commands.

```python
# Compile LaTeX to plain text
plain_text = file.latex_compile(r"V_{SC} = \frac{N}{G}")
```

**Converting LaTeX to Markdown**: Transforms LaTeX content into Markdown format.

```python
# Convert LaTeX to Markdown
markdown_content = file.tex_to_markdown(r"\section{Hello World}")
```

**Generating HTML with MathJax Support**: Creates an HTML file displaying LaTeX content using MathJax.

```python
# Convert LaTeX to HTML
html_content = file.latex_to_html(r"V_{SC} = \frac{YL_{bank}}{YL_{official}}", "output.html")
```

**Rendering LaTeX as an Image**: Generates a visual representation of LaTeX formulas as images.

```python
# Render LaTeX formula as an image
image_data = file.latex_to_image(r"V_{SC} = \sqrt{N}", "output.png")
```

---

### **12. Python File Handling**
The `File` class includes enhanced support for managing and manipulating Python files, such as executing scripts and dynamically adding code blocks.

#### **Executing Python Files**
You can execute a Python file with optional arguments and capture its output.

```python
# Run a Python script
output = file.py_run("example.py", args=["--arg1", "value"])
print(output)
```

#### **Adding Code to Python Files**
Dynamically add new functions or code snippets to an existing Python file.

**Adding Code to the End of a File**:
```python
new_function = """
def say_hello():
    print("Hello, Python!")
"""
file.py_add_code("example.py", new_function, position="end")
```

**Adding Code to the Start of a File**:
```python
new_function = """
def initialize():
    print("Initialization complete!")
"""
file.py_add_code("example.py", new_function, position="start")
```

**Adding Code at a Specific Line**:
```python
new_code = "print('This is a new line of code.')"
file.py_add_code("example.py", new_code, position=5)
```

---

### **Error Handling**
The `File` class incorporates robust error handling mechanisms to deal with:
- Missing files or directories.
- Invalid formats (e.g., corrupted JSON or XML).
- Permission issues.

For instance, if a file is missing during a `json_read` operation, it will automatically create an empty JSON file to ensure smooth operation.

---

### **Advantages**
- **Versatile**: Supports a wide variety of file formats and operations.
- **Error-Resilient**: Handles common issues like missing files or invalid data gracefully.
- **Customizable**: Flexible options for path validation and directory management.
- **Integrated**: Provides a unified API for diverse file handling needs.

---

The `File` class is a powerful addition to any Python developer's toolkit, offering a comprehensive suite of file management capabilities in a single interface. Whether you are dealing with structured data files or generating dynamic outputs, this class simplifies and accelerates your workflow.

---

### **Comprehensive Guide to Using the `ScriptRunner` Class**

The `ScriptRunner` class provides a streamlined interface for executing scripts across various interpreters, such as Node.js, Python, or others. It supports input handling, terminal execution, and capturing output, making it ideal for dynamic script management.

---

### **Initialization**
The `ScriptRunner` is initialized with a default interpreter, which will be used unless another is specified during execution.

```python
import YoungLion

# Initialize with a default interpreter (Node.js)
runner = Younglion.ScriptRunner(default_interpreter="node")

# Change the default interpreter
runner.set_default_interpreter("python")
```

---

### **Key Features and Methods**

#### **1. Setting and Validating Paths**
The `_validate_path` method ensures the provided script path is valid and converts it to an absolute path. If the file does not exist, it raises a `FileNotFoundError`.

```python
# Example usage (internal)
validated_path = runner._validate_path("script.js")
print(validated_path)  # Outputs the absolute path of the script
```

---

#### **2. Running Scripts**
The `run_script` method is the core functionality of this class. It allows executing scripts with a specified interpreter, in the terminal or background, with optional input and output handling.

**Parameters**:
- `path`: Path to the script file.
- `interpreter`: Interpreter to use (defaults to the class's default interpreter).
- `terminal`: If `True`, runs the script in a terminal window.
- `inputs`: Input data passed as a string or list of strings.
- `output`: If `True`, captures and returns the script output.

**Example: Basic Script Execution**
```python
# Run a Node.js script in the background
output = runner.run_script("script.js")
print(output)  # Prints the script output
```

**Example: Changing Interpreters**
```python
# Run a Python script with inputs
output = runner.run_script("script.py", interpreter="python", inputs=["arg1", "arg2"])
print(output)
```

**Example: Terminal Execution**
```python
# Run a script in the terminal (e.g., on macOS/Linux)
runner.run_script("script.js", terminal=True)
```

---

#### **3. Handling Inputs**
The `inputs` parameter can handle either a single string or a list of strings. The class ensures the inputs are formatted correctly for the script.

**Example: Passing Inputs**
```python
# Pass a single input string
runner.run_script("script.js", inputs="input_data")

# Pass multiple inputs as a list
runner.run_script("script.js", inputs=["arg1", "arg2", "arg3"])
```

---

#### **4. Output Management**
By default, the method captures and returns the script's output when executed in the background. If `output` is set to `False`, the script is executed without returning the output.

**Example: Suppressing Output**
```python
# Execute without returning output
runner.run_script("script.js", output=False)
```

---

#### **5. Terminal Execution**
When `terminal=True`, the script is run in a terminal window. This feature depends on the operating system and requires a terminal emulator.

- **Windows**: Uses the `cmd` terminal.
- **macOS/Linux**: Uses `xterm` or similar terminal emulators.

**Example: Terminal Execution**
```python
# Run a script in a terminal
runner.run_script("script.js", terminal=True)
```

If no terminal emulator is found, a `RuntimeError` is raised.

---

### **Error Handling**
The `ScriptRunner` class includes robust error handling for common issues:
1. **File Not Found**: If the script file path is invalid or does not exist.
2. **Interpreter Not Found**: If the specified interpreter is unavailable.
3. **Execution Errors**: If the script fails during execution (e.g., syntax errors).

**Example: Error Handling**
```python
try:
    runner.run_script("nonexistent.js")
except FileNotFoundError as e:
    print(f"Error: {e}")
except RuntimeError as e:
    print(f"Execution Error: {e}")
```

---

### **Changing the Default Interpreter**
You can dynamically update the default interpreter using the `set_default_interpreter` method.

```python
# Change to Python as the default interpreter
runner.set_default_interpreter("python")

# Execute a Python script using the new default interpreter
runner.run_script("example.py")
```

---

### **Advantages**
- **Flexibility**: Supports multiple interpreters (e.g., Node.js, Python).
- **Input Handling**: Seamless integration of inputs for scripts.
- **Terminal/Background Execution**: Run scripts in various modes depending on your needs.
- **Cross-Platform**: Works on Windows, macOS, and Linux with appropriate configurations.

---

### **Usage Scenarios**
- **Automated Script Execution**: Dynamically run scripts for tasks such as testing or data processing.
- **Multi-Interpreter Environments**: Manage scripts in different programming languages without switching environments.
- **Real-Time Input/Output**: Capture output and integrate with larger Python workflows.

The `ScriptRunner` class is a powerful utility for developers needing streamlined script execution across diverse environments. It bridges the gap between Python and other runtime environments, making it an essential tool for automation and scripting.

---

### **Comprehensive Guide to Using the `TaskScheduler` Class**

The `TaskScheduler` class is a robust solution for managing and executing tasks with features such as priority-based scheduling, pausing/resuming tasks, repeating intervals, and detailed task tracking. Designed with multi-threading and thread safety, it is ideal for building dynamic and flexible applications.

---

### **Initialization**
The `TaskScheduler` initializes the necessary data structures and locks for managing tasks. 

```python
import YoungLion

# Initialize a TaskScheduler instance
scheduler = YoungLion.TaskScheduler()
```

---

### **Key Features and Methods**

#### **1. Scheduling Tasks**
The `schedule_task` method allows scheduling tasks with optional repeating intervals and priority control.

**Parameters**:
- `task`: The callable function to execute.
- `interval`: Time interval (in seconds) for repeating tasks. If `None`, the task runs only once.
- `repeat`: Whether the task repeats (`True`) or runs once (`False`).
- `priority`: Lower values indicate higher priority.

**Returns**: A unique `task_id` for tracking the task.

**Example: One-Time Task**
```python
# Schedule a one-time task
task_id = scheduler.schedule_task(lambda: print("Hello, world!"), repeat=False)
```

**Example: Repeating Task**
```python
# Schedule a repeating task with an interval of 5 seconds
task_id = scheduler.schedule_task(lambda: print("Repeating task"), interval=5, repeat=True)
```

**Example: Priority-Based Task Scheduling**
```python
# Schedule tasks with different priorities
scheduler.schedule_task(lambda: print("High priority task"), priority=1)
scheduler.schedule_task(lambda: print("Low priority task"), priority=10)
```

---

#### **2. Pausing and Resuming Tasks**
Tasks can be paused and resumed using their unique `task_id`.

**Pausing a Task**
```python
# Pause a running task
scheduler.pause_task(task_id)
```

**Resuming a Task**
```python
# Resume a paused task
scheduler.resume_task(task_id)
```

**Example: Pausing and Resuming**
```python
# Pause and resume a repeating task
scheduler.pause_task(task_id)
scheduler.resume_task(task_id)
```

---

#### **3. Canceling Tasks**
Tasks can be canceled at any point using their `task_id`. This sets the task's status to `"cancelled"` and prevents further execution.

**Example: Cancel a Task**
```python
scheduler.cancel_task(task_id)
```

---

#### **4. Listing Tasks**
The `list_tasks` method displays all scheduled tasks with their:
- **Status**: `running`, `paused`, `queued`, or `cancelled`.
- **Priority**: Task priority level.
- **Repeat**: Whether the task repeats.

**Example: List All Tasks**
```python
scheduler.list_tasks()
```

**Sample Output**:
```
Scheduled Tasks:
ID: 12345, Status: running, Priority: 5, Repeat: True
ID: 67890, Status: paused, Priority: 10, Repeat: False
```

---

#### **5. Thread Safety**
The `TaskScheduler` uses threading locks to ensure thread-safe operations, especially when modifying shared data like `tasks` and `task_status`.

**Internal Example: Lock Usage**
```python
with self.lock:
    # Safe access or modification of shared resources
    self.task_status[task_id] = "paused"
```

---

### **Advanced Concepts**

#### **Task Lifecycle**
1. **Queued**: The task is added to the priority queue but has not started execution.
2. **Running**: The task is actively executing.
3. **Paused**: The task is temporarily halted and can be resumed.
4. **Cancelled**: The task is stopped and will not execute further.
5. **Completed**: The task has finished execution.

#### **Priority Queue**
Tasks are added to a priority queue (`PriorityQueue`), ensuring higher-priority tasks are executed first.

---

### **Error Handling**
The `TaskScheduler` provides robust error handling:
- Ensures invalid operations (e.g., pausing a completed task) are gracefully managed.
- Catches and logs exceptions during task execution without crashing the scheduler.

**Example: Error Handling**
```python
# Schedule a task with intentional error
def faulty_task():
    raise ValueError("An intentional error.")

scheduler.schedule_task(faulty_task)

# Output: Task <task_id> encountered an error: An intentional error.
```

---

### **Advantages**
- **Flexibility**: Supports both one-time and repeating tasks.
- **Priority-Based Execution**: Ensures critical tasks are executed first.
- **Thread Safety**: Enables safe multi-threaded task management.
- **Dynamic Control**: Tasks can be paused, resumed, and canceled dynamically.

---

### **Usage Scenarios**
1. **Background Data Processing**: Schedule repeating tasks to fetch or process data periodically.
2. **Dynamic Workflows**: Adjust task execution based on changing priorities or conditions.
3. **Task Automation**: Automate processes with time-based or event-driven triggers.

The `TaskScheduler` class simplifies complex task management while maintaining flexibility and control. It is a powerful utility for developers needing reliable and dynamic task scheduling in Python applications.

---

### **Comprehensive Guide to Using the `Logger` Class**

The `Logger` class provides a structured and customizable logging solution for Python applications. It supports logging at various levels, including `INFO`, `WARNING`, and `ERROR`, with output directed to both console and log files.

---

### **Initialization**
The `Logger` class initializes with a specified log file and default log level.

```python
import YoungLion

# Create a logger with default log level (INFO) and log file
logger = YoungLion.Logger(log_file="application.log", log_level="INFO")
```

**Parameters**:
- `log_file`: Path to the log file (default: `app.log`).
- `log_level`: Default logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`).

---

### **Key Features and Methods**

#### **1. Setting Log Levels**
The `set_log_level` method updates the logging level dynamically.

**Example: Setting Log Level**
```python
logger.set_log_level("DEBUG")  # Enables detailed debug-level logs
```

Supported log levels:
- `DEBUG`: Detailed debug information.
- `INFO`: General operational information.
- `WARNING`: Indicates potential issues.
- `ERROR`: Errors in application execution.
- `CRITICAL`: Severe errors causing application crashes.

---

#### **2. Logging Messages**
The `Logger` provides methods to log messages at different levels.

**Log an Informational Message**
```python
logger.log_info("Application started successfully.")
```

**Log a Warning**
```python
logger.log_warning("API response took longer than expected.")
```

**Log an Error**
```python
logger.log_error("Failed to connect to the database.")
```

**Example Output** (Console and `application.log`):
```
[2024-12-10 10:00:00] [INFO]: Application started successfully.
[2024-12-10 10:05:00] [WARNING]: API response took longer than expected.
[2024-12-10 10:10:00] [ERROR]: Failed to connect to the database.
```

---

#### **3. Configurable Handlers**
The logger is configured with both file and console handlers for dual output. The format is customizable and defaults to:
```
[<timestamp>] [<level>]: <message>
```

---

### **Advantages**
- **Dual Output**: Logs are saved to a file and displayed on the console.
- **Dynamic Configuration**: Update log levels during runtime.
- **Error Resilience**: Ensures critical logs are captured and tracked.

---

### **Usage Scenarios**
1. **Debugging**: Enable `DEBUG` logs to trace code execution.
2. **Monitoring**: Use `INFO` and `WARNING` logs for operational insights.
3. **Error Tracking**: Capture `ERROR` and `CRITICAL` logs for issue diagnosis.

---

### **Comprehensive Guide to Using the `EmailManager` Class**

The `EmailManager` class simplifies email management, providing functionalities for sending, scheduling, and checking inbox emails.

---

### **Initialization**
The class is initialized with SMTP details and login credentials.

```python
import YoungLion

# Initialize the EmailManager
email_manager = YoungLion.EmailManager(
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    email_address="your_email@gmail.com",
    email_password="your_password"
)
```

---

### **Key Features and Methods**

#### **1. Sending Emails**
The `send_email` method sends emails instantly.

**Example: Sending an Email**
```python
email_manager.send_email(
    to="recipient@example.com",
    subject="Test Email",
    body="This is a test email."
)
```

---

#### **2. Scheduling Emails**
The `schedule_email` method schedules an email to be sent at a specific time.

**Example: Scheduling an Email**
```python
from datetime import datetime, timedelta

# Schedule an email 1 hour from now
send_time = datetime.now() + timedelta(hours=1)
email_manager.schedule_email(
    to="recipient@example.com",
    subject="Scheduled Email",
    body="This email is sent at the scheduled time.",
    send_time=send_time
)
```

---

#### **3. Checking the Inbox**
The `check_inbox` method retrieves the latest 10 emails.

**Example: Checking Emails**
```python
emails = email_manager.check_inbox(user="your_email@gmail.com")
for subject, sender in emails:
    print(f"From: {sender}, Subject: {subject}")
```

---

### **Advantages**
- **Flexibility**: Immediate or scheduled email delivery.
- **Inbox Management**: Retrieve and display email metadata.
- **Error Handling**: Resilient to network or authentication issues.

---

### **Usage Scenarios**
1. **Notifications**: Send automated alerts to users.
2. **Reminders**: Schedule emails for important events.
3. **Report Delivery**: Email logs or reports periodically.

---

### **Comprehensive Guide to Using the `FileTransferManager` Class**

The `FileTransferManager` handles file uploads and downloads via FTP and SFTP protocols. It supports tracking transfer status, ensuring robust and transparent operations.

---

### **Initialization**
The `FileTransferManager` initializes with a transfer status dictionary.

```python
import YoungLion

# Initialize the manager
transfer_manager = YoungLion.FileTransferManager()
```

---

### **Key Features and Methods**

#### **1. Uploading Files**
The `upload` method uploads files using FTP or SFTP.

**Example: FTP Upload**
```python
transfer_id = transfer_manager.upload(
    file_path="local_file.txt",
    destination="/remote/path/file.txt",
    protocol="ftp",
    host="ftp.example.com",
    username="user",
    password="password"
)
```

**Example: SFTP Upload**
```python
transfer_id = transfer_manager.upload(
    file_path="local_file.txt",
    destination="/remote/path/file.txt",
    protocol="sftp",
    host="sftp.example.com",
    username="user",
    password="password",
    port=22
)
```

---

#### **2. Downloading Files**
The `download` method retrieves files using FTP or SFTP.

**Example: FTP Download**
```python
transfer_id = transfer_manager.download(
    remote_path="/remote/path/file.txt",
    local_path="local_file.txt",
    protocol="ftp",
    host="ftp.example.com",
    username="user",
    password="password"
)
```

---

#### **3. Checking Transfer Status**
Check the status of uploads or downloads using the transfer ID.

**Example: Checking Status**
```python
status = transfer_manager.check_transfer_status(transfer_id)
print(f"Transfer status: {status}")
```

---

### **Advantages**
- **Protocol Support**: Works with FTP and SFTP.
- **Status Tracking**: Provides real-time transfer updates.
- **Error Handling**: Ensures smooth recovery from failed transfers.

---

### **Usage Scenarios**
1. **Data Migration**: Automate file uploads and downloads.
2. **Backup Management**: Transfer backups to secure locations.
3. **Content Distribution**: Efficiently distribute files to multiple servers.

---

### **Comprehensive Guide to Using the `TextProcessor` Class**

The `TextProcessor` class offers a range of text analysis and manipulation tools. Its versatile methods can handle word counting, keyword searching, text replacement, readability scoring, and more. It is designed to simplify text processing tasks for applications such as natural language processing, data cleaning, and analysis.

---

### **Initialization**
The `TextProcessor` class does not require any specific initialization and can be directly used by calling its methods.

```python
from text_processor_module import TextProcessor

# Instantiate the TextProcessor
text_processor = TextProcessor()
```

---

### **Key Features and Methods**

#### **1. Word Counting**
The `word_count` method calculates the number of words in a given text.

**Example**:
```python
text = "This is a sample text with several words."
count = text_processor.word_count(text)
print(f"Word count: {count}")
```
**Output**:
```
Word count: 7
```

---

#### **2. Finding Keywords**
The `find_keywords` method identifies specific keywords and counts their occurrences.

**Example**:
```python
text = "Python is powerful. Python is easy to learn."
keywords = ["Python", "easy", "hard"]
result = text_processor.find_keywords(text, keywords)
print(result)
```
**Output**:
```python
{'Python': 2, 'easy': 1, 'hard': 0}
```

---

#### **3. Text Replacement**
The `replace_text` method replaces all occurrences of a substring with another string.

**Example**:
```python
text = "Hello world! Welcome to the world of Python."
replaced_text = text_processor.replace_text(text, "world", "universe")
print(replaced_text)
```
**Output**:
```
Hello universe! Welcome to the universe of Python.
```

---

#### **4. Sentence Counting**
The `sentence_count` method counts the number of sentences in a text.

**Example**:
```python
text = "This is a sentence. Here's another! And one more?"
count = text_processor.sentence_count(text)
print(f"Sentence count: {count}")
```
**Output**:
```
Sentence count: 3
```

---

#### **5. Character Counting**
The `character_count` method calculates the number of characters, optionally excluding spaces.

**Example**:
```python
text = "Hello, world!"
count_with_spaces = text_processor.character_count(text)
count_without_spaces = text_processor.character_count(text, include_spaces=False)
print(f"With spaces: {count_with_spaces}, Without spaces: {count_without_spaces}")
```
**Output**:
```
With spaces: 13, Without spaces: 11
```

---

#### **6. Most Frequent Words**
The `most_frequent_words` method identifies the most commonly used words.

**Example**:
```python
text = "apple banana apple orange banana apple orange"
top_words = text_processor.most_frequent_words(text, top_n=2)
print(top_words)
```
**Output**:
```python
[('apple', 3), ('banana', 2)]
```

---

#### **7. Removing Stopwords**
The `remove_stopwords` method removes specified stopwords from the text.

**Example**:
```python
text = "This is a simple text processing example."
stopwords = ["is", "a", "this"]
filtered_text = text_processor.remove_stopwords(text, stopwords)
print(filtered_text)
```
**Output**:
```
simple text processing example.
```

---

#### **8. Finding Unique Words**
The `unique_words` method extracts unique words from the text.

**Example**:
```python
text = "Python Python programming is fun!"
unique = text_processor.unique_words(text)
print(unique)
```
**Output**:
```python
['fun', 'is', 'programming', 'python']
```

---

#### **9. Text Summarization**
The `text_summary` method generates a summary by selecting the first few sentences.

**Example**:
```python
text = "Sentence one. Sentence two. Sentence three. Sentence four."
summary = text_processor.text_summary(text, max_sentences=2)
print(summary)
```
**Output**:
```
Sentence one. Sentence two.
```

---

#### **10. Finding the Longest Word**
The `find_longest_word` method identifies the longest word in the text.

**Example**:
```python
text = "Short and sweet words are sometimes powerful."
longest_word = text_processor.find_longest_word(text)
print(longest_word)
```
**Output**:
```
sometimes
```

---

#### **11. Readability Scoring**
The `calculate_readability` method computes the Flesch Reading Ease score for the text.

**Example**:
```python
text = "This is an example text for readability scoring. It calculates the ease of reading."
score = text_processor.calculate_readability(text)
print(f"Readability score: {score}")
```
**Output**:
```
Readability score: 76.5 (example value, may vary based on text)
```

---

### **Advantages**
- **Comprehensive Tools**: Covers a wide range of text processing functionalities.
- **Customizable**: Flexible parameters for various methods.
- **Efficient**: Lightweight and easy to integrate into applications.

---

### **Usage Scenarios**
1. **Natural Language Processing**: Preprocess text for machine learning models.
2. **Content Analysis**: Extract insights from articles, documents, or web content.
3. **Data Cleaning**: Remove stopwords, redundant phrases, or noise from raw text.
4. **Summarization**: Generate concise overviews for long texts or documents.

The `TextProcessor` class simplifies text processing and analysis, making it an essential utility for developers handling textual data.

---
## Contribution
Contributions to the **Young Lion Python Library** are welcome! Please open issues or submit pull requests to suggest enhancements or report bugs.

## LICENSE

This project is licensed under the [MIT](https://choosealicense.com/licenses/mit/) License.
