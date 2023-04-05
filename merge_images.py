from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout ,  QFileDialog, QButtonGroup, QRadioButton, QLineEdit, QLabel
from PyQt5.QtGui import QIntValidator
from PyQt5 import QtCore
import cv2
import os
import sys
import numpy as np


mode_group=None
mode_concat=""
r0=None
r1=None
window = None
maxwidth, maxheight = 400, 500
main_img=None
main_img_width=0
main_img_height=1

img1=None
original_img1=None
img2=None
img2_non_cropped=None
original_img2=None
app=None

scale_field=None
#rot_field=None
offx_field=None
offy_field=None
cropr_field=None
result_merged=None

size_field=None
    



def close_project():
    global app
    sys.exit(app.exec_())
    
def save():
    global main_img
    global window
    global scale_field
    #global rot_field
    global offx_field
    global offy_field
    global cropr_field
    if main_img is not None:
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
            tmp_metadata={}
            tmp_metadata["crop_1st"]=cropr_field.text()
            tmp_metadata["scale"]=scale_field.text()
            tmp_metadata["offset x"]=offx_field.text()
            tmp_metadata["offset y"]=offy_field.text()
            cv2.imwrite(filename, main_img)
            ext = '.'+ filename.split('.')[-1:][0]
            filefinal = filename.replace(ext,'')
            filefinal = filename + '_params_transform.txt'
            f = open(filefinal, "w")
            rows=[]
            for key, value in tmp_metadata.items():
                rows.append(key+"\t"+value)
            f.write("\n".join(rows))
            f.close()
        #cv2.destroyAllWindows()
        #close_project()

def resize():
    global maxwidth
    global size_field
    global main_img
    global img1
    maxwidth=int(size_field.text())
    merged_line=main_img.copy()
    
    
    #cv2.line(merged_line, (xline1, yline1), (xline2, yline2), (0, 0, 255), 10)
    xline1=img1.shape[1]
    xline2=img1.shape[1]
    yline1=0
    yline2=img1.shape[0]
    print((xline1, yline1))
    print((xline2, yline2))
    cv2.line(merged_line, (xline1, yline1), (xline2, yline2), (0, 0, 255), 10)
    display_simple(merged_line)

def reconcat():
    global img1
    global img2
    global mode_concat
    global main_img
    if mode_concat=="h":
        main_img=cv2.hconcat([img1,img2])
    elif mode_concat=="v":
        main_img=cv2.hconcat([img1, img2])
    
    
def prepare(imgs_path):
    global r0
    global r1
    global window
    global maxwidth
    global maxheight
    global main_img
    global main_img_width
    global main_img_height
    global img1
    global img2
    global original_img1
    global original_img2
    global img2_non_cropped
    global mode_concat
    
    
    tmp=None
    imgs=[]
    i=0
    ref_height=0
    ref_width=0
    
    xline1, yline1 = 0, 0
    xline2, yline2 = 0,0
    for path in imgs_path:
        #print(path)
        tmp0=cv2.imread(path)
        #tmp0=cv2.resize(tmp0, (0,0), fx=0.25, fy=0.25)

        if i==0:
            ref_height= tmp0.shape[0]
            ref_width= tmp0.shape[1]
        else:
            ref_height= min(ref_height, tmp0.shape[0])
            ref_width= min(ref_width, tmp0.shape[1])
        i=i+1
    i=0
    print("ref h")
    print(ref_height)
    print("ref w")
    print(ref_width)
    for path in imgs_path:
        if i<2:
            print(i)
            tmp1=cv2.imread(path)
            #tmp1=cv2.resize(tmp1, (0,0), fx=0.25, fy=0.25)
            ratio=1
            if r0.isChecked():
                #print('h')
                mode_concat="h"
                height=tmp1.shape[0]
                if height>ref_height:
                    ratio=ref_height/height
                    print(ratio)

            elif r1.isChecked():
                #print('v')
                mode_concat="v"
                width=tmp1.shape[1]
                if width>ref_width:
                    ratio=ref_width/width
          
                
            if ratio==1:
                print("ratio 1")
                imgs.append(tmp1)
            else:
                print("resize")
                #dim = (int(tmp1.shape[1] * ratio), int(tmp1.shape[0] * ratio))
                tmp1=cv2.resize(tmp1, (0,0), fx=ratio, fy=ratio)
                imgs.append(tmp1)
      
        if i==0:
            img1=tmp1
            original_img1=img1.copy()
        else:
            img2=tmp1
            
            print("keep "+path)
            original_img2=img2.copy()
            img2_non_cropped=img2.copy()
        i=i+1
           
    merged=None
    if r0.isChecked():
        #print('h')
        merged=cv2.hconcat(imgs)
    elif r1.isChecked():
        #print('v')
        merged=cv2.vconcat(imgs)
        
    #f1 = maxwidth / merged.shape[1]
    #f2 = maxheight / merged.shape[0]
    #f = min(f1, f2)  # resizing factor
    #dim = (int(merged.shape[1] * f), int(merged.shape[0] * f))
    #resized = cv2.resize(merged, dim)
    main_img=merged
    main_img_height=main_img.shape[0]
    main_img_width=main_img.shape[1]
    
    merged_line=merged.copy()
    print("h")
    print(merged_line.shape[0])
    print("w")
    print(merged_line.shape[1])
    
    #cv2.line(merged_line, (xline1, yline1), (xline2, yline2), (0, 0, 255), 10)
    xline1=img1.shape[1]
    xline2=img1.shape[1]
    yline1=0
    yline2=img1.shape[0]
    print((xline1, yline1))
    print((xline2, yline2))
    cv2.line(merged_line, (xline1, yline1), (xline2, yline2), (0, 0, 255), 10)
    #cv2.imshow("",resized)
    display_simple(merged_line)
  
def rescale(image, factor):
    global mode_concat
    global main_img_height
    global main_img_width
    tmp= cv2.resize(image, (0,0), fx=float(factor), fy=float(factor))
    if mode_concat=="h":
        if tmp.shape[0]<main_img_height:
            tmp=cv2.copyMakeBorder(tmp, 0, main_img_height- tmp.shape[0], 0,0, cv2.BORDER_CONSTANT,0)
        elif tmp.shape[0]>main_img_height:
            tmp=tmp[0:main_img_height, 0:tmp.shape[1]]
    elif mode_concat=="v":
        if tmp.shape[1]<main_img_width:
            tmp=cv2.copyMakeBorder(tmp, 0, 0, 0,main_img_width- tmp.shape[1], cv2.BORDER_CONSTANT,0)
        if tmp.shape[1]>main_img_width:
            tmp=tmp[0:tmp.shape[0], 0:main_img_width]
    return tmp
    
def offsetx_image(image, offset_w):
    offset_w=int(offset_w)
    returned=image
    print(offset_w)
    if offset_w<0 and abs(offset_w)<image.shape[1] :
        returned=image[0:image.shape[0], abs(offset_w):image.shape[1]]   
        returned=cv2.copyMakeBorder(returned, 0, 0, 0, abs(offset_w),  cv2.BORDER_CONSTANT, 0)
        print("pad_left")
    elif abs(offset_w)<image.shape[1]:
        returned=cv2.copyMakeBorder(image, 0, 0,  abs(offset_w), 0, cv2.BORDER_CONSTANT, 0)
        returned=returned[0:image.shape[0], 0:image.shape[1]]
        print("pad_right")
    print("p h")
    print(returned.shape[0])
    print("p w")
    print(returned.shape[1])
    return returned
    
def offsety_image(image, offset_h):
    offset_h=int(offset_h)
    returned=image
    print(offset_h)
    if offset_h<0 and abs(offset_h)<image.shape[0] :
        returned=image[abs(offset_h):image.shape[0], 0:image.shape[1]]   
        returned=cv2.copyMakeBorder(returned, 0, abs(offset_h), 0, 0,  cv2.BORDER_CONSTANT, 0)
        
    elif abs(offset_h)<image.shape[1]:
        returned=cv2.copyMakeBorder(image, abs(offset_h) , 0,  0, 0, cv2.BORDER_CONSTANT, 0)
        returned=returned[0:image.shape[0], 0:image.shape[1]]
        
    print("p h")
    print(returned.shape[0])
    print("p w")
    print(returned.shape[1])
    return returned
    
def crop_right_bottom(image, offset):
    offset=int(offset)
    returned=image
    if mode_concat=="v" and  offset<image.shape[0] :
        returned=image[0:(image.shape[0]-offset), 0:image.shape[1]]  
    elif mode_concat=="h" and  offset<image.shape[0]:
        returned=image[0:image.shape[0], 0:(image.shape[1]-offset)]
    return returned
    

def reset():
    global img1
    global original_img1
    global img2
    global original_img2
    global img2_non_cropped
    global main_img
    
    img1=original_img1
    img2_non_cropped=original_img2
    img2=original_img2
    reconcat()
    display_simple(main_img)
    
def transform():
    global scale_field
    #global rot_field
    global offx_field
    global offy_field
    global cropr_field
    global img1
    global img2
    global original_img1
    global original_img2
    global img2_non_cropped
    global main_img
    print("transfo")
    scale=scale_field.text()
    crop_r=cropr_field.text()
    #rotation=rot_field.text()
    off_x=offx_field.text()
    off_y=offy_field.text()
    #display_simple(original_img2)
    if float(scale)!=0.0:
        img2=rescale(original_img2, scale)       
        #img2_non_cropped=img2.copy()
    else:
        img2=original_img2
        
    if int(crop_r)!=0:
        #Fdisplay_simple(original_img1)
        #cv2.waitKey(0)
        img1=crop_right_bottom(original_img1, crop_r)
        #display_simple(img1)
        #cv2.waitKey(0)
    if int(off_x)!=0:
        img2=offsetx_image(img2, off_x)
        img2_non_cropped=img2.copy()    
    if int(off_y)!=0:
        img2=offsety_image(img2, off_y)
        img2_non_cropped=img2.copy()        
    print(scale)
    reconcat()
    display_simple(main_img)
    
def choose_img(x):
    #print("done")
    global mode_group
    global window
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    filenames, _ = QFileDialog.getOpenFileNames(window,"QFileDialog.getOpenFileNames()", "","All Files (*);;Python Files (*.py)", options=options)
    prepare(filenames)
        

def display_simple(ROI):
    global maxwidth
    global maxheight
    ref_height= ROI.shape[1]
    ref_width= ROI.shape[0]
    print(ref_height)
    print(ref_width)
    if ref_width>maxwidth:
        ratio=maxwidth/ref_width
        #print(ratio)
        
        #display_width=math.floor(ref_width/ratio)
        #print(maxheight)
        #print(display_width)
        #display = cv2.resize(ROI, (display_width, maxheight))
        display = cv2.resize(ROI, (0,0), fx=ratio, fy=ratio) 
        #PanZoomWindow(display,"test")
        cv2.imshow("",display)
    else:
        #PanZoomWindow(ROI,"test")
        cv2.imshow("",ROI)
        
def start():
    global mode_group
    global r0
    global r1
    global window
    global app
    global scale_field
    global size_field
    #global rot_field
    global offx_field
    global offy_field
    global cropr_field
    global maxwidth
    
    app = QApplication([])
    window = QWidget()
    window.setMinimumWidth(300)
    layout = QVBoxLayout()
    but_img=QPushButton('Choose images')
    layout.addWidget(but_img)
    but_img.clicked.connect(choose_img)
    
    lab_size=QLabel(window)
    lab_size.setText("Resize")
    layout.addWidget(lab_size)
    
    size_field=QLineEdit(window)
    size_field.setText(str(maxwidth))
    layout.addWidget(size_field)
    
    but_resize=QPushButton('Resize')
    layout.addWidget(but_resize)
    but_resize.clicked.connect(resize)
    
    mode_group=QButtonGroup(window) # Number group
    r0=QRadioButton(text="Horizontal")
    r0.setChecked(True)
    mode_group.addButton(r0)
    r1=QRadioButton(text="Vertical")
    mode_group.addButton(r1)
    layout.addWidget(r0)
    layout.addWidget(r1)
    
    lab_cropr=QLabel(window)
    lab_cropr.setText("Crop right/bottom 1st part")
    layout.addWidget(lab_cropr)
    
    cropr_field=QLineEdit(window)
    cropr_field.setText("0")
    layout.addWidget(cropr_field)
    
    lab_scale=QLabel(window)
    lab_scale.setText("Scale 2nd part")
    layout.addWidget(lab_scale)
    
    scale_field=QLineEdit(window)
    scale_field.setText("1.0")
    layout.addWidget(scale_field)
    
    #lab_rot=QLabel(window)
    #lab_rot.setText("Rotation")
    #layout.addWidget(lab_rot)
    
    #rot_field=QLineEdit(window)
    #rot_field.setText("0")
    #layout.addWidget(rot_field)
    
    lab_offx=QLabel(window)
    lab_offx.setText("Offset x")
    layout.addWidget(lab_offx)
    
    offx_field=QLineEdit(window)
    offx_field.setText("0")
    layout.addWidget(offx_field)
    
    lab_offy=QLabel(window)
    lab_offy.setText("Offset y")    
    layout.addWidget(lab_offy)
    
    offy_field=QLineEdit(window)
    offy_field.setText("0")
    layout.addWidget(offy_field)
    
    
    but_apply=QPushButton('Transform')
    layout.addWidget(but_apply)
    but_apply.clicked.connect(transform)
    
    but_reset=QPushButton('Reset')
    layout.addWidget(but_reset)
    but_reset.clicked.connect(reset)
    
    but_save=QPushButton('Save image')
    layout.addWidget(but_save)
    but_save.clicked.connect(save)
    
    #but_savehsv=QPushButton('Save HSV')
    #layout.addWidget(but_savehsv)
    #but_savehsv.clicked.connect(savehsv)




    window.setLayout(layout)
    window.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
    window.show()
    app.exec()


start()