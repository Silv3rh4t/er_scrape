import cv2

img = cv2.imread("template.png", 0)
edges = cv2.Canny(img, 50, 150)
cv2.imwrite("templated.png", edges)