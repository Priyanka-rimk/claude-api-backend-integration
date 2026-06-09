import os

def write_file_content(working_directory,file_name,content):
    abs_working_dir = os.path.abspath(working_directory)
    abs_target_path = os.path.abspath(os.path.join(working_directory, file_name))
    if not os.path.commonpath(
        [abs_working_dir, abs_target_path]
    ) == abs_working_dir or (not os.path.isfile(abs_target_path)):
        try:
            parent_dir=os.path.dirname(abs_target_path)
            if not os.path.isdir(parent_dir):
                os.makedirs(parent_dir)
        except Exception as e:
            print("error occured",e)
            return f"Error: {str(e)}"
        
        try:
            with open(abs_target_path,"w",encoding="utf-8") as f:
                f.write(content)
                return f"Successfully wrote {len(content)} characters to {file_name}"
        except Exception as e:
            print(e)
            return f"Error: {str(e)}"

WRITE_FILE_TOOL = {
    "name": "write_file_content",
    "description": "Create or overwrite a file inside the permitted working directory with the provided content.",
    "input_schema": {
        "type": "object",
        "properties": {
            "file_name": {
                "type": "string",
                "description": "Path to the file relative to the working directory."
            },
            "content": {
                "type": "string",
                "description": "Content to write into the file."
            }
        },
        "required": ["file_name", "content"]
    }
}