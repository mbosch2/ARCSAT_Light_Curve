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

"""
Once you have the reduced science images, you must loop all of them through this function to make the light curve
For example:
for i in science_list:
    do_aperture_photometry(i)
"""


aperture_sums=[]
times=[]

def do_aperture_photometry(
    image
):
"""
This function takes an image as an input and find the flux minus background of the target
It also finds the time the image was taken
It adds both of these to empty lists for graphing
"""
    sci_data = fits.open(image)
    sci_proc_data = sci_data[0].data.astype('f4')

    times.append(sci_data[0].header['Date-OBS'])
    #print(sci_data[0].header['Date-OBS'])
    
    # Select a blank region of the image
    data_blank = sci_proc_data[100:200, 900:1000]
    
    # Calculate the mean, median and standard deviation of the blank region
    mean, median, std = sigma_clipped_stats(data_blank, sigma=3.0)
    #print(f'Mean: {mean:.2f}, Median: {median:.2f}, Std: {std:.2f}')

    # Run DAOStarFinder
    daofind = DAOStarFinder(fwhm=5.0, threshold=5*std)
    sources = daofind(sci_proc_data - median)

    # Centroids of the source from DAOStarFinder
    xd = 512
    yd = 509
    
    # Get a small region around the source
    x0 = int(xd)
    y0 = int(yd)
    data = sci_proc_data[y0-10:y0+10, x0-10:x0+10]
    
    # Calculate the centroid using the 1D Gaussian algorithm.
    # It's important to remove the median background!
    xc, yc = centroid_1dg(data - median)

    # This centroid is with respect to the region we selected, so we need to add the offset
    xc += (x0 - 10)
    yc += (y0 - 10)
    
    # Define the annulus
    annulus = CircularAnnulus((xc, yc), r_in=10, r_out=15)

    annulus_stats = ApertureStats(sci_proc_data, annulus)
    back = annulus_stats.median
    std = annulus_stats.std

    aperture = CircularAperture((xc, yc), r=10)
    
    phot_table = aperture_photometry(sci_proc_data, aperture)
    flux = phot_table['aperture_sum'][0]
    aperture_area = aperture.area_overlap(sci_proc_data)
    flux_no_back = flux - back * aperture_area

    # Perform aperture photometry
    #phot_table = aperture_photometry(ccd37_proc_data - median, aperture)
    #print(phot_table)

    return aperture_sums.append(flux_no_back)
