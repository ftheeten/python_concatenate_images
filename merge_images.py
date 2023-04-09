from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QFormLayout ,  QFileDialog, QButtonGroup, QRadioButton, QLineEdit, QLabel, QCheckBox
from   PyQt5.QtCore import Qt
#from cv2 import imread, imwrite,line, hconcat, vconcat, resize, copyMakeBorder, imshow, BORDER_CONSTANT
#import numpy
import cv2 as cv2
from os import path, remove
#from PIL import Image as pil_image
from  imutils import rotate
import math


#pil_image.MAX_IMAGE_PIXELS = None

mode_group=None
mode_concat=""
r0=None
r1=None
window = None
maxwidth, maxheight = 400, 500
currentwidth_truncate, currentheight_truncate=0,0
main_img=None
main_img_width=0
main_img_height=1


imgs_path=['','']
img1=None
original_img1=None
img2=None
img2_non_cropped=None
original_img2=None
app=None

zoom_field=None
full_field=None
posx_field=None
posy_field=None
scale_field=None
rot_field=None
offx_field=None
offy_field=None
offx_field_zoom=None
offy_field_zoom=None
cropr_field=None

result_merged=None

size_field=None
    

label_display_width1=None
label_display_height1=None
label_display_width2=None
label_display_height2=None

label_display_widthfull=None
label_display_heightfull=None

zoom_factor=1
    

def set_size_display():
    label_display_width1.setText("Width image 1:"+str(img1.shape[1])+"px")
    label_display_height1.setText("Height image 1:"+str(img1.shape[0])+"px")
    label_display_width2.setText("Width image 2:"+str(img2.shape[1])+"px")
    label_display_height2.setText("Height image 2:"+str(img2.shape[0])+"px")
    
def save():
    global main_img
    global window
    global scale_field
    global rot_field
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
        if path.exists(filename):
            #print("remove")
            remove(filename)
        if filename:
            #print(filename)
            tmp_metadata={}
            tmp_metadata["crop_1st"]=cropr_field.text()
            tmp_metadata["scale"]=scale_field.text()
            tmp_metadata["rotate"]=rot_field.text()
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
        #destroyAllWindows()
        #close_project()

def p_resize():
    global maxwidth
    global size_field
    global main_img
    global img1
    global full_field
    global zoom_factor
    global zoom_field

    
    if full_field.isChecked():
        print("wrap")
        maxwidth=int(size_field.text())
        merged_line=main_img.copy()
        
        
        #line(merged_line, (xline1, yline1), (xline2, yline2), (0, 0, 255), 10)
        xline1=img1.shape[1]
        xline2=img1.shape[1]
        yline1=0
        yline2=img1.shape[0]
        print((xline1, yline1))
        print((xline2, yline2))
        cv2.line(merged_line, (xline1, yline1), (xline2, yline2), (0, 0, 255), 10)
        display_simple(merged_line)
    else:
        print("no_wrap")
        merged_line=main_img.copy()
        zoom_factor=abs(float(zoom_field.text()))
        p_resize_nowrap(merged_line, zoom_factor)

def p_resize_nowrap(ROI, ratio):
    global currentheight_truncate
    global currentwidth_truncate
    global offy_field_zoom
    global offx_field_zoom
    global size_field
    
   
    
    currentwidth_truncate=int(size_field.text())
    new_img=cv2.resize(ROI, (0,0), fx=ratio, fy=ratio)
   
    
    if(currentwidth_truncate<new_img.shape[1]):
        tmp_width=currentwidth_truncate
    else:
        tmp_width=new_img.shape[1]
    if(currentheight_truncate<new_img.shape[0]):
        tmp_height=currentheight_truncate
    else:
        tmp_height=new_img.shape[1]
    print(tmp_height)
    print(tmp_width)
    
    offy_zoom=math.floor(abs(int(offy_field_zoom.text()))*ratio)
    offx_zoom=math.floor(abs(int(offx_field_zoom.text()))*ratio)
    if offx_zoom>new_img.shape[1]:
        offx_zoom=new_img.shape[1]-1
        offx_field_zoom.setText(str(offx_zoom))
    if offy_zoom>new_img.shape[1]:
        offy_zoom=new_img.shape[0]-1
        offy_field_zoom.setText(str(offy_zoom))
    offx_zoom_final=offx_zoom
    offy_zoom_final=offy_zoom
    if tmp_height+offy_zoom_final>new_img.shape[0]:
        offy_zoom_final=0
    if tmp_width+offx_zoom_final>new_img.shape[1]:
        offx_zoom_final=0
    
    new_img=new_img[offy_zoom:tmp_height+offy_zoom_final, offx_zoom:tmp_width+offx_zoom_final]
    cv2.imshow("",new_img)
    
def reconcat():
    global img1
    global img2
    global mode_concat
    global main_img
    if mode_concat=="h":
        main_img=cv2.hconcat([img1,img2])
    elif mode_concat=="v":
        main_img=cv2.vconcat([img1, img2])
    
    
def prepare():
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
    global imgs_path
    
    global label_display_width1
    global label_display_height1
    global label_display_width2
    global label_display_height2
    
    #display_status("Working, please wait...")
    
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
        #pil_image1 = pil_image.open(path)
        #tmp0 = cv2.cvtColor(numpy.array(pil_image1), cv2.COLOR_RGB2BGR)
        #tmp0=resize(tmp0, (0,0), fx=0.25, fy=0.25)

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
            #pil_image1 = pil_image.open(path)
            #tmp1 = cv2.cvtColor(numpy.array(pil_image1), cv2.COLOR_RGB2BGR)
            #tmp1=resize(tmp1, (0,0), fx=0.25, fy=0.25)
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
    #resized = resize(merged, dim)
    main_img=merged
    main_img_height=main_img.shape[0]
    main_img_width=main_img.shape[1]
    
    merged_line=merged.copy()
    print("h")
    print(merged_line.shape[0])
    print("w")
    print(merged_line.shape[1])
    
    #line(merged_line, (xline1, yline1), (xline2, yline2), (0, 0, 255), 10)
    xline1=img1.shape[1]
    xline2=img1.shape[1]
    yline1=0
    yline2=img1.shape[0]
    print((xline1, yline1))
    print((xline2, yline2))
    cv2.line(merged_line, (xline1, yline1), (xline2, yline2), (0, 0, 255), 10)
    #imshow("",resized)
    display_simple(merged_line)
    set_size_display()
    ##display_status("Idle")
 
#def #display_status(text):
#    thread = Thread(target = threaded_status, args = (text,))
#    thread.start()
#    thread.join()
 
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
    
def rotate_image(image, r_angle):
    r_angle=float(r_angle)
    returned=rotate(image, angle=r_angle)
    #display_simple(returned)
    return returned
    
def reset():
    global img1
    global original_img1
    global img2
    global original_img2
    global img2_non_cropped
    global main_img
    #display_status("Working, please wait...")
    img1=original_img1
    img2_non_cropped=original_img2
    img2=original_img2
    reconcat()
    display_simple(main_img)
    #display_status("Idle") 
    
def transform():
    global scale_field
    global rot_field
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
    #display_status("Working, please wait...")
   
    
    scale=scale_field.text()
    crop_r=cropr_field.text()
    rotation=rot_field.text()
    off_x=offx_field.text()
    off_y=offy_field.text()
    #display_simple(original_img2)
    if float(scale)!=0.0:
        img2=rescale(original_img2, scale)       
        #img2_non_cropped=img2.copy()
    else:
        img2=original_img2
    if float(rotation)!=0.0:
        img2=rotate_image(img2, rotation)    
    if int(crop_r)!=0:
        #Fdisplay_simple(original_img1)
        #waitKey(0)
        img1=crop_right_bottom(original_img1, crop_r)
        #display_simple(img1)
        #waitKey(0)
    if int(off_x)!=0:
        img2=offsetx_image(img2, off_x)
        img2_non_cropped=img2.copy()    
    if int(off_y)!=0:
        img2=offsety_image(img2, off_y)
        img2_non_cropped=img2.copy()        
    print(scale)
    reconcat()
    display_simple(main_img)
    #display_status("Idle")
    
    
def choose_img1(x):
    #print("done")
    global mode_group
    global window
    global imgs_paths
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    filename, _ = QFileDialog.getOpenFileName(window,"QFileDialog.getOpenFileNames()", "","All Files (*);;Python Files (*.py)", options=options)
    imgs_path[0]=filename
    
def choose_img2(x):
    #print("done")
    global mode_group
    global window
    global imgs_paths
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    filename, _ = QFileDialog.getOpenFileName(window,"QFileDialog.getOpenFileNames()", "","All Files (*);;Python Files (*.py)", options=options)
    imgs_path[1]=filename
    
        

def display_simple(ROI):    
    global maxwidth
    global maxheight
    global zoom_factor
    global zoom_field
    global currentheight_truncate
    global currentwidth_truncate
    ref_height= ROI.shape[0]
    ref_width= ROI.shape[1]
    print(ref_height)
    print(ref_width)
    if ref_width>maxwidth:
        ratio=maxwidth/ref_width
        #print(ratio)
        
        #display_width=math.floor(ref_width/ratio)
        #print(maxheight)
        #print(display_width)
        #display = resize(ROI, (display_width, maxheight))
        display = cv2.resize(ROI, (0,0), fx=ratio, fy=ratio)
        zoom_factor=ratio
        #PanZoomWindow(display,"test")
        cv2.imshow("",display)
        currentheight_truncate=display.shape[0]
        currentwidth_truncate=display.shape[1]
    else:
        #PanZoomWindow(ROI,"test")
        cv2.imshow("",ROI)
        zoom_factor=1
        currentheight_truncate=ROI.shape[0]
        currentwidth_truncate=ROI.shape[1]
    zoom_field.setText(str(round(zoom_factor,5)))    
    
def set_label(p_layout, text):
    global window
    lab=QLabel(window)
    lab.setText(text)
    p_layout.addRow(lab)
    return lab
    
def set_lineedit(p_layout, text_label, text):
    global window   
    ctrl=QLineEdit(window)
    ctrl.setText(text)
    #p_layout.addWidget(ctrl)
    lab=QLabel(window)
    lab.setText(text_label)
    p_layout.addRow(lab, ctrl)
    return ctrl
    
def start():
    global mode_group
    global r0
    global r1
    global window

    
    global zoom_field
    global full_field
    global posx_field
    global posy_field
    global scale_field
    global size_field
    global rot_field
    global offx_field
    global offy_field_zoom
    global offx_field_zoom
    global offy_field
    global cropr_field
    global maxwidth
    
    global label_display_width1
    global label_display_height1
    global label_display_width2
    global label_display_height2
    global label_display_widthfull
    global label_display_heightfull
    
    
    app = QApplication([])
    window = QWidget()
    window.setMinimumWidth(300)
    layout = QFormLayout()
    
    but_img1=QPushButton('Choose image 1')
    layout.addRow(but_img1)
    but_img1.clicked.connect(choose_img1)
    
    but_img2=QPushButton('Choose image 2')
    layout.addRow(but_img2)
    but_img2.clicked.connect(choose_img2)
    
    mode_group=QButtonGroup(window) # Number group
    r0=QRadioButton(text="Horizontal")
    r0.setChecked(True)
    mode_group.addButton(r0)
    r1=QRadioButton(text="Vertical")
    mode_group.addButton(r1)
    layout.addRow(r0)
    layout.addRow(r1)
    
    but_go=QPushButton('Load')
    layout.addRow(but_go)
    but_go.clicked.connect(prepare)
    
    label_display_width1=set_label(layout, "width image 1:")
    label_display_height1=set_label(layout, "height image 1 :")
    label_display_width2=set_label(layout, "width image 2:")
    label_display_height2=set_label(layout, "height image 1:")
    
    #set_label(layout, "Size width")
    
    size_field=set_lineedit(layout,"Size width", str(maxwidth) )
    
    
    zoom_field=set_lineedit(layout, "Zoom factor",  "0")
    full_field=QCheckBox(window)
    full_field.setChecked(True)
    lab_full=QLabel(window)
    lab_full.setText("Wrap full image")
    layout.addRow(lab_full, full_field)
    offx_field_zoom=set_lineedit(layout,  "Offset x (zoom)", "0")
    offy_field_zoom=set_lineedit(layout,"Offset y (zoom)", "0")
    but_resize=QPushButton('Resize and move')
    layout.addRow(but_resize)
    but_resize.clicked.connect(p_resize)
    
    
    
    #set_label(layout, "Crop right/bottom 1st part")
    
    
    cropr_field=set_lineedit(layout, "Crop right/bottom 1st part",  "0")
   
    #set_label(layout, "Scale 2nd part")
    
    scale_field=set_lineedit(layout, "Scale 2nd part", "1.0")
    
    #set_label(layout, "Rotation")
    
    rot_field=set_lineedit(layout, "Rotation", "0.0")
    
    #set_label(layout, "Offset x")
    
    offx_field=set_lineedit(layout,  "Offset x", "0")
    
    #set_label(layout, "Offset y")
    
    offy_field=set_lineedit(layout,"Offset y", "0")
    
    
    
    but_apply=QPushButton('Transform')
    layout.addRow(but_apply)
    but_apply.clicked.connect(transform)
    
    but_reset=QPushButton('Reset')
    layout.addRow(but_reset)
    but_reset.clicked.connect(reset)
    
    but_save=QPushButton('Save image')
    layout.addRow(but_save)
    but_save.clicked.connect(save)
    
    #but_savehsv=QPushButton('Save HSV')
    #layout.addWidget(but_savehsv)
    #but_savehsv.clicked.connect(savehsv)


    

    window.setLayout(layout)
    window.setWindowFlags(Qt.WindowStaysOnTopHint)
    window.show()
    app.exec()

if __name__ == '__main__':
    start()