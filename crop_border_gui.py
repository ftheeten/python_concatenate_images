from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout ,  QFileDialog, QButtonGroup, QRadioButton
from PyQt5 import QtCore
import cv2
import os
import sys
import math
import numpy as np

window = None
maxwidth, maxheight = 400, 700
main_img=None
app=None
list_rect=None
current_img=0
last_img=0
treshold_area=2000

def find_rect(p_img):
    global treshold_area 
    #image = cv2.resize(p_img, (0,0), fx=0.5, fy=0.5) 
    image=p_img
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #display_simple(gray)
    blur = cv2.medianBlur(gray, 5)
    #display_simple(blur)
    erode_kernel = np.ones((100, 100), np.uint8)
  
    # Using cv2.erode() method 
    eroded = cv2.erode(blur, erode_kernel) 
    #display_simple(eroded)
    
    sharpen_kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    sharpen = cv2.filter2D(eroded, -1, sharpen_kernel)
    #display_simple(sharpen)
    
    
    # Threshold and morph close
    thresh = cv2.threshold(sharpen, 64, 255, cv2.THRESH_BINARY_INV)[1]
    #display_simple(thresh)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    close = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)

    # Find contours and filter using threshold area
    
    cnts = cv2.findContours(close, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    list_areas={}
    for c in cnts:
        #print(c)
        area = cv2.contourArea(c)
        if area>=treshold_area:
            x,y,w,h = cv2.boundingRect(c)
            area=w*h
            if not area in list_areas:
                list_areas[area]=[]
            list_areas[area].append([x,y,w,h])
    list_areas=dict(sorted(list_areas.items(), reverse=True))
    result=[]
    for k, v in list_areas.items():
        for v2 in v:
            result.append(v2)
    return result

def c_previous():
    global main_img
    global current_img
    global last_img
    global list_rect
    print("prev")
    if current_img>0:
        current_img=current_img-1
        page_image(current_img, main_img, list_rect )
    
    
def c_next():
    global main_img
    global current_img
    global last_img
    global list_rect
    print("next")
    if current_img<last_img-1:
        current_img=current_img+1
        page_image(current_img, main_img, list_rect )
    
def page_image(position,img, list_coord):
    current_pos=list_coord[position]
    display(img, current_pos)

def display_simple(ROI):
    global maxwidth
    global maxheight
    ref_height= ROI.shape[1]
    ref_width= ROI.shape[0]
    if ref_height>maxheight:
        ratio=ref_height/maxheight
        display_width=math.floor(ref_width/ratio)
        display = cv2.resize(ROI, (display_width, maxheight))
        cv2.imshow("",display)        
    else:
        cv2.imshow("",ROI)
    cv2.waitKey(0)

def display(img, current_coords):
    global maxwidth
    global maxheight
    #global main_img
    #global current_img
    #global last_img
    ROI = img[current_coords[1]:current_coords[1]+current_coords[3], current_coords[0]:current_coords[0]+current_coords[2]]
    ref_height= ROI.shape[1]
    ref_width= ROI.shape[0]
    if ref_height>maxheight:
        ratio=ref_height/maxheight
        display_width=math.floor(ref_width/ratio)
        display = cv2.resize(ROI, (display_width, maxheight))
        cv2.imshow("",display)        
    else:
        cv2.imshow("",ROI)

def prepare(img_path):
    #global window
    global maxwidth
    global maxheight
    global main_img
    global current_img
    global last_img
    global list_rect
    
    main_img=cv2.imread(img_path)
    main_img = cv2.resize(main_img, (0,0), fx=0.5, fy=0.5)
    '''
    ref_height= main_img.shape[1]
    ref_width= main_img.shape[0]
    if ref_height>maxheight:
        ratio=ref_height/maxheight
        display_width=math.floor(ref_width/ratio)
        display = cv2.resize(main_img, (display_width, maxheight))
        cv2.imshow("",display)        
    else:
        cv2.imshow("",main_img)
    '''
    list_rect=find_rect(main_img)
    print(list_rect)
    current_img=0
    last_img=len(list_rect)
    print(last_img)
    page_image(0, main_img, list_rect )


    
def save():
    global window
    global main_img
    global current_img
    global last_img
    global list_rect
    if main_img is not None:
        current_coords=list_rect[current_img]
        ROI = main_img[current_coords[1]:current_coords[1]+current_coords[3], current_coords[0]:current_coords[0]+current_coords[2]]
        #print('save')
        tmpdial=QFileDialog()
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        #options |= QFileDialog.DontConfirmOverwrite 
        
        filename, _ = tmpdial.getSaveFileName(window, 
                "Save File", "", "All Files(*);;Text Files(*.txt)", options = options)
        if os.path.exists(filename):
            #print("remove")
            os.remove(filename)
        if filename:
            #print(filename)
            cv2.imwrite(filename, ROI)
        cv2.destroyAllWindows()
        close_project()
        
def choose_img(x):
    #print("done")
    global mode_group
    global window
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    filename, _ = QFileDialog.getOpenFileName(window,"QFileDialog.getOpenFileNames()", "","All Files (*);;Python Files (*.py)", options=options)
    prepare(filename)
    
def start():
    global window
    global app
    app = QApplication([])
    window = QWidget()
    window.setMinimumWidth(300)
    layout = QVBoxLayout()
    but_img=QPushButton('Choose images')
    layout.addWidget(but_img)
    but_img.clicked.connect(choose_img)
    
    but_prev=QPushButton('Previous')
    layout.addWidget(but_prev)
    but_prev.clicked.connect(c_previous)
    
    but_next=QPushButton('Next')
    layout.addWidget(but_next)
    but_next.clicked.connect(c_next)
    
    but_save=QPushButton('Save image')
    layout.addWidget(but_save)
    but_save.clicked.connect(save)
    
    window.setLayout(layout)
    window.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
    window.show()
    app.exec()

start()