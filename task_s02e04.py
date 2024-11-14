import json
import os
from lib.openai_api import ask_agent, transcribe_audio
from lib.task_api import send_task

WORKING_DIR = "course-resources/pliki_z_fabryki/"


def ask_chatgpt(text):
    prompt = """
    You'll be given a text (an automated monitoring robot report written in Polish). Your task is to categorize it according to the rules below:
    1. If the text mentions humans being captured or encountered during the patrol, return "people" string in the last line of your answer.
    2. If the text mentions hardware fixes (but not updates), return "hardware" string in the last line of your answer.
    3. If the text doesn't mention neither people nor hardware, return "none" string in the last line.
    You'll never receive a text that mentions both people and hardware.
    """
    output = ask_agent(prompt, questions=text, use_langfuse=True, model="gpt-4o-mini", temperature=0.1, max_tokens=1000, name="human-or-hardware-detector-v1")
    return output.split("\n")[-1].strip()

def transcribe_files():
    files = [os.path.join(WORKING_DIR, f) for f in os.listdir(WORKING_DIR) if f.endswith(".png") or f.endswith(".mp3")]
    print(files)
    for file in files:
        if file.endswith(".mp3") or file.endswith(".png"):
            output_file_path = file[:-4] + ".tmp"
            print(f"Output file path: {output_file_path}")
            if not os.path.exists(output_file_path):
                print(f"Processing file {file}...")
                transcript = "";
                if file.endswith(".mp3"):
                    transcript = transcribe_audio(file)
                    print(transcript)
                else:
                    transcript = ask_agent(questions=["Please read the text from the image and return it as a string, without adding any additional text or comments."], image_paths=[file])
                with open(output_file_path, "w", encoding="utf-8") as f:
                    f.write(transcript)
            else:
                print(f"File {output_file_path} already exists. SKipping.")

def _init_categories():
    tmp_file_path = "tmp/task_s02e04.json"
    if os.path.exists(tmp_file_path):
        with open(tmp_file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {
            "people": [],
            "hardware": [],
            "none": []
        }

def _write_categories(categories):
    with open("tmp/task_s02e04.json", "w", encoding="utf-8") as f:
        json.dump(categories, f, indent=4, ensure_ascii=False)


def categorize_files():
    categories = _init_categories()
    files = [f for f in os.listdir(WORKING_DIR) if f[-4:] in [".mp3", ".txt", ".png"]]
    for file_name in files:
        if file_name not in categories["people"] and file_name not in categories["hardware"] and file_name not in categories["none"]:
            print(f"Categorizing file {file_name}...")
            processed_file_name = file_name if file_name.endswith(".txt") else file_name[:-4] + ".tmp"
            print(f"Processed file name: {processed_file_name}")
            with open(os.path.join(WORKING_DIR, processed_file_name), "r", encoding="utf-8") as f:
                category = ask_chatgpt(f.read()).lower().strip()
                if not category in ["people", "hardware", "none"]:
                    raise Exception(f"Invalid category: {category}")                
                categories[category].append(file_name)
            _write_categories(categories)
        else:
            print(f"File {file_name} already categorized. Skipping.")
    return categories


if __name__ == "__main__":
    # Phase I - Convert files to text
    transcribe_files()
    # Phase II - For each text file, ask agent to categorize it, if it's not already categorized
    categories = categorize_files()
    # Phase III - Send response
    del categories["none"]
    print(json.dumps(categories, indent=4, ensure_ascii=False))
    send_task('kategorie', categories)
