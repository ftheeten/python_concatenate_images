from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout ,  QFileDialog, QButtonGroup, QRadioButton
from PyQt5 import QtCore
import cv2
import os
import sys
#mode_hv="v"

mode_group=None
r0=None
r1=None
window = None
maxwidth, maxheight = 400, 500
main_img=None

def close_project():
    sys.exit(app.exec_())
    
def save():
    global main_img
    if main_img is not None:
        print('save')
        tmpdial=QFileDialog()
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        #options |= QFileDialog.DontConfirmOverwrite 
        
        filename, _ = tmpdial.getSaveFileName(None, 
                "Save File", "", "All Files(*);;Text Files(*.txt)", options = options)
        if os.path.exists(filename):
            print("remove")
            os.remove(filename)
        if filename:
            print(filename)
            cv2.imwrite(filename, main_img)
        cv2.destroyAllWindows()
        close_project()
    
def prepare(imgs_path):
    global r0
    global r1
    global window
    global maxwidth
    global maxheight
    global main_img
    tmp=None
    imgs=[]
    i=0
    ref_height=0
    ref_width=0
    for path in imgs_path:
        print(path)
        tmp0=cv2.imread(path)
        print(tmp0.shape[1])
        print(tmp0.shape[0])
       
        #imgs.append(tmp0)
        if i==0:
            ref_height= tmp0.shape[1]
            ref_width= tmp0.shape[0]
        else:
            ref_height= min(ref_height, tmp0.shape[1])
            ref_width= min(ref_width, tmp0.shape[0])
        i=i+1
    for path in imgs_path:
        tmp1=cv2.imread(path)
        ratio=1
        if r0.isChecked():
            print('h')
            height=tmp1.shape[0]
            if height>ref_height:
                ratio=ref_height/height
        elif r1.isChecked():
            print('v')
            width=tmp1.shape[1]
            if width>ref_width:
                ratio=ref_width/width
        if ratio==1:
            imgs.append(tmp1)
        else:
            dim = (int(tmp1.shape[1] * ratio), int(tmp1.shape[0] * ratio))
            tmp1=cv2.resize(tmp1, dim)
            imgs.append(tmp1)
           
    merged=None
    if r0.isChecked():
        print('h')
        merged=cv2.hconcat(imgs)
    elif r1.isChecked():
        print('v')
        merged=cv2.vconcat(imgs)
        
    f1 = maxwidth / merged.shape[1]
    f2 = maxheight / merged.shape[0]
    f = min(f1, f2)  # resizing factor
    dim = (int(merged.shape[1] * f), int(merged.shape[0] * f))
    resized = cv2.resize(merged, dim)
    main_img=merged
    cv2.imshow("",resized)
    
   
    

    
def choose_img(x):
    print("done")
    global mode_group
    
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    filenames, _ = QFileDialog.getOpenFileNames(None,"QFileDialog.getOpenFileNames()", "","All Files (*);;Python Files (*.py)", options=options)
    prepare(filenames)
        
        
def start():
    global mode_group
    global r0
    global r1
    global window
    app = QApplication([])
    window = QWidget()
    window.setMinimumWidth(300)
    layout = QVBoxLayout()
    but_img=QPushButton('Choose images')
    layout.addWidget(but_img)
    but_img.clicked.connect(choose_img)
    
    mode_group=QButtonGroup(window) # Number group
    r0=QRadioButton(text="Horizontal")
    r0.setChecked(True)
    mode_group.addButton(r0)
    r1=QRadioButton(text="Vertical")
    mode_group.addButton(r1)
    layout.addWidget(r0)
    layout.addWidget(r1)
    
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