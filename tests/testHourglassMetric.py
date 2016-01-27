import numpy as np
import unittest
import lsst.sims.maf.metrics as metrics


class TestHourglassmetric(unittest.TestCase):

    def testHourglassMetric(self):
        """Test the hourglass metric """
        names = ['expMJD', 'night', 'filter']
        types = [float, float, '|S1']
        for npts in [10,100,1000]:
            data = np.zeros(npts, dtype=zip(names, types))
            data['night'] = np.round(np.arange(0, 5, 1./npts))[:npts]+1
            data['expMJD'] = np.arange(0, 5, 1./npts)[:npts] + 59580 + data['night']

            data['filter'] = 'r'
            slicePoint = [0]
            metric = metrics.HourglassMetric()
            result = metric.run(data, slicePoint)
            pernight = result['pernight']
            perfilter = result['perfilter']
            # Check that the format is right at least
            assert(np.size(perfilter) > 2)
            assert(np.size(pernight) == np.size(np.unique(data['night'])))
            assert(len(pernight.dtype.names) == 9)


if __name__ == '__main__':

    unittest.main()
