import os

import progressbar
from PIL import Image
from lxml import etree

from config import config


def create_img_pix(path_to_xml: str, path_to_pix_img: str, path_to_png: str, path_to_img: str) -> None:
    """
    Function for converting XML markup to a color map and combining the map and the resulting image.
    :param path_to_xml: str - the path to the XML markup.
    :param path_to_pix_img: str - the path to the directory where the result will be saved.
    :param path_to_png: str - the path to the colored class instances.
    :param path_to_img: str - the path to the resulting images.
    :return:
    """
    count_of_files = len(os.listdir(path_to_xml))
    progress_count = 0
    print('\n*****Create double-images for pix-dataset: *****')
    bar = progressbar.ProgressBar(maxval=count_of_files, widgets=config.widgets).start()

    # loop through XML files
    for xml_name in os.listdir(path_to_xml):
        progress_count += 1
        _, ext = os.path.splitext(xml_name)
        if ext.lower() not in ['.xml']:
            continue
        bar.update(progress_count)
        img_name = xml_name.replace('.xml', '.jpg')

        # path to a single XML file
        full_file_name_xml = os.path.join(path_to_xml, xml_name)

        # path to a single resulting image
        full_file_name_img = os.path.join(path_to_img, img_name)

        # path to a single merged image
        full_file_name_pix_img = os.path.join(path_to_pix_img, img_name)
        img = Image.open(full_file_name_img).convert("RGBA")
        size = img.size
        pix_img = Image.new("RGB", (size[0] * 2, size[1]), '#191919')
        pix_img.paste(img, (0, 0), img)
        tree = etree.parse(full_file_name_xml)
        file = tree.getroot()
        label = file.xpath(".//name")
        xmin = file.xpath(".//xmin")
        xmax = file.xpath(".//xmax")
        ymin = file.xpath(".//ymin")
        ymax = file.xpath(".//ymax")
        for i in range(len(label)):
            full_file_name_png = os.path.join(path_to_png, label[i].text + '.png')
            btn = Image.open(full_file_name_png)
            btn.crop((int(xmin[i].text), int(ymin[i].text), int(xmax[i].text), int(ymax[i].text)))
            pix_img.paste(btn, (int(xmin[i].text) + size[0], int(ymin[i].text)), btn)
        pix_img.save(full_file_name_pix_img)
    bar.finish()
