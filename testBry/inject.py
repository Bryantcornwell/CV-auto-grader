from PIL import Image
import sys
import numpy as np


if __name__ == '__main__':
    # Load an image
    im = Image.open(sys.argv[1])

    # Get list of strings from answer key txt file.
    with open(sys.argv[2], 'r') as txt_file:
        lines = txt_file.readlines()
    remove = ' 0123456789\n'
    answer_list = []
    for line in lines:
        for c in remove:
            line = line.replace(c, "")
        answer_list.append(line)
    print("\nAnswer key:\n", answer_list, "\nNumber of Questions/Answer pairs:", len(answer_list))

    # Since we need at least 31 options for answers. We will need 5 binary pixels to encode one answer. (2^5 = 32)
    answer_dict = {'A': '00000', 'B': '00001', 'C': '00010', 'D': '00011', 'E': '00100', 'AB': '00101', 'AC': '00110',
                   'AD': '00111', 'AE': '01000', 'BC': '01001', 'BD': '01010', 'BE': '01011', 'CD': '01100',
                   'CE': '01101', 'DE': '01110', 'ABC': '01111', 'ABD': '10000', 'ABE': '10001', 'ACD': '10010',
                   'ACE': '10011', 'ADE': '10100', 'BCD': '10101', 'BCE': '10110', 'BDE': '10111', 'CDE': '11000',
                   'ABCD': '11001', 'ABCE': '11010', 'ABDE': '11011', 'ACDE': '11100', 'BCDE': '11101',
                   'ABCDE': '11110'}
    print("\nDictionary length:", len(answer_dict))
    binary_list = []
    for key in answer_list:
        value = answer_dict[key]
        #print(key, value)
        binary_list.append(value)
    print("\nEncoded Answer key:\n", binary_list)
    binary_str = "".join(binary_list)
    print("\nBinary string:\n", binary_str, "\nNumber of pixels to encode:", len(binary_str))


    # Build something I can read with the data from the answers
    bi_matrix = np.array([int(x) for x in binary_str]).reshape((17,25))
    #print(bi_matrix)
    scale = 2
    scaled_matrix = np.ones((bi_matrix.shape[0]*scale, bi_matrix.shape[1]*scale))
    for x in range(bi_matrix.shape[0]):
        for y in range(bi_matrix.shape[1]):
            scaled_matrix[x*scale:x*scale+scale, y*scale:y*scale+scale] = bi_matrix[x, y]

    # Form the QR/bar code with a matrix.
    inject = np.ones((36, 74), dtype=np.uint8)
    (inject[0:36, 1:11], inject[0:36, 63:73]) = (0, 0)
    (inject[4:8, 4:8], inject[4:8, 66:70], inject[28:32, 4:8]) = (1, 1, 1)
    (inject[5:7, 5:7], inject[5:7, 67:69], inject[29:31, 5:7]) = (0, 0, 0)
    # Add the matrix to the center of the boundary. Bitmap inverts the color.
    inject[1:35, 12:62] = scaled_matrix
    # The fromarray() function did not read binary, so multiplied matrix by 255.
    bi_im = Image.fromarray(inject*255)
    #bi_im.show()

    # Paste the QR/bar code on image and save.
    im.paste(bi_im, (int(11 * im.width / 13), int(19 * im.height / 20)))
    im.save(sys.argv[3])
    print("Injected image saved as", sys.argv[3]+'".')
