# python optimize.py {DIRECTORY} --use-optipng

import os
import argparse
from PIL import Image
import subprocess
from tqdm import tqdm

# типи файлів які оптимізувати
SUPPORTED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp', '.bmp'}

# оптимізація якості
REQUALITY=False
QUALITY=99

def check_dependency(command):
    """Check if a command-line tool is available."""
    try:
        subprocess.run([command, "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except FileNotFoundError:
        return False

def get_file_size(file_path):
    """Get file size in bytes."""
    return os.path.getsize(file_path)

def format_size(size):
    """Format size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"

def optimize_with_pillow(file_path):
    """Optimize image with Pillow."""
    try:
        img = Image.open(file_path)
        if REQUALITY :
            img.save(file_path, optimize=True, quality=QUALITY)
        else:
            img.save(file_path, optimize=True)
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def optimize_with_optipng(file_path):
    """Optimize PNG with optipng."""
    try:
        subprocess.run(["optipng", "-o2", file_path], check=True, stdout=subprocess.DEVNULL)
    except Exception as e:
        print(f"Error optimizing {file_path} with optipng: {e}")

def optimize_images(directory, use_optipng):
    """Optimize images in the directory."""
    if use_optipng and not check_dependency("optipng"):
        print("Error: optipng is not installed. Please install it to use this feature.")
        return

    original_total_size = 0
    optimized_total_size = 0

    # Get all image files in the directory recursively
    image_files = [
        os.path.join(root, file)
        for root, _, files in os.walk(directory)
        for file in files
        if os.path.splitext(file.lower())[1] in SUPPORTED_EXTENSIONS
    ]

    # Progress bar for the entire process
    with tqdm(total=len(image_files), desc="Optimizing images", unit="file") as pbar:
        for file_path in image_files:
            original_size = get_file_size(file_path)
            original_total_size += original_size

            # Optimize with Pillow
            optimize_with_pillow(file_path)

            # Optionally optimize with optipng
            if use_optipng and file_path.lower().endswith('.png'):
                optimize_with_optipng(file_path)

            optimized_size = get_file_size(file_path)
            optimized_total_size += optimized_size

            pbar.update(1)

    # Calculate total reduction percentage
    reduction_total = (original_total_size - optimized_total_size) / original_total_size * 100 if original_total_size > 0 else 0
    savings_total = (optimized_total_size / original_total_size * 100) if original_total_size > 0 else 0

    # Print summary
    print("\nOptimization Summary:")
    print(f"Original Total Size: {format_size(original_total_size)}")
    print(f"Optimized Total Size: {format_size(optimized_total_size)}")
    print(f"Total Reduction: {reduction_total:.2f}%")
    print(f"Space Saved: {100 - savings_total:.2f}%")

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Optimize images in a directory.")
    parser.add_argument("directory", nargs="?", default=os.getcwd(), help="Path to the directory containing images (default: current directory).")
    parser.add_argument("--use-optipng", action="store_true", help="Use optipng for additional PNG optimization.")
    args = parser.parse_args()

    # Optimize images
    optimize_images(args.directory, args.use_optipng)
