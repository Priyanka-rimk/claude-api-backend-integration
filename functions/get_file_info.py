import os

def get_files_info(working_directory:str, directory:str='.')->str:
    abs_working_dir_path=os.path.abspath(working_directory)
    target_dir=os.path.normpath(os.path.join(abs_working_dir_path,directory))
    valid_target_dir=os.path.commonpath([abs_working_dir_path,target_dir])==abs_working_dir_path
    if not valid_target_dir:
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
    return (f"size will be {os.path.getsize(target_dir)},isdir {os.path.isdir(target_dir)}")

GET_FILE_INFO_TOOL={
    "name":"get_files_info",
    "description":"Validate file path in a specified directory relative to the working directory, providing file size and directory status",
    "input_schema":{
        "type":"object",
        "properties":{
            "directory": {
                "type": "string",
                "description": "Directory give the path of file to know about it"
            }
        },
        "required":["working_directory"]
    }
}