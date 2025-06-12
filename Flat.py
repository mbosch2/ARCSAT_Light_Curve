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
def create_median_flat(
    flat_list,
    bias_filename,
    median_flat_filename,
    dark_filename=None,
):
    """This function must:

    - Accepts a list of flat file paths to combine as flat_list. Make sure all
      the flats are for the same filter.
    - Accepts a median bias frame filename as bias_filename (the one you created using
      create_median_bias).
    - Reads all the images in flat_list and creates a list of 2D numpy arrays.
    - Read the bias frame.
    - Subtracts the bias frame from each flat image.
    - Optionally you can pass a dark frame filename as dark_filename and subtract
      the dark frame from each flat image 
    - Uses a sigma clipping algorithm to combine all the bias-corrected flat frames
      using the median and removing outliers outside 3-sigma for each pixel.
    - Creates a normalised flat divided by the median flat value.
    - Saves the resulting median flat frame to a FITS file with the name
      median_flat_filename.
    - Returns the normalised median flat frame as a 2D numpy array.

    """
    #add filter input for filter, then this works for any filter, default r'
    #even if everything is called r, it will work for anything, check how header works
    flats_r = []
    bias = fits.getdata(bias_filename)
    if dark_filename==None:
      dark=0
    else:
        dark=fits.getdata(dark_filename)
    for i in flat_list:
        flat = fits.open(i)
        if flat[0].header['FILTER'] == "R":
            expt = flat[0].header['EXPTIME']
            flats_r.append(flat[0].data.astype('f4') - bias - dark*expt )

    # Mask using sigma-clipping
    flats_r_masked = sigma_clip(flats_r, cenfunc='median', sigma=3, axis=0)

    # This is a placeholder for the actual implementation.
    combined = numpy.ma.median(flats_r_masked, axis=0).data
    flat_median = numpy.ma.median(combined)
    median_flat = combined/flat_median
    median_flat[combined == 0] = 1

    # See code in create_median_bias for how to create a new FITS file
    # from the resulting median flat frame.
    primary = fits.PrimaryHDU(data=median_flat, header=fits.Header())
    hdul = fits.HDUList([primary])
    hdul.writeto(median_flat_filename, overwrite=True)

    return median_flat
