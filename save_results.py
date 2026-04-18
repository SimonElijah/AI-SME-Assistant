import os
from datetime import datetime

def save_result(text, folder="saved_results"):
    # Create folder if not exist
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Create file name using date and time
    filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".txt"
    filepath = os.path.join(folder, filename)

    # Save text
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)

    return filepath
