cimport cython
from . utils cimport rotl
from . cimport SplitMix64
from libc.stdint cimport uint64_t

# Based on http://prng.di.unimi.it/xoshiro256starstar.c

cdef class XoShiRo256StarStar:
    def __cinit__(self, uint64_t seed):
        cdef SplitMix64 rng = SplitMix64(seed)
        self.s0 = rng.nextUInt64()
        self.s1 = rng.nextUInt64()
        self.s2 = rng.nextUInt64()
        self.s3 = rng.nextUInt64()

    cdef uint64_t nextUInt64(self):
        cdef uint64_t result = rotl(self.s1 * <uint64_t>5, <uint64_t>7) * <uint64_t>9

        cdef uint64_t t = self.s1 << <uint64_t>17

        self.s2 ^= self.s0
        self.s3 ^= self.s1
        self.s1 ^= self.s2
        self.s0 ^= self.s3

        self.s2 ^= t

        self.s3 = rotl(self.s3, <uint64_t>45)

        return result

    cdef long long nextLongLong(self):
        return <long long>self.nextUInt64()

    cdef long nextLong(self):
        return <long>self.nextUInt64()

    cdef int nextInt(self):
        return <int>self.nextUInt64()

    cdef bint nextBoolean(self):
        return self.nextUInt64() < <uint64_t>0

    @cython.cdivision(True)
    cdef uint64_t nextUInt64UpperBound(self, uint64_t n):
        cdef uint64_t t = self.nextUInt64()
        cdef uint64_t nMinus1 = n - <uint64_t>1
        cdef uint64_t u = t >> <uint64_t>1
        while True:
            t = u % n
            if (u + nMinus1 - t) >= <uint64_t>0:
                return t
            u = self.nextUInt64() >> <uint64_t>1

    cdef long long nextLongLongUpperBound(self, uint64_t n):
        return <long long>self.nextUInt64UpperBound(n)

    cdef long nextLongUpperBound(self, uint64_t n):
        return <long>self.nextUInt64UpperBound(n)

    cdef int nextIntUpperBound(self, uint64_t n):
        return <int>self.nextUInt64UpperBound(n)

    cdef uint64_t nextUInt64DoubleBound(self, uint64_t start, uint64_t end):
        return start + self.nextUInt64UpperBound(end - start)

    cdef long long nextLongLongDoubleBound(self, uint64_t start, uint64_t end):
        return <long long>self.nextUInt64DoubleBound(start, end)

    cdef long nextLongDoubleBound(self, uint64_t start, uint64_t end):
        return <long>self.nextUInt64DoubleBound(start, end)

    cdef int nextIntDoubleBound(self, uint64_t start, uint64_t end):
        return <int>self.nextUInt64DoubleBound(start, end)

