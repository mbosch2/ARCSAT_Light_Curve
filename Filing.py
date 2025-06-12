"""
This file contains code to sort a directory (ARCSAT_1 in this case) into different lists
This makes using the other files easier, but is not needed
"""
import os
directory_path = os.path.expanduser('ARCSAT_1')
file_list=[]
for file_name in os.listdir(directory_path):
    #Check if it is a file
  if os.path.isfile(os.path.join(directory_path, file_name)):
    file_list.append(file_name)
#We define empty lists for the files to get sorted into
bias_list=[]
dark_list=[]
flat_list=[]
science_list=[]
#We loop over the files and sort them
for i in file_list:
        data = fits.open(directory_path +'/'+ i)
        if data[0].header['IMAGETYP'] == "BIAS":
            bias_list.append(directory_path +'/'+i)
        if data[0].header['IMAGETYP'] == "DARK":
            dark_list.append(directory_path +'/'+i)
        if data[0].header['IMAGETYP'] == "FLAT":
            flat_list.append(directory_path+'/'+i)
        else: science_list.append(directory_path+'/'+i)
"""
This is some code to check Readout noise and gain for the reduction, included here as it is not strictly necessary for the reduction
But its good to have
"""
data1 = fits.getdata(f'~/work/ccd-reductions-mbosch2/ARCSAT_1/domeflat_R_001.fits').astype('f4')
data2 = fits.getdata(f'~/work/ccd-reductions-mbosch2/ARCSAT_1/domeflat_R_002.fits').astype('f4')

#We use the flat files to find gain
flat_diff = data1 - data2
flat_diff_var = numpy.var(flat_diff)

# Get the signal as the average of the two images
mean_signal = 0.5 * numpy.mean(data1 + data2)
    
#Calculate the gain
gain = float(2 * mean_signal / flat_diff_var)

#We use the Bias files to find the readout noise
data3 = fits.getdata(f'~/work/ccd-reductions-mbosch2/ARCSAT_1/Bias_BIN1_20250527_111044.fits').astype('f4')
data4 = fits.getdata(f'~/work/ccd-reductions-mbosch2/ARCSAT_1/Bias_BIN1_20250527_111058.fits').astype('f4')

bias_diff = data3 - data4
bias_diff_var = numpy.var(bias_diff)

# Calculate the readout noise
readout_noise_adu = numpy.sqrt(flat_diff_var / 2)
readout_noise = float(readout_noise_adu * gain)

print(gain)
print(readout_noise)
