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

import unittest
from raysect.core.math import AffineMatrix, translate, rotate_x, rotate_y, rotate_z, rotate_vector, rotate, Vector
from math import sin, cos, pi, sqrt

# TODO: Port to Cython to allow testing of the Cython API

class TestAffineMatrix(unittest.TestCase):

    def test_initialise_default(self):
        """Default initialisation should be an identity matrix."""

        m = AffineMatrix()

        r = [[1,0,0,0],
             [0,1,0,0],
             [0,0,1,0],
             [0,0,0,1]]

        for i, row in enumerate(r):
            for j, v in enumerate(row):

                self.assertEqual(m[i,j], v, "Default initialisation is not an identity matrix (R"+str(i)+", C"+str(j)+").")

    def test_initialise_4x4_indexable(self):
        """Initialisation with an 4 x 4 indexable object."""

        r = [[1.5, 2.1, -3.2, 1.8],
             [5, 10, -4.1, 1.2],
             [4.2, 3.3, -9.0, 23.0],
             [1.7, 3.1, 6.6, -9.8]]

        m = AffineMatrix(r)

        for i, row in enumerate(r):
            for j, v in enumerate(row):

                self.assertEqual(m[i,j], v, "Initialisation with 4x4 indexable failed (R"+str(i)+", C"+str(j)+").")

    def test_initialise_16_element_indexable(self):
        """Initialisation with a 16 element array."""

        r = [1.5, 2.1, -3.2, 1.8,
             5, 10, -4.1, 1.2,
             4.2, 3.3, -9.0, 23.0,
             1.7, 3.1, 6.6, -9.8]

        m = AffineMatrix(r)

        for i in range(0, 4):
            for j in range(0, 4):

                self.assertEqual(m[i,j], r[4*i + j], "Initialisation with 16 element indexable failed (R"+str(i)+", C"+str(j)+").")

    def test_initialise_affine_matrix(self):
        """Initialisation with a _Mat4 matrix."""

        r = AffineMatrix([1.5, 2.1, -3.2, 1.8,
                          5, 10, -4.1, 1.2,
                          4.2, 3.3, -9.0, 23.0,
                          1.7, 3.1, 6.6, -9.8])

        m = AffineMatrix(r)

        for i in range(0, 4):
            for j in range(0, 4):

                self.assertEqual(m[i,j], r[i,j], "Initialisation with 16 element indexable failed (R"+str(i)+", C"+str(j)+").")

    def test_initialise_invalid(self):
        """Invalid initialisation should raise a TypeError."""

        with self.assertRaises(TypeError, msg="Initialised with a string did not raise a TypeError."):
            AffineMatrix("spoon")

        with self.assertRaises(TypeError, msg="Initialised with a list containing too few items did not raise a TypeError."):
            AffineMatrix([[1.0, 2.0], [3.0, 4.0]])

    def test_indexing(self):
        """Getting/setting matrix elements via indexing."""

        m = AffineMatrix()

        for row in range(0,4):
            for column in range(0,4):

                m[row, column] = row * 1.2 - column * 5.1

        for row in range(0,4):
            for column in range(0,4):

                self.assertEqual(m[row, column], row * 1.2 - column * 5.1, "Setting/getting via indexing failed (R"+str(row)+", C"+str(column)+").")

        # __getitem__ indexes outside the range [0,3] are invalid for rows, should raise an IndexError
        for column in range(0, 4):
            with self.assertRaises(IndexError, msg="Invalid row indexing did not raise an IndexError (__getitem__)"):
                m[-1, column]
                m[4, column]

        # __setitem__ indexes outside the range [0,3] are invalid for rows, should raise an IndexError
        for column in range(0, 4):
            with self.assertRaises(IndexError, msg="Invalid row indexing did not raise an IndexError (__setitem__)"):
                m[-1, column] = 5.0
                m[4, column] = 5.0

        # __getitem__ indexes outside the range [0,3] are invalid for columns, should raise an IndexError
        for row in range(0, 4):
            with self.assertRaises(IndexError, msg="Invalid row indexing did not raise an IndexError (__getitem__)"):
                m[row, -1]
                m[row, 4]

        # __setitem__ indexes outside the range [0,3] are invalid for columns, should raise an IndexError
        for row in range(0, 4):
            with self.assertRaises(IndexError, msg="Invalid row indexing did not raise an IndexError (__setitem__)"):
                m[row, -1] = 5.0
                m[row, 4] = 5.0

        # trying to index __getitem__ with less than a two element indexable (ie m[row, column]) or simple wrong (!) should raise an IndexError
        with self.assertRaises(IndexError, msg="Invalid indexing object did not raise an IndexError (__getitem__)"):
                m[1]
                m["spoon"]

        # trying to index __setitem__ with less than a two element indexable (ie m[row, column]) or simple wrong (!) should raise an IndexError
        with self.assertRaises(IndexError, msg="Invalid indexing object did not raise an IndexError (__setitem__)"):
                m[1] = 5.0
                m["spoon"] = 5.0

    def test_multiply(self):
        """Matrix multiply operator."""

        m = AffineMatrix([[1,2,3,4],
                          [5,6,2,8],
                          [9,10,4,9],
                          [4,14,15,16]])

        minv = AffineMatrix([[258/414, -132/414, 120/414, -66/414],
                             [-381/414, 81/414, -36/414, 75/414],
                             [210/414, -162/414, 72/414, -12/414],
                             [72/414, 114/414, -66/414, -12/414]])

        r = [[1,0,0,0],
             [0,1,0,0],
             [0,0,1,0],
             [0,0,0,1]]

        # matrix multiplied by its inverse should equal the identity matrix
        t = m * minv
        self.assertTrue(isinstance(t, AffineMatrix), "AffineMatrix * AffineMatrix did not return an AffineMatrix.")
        for i, row in enumerate(r):
            for j, v in enumerate(row):

                self.assertAlmostEqual(t[i,j], v, places = 14, msg = "Matrix multiplication failed (R"+str(i)+", C"+str(j)+").")

    def test_inverse(self):
        """Matrix inverse."""

        m = AffineMatrix([[1,2,3,4],
                          [5,6,2,8],
                          [9,10,4,9],
                          [4,14,15,16]])

        r = [[258/414, -132/414, 120/414, -66/414],
             [-381/414, 81/414, -36/414, 75/414],
             [210/414, -162/414, 72/414, -12/414],
             [72/414, 114/414, -66/414, -12/414]]

        minv = m.inverse()

        for i, row in enumerate(r):
            for j, v in enumerate(row):

                self.assertAlmostEqual(minv[i,j], v, places = 14, msg = "Inverse calculation failed (R"+str(i)+", C"+str(j)+").")

    def test_factory_translate(self):
        """Translation matrix factory function."""

        m = translate(1.3, 4.5, 2.2)

        r = [[1, 0, 0, 1.3],
             [0, 1, 0, 4.5],
             [0, 0, 1, 2.2],
             [0, 0, 0, 1]]

        for i, row in enumerate(r):
            for j, v in enumerate(row):

                self.assertAlmostEqual(m[i,j], v, places = 14, msg = "Transform matrix generation failed (R"+str(i)+", C"+str(j)+").")

    def test_factory_rotate_x(self):
        """Rotation about x-axis matrix factory function."""

        m = rotate_x(67)

        a = pi * 67 / 180

        r = [[1, 0, 0, 0],
             [0, cos(a), -sin(a), 0],
             [0, sin(a), cos(a), 0],
             [0, 0, 0, 1]]

        for i, row in enumerate(r):
            for j, v in enumerate(row):

                self.assertAlmostEqual(m[i,j], v, places = 14, msg = "Rotate_x matrix generation failed (R"+str(i)+", C"+str(j)+").")

    def test_factory_rotate_y(self):
        """Rotation about y-axis matrix factory function."""

        m = rotate_y(-7.3)

        a = pi * -7.3 / 180

        r = [[cos(a), 0, sin(a), 0],
             [0, 1, 0, 0],
             [-sin(a), 0, cos(a), 0],
             [0, 0, 0, 1]]

        for i, row in enumerate(r):
            for j, v in enumerate(row):

                self.assertAlmostEqual(m[i,j], v, places = 14, msg = "Rotate_y matrix generation failed (R"+str(i)+", C"+str(j)+").")

    def test_factory_rotate_z(self):
        """Rotation about z-axis matrix factory function."""

        m = rotate_z(23)

        a = pi * 23 / 180

        r = [[cos(a), -sin(a), 0, 0],
             [sin(a), cos(a), 0, 0],
             [0, 0, 1, 0],
             [0, 0, 0, 1]]

        for i, row in enumerate(r):
            for j, v in enumerate(row):

                self.assertAlmostEqual(m[i,j], v, places = 14, msg = "Rotate_z matrix generation failed (R"+str(i)+", C"+str(j)+").")

    def test_factory_rotate_vector(self):
        """Rotation about vector matrix factory function."""

        m = rotate_vector(54, Vector(1.0, 0.22, 0.34))

        s = sin(pi*54/180)
        c = cos(pi*54/180)

        x = 1.0
        y = 0.22
        z = 0.34

        # normalise
        l = sqrt(x * x + y * y + z * z)
        x = x / l
        y = y / l
        z = z / l

        r = [[x*x+(1-x*x)*c, x*y*(1-c)-z*s, x*z*(1-c)+y*s, 0],
             [x*y*(1-c)+z*s, y*y+(1-y*y)*c, y*z*(1-c)-x*s, 0],
             [x*z*(1-c)-y*s, y*z*(1-c)+x*s, z*z+(1-z*z)*c, 0],
             [0, 0, 0, 1]]

        for i, row in enumerate(r):
            for j, v in enumerate(row):

                self.assertAlmostEqual(m[i,j], v, places = 14, msg = "Rotate_vector matrix generation failed (R"+str(i)+", C"+str(j)+").")

    def test_factory_rotate(self):
        """Rotation by yaw, pitch and roll factory function."""

        m = rotate(63, -40, 12)
        r = rotate_y(-63) * rotate_x(40) * rotate_z(12)

        for i in range(0, 4):
            for j in range(0, 4):

                self.assertAlmostEqual(m[i,j], r[i,j], places = 14, msg = "Rotate matrix generation failed (R"+str(i)+", C"+str(j)+").")


if __name__ == "__main__":
    unittest.main()