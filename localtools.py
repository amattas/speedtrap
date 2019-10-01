import os


class LocalTools:

    def __init__(self, config):
        self._config = config

    @staticmethod
    def clean_local(config):
        for filename in os.listdir(config.storage_path):
            if filename.endswith(config.database_filename):
                os.remove(config.database_path+filename)
            if filename.endswith(config.camera_file_extension):
                os.remove(config.database_path+filename)
