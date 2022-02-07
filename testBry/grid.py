# Import the Image and ImageFilter classes from PIL (Pillow)
from PIL import Image
from PIL import ImageFilter
import sys
import numpy as np

def convolution(image, kernel):
    # Flip kernel horizontally and vertically for convolution.
    kernel = np.flipud(kernel)
    kernel = np.fliplr(kernel)
    # Get the amount edge pixels that will be undetermined in the final image.
    ker_radius = kernel.shape[0] // 2
    # Create a new image to transfer the convolved image pixels into from the original image.
    # Reference: https://pillow.readthedocs.io/en/stable/reference/Image.html
    new_image = Image.new("RGB", (image.width, image.height), color=0)
    for x in range(ker_radius, image.width - ker_radius):
        for y in range(ker_radius, image.height - ker_radius):
            # For each inner pixel, calculate the new RGB values for the resulting pixel.
            mt_list = [0, 0, 0]
            for w in range(x - ker_radius, x + ker_radius + 1):
                for h in range(y - ker_radius, y + ker_radius + 1):
                    p = image.getpixel((w, h))
                    # Calculate the value for each RGB dimension per pixel.
                    for i in range(3):
                        mt_list[i] += p[i] * kernel[h - y + ker_radius, w - x + ker_radius]
            new_image.putpixel((x, y), tuple([int(n) for n in mt_list]))
    # Crops out the undetermined edge pixels from the original image. Reference: Image.crop() from PIL
    # Reference: https://pillow.readthedocs.io/en/stable/reference/Image.html
    new_image = new_image.crop((ker_radius, ker_radius, new_image.width - ker_radius, new_image.height - ker_radius))
    return new_image


if __name__ == '__main__':
    # Load an image
    im = Image.open(sys.argv[1])

    # Check its width, height, and number of color channels
    print("Image is %s pixels wide." % im.width)
    print("Image is %s pixels high." % im.height)
    print("Image mode is %s." % im.mode)

    # Let's create a grayscale version of the image:
    # the "L" means there's only a single channel, "Lightness"
    gray_im = im.convert("L")

    # Create a new blank color image the same size as the input
    color_im = Image.new("RGB", (im.width, im.height), color=0)
    # gray_im.save("gray.png")

    # Highlights any very dark areas with yellow.
    for x in range(im.width):
        for y in range(im.height):
            p = gray_im.getpixel((x, y))
            if p < 50:
                (R, G, B) = (255, 255, 0)
                color_im.putpixel((x, y), (R, G, B))
            else:
                color_im.putpixel((x, y), (0, 0, 0))
    color_im.show()

    # Need to create a horizontal or vertical line based on the yellow pixels

    kern = np.array([[0, 1, 0],
                     [0, 1, 0],
                     [0, 1, 0],
                     [0, 1, 0],
                     [0, 1, 0],
                     [0, 1, 0],
                     [0, 1, 0]])

    color_im = convolution(color_im, kern)

    for x in range(im.width):
        for y in range(im.height):
            p = color_im.getpixel((x, y))
            if p[0] > 5 and p[1] > 5:
                (R, G, B) = (255, 255, 0)
                color_im.putpixel((x, y), (R, G, B))
            else:
                color_im.putpixel((x, y), (0, 0, 0))
    color_im.show()
    print('Done')

    # box = [0, 0, 0, 1, 1, 1, 0, 0, 0]
    # test = color_im.filter(ImageFilter.Kernel((3, 3), box, sum(box)))


    # Show the image. We're commenting this out because it won't work on the Linux
    # server (unless you set up an X Window server or remote desktop) and may not
    # work by default on your local machine. But you may want to try uncommenting it,
    # as seeing results in real-time can be very useful for debugging!
    # color_im.show()

    # Save the image
    # color_im.save("output.png")

    # This uses Pillow's code to create a 5x5 mean filter and apply it to
    # our image. In the lab, you'll need to write your own convolution code (using
    # "for" loops, but you can use Pillow's code to check that your answer is correct.
    # Since the input is a color image, Pillow applies the filter to each
    # of the three color planes (R, G, and B) independently.
    # box = [1] * 25
    # result = color_im.filter(ImageFilter.Kernel((5, 5), box, sum(box)))
    # result.show()