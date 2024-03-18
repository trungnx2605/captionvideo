#phần lấy screenhost

import cv2
import os
from pathlib import Path

source_folder = '/Users/trungnguyen/Desktop/Vlog 4'
target_folder = '/Users/trungnguyen/Desktop/Vlog 4/screenshot'

# Ensure target folder exists
if not os.path.exists(target_folder):
    os.makedirs(target_folder)

# Adjusted to handle both lowercase and uppercase extensions
videos = [f for f in os.listdir(source_folder) if f.lower().endswith(('.mp4', '.MP4'))]
print(f"Found {len(videos)} videos.")

for idx, video in enumerate(videos):
    video_path = os.path.join(source_folder, video)
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"Error opening video file {video}")
        continue

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_number = int(4 * fps)

    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

    success, image = cap.read()
    if success:
        # Resize image to 1280x720
        resized_image = cv2.resize(image, (854, 480))
        
        screenshot_path = os.path.join(target_folder, f"{Path(video).stem}.jpg")  # Changed to .jpg
        cv2.imwrite(screenshot_path, resized_image)  # Save resized image
        print(f"[{idx + 1}/{len(videos)}] Screenshot taken for video: {video}, saved to: {screenshot_path}")
    else:
        print(f"Failed to take screenshot for video: {video}")
    
    cap.release()

print("Process completed.")


#phần handle với openai


import os
import shutil
import base64
import requests

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_image_categorization(api_key, base64_image):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "You will be provided an image, your task is: read the image and categorize it following JSON format: 'Shot':Medium shot, Wide shot, Close-up shot | 'Setting':Indoor, Outdoor, Urban, Rural | 'Location':Bookstore, Home, Street, Park, Office | 'Subject':People, Nature, Objects, Animals, Architecture | 'Activity':Browsing, Walking, Eating, Working, Playing | 'Dominant Colors':Monochrome, Multicolor, Warm tones, Cool tones | 'Mood':Educational, Festive, Somber, Relaxing, Energetic | 'Lighting':Artificial, Natural, Mixed, Dark | 'Presence of People':None, Partial, Full body, Crowded"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    return response.json()

def rename_and_copy_image(original_image_path, categorization, destination_folder):
    base_filename = os.path.basename(original_image_path)
    filename_without_ext, ext = os.path.splitext(base_filename)
    new_filename = f"{filename_without_ext}_{'_'.join(categorization.values())}{ext}"
    os.makedirs(destination_folder, exist_ok=True)
    new_path = os.path.join(destination_folder, new_filename)
    shutil.copy(original_image_path, new_path)

def process_folder(folder_path, destination_folder, api_key):
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
            try:
                image_path = os.path.join(folder_path, filename)
                base64_image = encode_image(image_path)
                response = get_image_categorization(api_key, base64_image)
                
                categorization_content = response['choices'][0]['message']['content']
                categorization_json = eval(categorization_content.replace('```json', '').replace('```', ''))
                
                rename_and_copy_image(image_path, categorization_json, destination_folder)
                print(f"Processed and copied {filename} successfully.")
            except Exception as e:
                print(f"An error occurred while processing {filename}: {e}")

# Your OpenAI
api_key = "api_key"

# Path to your folder containing images
folder_path = "/Users/trungnguyen/Desktop/Vlog 4/screenshot"
destination_folder = "/Users/trungnguyen/Desktop/Vlog 4/screenshot with caption"

process_folder(folder_path, destination_folder, api_key)


#phần dò tên ở screenshot với caption và dò video để đổi tên


import os

def rename_videos_to_match_images(folder_a, folder_b):
    # List all video files in Folder A
    video_files = [f for f in os.listdir(folder_a) if f.lower().endswith(('.mp4', '.MP4'))]
    
    # List all image files in Folder B
    image_files = [f for f in os.listdir(folder_b) if f.lower().endswith('.jpg')]
    
    for video_file in video_files:
        video_name_without_extension = os.path.splitext(video_file)[0]
        
        # Check if there's a matching image file
        for image_file in image_files:
            if image_file.startswith(video_name_without_extension):
                # Prepare the new video name by using the entire image file name but replacing the extension with the video's extension
                video_file_extension = os.path.splitext(video_file)[1]
                new_video_name = os.path.splitext(image_file)[0] + video_file_extension
                
                os.rename(os.path.join(folder_a, video_file), os.path.join(folder_a, new_video_name))
                print(f'Renamed "{video_file}" to "{new_video_name}"')
                break

# Example usage
folder_a = '/Users/trungnguyen/Desktop/Vlog 4'
folder_b = '/Users/trungnguyen/Desktop/Vlog 4/screenshot with caption'
rename_videos_to_match_images(folder_a, folder_b)





