import os

MAX_CHAR=1000;

def get_file_content(working_directory, file_name):
    abs_working_dir = os.path.abspath(working_directory)
    abs_target_path = os.path.abspath(os.path.join(working_directory, file_name))
    if not os.path.commonpath(
        [abs_working_dir, abs_target_path]
    ) == abs_working_dir or (not os.path.isfile(abs_target_path)):
        return f"{abs_target_path} maybe wrong path or not a file"
    
    with open(abs_target_path,"r") as f:
        file_content=f.read(MAX_CHAR)
        return file_content
    
GET_FILE_CONTENT_TOOL = {
    "name": "get_file_content",
    "description": "Read the contents of a file from the permitted working directory. Returns up to 1000 characters.",
    "input_schema": {
        "type": "object",
        "properties": {
            "file_name": {
                "type": "string",
                "description": "Path to the file relative to the working directory."
            }
        },
        "required": ["file_name"]
    }
}