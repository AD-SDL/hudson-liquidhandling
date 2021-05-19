import os
import shutil


def archive(filenames, directory):
    """
    filenames = list of files or directories to archive, [path1, path2, ect. ]
    directory = path to directory which will contain archive folder
    """
    try:
        # create archive folder if doesn't exist
        archive_path = os.path.join(directory, "archive" + os.path.sep)
        if not os.path.exists(os.path.dirname(archive_path)):
            os.makedirs(archive_path)

        # move each file into archive folder
        for i in range(len(filenames)):

            new_path = os.path.join(archive_path, os.path.basename(filenames[i]))

            # if file already exists in archive, force overwrite (for testing)
            if os.path.exists(new_path):
                os.remove(new_path)

            # os.rename(filenames[i], new_filename)
            shutil.move(filenames[i], archive_path)

    except OSError as e:
        print("Error: could not archive sent files")
        print(e)
