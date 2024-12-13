import os
import zipfile
import img2pdf
import shutil
import subprocess
import rarfile
from time import sleep

def ensure_unrar():
    """Ensures unrar is installed and configured."""
    try:
        # Try running the unrar command to check if it's available
        subprocess.run(["unrar"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("Unrar not found. Make sure to install it from the following link :\n https://www.rarlab.com/rar_add.htm")
        sleep(20)
        exit(0)

def list_comic_files(targetDir="."):
    comic_files = []
    for name in os.listdir(targetDir):
        current = os.path.join(targetDir, name)
        if os.path.isdir(current):
            comic_files.extend(list_comic_files(current))
        elif os.path.isfile(current) and os.path.splitext(name)[1].lower() in ['.cbz', '.cbr']:
            comic_files.append({"name": name, "path": os.path.abspath(current)})

    return sorted(comic_files, key=lambda x: x['name'])

def extract_images_from_archive(archive_path, temp_dir):
    # Determine if the archive is CBZ or CBR
    ext = os.path.splitext(archive_path)[1].lower()
    if ext == '.cbz':
        with zipfile.ZipFile(archive_path, 'r') as archive:
            files = [f for f in archive.namelist() if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            for file in sorted(files):
                archive.extract(file, temp_dir)
    elif ext == '.cbr':
        with rarfile.RarFile(archive_path, 'r') as archive:
            files = [f for f in archive.namelist() if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            for file in sorted(files):
                archive.extract(file, temp_dir)
    else:
        raise ValueError("Unsupported file format")
    
def get_image_paths(temp_dir):
    image_paths = []
    
    # Use os.walk to traverse all subdirectories
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_paths.append(os.path.join(root, file))
    
    # Sort the image paths (if needed)
    return sorted(image_paths)

def convert_comic_to_pdf(comic_path, output_path):
    temp_dir = 'temp_images'
    
    # Ensure the temp_images directory is empty
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)

    extract_images_from_archive(comic_path, temp_dir)
    
    # Collect all extracted images
    image_paths = get_image_paths(temp_dir)
    
    # Convert images to PDF
    with open(output_path, 'wb') as f:
        f.write(img2pdf.convert(image_paths))

    shutil.rmtree(temp_dir)

        
def convert_all_comic_files():

    ensure_unrar()

    targetDir = input("Enter the target directory path: ")
    if not targetDir:
        targetDir = "."
    if not os.path.exists(targetDir):
        print(f"Directory {targetDir} does not exist")
        return
    
    print('---------------------------------------------------------')
    comic_files = list_comic_files(targetDir)
    print("Comic Files found:")
    if not comic_files:
        print("No CBZ or CBR files found")
        return
    for file in comic_files:
        print(f"- {file['path']}")
    print('---------------------------------------------------------')
    
    answer = input("Do you want to convert all comic files to PDF? (y/n): ")
    while answer.lower() not in ['y', 'n']:
        answer = input("Please enter 'y' or 'n': ")
    if answer.lower() != 'y':
        print("Exiting without converting any files...")
        return
    
    print('---------------------------------------------------------')
    for comic_file in comic_files:
        output_path = os.path.splitext(comic_file["path"])[0] + ".pdf"
        if os.path.exists(output_path):
            print(f"Skipping {comic_file['name']} as PDF already exists")
            continue
        convert_comic_to_pdf(comic_file["path"], output_path)
        print(f"Converted {comic_file['name']} to PDF")

convert_all_comic_files()
