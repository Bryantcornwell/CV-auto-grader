from PIL import Image
import sys
import numpy as np


if __name__ == '__main__':
    # Load the injected image
    im = Image.open(sys.argv[1]).convert('L')

    # Since we need at least 31 options for answers. We will need 5 binary pixels to encode one answer. (2^5 = 32)
    answer_dict = {'00000': 'A', '00001': 'B', '00010': 'C', '00011': 'D', '00100': 'E', '00101': 'AB', '00110': 'AC',
                   '00111': 'AD', '01000': 'AE', '01001': 'BC', '01010': 'BD', '01011': 'BE', '01100': 'CD',
                   '01101': 'CE', '01110': 'DE', '01111': 'ABC', '10000': 'ABD', '10001': 'ABE', '10010': 'ACD',
                   '10011': 'ACE', '10100': 'ADE', '10101': 'BCD', '10110': 'BCE', '10111': 'BDE', '11000': 'CDE',
                   '11001': 'ABCD', '11010': 'ABCE', '11011': 'ABDE', '11100': 'ACDE', '11101': 'BCDE',
                   '11110': 'ABCDE'}
    #kernel = np.zeros((12, 10), dtype=np.uint8)
    #(kernel[4:8, 3:7], kernel[5:7, 4:6]) = (1, 0)

    # Determine the area of the form that the QR code should be located within.
    win_width, win_height = int(11 * im.width / 13), int(19 * im.height / 20)
    test_space = im.crop((win_width-25, win_height-15, win_width+100, win_height+50))
    # Determine the location of the QR code by comparing lists of pixel values
    check_list = [0, 0, 0, 255, 0, 0, 255, 0, 0, 0]
    pixel_list = []
    for x in range(test_space.width):
        a_list = []
        for y in range(test_space.height):
            p = test_space.getpixel((x, y))
            if p < 150:
                p = 0
                test_space.putpixel((x, y), p)
            else:
                p = 255
                test_space.putpixel((x, y), p)
            a_list.append(p)
            if a_list[-10:] == check_list:
                pixel_list.append((x, y))
            else:
                pass
    #print(pixel_list)
    #print((pixel_list[0][1] + 12, pixel_list[0][0] - 14))
    #print((pixel_list[0][1] + 12, pixel_list[0][0] + 19))
    #print((pixel_list[0][1] + 61, pixel_list[0][0] - 14))
    #print((pixel_list[0][1] + 61, pixel_list[0][0] + 19))
    #test_space.putpixel((pixel_list[0][1] + 12, pixel_list[0][0] - 14), 150)
    #test_space.putpixel((pixel_list[0][1] + 12, pixel_list[0][0] + 19), 150)
    #test_space.putpixel((pixel_list[0][1] + 61, pixel_list[0][0] - 14), 150)
    #test_space.putpixel((pixel_list[0][1] + 61, pixel_list[0][0] + 19), 150)
    #test_space.show()
    #print(test_space.getpixel((pixel_list[0][1] + 12, pixel_list[0][0] - 14)))
    # Use the location of the first point to determine the encoded matrix.
    mat_width = (pixel_list[0][1] + 61) - (pixel_list[0][1] + 12)
    mat_height = (pixel_list[0][1] + 19) - (pixel_list[0][1] - 14)
    # Convert the 2x2 pixel matrix to a single pixel matrix.
    mat_values = []
    for h in range(16, mat_height + 16, 2):
        for w in range(37, mat_width+37, 2):
            if test_space.getpixel((w, h)) == 255:
                test_space.putpixel((w, h), 1)
            #test_space.putpixel((w, h), 150)
            mat_values.append(str(test_space.getpixel((w, h))))
    print(mat_values)
    # In order to use the dictionary to decode the answers, every five list values need to be combined.
    binary_list = []
    for i in range(85):
        binary_list.append("".join(mat_values[0+5*i:5 + 5*i]))
    print(binary_list)
    # Decode the answers using the dictionary and prepare the numbered output for each answer.
    answer_list = []
    print(answer_dict[binary_list[0]])
    count = 1
    for value in binary_list:
        key = answer_dict[value]
        answer_list.append(str(count)+" "+key)
        count += 1
    print(answer_list)
    # Create and save a text file for the answer key output.
    with open(sys.argv[2], 'w') as txt_file:
        txt_file.write("\n".join(answer_list))
    print("\nThe answer key is saved as", '"'+sys.argv[2]+'".')
