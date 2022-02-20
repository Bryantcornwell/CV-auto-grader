
# Assignment #1 Report
Group Members: Deepak Duggirala, Bryant Cornwell, Li Sun

## Abstract
As a widely used grading technology, the generation and recognition of answer sheets improve the efficiency and decrease the human error. It can be implemented by With multiple programming languages with full-fledged templates. However, we abandon flaring libraries and try to achieve a fairly robust model only with basic mathmetic packages and pillow library, so that laying the ground of learning of image encryption/decryption, line detection, filterings, segmentation, etc.

## Introduction
With 5 options, A...E, per question and binary encryption, we use 5-digit binary array to represent the solutions. For extracting the solution area, we try methods of grid overlay, othogonal lines, and vertical patches. Besides, we detect the occurence of handwitten letter via density of pixels.

## Methods
### Inject.py
Run the code from the terminal using the following format on the linux server and ensure to type the file names for the  '< >' desired arguments below:

    python3 inject.py <image_name.jpg> <key_name.txt> <injected_output.jpg>
The first task of inject.py was to open the image using the PIL library and create a list of each line of the answer key file. The numbers and special characters were then removed to generate a list of answer. The first idea of encrypting the answer key was to use character encoding. However, failed to find an accurate/robust way to read decrypt the answer key without using other computer vision libraries.

From there the team discussed ways of implementing a QR-code and bar code using information and ideas from Wikipedia [1]. Since bar and QR codes use black and white pixels, we determined that we would need to encode the answers using binary operations. To encode all 31 answer options, it required five pixels per question (2^5 = 32). The group decided that the encoded answers would need be scaled up to avoid noise. 

There are 85x5=425 total pixels, so a 17x25 matrix to fit into the QR code was used to create a better representation. An answer dictionary was created and utilized to convert the answers to a 5-digit binary string. This binary list was concatenated to a single string then to a 17x25 matrix of int values. From here, the matrix was scaled up to a 34x50 matrix by converting a single pixel to a 2x2 super-pixel. 

The QR code was developed based on the 34x50 matrix as seen in Figure #1; where the gray portion of the image is where the encoded answer matrix would be placed. The scaled matrix is then placed within the QR code boundary, and all values were multiplied by 255 to generate white pixels. Figure #2 shows an example of a QR code for the a-27 test answer key. The “Image.fromarray()” function was used to convert the NumPy array into an image object [2]. To put the encoded image object on the required input image, the “ImageDraw.Draw().bitmap()” function was used at first to draw the binary image on the required input image, but was removed as the resulting QR code pixels were inverted. Instead, the “Image.paste()” function was utilized to place and position the image object on the desired image [3]. The injected image was saved to a file to conclude the program.
#### Figure 1. QR code boundary.
![QRboundary.png](testBry/QRboundary.png)
#### Figure 2. QR code example.
![QRexample.png](testBry/QRexample.png)

### Extract.py
Run the code from the terminal using the following format on the linux server and ensure to type the file names for the  '< >' desired arguments below:

    python3 extract.py <image_name.jpg> <output.txt> 
The first task of extract.py was to open the image using the PIL library and create a dictionary to decrypt the binary answers. The image was cropped to a small region using the relative location of where the QR code was injected. 

The first approach to detect the QR code did not go as expected. A convolution was performed on the cropped region using a kernel similar to the three boundary boxes. The idea was to find the center coordinates of the three boundary boxes using of the brightest value after convolution. Figure #3 is the result of this experiment.

The next approach at QR code detection was a pixel scanning method. A check list was generated based on a segment of pixel values that ranged across the center of the QR boundary box, and used to compare against a list of similar length of scanned values. To deal with noise during scanning, each pixel is replaced by 255 or 0 if the original value was less than 150 or not. The values of pixels in each row of the image are saved to a list and compared against the boundary box check list. The x and y coordinates are saved in a point list each time the previous values in the scanned row list and check list values match. These points correspond to the pixel located at the middle-right of the boundary box.

The height and width of the binary matrix was found based on the points in the point list. The values were extracted, altered 255 values to 1, and added to list as a string type using the detected matrix boundaries. Every five characters are combined to generate a list used to decrypt the binary answer. During the decryption, the question/answer number is concatenated with the corresponding answer. The answer key list was combined with newline characters (‘\n’), written, and saved to the output file to conclude the program.
#### Figure 3. Convolution performed on a QR code example.
![QRconvolution.png](testBry/QRconvolution.png)
## Results

 
 
## Discussion


## Conclusions



## Acknowledges
### Bryant Cornwell 
Wrote a majority of the code for inject.py and extract.py, and contributed to the research and ideas for developing the QR code. Also provided partial starter code and ideas for tackling the Hough Transform utilizing methods and ideas from Wikipedia [4]. For the report, Wrote the inject.py and extract.py sub-sections within the Methods section. 
### Deepak Duggirala
Provided initial QR code detection approach. Wrote the grade.py. Details are shown in grade-report.md. Wrote the whole grade-report.md.
### Li Sun
Contributed to the research and ideas for developing the QR code. Helped to test codes on burrow.luddy.indiana.edu. Wrote the abstract, introduction, .... parts of this report.

## References
[1] https://en.wikipedia.org/wiki/QR_code

[2] https://pillow.readthedocs.io/en/stable/reference/Image.html?highlight=fromarray#PIL.Image.fromarray

[3] https://pillow.readthedocs.io/en/stable/reference/Image.html?highlight=paste#PIL.Image.Image.paste

[4] https://en.wikipedia.org/wiki/Hough_transform#Kernel-based_Hough_transform_(KHT)


