#!/usr/bin/env python3

import math

from PIL import Image as Image

# NO ADDITIONAL IMPORTS ALLOWED!


def get_pixel(image, x, y, out_bound=None):
    '''
    Returns the value at pixel (x,y).

    Row-major formula: M*y +x, where
    M is the width

    Parameters
    ----------
        image : dictionary
            Image to be analyzed

        x : int
            X-coord 

        y : int
            Y-coord

        out_bound : string
            * "zero" gives out bound pixels w/ value 0
            * "extend" gives out bound pixels w/ value of the boundary pixels
            * "wrap" gives out bound pixels w/ value of the original pattern

    Returns
    -------
        pixel : float
            Pixel between 0 and 255 at
            that given location at the image
    '''
    M = image['width']
    N = image['height']

    # if the pixel is within the image

    if not (x<0 or x>M-1) and not (y<0 or y>N-1): 
        return image['pixels'][M*y + x]

    # if the pixel is out of bound

    else:

        # if out_bound mode is "zero"
        if out_bound == "zero": 
            return 0

        elif out_bound == "wrap":
            
            # see in which position
            # it would correspond
            x_ = x % M
            y_ = y % N

            return image['pixels'][M*y_+x_]

        elif out_bound == "extend": 
            
            # upper left corner
            if x <=0 and y <= 0:  return image['pixels'][M*0 + 0]
            
            # upper right corner
            elif x >= M-1 and y<=0: return image['pixels'][M*0 + M-1]

            # bottom left corner
            elif x <= 0 and y>= N-1: return image['pixels'][M*(N-1) + 0]

            # bottom right corner
            elif x >= M-1 and y>= N-1: return image['pixels'][M*(N-1) + M-1]

            # either x or y lie within the image boundaries
            else:
                
                # upper part
                if y<=0: return image['pixels'][M*0 + x]

                # right part
                elif x>=M-1: return image['pixels'][M*y + M-1]

                # left part
                elif x<=0: return image['pixels'][M*y + 0]

                # bottom part
                elif y>= N-1: return image['pixels'][M*(N-1) + x]

def set_pixel(image, x, y, c):
    '''
    Changes the value at pixel (x,y) to c.
    Row-major formula: M*y +x, where
    M is the width of the Matrix

    Parameters
    ----------
        image : dictionary
            Image to be analyzed

        x : int
            X-coord 

        y : int
            Y-coord

        c : int
            New value t

    Returns
    -------
        None
    '''
    M = image['width']

    image['pixels'][M*y + x] = c

def apply_per_pixel(image, func):
    '''
    Apply a function to every pixel

    Parameters
    ----------
        image : dict
            Image to be modified

        func : function object
            Function to be applied to every pixel

    Returns
    -------
        result : dict
            Returns modified copy of original image 
    '''

    result = {
        'height': image['height'],
        'width': image['width'],
        'pixels': image['pixels'],
    }
    for y in range(image['height']):
        for x in range(image['width']):
            color = get_pixel(image, x, y)
            newcolor = func(color)
            set_pixel(result, x, y, newcolor)
    return result

def inverted(image):
    '''
    Inverts the image

    Parameters
    ----------
        image : dictionary
            Image to be inverted

    Returns
    -------
        inverted_image : dictionary
    '''
    inverted_image = {
        'height': image['height'],
        'width': image['width'],
        'pixels': image['pixels'][:],
    }
    inverted_image = apply_per_pixel(inverted_image, lambda c: 255-c)

    return inverted_image

def contrast(image):
    
    minIntensity = 255
    maxIntensity = 0
    
    M,N = image['width'], image['height']
    
    for x in range(M):
        for y in range(N):
        
            minIntensity = min(minIntensity, get_pixel(image, x,y))
            maxIntensity = max(maxIntensity, get_pixel(image,x,y))
    
    maxIntensity = 0.95 * maxIntensity
    minIntensity = 0.95 * minIntensity
    def contr(pixel):
        
        return int(255*((pixel - minIntensity) /(maxIntensity - minIntensity)))
    
    return apply_per_pixel(image, contr)
# HELPER FUNCTIONS    

def correlate(image, kernel, boundary_behavior):
    """
    Compute the result of correlating the given image with the given kernel.
    `boundary_behavior` will one of the strings 'zero', 'extend', or 'wrap',
    and this function will treat out-of-bounds pixels as having the value zero,
    the value of the nearest edge, or the value wrapped around the other edge
    of the image, respectively.

    if boundary_behavior is not one of 'zero', 'extend', or 'wrap', return
    None.

    Otherwise, the output of this function should have the same form as a 6.009
    image (a dictionary with 'height', 'width', and 'pixels' keys), but its
    pixel values do not necessarily need to be in the range [0,255], nor do
    they need to be integers (they should not be clipped or rounded at all).

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.

    Kernel
    ------
        kernel : dict
            Dictionary in the following form:
            {
                'width' : int,
                'height' : int,
                'pixels' : list
            }
    """
    # Check boundary behavior validation
    if boundary_behavior not in ['zero', 'wrap', 'extend']: 
        return None

    def apply_kernel_per_pixel(image, copy, kernel, x, y, boundary_behavior):
        '''
        Apply kernel to each a pixel
        in the copied version of 
        original image

        Parameters
        ---------
            image : dict
                Original image in the form:

                {
                'width' : int,
                'height' : int,
                'pixels' : list
                }

            copy : dict
                Copied image to be modified in the form:

                {
                'width' : int,
                'height' : int,
                'pixels' : list
                }

            kernel : dict
                Kernel to be correlated with image in the form:

                {
                'width' : int,
                'height' : int,
                'pixels' : list
                }

            x : int
                x-coordinate for the pixel in row-major form

            y : int
                y-coordinate for the pixel in the row-major form

            boundary_behavior : string
                * "zero" gives out bound pixels w/ value 0
                * "extend" gives out bound pixels w/ value of the boundary pixels
                * "wrap" gives out bound pixels w/ value of the original pattern

        Returns
        -------
            None
        '''
        Mk = kernel['width']
        M = correlate_image['width']
        new_value = 0

        half = Mk//2

        for yk in range(kernel['height']):
            for xk in range(kernel['width']):
        
                new_value += (get_pixel(image,x+xk-half, y+yk-half, boundary_behavior) * kernel['pixels'][Mk*yk + xk])

        copy['pixels'][M*y + x] = new_value

    # Init variables
    correlate_image = {
        'width' : image['width'],
        'height' : image['height'],
        'pixels' : [None for _ in image['pixels']]
    }

    # for each pixel in the original image
    for y in range(image['height']):
        for x in range(image['width']):

            apply_kernel_per_pixel(image, correlate_image,kernel, x,y, boundary_behavior)

    return correlate_image

def round_and_clip_image(image):
    """
    Given a dictionary, ensure that the values in the 'pixels' list are all
    integers in the range [0, 255].

    All values should be converted to integers using Python's `round` function.

    Any locations with values higher than 255 in the input should have value
    255 in the output; and any locations with values lower than 0 in the input
    should have value 0 in the output.
    """
    
    # iterate over all pixels values
    for i in range(len(image['pixels'])):
        
        # if pixel is < 0
        if image['pixels'][i] < 0: 
            image['pixels'][i] = 0
        
        # if pixel > 255
        elif image['pixels'][i] > 255: 
            image['pixels'][i] = 255

        # if 0 <= pixel <= 255, cast round in it
        image['pixels'][i] = round(image['pixels'][i])

    return image

# FILTERS

def blurred(image, n, boundary_behavior='extend'):
    """
    Return a new image representing the result of applying a box blur (with
    kernel size n) to the given input image.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    # first, create a representation for the appropriate n-by-n kernel (you may
    # wish to define another helper function for this)
    def get_blur_kernel(n):
        '''
        Returns kernel of size n x n in which
        each cell has value 1/(n^2)

        Parameters
        ----------
            n : int
                Size of kernel

        Returns
        -------
            kernel : dict
                Kernel for blurred
        '''
        val = 1/(n**2)

        kernel = {
            'width' : n,
            'height' : n,
            'pixels' : [val for _ in range(n**2)]
        }

        return kernel

    # then compute the correlation of the input image with that kernel using
    # the 'extend' behavior for out-of-bounds pixels
    result = correlate(image, get_blur_kernel(n), boundary_behavior)

    # and, finally, make sure that the output is a valid image (using the
    # helper function from above) before returning it.
    round_and_clip_image(result)

    return result

def sharpened(image, n):
    '''
    Returns a sharpened version of image
    Does not modify the given parameters

    Parameters
    ----------
        image : dict
            Dictionary representing the images

        n : int
            Size of the blur kernel

    Returns
    -------
        sharpened_image : dict
            Dictionary representing sharpened image
    '''
    unsharp_mask = blurred(image, n)

    sharpened_image = {
        'width' : image['width'],
        'height' : image['height'],
        'pixels' : [2*i - b for (i,b) in zip(image['pixels'],unsharp_mask['pixels'])]
    }

    round_and_clip_image(sharpened_image)

    return sharpened_image

def edges(image):
    '''
    Runs edge-detection algorithm in image
    Does not modify given parameters

    Parameters
    ----------
        image : dict
            Original image

    Returns
    -------
        edge_image : dict
            Edge-detected image
    '''

    # init variables
    Kx = {
        'width': 3,
        'height': 3,
        'pixels' : [-1, 0, 1,
                    -2, 0, 2,
                    -1, 0, 1]
    }

    Ky = {
        'width':3,
        'height':3,
        'pixels':[-1, -2, -1,
                  0, 0, 0,
                  1, 2, 1]
    }

    # get correlated image
    O_x = correlate(image, Kx,'extend')
    O_y = correlate(image, Ky, 'extend')

    # merging kernels
    edge_image = {
        'width' : image['width'],
        'height' : image['height'],
        'pixels' : [math.sqrt(x**2 + y**2) for (x,y) in zip(O_x['pixels'], O_y['pixels'])]
    }

    # validating image
    round_and_clip_image(edge_image)

    return edge_image

# COLOR FILTERS

def color_filter_from_greyscale_filter(filt):

    """
    Given a filter that takes a greyscale image as input and produces a
    greyscale image as output, returns a function that takes a color image as
    input and produces the filtered color image.
    """

    def color_layers(image):
        '''
        Returns the R, G, B image of the original image
        
        Parameters
        ----------
            image : dict
                Image to be analyzed

        Returns
        -------
            R : dict
                Dictionary containing the Red values for pixel

            G : dict
                Dictionary containing the Green values for pixel

            B : dict
                Dictionary containing the Blue values for pixel
        '''
        R = {
            'width' : image['width'],
            'height' : image['height'],
            'pixels' : [r for (r,_,_) in image['pixels']]
        }

        G = {
            'width' : image['width'],
            'height' : image['height'],
            'pixels' : [g for (_,g,_) in image['pixels']]
        }

        B = {
            'width' : image['width'],
            'height' : image['height'],
            'pixels' : [b for (_,_,b) in image['pixels']]
        }

        return R,G,B
    
    def color_filt(image):
        # get layers
        R,G,B = color_layers(image)

        # apply filter
        R_f, G_f, B_f = filt(R), filt(G), filt(B)

        # merge R,G,B
        return {
            'width' : image['width'],
            'height' : image['height'],
            'pixels' : [(r,g,b) for (r,g,b) in zip(R_f['pixels'], G_f['pixels'], B_f['pixels'])]
        }
    
    return color_filt

def make_blur_filter(n):
    '''
    Returns a function that applies 
    blur filter to the image

    Parameters
    ----------
        n : int
            Size of kernel to be blurred

    Returns 
    -------
        blur_grey : function object
            Function that accepts the image
            as parameters and returns
            its blurred version
    '''

    def blur_grey(image):
        '''
        Blurs the image

        Parameters
        ----------
            image : dict
                Image to be blurred

        Returns
        -------
            Copy of the blurred image
        '''

        return blurred(image,n)

    return blur_grey

def make_sharpen_filter(n):
    '''
    Returns a function that applies 
    sharpen filter to the image

    Parameters
    ----------
        n : int
            Size of kernel to be sharpenedd

    Returns 
    -------
        sharpen_grey : function object
            Function that accepts the image
            as parameters and returns
            its sharpened version
    '''
    def sharpen_grey(image):
        '''
        Sharpens the image

        Parameters
        ----------
            image : dict
                Image to be sharpened

        Returns
        -------
            Sharpened copy of the image
        '''

        return sharpened(image, n)
    
    return sharpen_grey

def filter_cascade(filters):
    """
    Given a list of filters (implemented as functions on images), returns a new
    single filter such that applying that filter to an image produces the same
    output as applying each of the individual ones in turn.
    """

    def apply_filters(image):
        '''
        Returns a function that applies all filters to the image

        Parameters
        ----------
            image : dict
                Image to be modified

        Returns
        -------
            Modified image
        '''
        res = image

        for filter in filters:
            new = filter(res)
            res = new

        return res

    return apply_filters

def threshold_grey(image, threshold, invert=False):

    res = {
        'width' : image['width'],
        'height' : image['height'],
        'pixels' : image['pixels']
    }

    for i in range(len(res['pixels'])):

        if res['pixels'][i] <= threshold:
            res['pixels'][i] = 0

        else:
            res['pixels'][i] = 255

    if invert:
        return inverted(res)

    return res
# HELPER FUNCTIONS FOR LOADING AND SAVING IMAGES  

def load_greyscale_image(filename):
    """
    Loads an image from the given file and returns an instance of this class
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_greyscale_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()
        if img.mode.startswith('RGB'):
            pixels = [round(.299 * p[0] + .587 * p[1] + .114 * p[2])
                      for p in img_data]
        elif img.mode == 'LA':
            pixels = [p[0] for p in img_data]
        elif img.mode == 'L':
            pixels = list(img_data)
        else:
            raise ValueError('Unsupported image mode: %r' % img.mode)
        w, h = img.size
        return {'height': h, 'width': w, 'pixels': pixels}


def save_greyscale_image(image, filename, mode='PNG'):
    """
    Saves the given image to disk or to a file-like object.  If filename is
    given as a string, the file type will be inferred from the given name.  If
    filename is given as a file-like object, the file type will be determined
    by the 'mode' parameter.
    """
    out = Image.new(mode='L', size=(image['width'], image['height']))
    out.putdata(image['pixels'])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


def load_color_image(filename):
    """
    Loads a color image from the given file and returns a dictionary
    representing that image.

    Invoked as, for example:
       i = load_color_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img = img.convert('RGB')  # in case we were given a greyscale image
        img_data = img.getdata()
        pixels = list(img_data)
        w, h = img.size
        return {'height': h, 'width': w, 'pixels': pixels}


def save_color_image(image, filename, mode='PNG'):
    """
    Saves the given color image to disk or to a file-like object.  If filename
    is given as a string, the file type will be inferred from the given name.
    If filename is given as a file-like object, the file type will be
    determined by the 'mode' parameter.
    """
    out = Image.new(mode='RGB', size=(image['width'], image['height']))
    out.putdata(image['pixels'])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


if __name__ == '__main__':
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place for
    # generating images, etc.
    
    #----------Problem 3.3-----------
    # bluegill = load_greyscale_image('6009/lab01/test_images/bluegill.png')
    # g_bluegill = inverted(bluegill)
    # save_greyscale_image(g_bluegill,'g_bluegill.png')  
      
    #---------Problem 4.4------------
    # kernel = {
    #     'width':13,
    #     'height':13,
    #     'pixels':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #               1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    # }


    # pigbird = load_greyscale_image('6009/lab01/test_images/pigbird.png')

    # pigbird_zero = round_and_clip_image(correlate(pigbird, kernel, 'zero'))
    # pigbird_wrap = round_and_clip_image(correlate(pigbird, kernel, 'wrap'))
    # pigbird_extend = round_and_clip_image(correlate(pigbird, kernel, 'extend'))

    # save_greyscale_image(pigbird_zero, "pigbird_zero_def.png")
    # save_greyscale_image(pigbird_wrap, "pigbird_wrap_def.png")
    # save_greyscale_image(pigbird_extend, "pigbird_extend_def.png")
    
    #-------Problem 5.1---------
    # cat = load_greyscale_image('6009/lab01/test_images/cat.png')

    # cat_blur = blurred(cat, 13)
    # cat_blur_zero = blurred(cat, 13, 'zero')
    # cat_blur_wrap = blurred(cat, 13, 'wrap')

    # save_greyscale_image(cat_blur,'cat_blur1.png') 
    # save_greyscale_image(cat_blur_zero, 'cat_blur_zero.png')
    # save_greyscale_image(cat_blur_wrap, 'cat_blur_wrap.png')
    
    #--------Problem 5.2---------
    # python = load_greyscale_image("6009/lab01/test_images/python.png")

    # sharp_python = sharpened(python, 11)

    # save_greyscale_image(sharp_python, 'sharp_python.png')
    
    #--------Problem 6.1----------
    # construct = load_greyscale_image('6009/lab01/test_images/construct.png')

    # edges_construct = edges(construct)

    # save_greyscale_image(edges_construct, 'edges_construct.png')

    #--------Problem 9.1----------
    # cat = load_color_image('6009/lab01/test_images/cat.png')

    # color_inverted = color_filter_from_greyscale_filter(inverted)

    # inverted_color_cat = color_inverted(cat)

    # save_color_image(inverted_color_cat, 'inverted_color_cat.png')

    #---------Problem 9.3----------
    # python = load_color_image('6009/lab01/test_images/python.png')

    # blur_grey = make_blur_filter(n=9)

    # blur_rgb = color_filter_from_greyscale_filter(blur_grey)

    # python_color_blurred = blur_rgb(python)

    # save_color_image(python_color_blurred, 'python_color_blurred.png')

    # sparrowchick = load_color_image('6009/lab01/test_images/sparrowchick.png')

    # sharpen_grey = make_sharpen_filter(n=7)

    # sharpen_rgb = color_filter_from_greyscale_filter(sharpen_grey)

    # sparrowchick_color_sharpened = sharpen_rgb(sparrowchick)

    # save_color_image(sparrowchick_color_sharpened, 'sparrowchick_color_sharpened.png')

    #----------Problem 10.1---------
    # filter1 = color_filter_from_greyscale_filter(edges)
    # filter2 = color_filter_from_greyscale_filter(make_blur_filter(5))
    # filt = filter_cascade([filter1, filter1, filter2, filter1])

    # frog = load_color_image('6009/lab01/test_images/frog.png')

    # filt_frog = filt(frog)

    # save_color_image(filt_frog, 'filt_frog.png')

    #---------Creative Section 1--------
    # tree = load_color_image('6009/lab01/test_images/tree.png')

    # threshold_grey = make_threshold_filter(128)

    # threshold_rgb = color_filter_from_greyscale_filter(threshold_grey)

    # threshold_tree = threshold_rgb(tree)
 
    # save_color_image(threshold_tree, 'threshold_tree3.png')

    #----------Creative Section 2---------
    # chess = load_greyscale_image('6009/lab01/test_images/chess.png')

    # grey_chess = threshold_grey(chess, 128)

    # inv_grey_chess = threshold_grey(chess, 128, invert=True)

    # save_greyscale_image(grey_chess, 'grey_chess4.png')
    # save_greyscale_image(inv_grey_chess, 'inv_grey_chess4.png')
    
    # felpudo = load_color_image('/Users/thiagodesouza/Codes/6009/lab01/felpudo_ori.jpeg')
    
    # filter1 = color_filter_from_greyscale_filter(edges)
    # filter2 = color_filter_from_greyscale_filter(make_blur_filter(5))
    # filt = filter_cascade([filter1, filter1, filter2, filter1])
    
    # felpudo = filt(felpudo)
    
    # save_color_image(felpudo, 'felpudo_mod.jpeg', mode='JPEG')
    twocats = load_color_image("/Users/thiagodesouza/Codes/6009/lab01/test_images/twocats.png")
    
    contrast_color = color_filter_from_greyscale_filter(contrast)
    
    twocats = contrast_color(twocats)
    
    save_color_image(twocats, 'twocats_mod.png')
    
    
    
