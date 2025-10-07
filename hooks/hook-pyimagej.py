from PyInstaller.utils.hooks import copy_metadata, collect_data_files

datas = copy_metadata('pyimagej')
datas += collect_data_files('pyimagej')
