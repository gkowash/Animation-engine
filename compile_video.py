import cv2
import os
import time

print('Compiling video...')

image_folder = 'frames'
video_name = f'videos/anim_{round(time.time())}.avi'

images = sorted([img for img in os.listdir(image_folder) if img.endswith(".jpg")])
frame = cv2.imread(os.path.join(image_folder, images[0]))
height, width, layers = frame.shape

video = cv2.VideoWriter(video_name, 0, 30, (width,height))

for image in images:
    video.write(cv2.imread(os.path.join(image_folder, image)))

cv2.destroyAllWindows()
video.release()

print('Video compiled.')

#os.system('rm -r frames')
#os.system('mkdir frames')
