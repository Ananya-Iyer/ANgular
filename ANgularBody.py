import os
import json
import glob
import shutil
import inspect
import subprocess
import platform

import maya.OpenMayaUI as openUI
import pymel.core as pm
import imp

if "2016" in pm.about(v=1):
    from PySide import QtGui, QtCore
    from PySide import QtGui as QtWidgets
    from PySide.QtGui import *
    from PySide.QtCore import Qt
    from shiboken import wrapInstance
    maya_2016 = True
else:
    from PySide2 import QtGui, QtCore
    from PySide2 import QtWidgets
    from PySide2.QtWidgets import QAbstractItemView
    from PySide2.QtGui import *
    from PySide2.QtCore import Qt
    from shiboken2 import wrapInstance
    maya_2016 = False
import ANgularBrain as brain
import cwd as getCurrentDirectory


for __module in (brain, getCurrentDirectory):
    imp.reload(__module)

__TOOL_NAME__ = "ANgular"
cwd = getCurrentDirectory.getcwd()
_FFMPEG_EXE_PATH_ = '{}/ffmpeg_exe/ffmpeg.exe'.format(cwd)
_PLATFORM_ = platform.system()

def printdebug(*args):
    print(args)
    if "debug" in list(os.environ.keys()):
        if os.environ["debug"]=="true":
            print("\n".join(args))

def main_maya_win():
    """
    a helper function to make the tool child of maya
    """
    main_win = openUI.MQtUtil.mainWindow()
    return wrapInstance(int(main_win),QtWidgets.QWidget)

def delete_widget_instances(maya_window, tool_name):

    for i in maya_window.children():
        if i and i.objectName()==tool_name:
            i.setParent(None)
            i.deleteLater()
            return

class PlayblastUI(QtWidgets.QDialog):
    def __init__(self, parent = main_maya_win()):
        QtWidgets.QDialog.__init__(self,parent)
        self.setWindowTitle(__TOOL_NAME__)
        self.setObjectName(__TOOL_NAME__)
        self.resize(400,400)
        self.setup_ui()
        self.normal_layout_maps = ("0_0", "w0_0", "0_h0", "w0_h0")
        self.three_layout_maps = ("0_0", "w0_0", "w0_h1", "w0_h0")
        self.base_command = '"{}"'.format(_FFMPEG_EXE_PATH_)
        self.__force_close__ = False
        if not os.path.exists(_FFMPEG_EXE_PATH_):
            pm.confirmDialog(icon='critical', title='FFMPEG missing', message='FFMPEG is missing from your ANgular directory, make sure ANgular directory has ffmpeg.exe in it')
            self.__force_close__ = True
            self.close()
            raise ValueError ('FFMPEG is missing from your ANgular directory, make sure ANgular directory has ffmpeg.exe in it')
        image_path = os.path.join(cwd, '{}.png'.format(__TOOL_NAME__))
        self.setWindowIcon(QtGui.QIcon(image_path))

    def setup_ui(self):
        main_layout = QtWidgets.QVBoxLayout()
        tab_widget = QtWidgets.QTabWidget()

        self.file_menu = QtWidgets.QMenuBar()
        edit_menu = self.file_menu.addMenu("&Edit")
        help_menu = self.file_menu.addMenu("&Help")

        save_settings_action = QtWidgets.QAction("Save Settings", self)
        save_settings_action.setShortcut("Ctrl+S")
        save_settings_action.triggered.connect(self.save_settings)
        reset_settings_action = QtWidgets.QAction("Reset Settings", self)
        reset_settings_action.setShortcut("Ctrl+R")
        reset_settings_action.triggered.connect(self.reset_settings)

        edit_menu.addAction(save_settings_action)
        edit_menu.addAction(reset_settings_action)

        about_action = QtWidgets.QAction("About", self)
        about_action.triggered.connect(self.about_the_tool)

        help_menu.addAction(about_action)

        main_layout.addWidget(self.file_menu)

        tab1_widget = QtWidgets.QWidget()
        self.options_layout = QtWidgets.QVBoxLayout()

        self.file_horizontal_layout = QtWidgets.QHBoxLayout()
        self.file_label = QtWidgets.QLabel("File Path: ")
        self.file_horizontal_layout.addWidget(self.file_label)
        self.file_input_line_edit = QtWidgets.QLineEdit()
        self.file_horizontal_layout.addWidget(self.file_input_line_edit)
        self.file_browse_btn = QtWidgets.QPushButton(clicked = self.set_file_path)
        self.file_browse_btn.setIcon(QtGui.QIcon(":fileOpen.png"))
        self.file_horizontal_layout.addWidget(self.file_browse_btn)
        self.options_layout.addLayout(self.file_horizontal_layout)

        self.output_file_layout = QtWidgets.QHBoxLayout()
        self.output_file_name_label = QtWidgets.QLabel("Output File: ")
        self.output_file_layout.addWidget(self.output_file_name_label)
        self.output_file_name_line_edit = QtWidgets.QLineEdit()
        self.output_file_layout.addWidget(self.output_file_name_line_edit)
        self.options_layout.addLayout(self.output_file_layout)

        self.camera_align_layout = QtWidgets.QVBoxLayout()
        self.camera_views_label = QtWidgets.QLabel("Cameras: ")
        self.camera_align_layout.addWidget(self.camera_views_label)
        self.camera_list_widget = QtWidgets.QListWidget()
        self.camera_list_widget.addItems(brain.PlayblastFuncs.get_cameras())
        self.camera_list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.camera_align_layout.addWidget(self.camera_list_widget)
        self.options_layout.addLayout(self.camera_align_layout)

        self.frame_range_horizontal_layout = QtWidgets.QHBoxLayout()
        self.frame_range_label = QtWidgets.QLabel("Frame Range: ")
        self.frame_range_horizontal_layout.addWidget(self.frame_range_label)
        start_frame, end_frame = brain.PlayblastFuncs.get_frame_range()
        self.start_range = QtWidgets.QSpinBox()
        self.start_range.setRange(-12000, 12000)
        self.start_range.setValue(start_frame)
        self.frame_range_horizontal_layout.addWidget(self.start_range)
        self.to_label = QtWidgets.QLabel(" to ")
        self.frame_range_horizontal_layout.addWidget(self.to_label)
        self.end_range = QtWidgets.QSpinBox()
        self.end_range.setRange(-12000, 12000)
        self.end_range.setValue(end_frame)
        self.frame_range_horizontal_layout.addWidget(self.end_range)
        self.options_layout.addLayout(self.frame_range_horizontal_layout)

        self.playblast_horizontal_layout = QtWidgets.QHBoxLayout()
        self.add_audio_checkbox = QtWidgets.QCheckBox('Include Audio')
        self.add_audio_checkbox.setChecked(1)
        self.playblast_horizontal_layout.addWidget(self.add_audio_checkbox)
        self.playblast_btn = QtWidgets.QPushButton(" Playblast ", clicked= self.take_playblast)
        self.playblast_btn.setFixedSize(QtCore.QSize(300, 25))
        self.playblast_horizontal_layout.addWidget(self.playblast_btn)

        self.options_layout.addLayout(self.playblast_horizontal_layout)

        tab1_widget.setLayout(self.options_layout)


        tab2_widget = QtWidgets.QWidget()

        self.display_layout = QtWidgets.QVBoxLayout()

        self.resolution_layout = QtWidgets.QHBoxLayout()
        self.resolution_label = QtWidgets.QLabel("Resolution: ")
        self.resolution_layout.addWidget(self.resolution_label)
        self.resolution_combo_box = QtWidgets.QComboBox()
        self.resolution_combo_box.addItems(brain.PlayblastFuncs.get_resolution())
        self.resolution_layout.addWidget(self.resolution_combo_box)
        self.display_layout.addLayout(self.resolution_layout)

        self.view_polys_layout = QtWidgets.QHBoxLayout()
        self.view_poly = QtWidgets.QLabel("View Only Polygons: ")
        self.view_polys_layout.addWidget(self.view_poly)
        self.view_polys_checkbox = QtWidgets.QCheckBox()
        self.view_polys_layout.addWidget(self.view_polys_checkbox)
        self.display_layout.addLayout(self.view_polys_layout)

        self.quality_horizontal_layout = QtWidgets.QHBoxLayout()
        self.quality_label = QtWidgets.QLabel("Quality: ")
        self.quality_horizontal_layout.addWidget(self.quality_label)
        self.quality_value_line_edit = QtWidgets.QLineEdit()
        self.quality_value_line_edit_validator = QtGui.QIntValidator(0, 100, self)
        self.quality_value_line_edit.setValidator(self.quality_value_line_edit_validator)
        self.quality_value_line_edit.returnPressed.connect(self.set_quality_lineedit_to_slider)
        self.quality_horizontal_layout.addWidget(self.quality_value_line_edit)
        self.quality_value_slider = QtWidgets.QSlider(Qt.Horizontal)
        self.quality_value_slider.setMinimum(0)
        self.quality_value_slider.setMaximum(100)
        self.quality_value_slider.valueChanged.connect(self.set_quality_slider_to_lineedit)
        self.quality_horizontal_layout.addWidget(self.quality_value_slider)
        self.display_layout.addLayout(self.quality_horizontal_layout)

        self.format_horizontal_layout = QtWidgets.QHBoxLayout()
        self.format_label = QtWidgets.QLabel("Format : ")
        self.format_horizontal_layout.addWidget(self.format_label)
        self.format_combo_box = QtWidgets.QComboBox()
        self.format_combo_box.addItems(brain.PlayblastFuncs.get_playblast_formats())
        self.format_combo_box.currentIndexChanged.connect(self.set_codecs)
        self.format_horizontal_layout.addWidget(self.format_combo_box)
        self.display_layout.addLayout(self.format_horizontal_layout)

        self.codec_horizontal_layout = QtWidgets.QHBoxLayout()
        self.codec_label = QtWidgets.QLabel("Codec : ")
        self.codec_horizontal_layout.addWidget(self.codec_label)
        self.codec_combo_box = QtWidgets.QComboBox()
        self.codec_horizontal_layout.addWidget(self.codec_combo_box)
        self.display_layout.addLayout(self.codec_horizontal_layout)

        tab2_widget.setLayout(self.display_layout)

        tab_widget.addTab(tab1_widget,"Options")
        #tab_widget.addTab(tab2_widget, "Cam Positions")
        tab_widget.addTab(tab2_widget,"Display")
        main_layout.addWidget(tab_widget)
        self.setLayout(main_layout)

        '''
        Initial Value Setters
        '''

        self.set_quality_lineedit_to_slider()
        self.set_quality_slider_to_lineedit()    
        self.set_codecs()
        self.load_settings()

    def closeEvent(self, event):
        if self.__force_close__:
            return event.accept()

        reply = QtWidgets.QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def set_codecs(self, *args):
        '''
        sets the codecs from selected formats
        '''
        self.codec_combo_box.clear()
        self.codec_combo_box.addItems(brain.PlayblastFuncs.get_codecs(self.format_combo_box.currentText()))

    def set_quality_slider_to_lineedit(self, *args):
        '''
        gets the slider value and sets same value in quality line edit
        '''
        self.quality_value_line_edit.setText(str(self.quality_value_slider.value()))

    def set_quality_lineedit_to_slider(self, *args):
        '''
        gets the line edit value and sets same value in slider
        '''
        try:
            value = int(self.quality_value_line_edit.text())

        except:
            value = 100
        
        if value <= self.quality_value_slider.maximum() and value >= self.quality_value_slider.minimum() :
            self.quality_value_slider.setValue(value)
        else:
            pm.displayWarning('Value exceeds the range {} - {}'.format(self.quality_value_slider.minimum(), self.quality_value_slider.maximum()))
            self.quality_value_slider.setValue(0)

    def set_file_path(self):
        '''
        sets the file save path
        '''
        browse_path = brain.PlayblastFuncs.file_browsing()
        old_text = self.file_input_line_edit.text()
        self.file_input_line_edit.setText(browse_path if browse_path else old_text)

    def get_settings_dir(self):
        """
        """
        home_dir = os.path.expanduser("~")
        playblast_dir = "{}/playblast".format(home_dir)
        if not os.path.exists(playblast_dir):
            os.makedirs(playblast_dir)
        return playblast_dir

    def load_settings(self, *args):
        """
        loads the default saved settings from json file
        """
        if not os.path.exists("{}/tool_settings.json".format(self.get_settings_dir())):
            return

        with open('{}/tool_settings.json'.format(self.get_settings_dir()), 'r') as reader:
            data_to_load = json.load(reader)

        self.quality_value_line_edit.setText(data_to_load.get("quality", ""))
        self.quality_value_slider.setValue(int(data_to_load.get(str("quality"), 100)))
        if maya_2016:
            format_index = self.format_combo_box.findText(data_to_load.get("format", ""), QtCore.Qt.MatchFixedString)
            if format_index >= 0:
                self.format_combo_box.setCurrentIndex(format_index)
            codec_index = self.codec_combo_box.findText(data_to_load.get("codec", ""), QtCore.Qt.MatchFixedString)
            if codec_index >= 0:
                self.codec_combo_box.setCurrentIndex(codec_index)
            # self.format_combo_box.setItemText(data_to_load.get("format", ""))
            # self.codec_combo_box.setItemText(data_to_load.get("codec", "")) 
        else:
            self.format_combo_box.setCurrentText(data_to_load.get("format", ""))
            self.codec_combo_box.setCurrentText(data_to_load.get("codec", ""))
        self.file_input_line_edit.setText(data_to_load.get("file_path", ""))

    def save_settings(self, reset=False, *args):
        """
        saves the user settings to json file
        """
        quality_line_edit_value = self.quality_value_line_edit.text()
        format_combobox_value = self.format_combo_box.currentText()
        codec_combobox_value = self.codec_combo_box.currentText()
        file_path_line_edit = self.file_input_line_edit.text()
        if reset == False:
            data_to_write_dict = {"quality": quality_line_edit_value, "format": format_combobox_value, 
            "codec": codec_combobox_value, "file_path": file_path_line_edit}
            
        else:
            data_to_write_dict = {"quality": "100", "format": "", "codec": "", "file_path": ""}
            self.quality_value_line_edit.setText(data_to_write_dict["quality"])
            self.format_combo_box.setCurrentText(data_to_write_dict["format"])
            self.codec_combo_box.setCurrentText(data_to_write_dict["codec"])
            self.file_input_line_edit.setText(data_to_write_dict["file_path"])
        
        with open ("{}/tool_settings.json".format(self.get_settings_dir()), "w") as writer:
            json.dump(data_to_write_dict, writer)
    
    def reset_settings(self, *args):
        """
        resets the user settings in json file to default
        """
        self.save_settings(reset=True)

    def about_the_tool(self, *args):
        """
        summary of the tool
        """        
        main_wid = QtWidgets.QDialog()
        wid_layout = QtWidgets.QHBoxLayout()
        main_wid.setWindowTitle("About Tool")
        main_wid.resize(400,200)
        urlLink='<a href=\"https://toolderado.wordpress.com/contact/\" style=\"color:light  green;\">Contact Us</a>' 
        label = QtWidgets.QLabel()
        label.setText(urlLink)
        label.setOpenExternalLinks(True)
        wid_layout.addWidget(label)
        main_wid.setLayout(wid_layout)
        main_wid.exec_()

    def get_scene_name(self):
        '''
        Gets the right scene name
        '''
        return self.output_file_name_line_edit.text() if self.output_file_name_line_edit.text() != "" else pm.sceneName().namebase if pm.sceneName().namebase != "" else "output"

    def get_extension_from_selection(self):
        '''
        Gets the extension from the selected format.
        '''
        extension = brain.PlayblastFuncs.get_video_extension(self.format_combo_box.currentText())
        if not extension:
            extension = ''
        return extension

    def compile_playblasts(self, temp_playblast_path, final_playblast_path, all_playblasts_list):
        base_command = self.base_command
        audio_file = brain.PlayblastFuncs.get_audio(self.add_audio_checkbox)
        if len(all_playblasts_list) > 1:
            for i in all_playblasts_list:
                base_command = '{0} -i "{1}" '.format(base_command, i)
            base_command += '-filter_complex "'
            for index, i in enumerate(all_playblasts_list):
                width = -1
                height = 720
                if index > 0:
                    height = height/2
                if len(all_playblasts_list) == 3:
                    base_command += '[{0}]scale={1}:{2}[v{0}];'.format(index, width, height)
                
                else:
                    base_command += '[{}:v]'.format(index)
            filter_layout = self.three_layout_maps if len(all_playblasts_list) == 3 else self.normal_layout_maps
            for index, i in enumerate(all_playblasts_list):
                if len(all_playblasts_list)==3:
                    base_command += '[v{}]'.format(index)
                if index == (len(all_playblasts_list)-1):
                    base_command += 'xstack=inputs={}:layout={}[v]" -map "[v]" -c:v libx264 -y "{}"'.format(len(all_playblasts_list), "|".join(filter_layout[:len(all_playblasts_list)]), temp_playblast_path)
            self.run_ffmpeg_command(base_command)
                
        elif len(all_playblasts_list) == 1:
            temp_playblast_path = all_playblasts_list[0]
            if not audio_file:
                if '%4d' in temp_playblast_path:
                    base_command += '-i "{}" -y "{}"'.format(temp_playblast_path, final_playblast_path)
                    if not self.run_ffmpeg_command(base_command):
                        temp_playblast_path = final_playblast_path
                else:
                    try:
                        shutil.copy(temp_playblast_path, final_playblast_path)
                    except:
                        final_playblast_path = temp_playblast_path

        if audio_file:
            self.add_audio_to_video(audio_file, temp_playblast_path, final_playblast_path)
            all_playblasts_list.append(temp_playblast_path)

        return all_playblasts_list



    def take_playblast(self):
        '''
        takes playblast as per user settings
        '''
        if not self.file_input_line_edit.text():
            return pm.confirmDialog(icon='warning', title='Warning', message='File Path is empty.\nPlease give a file path')
        selected_cam_items = self.camera_list_widget.selectedItems()
        if not selected_cam_items:
            return pm.confirmDialog(icon='warning', title='Warning', message='Please select atleast 1 camera')
        if len(selected_cam_items) > 4:
            return pm.confirmDialog(icon='warning', title='Warning', message='You can select Maximum upto 4 cameras')
        extension = self.get_extension_from_selection()
        start_frame = self.start_range.value()
        end_frame = self.end_range.value()
        all_playblasts = []
        scene_name = self.get_scene_name()
        _format = self.format_combo_box.currentText()
        width, height = self.resolution_combo_box.currentText().split('x')

        for cam in selected_cam_items:
            pm.lookThru(cam.text())
            all_panels = pm.getPanel(vis=1)

            if _format not in ('image',):                        
                playblast_path = "{}/{}_{}.{}".format(self.file_input_line_edit.text(), scene_name, cam.text(), extension)
            else:
                playblast_path = "{}/{}_{}".format(self.file_input_line_edit.text(), scene_name, cam.text())

            if self.view_polys_checkbox.isChecked():
                for panel in all_panels:
                    if pm.modelPanel(panel, q=1, ex=1) == 1:
                        pm.modelEditor(panel, e=1, allObjects=False)
                        pm.modelEditor(panel, e=1, polymeshes=True)
                        break
            output = pm.playblast(f=playblast_path,
                        st=start_frame, 
                        et=end_frame,
                        qlt=int(self.quality_value_line_edit.text()), 
                        fmt=self.format_combo_box.currentText(),
                        c=self.codec_combo_box.currentText(),
                        fo=1,
                        v=0,
                        os=1,
                        w=int(width),
                        h=int(height))
                        
            if '.####.' in output:
                output = output.replace('.####.', '.%4d.')
            all_playblasts.append(output)

        final_playblast_path = "{}/{}.{}".format(self.file_input_line_edit.text(), self.get_scene_name(), extension)
        self.make_final_playblast(final_playblast_path, all_playblasts)

    def make_final_playblast(self, final_playblast_path, all_playblasts):
        '''
        takes playblast as per user settings
        '''
        extension = self.get_extension_from_selection()
        scene_name = self.get_scene_name()
        
        audio_file = brain.PlayblastFuncs.get_audio(self.add_audio_checkbox)
        if audio_file:
            temp_playblast_path = "{}/temp_{}.{}".format(self.file_input_line_edit.text(), scene_name, extension)
        else:
            temp_playblast_path = final_playblast_path

        all_playblasts = self.compile_playblasts(temp_playblast_path, final_playblast_path, all_playblasts)
        os.startfile(final_playblast_path)

        for i in list(set(all_playblasts)):
            if '%4d' in i:
                self.delete_image_sequences(i)
            else:
                self.remove_file(i)

    def delete_image_sequences(self, image_playblast_path):
        all_paths = glob.glob(image_playblast_path.replace('%4d', '*'))
        for i in all_paths:
            self.remove_file(i)

    def remove_file(self, file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            pm.displayWarning("Cannot delete the {}".format(file_path))

    
    def add_audio_to_video(self, audio_path, video_path, output_path):
        '''
        adds the audio to given video
        '''
        audio_base_command = self.base_command
        audio_video_merge_command = "{} -i {} -i {} -y {}" .format(audio_base_command, audio_path, video_path, output_path)
        return self.run_ffmpeg_command(audio_video_merge_command)
    
    def run_ffmpeg_command(self, command_to_run):
        '''
        runs the ffmpeg compilation headless command
        '''
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        try:
            if _PLATFORM_ == 'Darwin':
                env = {'PATH': '/usr/local/bin:/usr/bin:/bin'}
                process = subprocess.Popen(command_to_run, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()
                process.wait()
                return True
            else:
                process = subprocess.Popen(command_to_run, startupinfo= si)
                process.communicate()
                process.wait()
                return True
        except Exception as e:
            pm.confirmDialog(icon = 'critical', title = 'Error', message = 'Following error occurred while compiling video \n{}'.format(e))
            return False

def main():
    delete_widget_instances(main_maya_win(), __TOOL_NAME__)
    GUI = PlayblastUI()
    GUI.show()

