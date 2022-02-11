from PIL import Image, ImageDraw, ImageFont
from PIL import ImageFilter
import sys
import random


if __name__ == '__main__':
    # Load an image
    im = Image.open(sys.argv[1])

    # Check its width, height, and number of color channels
    print("Image is %s pixels wide." % im.width)
    print("Image is %s pixels high." % im.height)
    print("Image mode is %s." % im.mode)

    # Pixels are accessed via an (X,Y) tuple.
    # The coordinate system starts at (0,0) in the upper left-hand corner,
    # and increases moving right (first coordinate) and down (second coordinate).
    # So it's a (col, row) indexing system, not (row, col) like we're used to
    # when dealing with matrices or 2d arrays.
    print("Pixel value at (10,10) is %s" % str(im.getpixel((10, 10))))

    # Get list of strings from answer key txt file.
    with open(sys.argv[2], 'r') as txt_file:
        lines = txt_file.readlines()

    # Build something I can read with the data from the answers

    # Paste on image and save.
"""
    # Create font and size
    font = ImageFont.truetype("arial.ttf", 20)
    # draw text on document
    d = ImageDraw.Draw(im)
    d.multiline_text((2 * im.width / 3, im.height - 50), "Encryption_placeholder", font=font)
    im.show()
    #gray_im.save("gray.png")
"""