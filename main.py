# -*- coding: utf-8 -*-
from fontTools.ttLib import TTFont
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import numpy as np
import os


def get_cmap(font_file):
    """
    Get unicode cmap - Character to Glyph Index Mapping Table

    font_file: path of font file
    """
    try:
        font = TTFont(font_file)
    except:
        return None

    try:
        cmap = font.getBestCmap()
    except:
        return None
    font.close()
    return cmap


def get_decimal_unicode(font_file):
    """
    Get unicode (decimal mode - radix=10) of font.
    """
    cmap = get_cmap(font_file)
    if cmap is None:
        return None
    try:
        decimal_unicode = list(cmap.keys())
    except:
        decimal_unicode = None
    return decimal_unicode


def decimal_to_hex(decimal_unicode, prefix='uni'):
    """
    Convert decimal unicode (radix=10) to hex unicode (radix=16, str type)
    """

    def _regularize(single_decimal_unicode, prefix):
        # result of hex() contains prefix '0x', such as '0x61',
        # while font file usually use 'uni0061',
        # so support changing prefix and filling to width 4 with 0
        h = hex(single_decimal_unicode)
        single_hex_unicode = prefix + h[2:].zfill(4)
        return single_hex_unicode

    is_single_code = False
    if not isinstance(decimal_unicode, (list, tuple)):
        decimal_unicode = [decimal_unicode]
        is_single_code = True

    hex_unicode = [_regularize(x, prefix) for x in decimal_unicode]

    if is_single_code:
        hex_unicode = hex_unicode[0]
    return hex_unicode


def decimal_to_char(decimal_unicode):
    """
    Convert decimal unicode (radix=10) to characters
    """
    is_single_code = False
    if not isinstance(decimal_unicode, (list, tuple)):
        decimal_unicode = [decimal_unicode]
        is_single_code = True

    char = [chr(x) for x in decimal_unicode]

    if is_single_code:
        char = char[0]
    return char


def get_bbox_offset(bbox, image_size):
    """
    Get offset (x, y) for moving bbox to the center of image

    bbox: bounding box of character, containing [xmin, ymin, xmax, ymax]
    """
    if not isinstance(image_size, (list, tuple)):
        image_size = (image_size, image_size)

    center_x = image_size[0] // 2
    center_y = image_size[1] // 2
    xmin, ymin, xmax, ymax = bbox
    bbox_xmid = (xmin + xmax) // 2
    bbox_ymid = (ymin + ymax) // 2
    offset_x = center_x - bbox_xmid
    offset_y = center_y - bbox_ymid
    return offset_x, offset_y


def char_to_image(char, font_pil, image_size, bg_color=255, fg_color=0):
    """
    Generate an image containing single character in a font.

    char: such as '中' , 'a' ...
    font_pil: result of PIL.ImageFont
    """
    try:
        bbox = font_pil.getbbox(char)
    except:
        return None

    if not isinstance(image_size, (list, tuple)):
        image_size = (image_size, image_size)
    offset_x, offset_y = get_bbox_offset(bbox, image_size)
    offset = (offset_x, offset_y)

    # convert ttf/otf to bitmap image using PIL
    image = Image.new('L', image_size, bg_color)
    draw = ImageDraw.Draw(image)
    draw.text(offset, char, font=font_pil, fill=fg_color)
    return image


def font2image(font_file,
               font_size,
               image_size,
               decimal_unicode=None,
               bg_color=255,
               fg_color=0):
    """
    Generate images from a font.

    font_size: size of font when reading by PIL, type=float
    image_size: image_size should normally be larger than font_size
    decimal_unicode: if not None, only generate images of decimal_unicode
    name_mode: if not 'char', then will be like 'uni0061'
    """

    font_pil = ImageFont.truetype(font_file, font_size)
    if not isinstance(image_size, (list, tuple)):
        image_size = (image_size, image_size)

    if decimal_unicode is None:
        decimal_unicode = get_decimal_unicode(font_file)

    arr = []
    
    for code in decimal_unicode:
        char = chr(code)

        image = char_to_image(char, font_pil, image_size, bg_color, fg_color)
        if image is None:
            continue
        
        
        iml = list(image.getdata())
        arr += iml
            
    print(len(decimal_unicode),len(arr))
    start_arr = np.array(arr,dtype=np.uint8)
    end_arr = np.array(decimal_unicode,dtype=np.uint32)

    out_folder,ext = os.path.splitext(os.path.basename(font_file))

    os.makedirs(out_folder)

    start_arr.tofile(out_folder + '/img_u8.raw')
    end_arr.tofile(out_folder +'/unicode_u32.raw')
    
    f0 = open(out_folder + '/img_u8.raw','rb')
    f1 = open(out_folder + '/unicode_u32.raw','rb')
    f = open(out_folder + f'/img(0)-unicode({hex(len(arr))}).raw','wb+')

    f.write(f0.read())
    f.write(f1.read())

    f0.close()
    f1.close()
    f.close()


if __name__ == '__main__':
    font_file = r'GB2312.ttf'
    #font_file = r'SourceHanSerifSC-SemiBold.otf'
    font2image(font_file, 16, 16)

