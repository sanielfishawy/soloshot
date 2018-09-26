import PIL.Image
import cv2


cap = cv2.VideoCapture('/Volumes/WD/soloshot_video/park.mp4')
cv2.CAP_PROP_FRAME_COUNT
cv2.CAP_PROP_POS_MSEC

success, im1 = cap.read()

cap.set(cv2.CAP_PROP_POS_MSEC, 40*1000)

success, im2 = cap.read()
p1 = PIL.Image.fromarray(im1)
p2 = PIL.Image.fromarray(im2)
p1.show()
p2.show()