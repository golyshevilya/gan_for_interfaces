import progressbar
import sys
# Конфиг файл

# директории

# путь до проекта
work_dir = sys.path[0]
# директория с конфигурационными файлами
dir_config = 'config'

# директория с входными данными
dir_input_data = 'input_data'
# директория с экземплярами каждого класса
dir_original = 'png_boxes_original'
# директория с раскрашенными экземплярами каждого класса
dir_color_boxes = 'png_boxes_color'

# директория с выходными данными
dir_output_data = 'output_data'
# директория с преобразованными входными примерами
dir_prepare_boxes = 'png_boxes'
# директория с изображениями
dir_result_img = 'img'
# директория с xml разметкой
dir_result_xml = 'xml'
# директория результирующим датасетом
dir_dataset = 'train'

# текстовый файл с данными по классам
file_with_classnames = r'config\voc_annotation.txt'
# размер изображения
image_size = {
    'height': 1024,
    'width': 512
}
# размер матрицы
matrix_size = (4, 4)
# размер ячейки матрицы
step = {
    'height': image_size['height'] // matrix_size[0],
    'width': image_size['width'] // matrix_size[1]
}
# директория с результирующими изображениями
dir_pix_img = r'output_data\img'
# директория с результирующей xml разметкой
dir_pix_xml = r'output_data\xml'
# директория с изначальными изображениями классов
dir_or = r'input_data\png_boxes_original'
# директория с преобразованными изображениями классов
dir_jpg = r'output_data\png_boxes'
# параметры для настройки загрузчика
widgets = [
    progressbar.Percentage(),
    progressbar.Bar(left='|', marker='█', right='|'),  # Прогресс
    progressbar.AnimatedMarker(),
    progressbar.Timer(format=' Current time: %(elapsed)s '),
    progressbar.AbsoluteETA(format='| Est. finish: %(eta)s', )
]
