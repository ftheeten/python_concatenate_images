from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout ,  QFileDialog, QButtonGroup, QRadioButton, QLineEdit, QLabel
from   PyQt5.QtCore import Qt
from cv2 import imread, imwrite,line, hconcat, vconcat, resize, copyMakeBorder, imshow, BORDER_CONSTANT
from os import path, remove
from  imutils import rotate

mode_group=None
mode_concat=""
r0=None
r1=None
window = None
maxwidth, maxheight = 400, 500
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
posx_field=None
posy_field=None
scale_field=None
rot_field=None
offx_field=None
offy_field=None
cropr_field=None

result_merged=None

size_field=None
    





    
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
            imwrite(filename, main_img)
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
    maxwidth=int(size_field.text())
    merged_line=main_img.copy()
    
    
    #line(merged_line, (xline1, yline1), (xline2, yline2), (0, 0, 255), 10)
    xline1=img1.shape[1]
    xline2=img1.shape[1]
    yline1=0
    yline2=img1.shape[0]
    print((xline1, yline1))
    print((xline2, yline2))
    line(merged_line, (xline1, yline1), (xline2, yline2), (0, 0, 255), 10)
    display_simple(merged_line)

def reconcat():
    global img1
    global img2
    global mode_concat
    global main_img
    if mode_concat=="h":
        main_img=hconcat([img1,img2])
    elif mode_concat=="v":
        main_img=hconcat([img1, img2])
    
    
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
        tmp0=imread(path)
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
            tmp1=imread(path)
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
                tmp1=resize(tmp1, (0,0), fx=ratio, fy=ratio)
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
        merged=hconcat(imgs)
    elif r1.isChecked():
        #print('v')
        merged=vconcat(imgs)
        
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
    line(merged_line, (xline1, yline1), (xline2, yline2), (0, 0, 255), 10)
    #imshow("",resized)
    display_simple(merged_line)
    ##display_status("Idle")
 
#def #display_status(text):
#    thread = Thread(target = threaded_status, args = (text,))
#    thread.start()
#    thread.join()
 
def rescale(image, factor):
    global mode_concat
    global main_img_height
    global main_img_width
    tmp= resize(image, (0,0), fx=float(factor), fy=float(factor))
    if mode_concat=="h":
        if tmp.shape[0]<main_img_height:
            tmp=copyMakeBorder(tmp, 0, main_img_height- tmp.shape[0], 0,0, BORDER_CONSTANT,0)
        elif tmp.shape[0]>main_img_height:
            tmp=tmp[0:main_img_height, 0:tmp.shape[1]]
    elif mode_concat=="v":
        if tmp.shape[1]<main_img_width:
            tmp=copyMakeBorder(tmp, 0, 0, 0,main_img_width- tmp.shape[1], BORDER_CONSTANT,0)
        if tmp.shape[1]>main_img_width:
            tmp=tmp[0:tmp.shape[0], 0:main_img_width]
    return tmp
    
def offsetx_image(image, offset_w):
    offset_w=int(offset_w)
    returned=image
    print(offset_w)
    if offset_w<0 and abs(offset_w)<image.shape[1] :
        returned=image[0:image.shape[0], abs(offset_w):image.shape[1]]   
        returned=copyMakeBorder(returned, 0, 0, 0, abs(offset_w),  BORDER_CONSTANT, 0)
        print("pad_left")
    elif abs(offset_w)<image.shape[1]:
        returned=copyMakeBorder(image, 0, 0,  abs(offset_w), 0, BORDER_CONSTANT, 0)
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
        returned=copyMakeBorder(returned, 0, abs(offset_h), 0, 0,  BORDER_CONSTANT, 0)
        
    elif abs(offset_h)<image.shape[1]:
        returned=copyMakeBorder(image, abs(offset_h) , 0,  0, 0, BORDER_CONSTANT, 0)
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
        #display = resize(ROI, (display_width, maxheight))
        display = resize(ROI, (0,0), fx=ratio, fy=ratio) 
        #PanZoomWindow(display,"test")
        imshow("",display)
    else:
        #PanZoomWindow(ROI,"test")
        imshow("",ROI)
    
def set_label(p_layout, text):
    lab=QLabel(window)
    lab.setText(text)
    p_layout.addWidget(lab)
    
def set_lineedit(p_layout, text):   
    ctrl=QLineEdit(window)
    ctrl.setText(text)
    p_layout.addWidget(ctrl)
    return ctrl
    
def start():
    global mode_group
    global r0
    global r1
    global window

    
    global zoom_field
    global posx_field
    global posy_field
    global scale_field
    global size_field
    global rot_field
    global offx_field
    global offy_field
    global cropr_field
    global maxwidth
    
    
    
    app = QApplication([])
    window = QWidget()
    window.setMinimumWidth(300)
    layout = QVBoxLayout()
    
    but_img1=QPushButton('Choose image 1')
    layout.addWidget(but_img1)
    but_img1.clicked.connect(choose_img1)
    
    but_img2=QPushButton('Choose image 2')
    layout.addWidget(but_img2)
    but_img2.clicked.connect(choose_img2)
    
    but_go=QPushButton('Load')
    layout.addWidget(but_go)
    but_go.clicked.connect(prepare)
    
    
    set_label(layout, "Size width")
    
    size_field=set_lineedit(layout,str(maxwidth) )
    
    
    but_resize=QPushButton('Resize width')
    layout.addWidget(but_resize)
    but_resize.clicked.connect(p_resize)
    
    mode_group=QButtonGroup(window) # Number group
    r0=QRadioButton(text="Horizontal")
    r0.setChecked(True)
    mode_group.addButton(r0)
    r1=QRadioButton(text="Vertical")
    mode_group.addButton(r1)
    layout.addWidget(r0)
    layout.addWidget(r1)
    
    set_label(layout, "Crop right/bottom 1st part")
    
    
    cropr_field=set_lineedit(layout, "0")
   
    set_label(layout, "Scale 2nd part")
    
    scale_field=set_lineedit(layout, "1.0")
    
    set_label(layout, "Rotation")
    
    rot_field=set_lineedit(layout, "0.0")
    
    set_label(layout, "Offset x")
    
    offx_field=set_lineedit(layout, "0")
    
    set_label(layout, "Offset y")
    
    offy_field=set_lineedit(layout, "0")
    
    
    
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
    window.setWindowFlags(Qt.WindowStaysOnTopHint)
    window.show()
    app.exec()

if __name__ == '__main__':
    start()