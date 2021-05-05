from src import item as it
import random
import numpy as np
import os
from xml.dom import minidom
from config import config
from xml.etree.ElementTree import Element, SubElement, tostring
import progressbar
from PIL import Image


def create_matrix() -> np.ndarray:
    """
    Function for creating a matrix to control the placement of class objects in the image.
    :return: np.ndarray
    """
    matrix = np.array([0] * (config.matrix_size[0] * config.matrix_size[1]), int)
    matrix = matrix.reshape(config.matrix_size)
    return matrix


def change_size(item: list) -> None:
    """
    Function for converting the original sample images of each class to the specified size and saving them to a
    separate directory.
    :param item: list - a list, each element is an instance of the Item class and contains information about which
    resolution to convert to.
    :return: None
    """
    # full path to the directory with the source examples of objects of each class
    path_or = os.path.join(config.work_dir, config.dir_input_data, config.dir_original)

    # getting the number of files in the source directory
    count_of_files = len(os.listdir(path_or))
    progress_count = 0
    print('\n*****Change size boxes: *****')
    bar = progressbar.ProgressBar(maxval=count_of_files, widgets=config.widgets).start()

    # loop through all source objects
    for element in os.listdir(path_or):
        base_name, ext = os.path.splitext(element)
        if ext not in ['.png']:
            continue
        progress_count += 1
        bar.update(progress_count)

        # full path to a single object
        full_name = os.path.join(path_or, element)

        # the full path where the class object will be saved after conversion
        full_res_name = os.path.join(config.work_dir, config.dir_output_data, config.dir_prepare_boxes, element)

        # opening the original image
        img = Image.open(full_name).convert("RGBA")
        img.load()

        # splitting an image into strips (R, G, B, A)
        bands = img.split()

        # filter for resizing an image
        resample = Image.ANTIALIAS

        # getting the initial dimensions of an object
        dim = [obj.size_start for obj in item if obj.name in base_name][0]

        # converting each color-light strip of the image to a new size
        bands = [b.resize(dim, resample) for b in bands]

        # combining all the stripes into a single image
        img = Image.merge('RGBA', bands)

        # saving the resulting image
        img.save(full_res_name)
    bar.finish()


def save_xml(filename: str, xml_code: Element) -> None:
    """
    Function for saving an XML file.
    :param filename: str - the full path to the file where you want to save it.
    :param xml_code: Element - an instance of a class that stores an XML structure for saving
    :return: None
    """
    # convert xml in strings
    xml_string = tostring(xml_code).decode()

    # parsing the resulting string
    xml_prettyxml = minidom.parseString(xml_string).toprettyxml()

    # save to a file
    with open(filename, 'w') as xml_file:
        xml_file.write(xml_prettyxml)


def new_data() -> None:
    """
    Function for generating images and XML markup and storing this data in the directories specified in the config file
    :return: None
    """
    # array with full parameters for each class
    item = []
    random.seed()

    # getting class names and their number from a file
    with open(config.file_with_classnames, 'r') as file:
        for line in file:
            str_ = line.split(' ')
            name = str_[0]
            count = str_[1][:-1]
            item.append(it.Item(name, count))

    # function for converting the source instances of each class to the initial dimensions
    change_size(item)

    # current class number
    index = 0

    # creating a variable responsible for the file number
    _count_ = 1
    print('\n*****Create image and xml for pix: *****')
    number_classes = len(item)

    # the list of accounting for the number of elements of each class
    list_count_of_each_class = [0] * number_classes
    progress_count = 0

    # counter of the total number of objects in the future dataset
    count_of_image = 0
    name_to_xml = str(_count_)

    # cycle through all class parameters
    for x in item:
        count_of_image += int(x.count)
    bar = progressbar.ProgressBar(maxval=count_of_image, widgets=config.widgets).start()

    # flag that is responsible for stopping the formation of the dataset
    flag = True

    # cycle for creating a dataset
    while flag:
        # a tuple that stores the size of an image
        size_ = (config.image_size['width'], config.image_size['height'])

        # creating an xml file
        root = Element("annotation")
        file = SubElement(root, "filename")
        file.text = str(name_to_xml + '.jpg')
        path = SubElement(root, "path")
        path.text = str(f'{config.dir_output_data}/{config.dir_result_img}/{name_to_xml}.jpg')
        size_tree = SubElement(root, "size")
        width = SubElement(size_tree, "width")
        width.text = str(int(size_[0]))
        height = SubElement(size_tree, "height")
        height.text = str(int(size_[1]))
        depth = SubElement(size_tree, "depth")
        depth.text = "3"

        # creating auxiliary arrays
        object_, name, xmin_, xmax_, ymax_, ymin_, bndbox = [], [], [], [], [], [], []

        # creating a new image with the specified dimensions and a black background
        img = Image.new("RGB", (config.image_size['width'], config.image_size['height']), '#191919')

        # flag that controls the fullness of the dataset
        flag_end = True

        # variable responsible for the number of files created
        end_file = 0

        # auxiliary variable for accessing arrays for xml markup
        number = 0

        # creating a matrix for the location of class objects
        matrix = create_matrix()

        # checking for boundary conditions
        while flag_end:
            end = 0
            if index >= number_classes:
                index = 0
            if list_count_of_each_class[index] >= int(item[index].count):
                while list_count_of_each_class[index] >= int(item[index].count):
                    index += 1
                    end += 1
                    if index == number_classes:
                        index = 0
                    if end == number_classes:
                        flag = False
                        break
            if not flag:
                break

            coeff_orientation = None

            # orientation check to generate the orientation coefficient
            if item[index].orientation == 0:  # original
                coeff_orientation = 1
            # elif(item[index].orientation == 1): # horizontal
            #     coeff_orientation = random.randrange(70, 80, 1) / 100
            # elif(item[index].orientation == 2): # vertical
            #     coeff_orientation = 100 / random.randrange(70, 80, 1)

            # if (item[index].current_size[1] + item[index].config.step_change_size <= item[index].size_finish[1]):
            #     item[index].orientation = (item[index].orientation + 1 if (item[index].orientation < 2) else 0)

            # the number of occupied cells in the matrix by width
            count_of_x_boxes_item = int(
                (item[index].current_size[1] // config.step['width'] + 1)
                if item[index].current_size[1] % config.step['width'] > 0
                else int(item[index].current_size[1] // config.step['width']))

            # the number of occupied cells in the matrix by height
            count_of_y_boxes_item = int(
                (item[index].current_size[0] // config.step['height'] + 1)
                if item[index].current_size[0] % config.step['height'] > 0
                else int(item[index].current_size[0] // config.step['height']))

            # the path to the prepared image of the class object
            full_file_name = os.path.join(config.work_dir,
                                          config.dir_output_data,
                                          config.dir_prepare_boxes,
                                          f'{item[index].name}.png')

            # the path to the prepared image of the class object opening the image and converting to RGBA
            button = Image.open(full_file_name).convert("RGBA")

            # flag for determining whether an object of the class will be added to the image
            done_item_box = False

            # cycle through the matrix in height
            for i in range(4):
                global j

                # cycle through the matrix in width
                for j in range(4):

                    # flag for adding a class object to an image
                    is_fit = True

                    # checking that an object of the class with the new dimensions is placed on the image
                    if (count_of_x_boxes_item + j < 5) and (count_of_y_boxes_item + i < 5):

                        # cycle through the allowed cells in height
                        for y in range(i, i + count_of_y_boxes_item):

                            # cycle through the allowed cells in width
                            for x in range(j, j + count_of_x_boxes_item):

                                # checking that the cells of the matrix in which we want to place the object are free
                                if matrix[y, x] > 0:
                                    # we transfer the flag to the stage of the impossibility of adding it
                                    is_fit = False
                                    break
                            if not is_fit:
                                break

                        # checking whether an object of the class can be added to the image
                        if is_fit:

                            # cycle through the allowed cells in height
                            for y in range(i, i + count_of_y_boxes_item):

                                # cycle through the allowed cells in width
                                for x in range(j, j + count_of_x_boxes_item):
                                    # note in the matrix that these cells are filled in
                                    matrix[y, x] = 1

                            # setting the flag for adding a class object to the true state
                            done_item_box = True
                            break

                # checking whether an object of the class can be added to the image
                if done_item_box:

                    # resetting the variable number of filled files
                    end_file = 0

                    # the width of the area required for the class object
                    width = (j + count_of_x_boxes_item) * config.step['width']

                    # the height of the area required for the class object
                    height = (i + count_of_y_boxes_item) * config.step['height']

                    # offset from the edge
                    random_indent = random.randrange(5, 15, 5) if ((item[index].current_size[1] == 100) or (
                            item[index].current_size[1] == 120)) else random.randrange(20, 40, 5)

                    width_min, height_min, width_max, height_max = None, None, None, None
                    # checking that the class object should be shifted to the upper-left corner relative to the start
                    # cell
                    if item[index].current_position == 1:
                        width_min = width - count_of_x_boxes_item * config.step['width'] + random_indent
                        height_min = height - count_of_y_boxes_item * config.step['height'] + random_indent
                        width_max = width - count_of_x_boxes_item * config.step['width'] + item[index].current_size[
                            1] + random_indent
                        height_max = height - count_of_y_boxes_item * config.step['height'] + item[index].current_size[
                            0] + random_indent
                        item[index].current_position += 1

                    # checking that the class object should be shifted to the upper-right corner relative to the start
                    # cell
                    elif item[index].current_position == 2:
                        width_min = width - item[index].current_size[1] - random_indent
                        height_min = height - count_of_y_boxes_item * config.step['height'] + random_indent
                        width_max = width - random_indent
                        height_max = height - count_of_y_boxes_item * config.step['height'] + item[index].current_size[
                            0] + random_indent
                        item[index].current_position += 1

                    # checking that the class object should be shifted to the lower-left corner relative to the start
                    # cell
                    elif item[index].current_position == 3:
                        width_min = width - count_of_x_boxes_item * config.step['width'] + random_indent
                        height_min = height - item[index].current_size[0] - random_indent
                        width_max = width - count_of_x_boxes_item * config.step['width'] + item[index].current_size[
                            1] + random_indent
                        height_max = height - random_indent
                        item[index].current_position += 1

                    # checking that the class object should be shifted to the lower-right corner relative to the start
                    # cell
                    elif item[index].current_position == 4:
                        width_min = width - item[index].current_size[1] - random_indent
                        height_min = height - item[index].current_size[0] - random_indent
                        width_max = width - random_indent
                        height_max = height - random_indent
                        item[index].current_position += 1

                    # checking that the class object should be shifted to the center part relative to the start cell
                    elif item[index].current_position == 5:
                        width_min = width - count_of_x_boxes_item * config.step['width'] / 2 - \
                                    item[index].current_size[1] / 2
                        height_min = height - count_of_y_boxes_item * config.step['height'] / 2 - \
                                     item[index].current_size[0] / 2
                        width_max = width - count_of_x_boxes_item * config.step['width'] / 2 + \
                                    item[index].current_size[1] / 2
                        height_max = height - count_of_y_boxes_item * config.step['height'] / 2 + \
                                     item[index].current_size[0] / 2
                        item[index].current_position = 1

                    progress_count += 1
                    bar.update(progress_count)

                    # filter for resizing an image
                    resample = Image.ANTIALIAS
                    button.load()

                    # splitting an image into strips (R, G, B, A)
                    bands = button.split()

                    # getting new object sizes
                    dim = (int(width_max - width_min), int(height_max - height_min))

                    # converting each color-light strip of the image to a new size
                    bands = [b.resize(dim, resample) for b in bands]

                    # combining all the stripes into a single image
                    button = Image.merge('RGBA', bands)

                    # inserting the resulting class object into the image
                    img.paste(button, (int(width_min), int(height_min)), button)

                    # adding a class name to xml
                    object_.append(SubElement(root, "object_"))
                    name.append(SubElement(object_[number], "name"))
                    name[number].text = str(item[index].name)
                    bndbox.append(SubElement(object_[number], "bndbox"))
                    xmin_.append(SubElement(bndbox[number], "xmin"))
                    xmin_[number].text = str(int(width_min))
                    ymin_.append(SubElement(bndbox[number], "ymin"))
                    ymin_[number].text = str(int(height_min))
                    xmax_.append(SubElement(bndbox[number], "xmax"))
                    xmax_[number].text = str(int(width_max))
                    ymax_.append(SubElement(bndbox[number], "ymax"))
                    ymax_[number].text = str(int(height_max))

                    # increasing the number of added objects for the current class
                    list_count_of_each_class[index] += 1

                    # increasing the auxiliary variable by 1
                    number += 1

                    # getting a new object height
                    height_current = (item[index].current_size[1] + item[index].step_change_size) * \
                                     item[index].current_size[0] / item[index].current_size[1]

                    # getting a new object width
                    item[index].current_size[1] = (
                        item[index].current_size[1] + item[index].step_change_size if item[index].current_size[1] +
                                                                                      item[index].step_change_size <=
                                                                                      item[index].size_finish[1] else
                        item[index].size_start[1])

                    # checking that the current width is equal to the initial width
                    if item[index].current_size[1] == item[index].size_start[1]:
                        height_current = item[index].size_start[0]

                    # getting the height
                    item[index].current_size[0] = height_current * coeff_orientation
                    break

            # checking that the class object did not fit into the file
            if not done_item_box:
                end_file += 1

            # checking that the number of filled files == the number of classes
            if end_file == number_classes:
                flag_end = False

            # moving the class number variable to the next class
            index += 1

        # saving the image
        img.save(os.path.join(config.work_dir, config.dir_output_data, config.dir_result_img, f'{str(_count_)}.jpg'))

        # path to the xml file
        name_ = os.path.join(config.work_dir, config.dir_output_data, config.dir_result_xml, f'{str(_count_)}.xml')

        # calling the function that saves the xml file
        save_xml(name_, root)

        # increasing the file number by 1
        _count_ += 1
    bar.finish()
