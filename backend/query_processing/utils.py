import os
def generate_path_to_attachment(filetype, filename, fileformat, prefix, filetype_folder, is_cwd_required = True):
            return ".".join(
               [ os.path.join(
                os.getcwd() if is_cwd_required else "",
                prefix,
                filetype_folder,
                filename
            ),
            fileformat
            ]
            )