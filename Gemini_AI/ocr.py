import google.generativeai as genai
import os
import re 

import os
import cv2


# Generate API key from here https://aistudio.google.com/app/apikey

os.environ["API_KEY"]="<API_KEY>"

genai.configure(api_key=os.environ["API_KEY"])


# Specify the directory you want to list files from
directory_path = 'images'

# Regular expression to match the number inside the parentheses
def extract_number(filename):
    match = re.search(r'\((\d+)\)', filename)
    return int(match.group(1)) if match else 0

# Get the list of all files in the directory and sort them based on the number in parentheses
files_and_dirs = sorted(os.listdir(directory_path), key=extract_number)

print(files_and_dirs)
whole_PDF_text = ''
# Loop through the items
for item in files_and_dirs:
    print("********************************",item)
    # Upload the file and print a confirmation
    sample_file = genai.upload_file(path=f"images/{item}",
                                    display_name=item)

    print(f"Uploaded file '{sample_file.display_name}' as: {sample_file.uri}")

    file = genai.get_file(name=sample_file.name)
    print(f"Retrieved file '{file.display_name}' as: {sample_file.uri}")


    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content([sample_file, "extract the text data in proper format from the given image."])

    if not os.path.exists("extracted_text"):
        os.makedirs("extracted_text")

    with open(f"extracted_text/{item.replace('.png','.txt')}","w",encoding='utf-8') as f:
        f.write(response.text)

with open("text_data_new.txt", "w", encoding='utf-8') as f:
    f.write(whole_PDF_text) 