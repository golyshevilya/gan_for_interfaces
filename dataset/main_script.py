import os
import shutil

from src import connecting_image_to_markup
from src import create_data
from config import config

if __name__ == '__main__':
    # path to the directory with the input data
    path_to_input_data = os.path.join(config.work_dir, config.dir_input_data)

    # checking for a directory with examples of each class
    if config.dir_original not in os.listdir(path_to_input_data):
        raise FileNotFoundError(f"Missing directory with examples of each class: "
                                f"{os.path.join(path_to_input_data, config.dir_original)}")

    # checking for a directory with colored examples of each class
    if config.dir_color_boxes not in os.listdir(path_to_input_data):
        raise FileNotFoundError(f"Missing directory with colored examples of each class: "
                                f"{os.path.join(path_to_input_data, config.dir_color_boxes)}")

    # checking the number of examples of original and colored ones
    path_to_original_files = os.path.join(path_to_input_data, config.dir_original)
    path_to_color_files = os.path.join(path_to_input_data, config.dir_color_boxes)
    count_original_files = len([name for name in os.listdir(path_to_original_files)
                                if os.path.isfile(os.path.join(path_to_original_files, name))])
    count_color_files = len([name for name in os.listdir(path_to_color_files)
                             if os.path.isfile(os.path.join(path_to_color_files, name))])
    if count_color_files != count_original_files:
        raise ResourceWarning(f"Number of source files:{count_original_files}; "
                              f"number of colorized files:{count_color_files}")

    # path to the output data directory
    path_to_output_data = os.path.join(config.work_dir, config.dir_output_data)

    # creating and deleting directories for output data
    if config.dir_output_data in os.listdir(config.work_dir):
        shutil.rmtree(path_to_output_data)
    path_to_prepare_files = os.path.join(path_to_output_data, config.dir_prepare_boxes)
    path_to_result_img = os.path.join(path_to_output_data, config.dir_result_img)
    path_to_result_xml = os.path.join(path_to_output_data, config.dir_result_xml)
    path_to_result_dataset = os.path.join(path_to_output_data, config.dir_dataset)
    os.makedirs(path_to_prepare_files)
    os.makedirs(path_to_result_img)
    os.makedirs(path_to_result_xml)
    os.makedirs(path_to_result_dataset)

    # generating images and xml markup
    create_data.new_data()

    # convert the XML markup to a color map and connect it to the image
    connecting_image_to_markup.create_img_pix(path_to_result_xml,
                                              path_to_result_dataset,
                                              path_to_color_files,
                                              path_to_result_img)

    print(f"\nThe resulting dataset is saved in the directory: {path_to_result_dataset}")
