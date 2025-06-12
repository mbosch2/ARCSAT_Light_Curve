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
def create_median_dark(dark_list, bias_filename, median_dark_filename):
    """
    - Accepts a list of dark file paths to combine as dark_list.
    - Accepts a median bias frame filename as bias_filename (the one you created using
      Bias.py).
    - Reads all the images in dark_list and create a list of 2D numpy arrays.
    - Reads the bias frame.
    - Subtracts the bias frame from each dark image.
    - Divides each dark image by its exposure time so that you get the dark current
      per second.
    - Uses a sigma clipping algorithm to combine all the bias-corrected dark frames
      using the median and removes outliers outside 3-sigma for each pixel.
    - Saves the resulting dark frame to a FITS file with the name median_dark_filename.
    - Returns the median dark frame as a 2D numpy array.

    """
    dark_images=[]
    bias = fits.getdata(bias_filename)
    for i in dark_list:
        dark = fits.open(i)
        dark_data = dark[0].data.astype('f4')
        expt = dark[0].header['EXPTIME']
        expt_div = expt if expt != 0 else 1
        dark_data_no_bias = (dark_data - bias)/expt
        dark_images.append(dark_data_no_bias)
        
    dark_masked = sigma_clip(dark_images, cenfunc='median', sigma=3, axis=0)
        
    median_dark = numpy.ma.mean(dark_masked, axis=0).filled(fill_value=0)
    

    # See code in create_median_bias for how to create a new FITS file
    # from the resulting median dark frame.
    primary = fits.PrimaryHDU(data=median_dark, header=fits.Header())
    hdul = fits.HDUList([primary])
    hdul.writeto(median_dark_filename, overwrite=True)

    return median_dark
