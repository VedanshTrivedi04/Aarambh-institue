import cv2
import os
import sys

def extract_frames():
    video_path = r"d:\Aarambh Intitute\my_coacing_nstitute_is_Aarambh.mp4"
    output_dir = r"d:\Aarambh Intitute\frontend\public\frames"
    os.makedirs(output_dir, exist_ok=True)
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video file {video_path}")
        sys.exit(1)
        
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Extracting {total_frames} frames ({w}x{h} @ {fps}fps) to {output_dir}...")
    
    count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_filename = os.path.join(output_dir, f"frame_{count:03d}.webp")
        # Save as WebP with quality 82 for great balance of sharpness and file size (~15KB per frame)
        cv2.imwrite(frame_filename, frame, [cv2.IMWRITE_WEBP_QUALITY, 82])
        count += 1
        if count % 40 == 0 or count == total_frames:
            print(f"Extracted {count}/{total_frames} frames...")
            
    cap.release()
    print(f"Successfully extracted all {count} frames!")
    
    total_size_mb = sum(os.path.getsize(os.path.join(output_dir, f)) for f in os.listdir(output_dir)) / (1024 * 1024)
    print(f"Total size of all frames: {total_size_mb:.2f} MB")

if __name__ == "__main__":
    extract_frames()
