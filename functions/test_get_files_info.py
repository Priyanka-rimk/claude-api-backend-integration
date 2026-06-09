from get_file_info import get_files_info
from get_file_content import get_file_content
from write_file import write_file_content
from run_python_file import run_python_file

# print(get_files_info("calculator", "."))
# print(get_files_info("calculator", "bin"))
# print(get_files_info("calculator", "../main.py"))
# print(get_files_info("calculator", "main.py"))
# print(get_files_info("calculator", "."))

# print(get_file_content("calculator","main.py"))
# print(get_file_content("calculator","pkg"))

# write_file_content("calculator","mains.txt","Heyyyyyyyyyyyy")
# write_file_content("calculator", "pkg/morelorem.txt", "lorem ipsum dolor sit amet")

run_python_file("calculator","main.py")