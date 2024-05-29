import struct
import sys

def is_inside_diamond(x, y, vertices):
    # Используем метод полуплоскостей для определения, находится ли точка внутри ромба
    def sign(p1, p2, p3):
        return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])

    b1 = sign((x, y), vertices[0], vertices[1]) < 0.0
    b2 = sign((x, y), vertices[1], vertices[2]) < 0.0
    b3 = sign((x, y), vertices[2], vertices[3]) < 0.0
    b4 = sign((x, y), vertices[3], vertices[0]) < 0.0

    return ((b1 == b2) and (b2 == b3) and (b3 == b4))

def create_bmp(width, height, color, filename, samples_per_pixel=4):
    # Вычисление размера строки в байтах, включая дополнительные байты для выравнивания
    bytes_per_row_without_padding = width * 3
    padding_size = (4 - (bytes_per_row_without_padding % 4)) % 4
    bytes_per_row_with_padding = bytes_per_row_without_padding + padding_size
    # Создание заголовка файла
    file_size = 54 + height * bytes_per_row_with_padding # Размер файла = заголовок + данные
    file_header = struct.pack('<2sIHHI', b'BM', file_size, 0, 0, 54)
    info_header = struct.pack('<IIIHHIIIIII', 40, width, height, 1, 24, 0, height * bytes_per_row_with_padding, 0, 0, 0, 0)
    # Создание изображения с учетом дополнительных байтов для выравнивания
    image_data = bytearray()
    padding = b'\x00' * padding_size
    # Рисование ромба с использованием метода полуплоскостей
    mid_x, mid_y = width // 2, height // 2
    # Определяем вершины ромба
    vertices = [(mid_x, 0), (width - 1, mid_y), (mid_x, height - 1), (0, mid_y)]

    for y in range(height):
        row = bytearray()
        for x in range(width):
            samples_inside = 0
            for sy in range(samples_per_pixel):
                for sx in range(samples_per_pixel):
                    sample_x = x + (sx + 0.5) / samples_per_pixel
                    sample_y = y + (sy + 0.5) / samples_per_pixel
                    if is_inside_diamond(sample_x, sample_y, vertices):
                        samples_inside += 1

            coverage = samples_inside / (samples_per_pixel * samples_per_pixel)
            if coverage > 0:
                r = int((1 - coverage) * 255 + coverage * color[2])
                g = int((1 - coverage) * 255 + coverage * color[1])
                b = int((1 - coverage) * 255 + coverage * color[0])
                row += struct.pack('BBB', b, g, r)
            else:
                row += b'\xFF\xFF\xFF'
        row += padding # Добавление дополнительных байтов для выравнивания
        image_data += row

    with open(filename, 'wb') as f:
        f.write(file_header)
        f.write(info_header)
        f.write(image_data)

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print("Usage: python script.py <width> <height> <color_hex> <output_filename>")
        sys.exit(1)

    width, height = int(sys.argv[1]), int(sys.argv[2])
    color_hex = sys.argv[3].lstrip('#')
    # Порядок цветов в BMP - BGR, а не RGB
    color = struct.pack('BBB', int(color_hex[4:6], 16), int(color_hex[2:4], 16), int(color_hex[:2], 16))
    filename = sys.argv[4]

    create_bmp(width, height, color, filename)
    print(f'Изображение успешно сфорировано и сохранено под названием {filename}')