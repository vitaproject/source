# Copyright (c) 2014, Dr Alex Meakins, Raysect Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     1. Redistributions of source code must retain the above copyright notice,
#        this list of conditions and the following disclaimer.
#
#     2. Redistributions in binary form must reproduce the above copyright
#        notice, this list of conditions and the following disclaimer in the
#        documentation and/or other materials provided with the distribution.
#
#     3. Neither the name of the Raysect Project nor the names of its
#        contributors may be used to endorse or promote products derived from
#        this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""
Unit tests for the Vector object.
"""

import unittest
from raysect.core.math import Vector, AffineMatrix
from math import sqrt

# TODO: Port to Cython to allow testing of the Cython API

class TestVector(unittest.TestCase):

    def test_initialise_default(self):
        """Default initialisation, unit vector pointing along z-axis."""

        v = Vector()
        self.assertEqual(v.x, 0.0, "Default initialisation is not (0,0,1) [X].")
        self.assertEqual(v.y, 0.0, "Default initialisation is not (0,0,1) [Y].")
        self.assertEqual(v.z, 1.0, "Default initialisation is not (0,0,1) [Z].")

    def test_initialise_indexable(self):
        """Initialisation with an indexable object."""

        v = Vector(1.0, 2.0, 3.0)
        self.assertEqual(v.x, 1.0, "Initialisation with indexable failed [X].")
        self.assertEqual(v.y, 2.0, "Initialisation with indexable failed [Y].")
        self.assertEqual(v.z, 3.0, "Initialisation with indexable failed [Z].")

    def test_initialise_invalid(self):
        """Initialisation with an invalid type should raise a TypeError."""

        with self.assertRaises(TypeError, msg="Initialised with a string."):
            Vector("spoon")

    def test_x(self):
        """Get/set x co-ordinate."""

        v = Vector(2.5, 6.7, -4.6)

        # get x attribute
        self.assertEqual(v.x, 2.5, "Getting x attribute failed.")

        # set x attribute
        v.x = 10.0
        self.assertEqual(v.x, 10.0, "Setting x attribute failed.")

    def test_y(self):
        """Get/set y co-ordinate."""

        v = Vector(2.5, 6.7, -4.6)

        # get y attribute
        self.assertEqual(v.y, 6.7, "Getting y attribute failed.")

        # set y attribute
        v.y = -7.1
        self.assertEqual(v.y, -7.1, "Setting y attribute failed.")

    def test_z(self):
        """Get/set z co-ordinate."""

        v = Vector(2.5, 6.7, -4.6)

        # get z attribute
        self.assertEqual(v.z, -4.6, "Getting z attribute failed.")

        # set z attribute
        v.z = 157.3
        self.assertEqual(v.z, 157.3, "Setting z attribute failed.")

    def test_indexing(self):
        """Getting/setting components by indexing."""

        v = Vector(2.5, 6.7, -4.6)

        v[0] = 1.0
        v[1] = 2.0
        v[2] = 7.0

        # check getting/setting via valid indexes
        self.assertEqual(v[0], 1.0, "Indexing failed [X].")
        self.assertEqual(v[1], 2.0, "Indexing failed [Y].")
        self.assertEqual(v[2], 7.0, "Indexing failed [Z].")

        # check invalid indexes
        with self.assertRaises(IndexError, msg="Invalid positive index did not raise IndexError."):

            r = v[4]

        with self.assertRaises(IndexError, msg="Invalid negative index did not raise IndexError."):

            r = v[-1]

    def test_length(self):
        """Get/set the vector length."""

        v = Vector(1.2, -3, 9.8)

        # get length
        r = sqrt(1.2 * 1.2 + 3 * 3 + 9.8 * 9.8)
        self.assertAlmostEqual(v.length, r, places = 14, msg="Vector returned incorrect length.")

        # set length
        v.length = 10.0
        rx = 1.2 / sqrt(1.2 * 1.2 + 3 * 3 + 9.8 * 9.8) * 10
        ry = -3 / sqrt(1.2 * 1.2 + 3 * 3 + 9.8 * 9.8) * 10
        rz = 9.8 / sqrt(1.2 * 1.2 + 3 * 3 + 9.8 * 9.8) * 10
        self.assertAlmostEqual(v.x, rx, 14, "Vector length was not set correctly [X].")
        self.assertAlmostEqual(v.y, ry, 14, "Vector length was not set correctly [Y].")
        self.assertAlmostEqual(v.z, rz, 14, "Vector length was not set correctly [Z].")

        # trying to rescale a zero length vector should raise a ZeroDivisionError
        v = Vector(0,0,0)
        with self.assertRaises(ZeroDivisionError, msg="Adjusting length of zero length vector did not raise a ZeroDivisionError."):

            v.length = 10.0

    def test_negate(self):
        """Negate operator."""

        r = -Vector(2.5, 6.7, -4.6)
        self.assertEqual(r.x, -2.5, "Negation failed [X].")
        self.assertEqual(r.y, -6.7, "Negation failed [Y].")
        self.assertEqual(r.z, 4.60, "Negation failed [Z].")

    def test_add(self):
        """Add operator."""

        # Vector + Vector, returns Vector
        a = Vector(-1.4, 0.2, 99.1)
        b = Vector(0.7, -64.0, -0.1)
        r = a + b
        self.assertTrue(isinstance(r, Vector), "Vector + Vector did not return a Vector.")
        self.assertEqual(r.x, -1.4 + 0.7, "Vector + Vector failed [X].")
        self.assertEqual(r.y, 0.2 - 64.0, "Vector + Vector failed [Y].")
        self.assertEqual(r.z, 99.1 - 0.1, "Vector + Vector failed [Z].")

    def test_subtract(self):
        """Subtract operator."""

        # Vector - Vector, returns Vector
        a = Vector(-1.4, 0.2, 99.1)
        b = Vector(0.7, -64.0, -0.1)
        r = a - b
        self.assertTrue(isinstance(r, Vector), "Vector - Vector did not return a Vector.")
        self.assertEqual(r.x, -1.4 - 0.7, "Vector - Vector failed [X].")
        self.assertEqual(r.y, 0.2 + 64.0, "Vector - Vector failed [Y].")
        self.assertEqual(r.z, 99.1 + 0.1, "Vector - Vector failed [Z].")

    def test_multiply(self):
        """Multiply operator."""

        v = Vector(-1.4, 0.2, 99.1)

        # c * Vector, returns Vector
        r = 0.23 * v
        self.assertTrue(isinstance(r, Vector), "c * Vector did not return a Vector.")
        self.assertEqual(r.x, 0.23 * -1.4, "c * Vector failed [X].")
        self.assertEqual(r.y, 0.23 * 0.20, "c * Vector failed [Y].")
        self.assertEqual(r.z, 0.23 * 99.1, "c * Vector failed [Z].")

        # Vector * c, returns Vector
        r = v * -2.6
        self.assertTrue(isinstance(r, Vector), "Vector * c did not return a Vector.")
        self.assertEqual(r.x, -2.6 * -1.4, "Vector * c failed [X].")
        self.assertEqual(r.y, -2.6 * 0.20, "Vector * c failed [Y].")
        self.assertEqual(r.z, -2.6 * 99.1, "Vector * c failed [Z].")

    def test_divide(self):
        """Division operator."""

        v = Vector(-1.4, 0.2, 99.1)

        # Vector / c, returns Vector
        r = v / 5.3
        self.assertTrue(isinstance(r, Vector), "Vector * c did not return a Vector.")
        self.assertEqual(r.x, -1.4 / 5.3, "Vector * c failed [X].")
        self.assertEqual(r.y, 0.20 / 5.3, "Vector * c failed [Y].")
        self.assertEqual(r.z, 99.1 / 5.3, "Vector * c failed [Z].")

        # dividing by zero should raise a ZeroDivisionError
        with self.assertRaises(ZeroDivisionError, msg="Dividing by zero did not raise a ZeroDivisionError."):

            r = v / 0.0

        # any other division operations should raise TypeError
        with self.assertRaises(TypeError, msg="Undefined division did not raised a TypeError."):

            r = 54.2 / v

        with self.assertRaises(TypeError, msg="Undefined division did not raised a TypeError."):

            r = v / v

    def test_normalise(self):
        """Testing normalise() method."""

        # normalise
        v = Vector(23.2, 0.12, -5.0)
        r = v.normalise()
        l = v.length
        self.assertTrue(isinstance(r, Vector), "Normalise did not return a Vector.")
        self.assertAlmostEqual(r.x, 23.2 / l, 14, "Normalise failed [X].")
        self.assertAlmostEqual(r.y, 0.12 / l, 14, "Normalise failed [Y].")
        self.assertAlmostEqual(r.z, -5.0 / l, 14, "Normalise failed [Z].")

        # attempting to normalise a zero length vector should raise a ZeroDivisionError
        v = Vector(0.0, 0.0, 0.0)
        with self.assertRaises(ZeroDivisionError, msg="Normalising a zero length vector did not raise a ZeroDivisionError."):

            r = v.normalise()

    def test_dot_product(self):
        """Testing dot product."""

        x = Vector(1,0,0)
        y = Vector(0,1,0)
        z = Vector(0,0,1)

        # orthogonal
        self.assertEqual(x.dot(y), 0.0, "Dot product of orthogonal vectors does not equal 0.0.")
        self.assertEqual(x.dot(z), 0.0, "Dot product of orthogonal vectors does not equal 0.0.")
        self.assertEqual(y.dot(z), 0.0, "Dot product of orthogonal vectors does not equal 0.0.")

        # orthonormal
        self.assertEqual(x.dot(x), 1.0, "Dot product of orthonormal vectors does not equal 1.0.")
        self.assertEqual(y.dot(y), 1.0, "Dot product of orthonormal vectors does not equal 1.0.")
        self.assertEqual(z.dot(z), 1.0, "Dot product of orthonormal vectors does not equal 1.0.")

        # arbitrary
        a = Vector(4, 2, 3)
        b = Vector(-1, 2, 6)
        self.assertEqual(a.dot(b), 4*-1 + 2*2 + 3*6, "Dot product of two arbitrary vectors gives the wrong value.")
        self.assertEqual(a.dot(b), b.dot(a), "a.b does not equal b.a.")

    def test_cross_product(self):
        """Testing cross product."""

        # raysect uses a right handed coordinate system
        x = Vector(1,0,0)
        y = Vector(0,1,0)
        z = Vector(0,0,1)

        # orthogonal
        r = x.cross(y)
        self.assertEqual(r.x, 0.0, "Cross product failed [X].")
        self.assertEqual(r.y, 0.0, "Cross product failed [Y].")
        self.assertEqual(r.z, 1.0, "Cross product failed [Z].")

        r = x.cross(z)
        self.assertEqual(r.x, 0.0, "Cross product failed [X].")
        self.assertEqual(r.y, -1.0, "Cross product failed [Y].")
        self.assertEqual(r.z, 0.0, "Cross product failed [Z].")

        r = y.cross(z)
        self.assertEqual(r.x, 1.0, "Cross product failed [X].")
        self.assertEqual(r.y, 0.0, "Cross product failed [Y].")
        self.assertEqual(r.z, 0.0, "Cross product failed [Z].")

        # orthonormal
        r = x.cross(x)
        self.assertEqual(r.x, 0.0, "Cross product failed [X].")
        self.assertEqual(r.y, 0.0, "Cross product failed [Y].")
        self.assertEqual(r.z, 0.0, "Cross product failed [Z].")

        r = y.cross(y)
        self.assertEqual(r.x, 0.0, "Cross product failed [X].")
        self.assertEqual(r.y, 0.0, "Cross product failed [Y].")
        self.assertEqual(r.z, 0.0, "Cross product failed [Z].")

        r = z.cross(z)
        self.assertEqual(r.x, 0.0, "Cross product failed [X].")
        self.assertEqual(r.y, 0.0, "Cross product failed [Y].")
        self.assertEqual(r.z, 0.0, "Cross product failed [Z].")

        # arbitrary Vector x Vector
        a = Vector(4, 2, 3)
        b = Vector(-1, 2, 6)

        r1 = a.cross(b)
        r2 = b.cross(a)

        self.assertTrue(isinstance(r, Vector), "Cross did not return a Vector.")

        self.assertEqual(r1.x, a.y * b.z - b.y * a.z, "Cross product failed [X].")
        self.assertEqual(r1.y, b.x * a.z - a.x * b.z, "Cross product failed [Y].")
        self.assertEqual(r1.z, a.x * b.y - b.x * a.y, "Cross product failed [Z].")

        self.assertEqual(r2.x, b.y * a.z - a.y * b.z, "Cross product failed [X].")
        self.assertEqual(r2.y, a.x * b.z - b.x * a.z, "Cross product failed [Y].")
        self.assertEqual(r2.z, b.x * a.y - a.x * b.y, "Cross product failed [Z].")

    def test_transform(self):
        """Testing transform() method."""

        m = AffineMatrix([[1,2,3,4],
                          [5,6,2,8],
                          [9,10,4,9],
                          [4,14,15,16]])

        v = Vector(-1, 2, 6)

        r = v.transform(m)

        self.assertTrue(isinstance(r, Vector), "Transform did not return a Vector.")
        self.assertEqual(r.x, 1 * -1 +  2 * 2 + 3 * 6, "Transform failed [X].")
        self.assertEqual(r.y, 5 * -1 +  6 * 2 + 2 * 6, "Transform failed [Y].")
        self.assertEqual(r.z, 9 * -1 + 10 * 2 + 4 * 6, "Transform failed [Z].")

    def test_copy(self):
        """Testing method copy()."""

        v = Vector(1.0, 2.0, 3.0)
        r = v.copy()

        # check a new instance has been created by modifying the original
        v.x = 5.0
        v.y = 6.0
        v.z = 7.0

        self.assertEqual(r.x, 1.0, "Copy failed [X].")
        self.assertEqual(r.y, 2.0, "Copy failed [Y].")
        self.assertEqual(r.z, 3.0, "Copy failed [Z].")

if __name__ == "__main__":
    unittest.main()



