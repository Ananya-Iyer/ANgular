import pymel.core as pm
if "2016" in pm.about(v=1):
    from PySide import QtGui as QtWidgets
else:
    from PySide2 import QtWidgets
class PlayblastFuncs():

    @staticmethod
    def file_browsing():
        '''
        Used to set output folder for playblast
        '''
        selected_file = QtWidgets.QFileDialog.getExistingDirectory (None,"Select Output Folder")
        return selected_file if selected_file else ""

    @staticmethod
    def get_cameras():
        '''
        gives a list of all existing cameras in the scene file to
        populate in the camera combo box
        '''
        return pm.listCameras()

    @staticmethod
    def get_frame_range():
        '''
        gets the start and end fframe ranges
        '''
        start_frame = pm.playbackOptions(query=1, minTime=1)
        end_frame = pm.playbackOptions(query=1, maxTime=1)
        return start_frame, end_frame

    @staticmethod
    def get_playblast_formats():
        '''
        gets all the available formats of playblasting
        '''
        return pm.playblast(q=1,format=1)

    @staticmethod
    def get_codecs(in_format):
        '''
        gets codec depending on the selected format
        '''
        if in_format in ('image',):
            return ('jpg', 'tiff', 'png', 'tga', 'bmp') 
        if in_format in ('qt'):
            return ('H.264',)
        return pm.mel.eval('playblast -format "{0}" -q -compression;'.format(in_format))

    @staticmethod
    def get_audio(checkbox_checked):
        '''
        gets the first audio file from maya scene
        '''
        if not checkbox_checked.isChecked():
            return
        audios = pm.ls(type='audio')
        if audios:
            return audios[0].filename.get()

    @staticmethod
    def get_video_extension(codec):
        '''
        gets the extension of codec so as to help compile playblast with its own extension
        '''
        if codec == 'avi':
            return 'avi'
        elif codec in ('qt', 'image'):
            return 'mov'
        return None

    @staticmethod
    def get_resolution():
        '''
        gives list of video resolution
        '''
        return ('1920x1080', '1280x720', '720x560', '640x480',)
