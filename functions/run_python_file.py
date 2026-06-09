import os
import subprocess


def run_python_file(working_directory: str, file_name: str):
    abs_working_dir = os.path.abspath(working_directory)
    abs_target_path = os.path.abspath(os.path.join(working_directory, file_name))
    if not os.path.commonpath(
        [abs_working_dir, abs_target_path]
    ) == abs_working_dir or (not os.path.isfile(abs_target_path)):
        return f"{abs_target_path} maybe wrong path or not a file"

    if not file_name.strip().endswith(".py"):
        return f"{file_name} is not a .py file"

    try:
        output = subprocess.run(
            ["python", file_name], timeout=30, cwd=abs_working_dir, capture_output=True
        )
        return f"{output.stdout} successfully ran {file_name} file"
    except Exception as e:
        return f"Error: {str(e)}"

RUN_PYTHON_FILE_TOOL = {
    "name": "run_python_file",
    "description": "Execute a Python file located inside the permitted working directory and return its output.",
    "input_schema": {
        "type": "object",
        "properties": {
            "file_name": {
                "type": "string",
                "description": "The Python file to execute, relative to the working directory."
            }
        },
        "required": ["file_name"]
    }
}