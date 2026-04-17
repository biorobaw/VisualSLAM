import argparse
import os
import glob
from PIL import Image
import multiprocessing
from functools import partial

def resize_image(image_path, output_dir, target_height=480, target_width=640, overwrite=False):
    try:
        with Image.open(image_path) as img:
            # Resize image using LANCZOS for high quality downsampling
            resized_img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
            
            if overwrite:
                save_path = image_path
            else:
                rel_path = os.path.basename(image_path)
                save_path = os.path.join(output_dir, rel_path)
                
            resized_img.save(save_path)
            return True
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Normalize Oxford and Webots image sets to 480p (640x480).")
    parser.add_argument("--input_dir", required=True, help="Path to input directory containing images.")
    parser.add_argument("--output_dir", default=None, help="Path to output directory. If not provided, creates 'normalized_480p' folder.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite the original images instead of saving to a new directory.")
    parser.add_argument("--ext", default="*.png", help="Image extension to search for (default: *.png).")
    parser.add_argument("--width", type=int, default=640, help="Target width (default: 640).")
    parser.add_argument("--height", type=int, default=480, help="Target height (default: 480).")
    
    args = parser.parse_args()
    
    input_dir = args.input_dir
    if not args.overwrite and args.output_dir is None:
        output_dir = os.path.join(input_dir, "normalized_480p")
        os.makedirs(output_dir, exist_ok=True)
    elif args.output_dir:
        output_dir = args.output_dir
        os.makedirs(output_dir, exist_ok=True)
    else:
        output_dir = None
        
    # Find images recursively or directly in the folder
    image_paths = glob.glob(os.path.join(input_dir, args.ext))
    if not image_paths:
        image_paths = glob.glob(os.path.join(input_dir, "**", args.ext), recursive=True)
        
    if not image_paths:
        print(f"No images found in {input_dir} matching {args.ext}")
        return
        
    print(f"Found {len(image_paths)} images. Starting normalization to {args.width}x{args.height}...")
    
    # Process in parallel to speed up execution for large datasets
    process_func = partial(resize_image, output_dir=output_dir, target_height=args.height, target_width=args.width, overwrite=args.overwrite)
    
    success_count = 0
    with multiprocessing.Pool() as pool:
        results = pool.map(process_func, image_paths)
        success_count = sum(results)
        
    print(f"Successfully normalized {success_count}/{len(image_paths)} images.")

if __name__ == '__main__':
    main()
