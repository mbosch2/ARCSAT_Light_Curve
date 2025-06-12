import numpy
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.stats import sigma_clip
from astropy.visualization import ImageNormalize, LinearStretch, ZScaleInterval
from astroscrappy import detect_cosmics
from astropy.stats import sigma_clipped_stats
from photutils.aperture import CircularAperture
from photutils.aperture import aperture_photometry
from photutils.aperture import CircularAnnulus
from photutils.aperture import ApertureStats
from photutils.profiles import RadialProfile
from photutils.centroids import centroid_1dg

def create_median_bias(bias_list, median_bias_filename):
    """This function must:

    - Accept a list of bias file paths as bias_list.
    - Read each bias file and create a list of 2D numpy arrays.
    - Use a sigma clipping algorithm to combine all the bias frames using
      the median and removing outliers outside 3-sigma for each pixel.
    - Save the resulting median bias frame to a FITS file with the name
      median_bias_filename.
    - Return the median bias frame as a 2D numpy array.

    """
    #Reading in the data and adding it into an empty list
    #We use a loop and make sure to take only part of the images to not crash the kernel
    bias_images = []
    for i in bias_list:
        bias_data = fits.getdata(i)
        bias_images.append(bias_data.astype('f4'))
    #We convert the array to a 3D numpy array, then apply sigma_clip with sigma 3

    bias_images_3d = numpy.array(bias_images)
    #bias_mean_2d = numpy.mean(bias_images_3d, axis=0)
    #median_bias = bias_mean_2d[1536:2560, 1536:2560]
    bias_images_masked = sigma_clip(bias_images_3d, cenfunc='median', sigma=3, axis=0)
    #We combine the layers into one bias image using a mean function
    median_bias = numpy.ma.mean(bias_images_masked, axis=0).filled(fill_value=0)

    # This is a placeholder for the actual implementation.
    #median_bias = None

    # Here is some code to create a new FITS file from the resulting median bias frame.
    # You can replace the header with something more meaningful with information.
    primary = fits.PrimaryHDU(data=median_bias, header=fits.Header())
    hdul = fits.HDUList([primary])
    hdul.writeto(median_bias_filename, overwrite=True)

  return median_bias
