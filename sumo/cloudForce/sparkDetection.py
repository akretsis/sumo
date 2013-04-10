
import math
import numpy

"""

.. module:: sparkDetection
  :synopsis: Spark or spike detection based on return

.. moduleauthor:: Kokkinos Panagiotis <kokkinop@gmail.com>, Kretsis Aristotelis <aakretsis@gmail.com> , Poluzois Soumplis <polibios@gmail.com>

"""


def based_on_return(signal):

	"""Spark or spike detection based on return.

		:param signal: The signal to use.
		:type signal: list.
		:returns:  list -- list of indexes in the signal where sparks have been found.
      
	"""
	
	alpha = 3

	found_sparks_index = []
	sparks = []

	for i in range(len(signal) -1):
		sparks.append((signal[i+1] - signal[i])/signal[i])

	sparks_avg = numpy.average(sparks)
	sparks_std = numpy.std(sparks)

	for i in range(len(sparks)):
		if sparks[i] > (sparks_avg + alpha*sparks_std):
			found_sparks_index.append(i)

	# return the index in the signal where sparks where found
	return found_sparks_index

