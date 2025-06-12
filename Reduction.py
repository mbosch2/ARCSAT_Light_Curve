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

def reduce_science_frame(
    science_filename,
    median_bias_filename,
    median_flat_filename,
    median_dark_filename,
    output_dir=".",
    reduced_science_filename="reduced_science.fits",
):
    """This function:

    - Accepts a science frame filename as science_filename.
    - Accepts a median bias frame filename as median_bias_filename (the one you created
      using create_median_bias).
    - Accepts a median flat frame filename as median_flat_filename (the one you created
      using create_median_flat).
    - Accepts a median dark frame filename as median_dark_filename (the one you created
      using create_median_dark).
    - Reads all files.
    - Subtracts the bias frame from the science frame.
    - Subtracts the dark frame from the science frame. Remember to multiply the
      dark frame by the exposure time of the science frame. The exposure time can
      be found in the header of the FITS file.
    - Corrects the science frame using the flat frame.
    - Removes cosmic rays.
    - Saves the resulting reduced science frame to a FITS file with the filename
      reduced_science_filename.
    - Returns the reduced science frame as a 2D numpy array.

    """
  # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract the base filename (e.g., "file.fits") from the full path
    base_filename = os.path.basename(science_filename)
    
    # Construct full path for the output file
    output_path = os.path.join(output_dir, base_filename)
    
    science = fits.open(science_filename)
    science_data = science[0].data.astype('f4')

    #Subtract bias
    bias_data = fits.getdata(median_bias_filename).astype('f4')
    science_data_proc = science_data - bias_data

    # Get the exposure time from the header
    exptime = science[0].header['EXPTIME']

    # Subtract the dark current, scaled to the exposure time
    dark_data = fits.getdata(median_dark_filename).astype('f4')
    dark_data_scaled = dark_data * exptime
    science_data_proc -= dark_data_scaled

    # Divide by the normalised flat-field image
    flat_data = fits.getdata(median_flat_filename).astype('f4')
    science_data_proc /= flat_data

    # Generate the cosmic ray mask and a cleaned image
    mask, reduced_science = detect_cosmics(science_data_proc)
      # Save the final image to disk
    science_hdu = fits.PrimaryHDU(data=reduced_science, header=science[0].header)
    science_hdu.header['COMMENT'] = 'Final science image'
    science_hdu.header['BIASFILE'] = ('median_bias_filename', 'Bias image used to subtract bias level')
    science_hdu.header['DARKFILE'] = ('median_dark_filename', 'Dark image used to subtract dark current')
    science_hdu.header['FLATFILE'] = ('median_flat_filename', 'Flat-field image used to correct flat-fielding')
    science_hdu.writeto(output_path, overwrite=True)
    return reduced_science
