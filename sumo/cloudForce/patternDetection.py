
import math
import numpy

"""
.. module:: patternDetection
  :synopsis: Pattern detection based on cross-correlation

.. moduleauthor:: Kokkinos Panagiotis <kokkinop@gmail.com>, Kretsis Aristotelis <aakretsis@gmail.com> , Poluzois Soumplis <polibios@gmail.com>

"""


def based_on_xcorr(signal):

	"""Pattern detection based on cross-correlation.

		:param signal: Signal to use.
		:type signal: list.
		:returns:  something.

	"""
	
	limit1 = 0.998
	limit2 = 0.6

	step_size_array = []
	sample_index_array = []

	corr = []
    
	for step_size in range(2,len(signal)):
		for sample_index in range(len(signal)):    
			cnt = 0
			for base_index in range(len(signal)):
                
				sigA = signal[sample_index:sample_index+step_size]
				sigB = signal[base_index*step_size:base_index*step_size+step_size]
                
				if(len(sigA) < step_size or len(sigB) < step_size):
					continue
                
				val1 = 0
                
				for i in range(len(sigA)):
					val1 = sigA[i]*sigA[i] + val1
                
				val2 = 0
                
				for i in range(len(sigB)):
					val2 = sigB[i]*sigB[i] + val2
       
				val3 = math.sqrt(val1*val2)
                
				norm_xcorr = numpy.correlate(sigA, sigB)/val3
                
				if(norm_xcorr >= limit1):
					cnt = cnt + 1    
                
				corr.append(norm_xcorr)

			if(cnt > 1 and cnt > limit2*len(signal)/step_size):
				step_size_array.append(step_size)
				sample_index_array.append(sample_index)

    
	return step_size_array, sample_index_array

