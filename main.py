import os
import zipfile
import img2pdf
import shutil

def list_CBZ_Files(targetDir="."):
    cbz_files = []
    for name in os.listdir(targetDir):
        current = os.path.join(targetDir, name)
        if os.path.isdir(current):
            cbz_files.extend(list_CBZ_Files(current))
        elif os.path.isfile(current) and os.path.splitext(name)[1].lower() == '.cbz':
            cbz_files.append({"name": name, "path": os.path.abspath(current)})

    return sorted(cbz_files, key=lambda x: x['name'])

def convert_cbz_to_pdf(cbz_path, output_path):
    temp_dir = 'temp_images'
    
    # Ensure the temp_images directory is empty
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)
    
    with zipfile.ZipFile(cbz_path, 'r') as cbz:
        # Get the list of image files in the CBZ archive
        image_files = sorted([f for f in cbz.namelist() if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
        
        image_paths = []
        for image_file in image_files:
            image_path = os.path.join(temp_dir, image_file)
            with cbz.open(image_file) as image_file_data:
                with open(image_path, 'wb') as f:
                    f.write(image_file_data.read())
            image_paths.append(image_path)
        
        # Convert images to PDF
        with open(output_path, 'wb') as f:
            f.write(img2pdf.convert(image_paths))
        
        # Clean up temporary directory
        shutil.rmtree(temp_dir)

# Convert all CBZ files to PDF
def convertAll_CBZ_Files():
    targetDir = input("enter  the target directory path : ")
    if (targetDir == ""):
        targetDir = "."
    if not os.path.exists(targetDir):
        print(f"Directory {targetDir} does not exist")
        return
    print('---------------------------------------------------------')
    cbz_files = list_CBZ_Files(targetDir)
    print("CBZ Files found:")
    if len(cbz_files) == 0:
        print("No CBZ files found")
        return
    for file in cbz_files:
        print(f"- {file['path']}")
    print('---------------------------------------------------------')
    answer = input("Do you want to convert all CBZ files to PDF? (y/n): ")
    while answer.lower() not in ['y', 'n']:
        answer = input("Please enter 'y' or 'n': ")
    if answer.lower() != 'y':
        print("Exiting without converting any files...")
        return
    print('---------------------------------------------------------')
    for cbz_file in cbz_files:
        output_path = os.path.splitext(cbz_file["path"])[0] + ".pdf"
        if os.path.exists(output_path):
            print(f"Skipping {cbz_file['name']} as PDF already exists")
            continue
        convert_cbz_to_pdf(cbz_file["path"], output_path)
        print(f"Converted {cbz_file['name']} to PDF")


convertAll_CBZ_Files()