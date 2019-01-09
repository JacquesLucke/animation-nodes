import numpy
from functools import lru_cache
from math import ceil, log, isclose

class Sound:
    def __init__(self, soundSequences):
        self.soundSequences = soundSequences

    def getSamplesInRange(self, start, end):
        if end <= start: raise ValueError("Invaild range!")
        maxSampleRate = max(sequence.data.sampleRate for sequence in self.soundSequences)
        samplesSize = int(maxSampleRate * (end - start))
        samples = numpy.zeros(samplesSize)

        for sequence in self.soundSequences:
            sequenceStart = sequence.start / sequence.fps
            sequenceEnd = sequence.end / sequence.fps
            if (sequenceStart > end or isclose(sequenceStart, end)
                or sequenceEnd < start or isclose(sequenceEnd, start)): continue

            i = int(max(start - sequenceStart, 0) * sequence.data.sampleRate)
            j = int((end - sequenceStart) * sequence.data.sampleRate) - 1
            chunk = sequence.data.samples[i:j] * sequence.volume

            i = int(max(sequenceStart - start, 0) / (end - start) * samplesSize)
            if sequence.data.sampleRate == maxSampleRate:
                samples[i:i + len(chunk)] += chunk
            else:
                pass # Variable sample rate, needs interpolation.
        return samples

    def computeSpectrum(self, start, end, beta = 6):
        samples = self.getSamplesInRange(start, end)
        chunk = numpy.zeros(2**ceil(log(len(samples), 2)))
        chunk[:len(samples)] = samples * getCachedKaiser(len(samples), beta)
        return numpy.abs(numpy.fft.rfft(chunk)) / len(samples) * 2

    def computeTimeSmoothedSpectrum(self, start, end, attack, release, smoothingSamples = 5, beta = 6):
        FFT = None
        duration = end - start
        for i in range(min(smoothingSamples, int(start // duration)), -1, -1):
            newFFT = self.computeSpectrum(start - i * duration, end - i * duration, beta = beta)
            if FFT is None: FFT = newFFT
            else:
                factor = numpy.array((attack, release))[(newFFT < FFT).astype(int)]
                FFT = FFT * factor + newFFT * (1 - factor)
        return FFT

    def computeIntensity(self, start, end, reductionFunction):
        return reductionFunction(numpy.abs(self.getSamplesInRange(start, end)))

    def computeTimeSmoothedIntensity(self, start, end, attack, release, smoothingSamples, reductionFunction):
        intensity = None
        duration = end - start
        for i in range(min(smoothingSamples, int(start // duration)), -1, -1):
            newIntensity = self.computeIntensity(start - i * duration, end - i * duration, reductionFunction)
            if intensity is None: intensity = newIntensity
            else:
                factor = release if newIntensity < intensity else attack
                intensity = intensity * factor + newIntensity * (1 - factor)
        return intensity

@lru_cache(maxsize = 16)
def getCachedKaiser(length, beta):
    return numpy.kaiser(length, beta)
