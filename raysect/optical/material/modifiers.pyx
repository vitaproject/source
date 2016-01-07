# cython: language_level=3

# Copyright (c) 2015, Dr Alex Meakins, Raysect Project
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

from raysect.optical.material.material cimport Material
from raysect.core.math.affinematrix cimport AffineMatrix3D
from raysect.core.scenegraph.primitive cimport Primitive
from raysect.core.scenegraph.world cimport World
from raysect.optical.ray cimport Ray
from raysect.core.math.point cimport Point3D
from raysect.core.math.vector cimport Vector3D
from raysect.core.math.affinematrix cimport new_affinematrix3d
from raysect.optical.spectrum cimport Spectrum
from raysect.core.math.normal cimport Normal3D, new_normal3d
from raysect.core.math.random cimport vector_hemisphere_cosine

# sets the maximum number of attempts to find a valid perturbed normal
# it is highly unlikely (REALLY!) this number will ever be reached, it is just there for my paranoia
# in the worst case 50% of the random hemisphere will always generate a valid solution... so P(fail) < 0.5^50!
DEF SAMPLE_ATTEMPTS = 50


cdef class Roughen(Material):
    """
    Modifies the surface normal to approximate a rough surface.

    This is a modifier material, it takes another material (the base material)
    as an argument.

    The roughen modifier works by randomly deflecting the surface normal about
    its true position before passing the intersection parameters on to the base
    material.

    The deflection is calculated by interpolating between the existing normal
    and a vector sampled from a cosine weighted hemisphere. The strength of the
    interpolation, and hence the roughness of the surface, is controlled by the
    roughness argument. The roughness argument takes a value in the range
    [0, 1] where 1 is a fully rough, lambert-like surface and 0 is a smooth,
    untainted surface.

    :param material: The base material.
    :param roughness: A double value in the range [0, 1].
    """

    cdef:
        Material material
        double roughness

    def __init__(self, Material material not None, double roughness):

        if roughness < 0 or roughness > 1.0:
            raise ValueError("Roughness must be a floating point value in the range [0, 1] where 1 is full roughness.")

        self.roughness = roughness
        self.material = material

    cpdef Spectrum evaluate_surface(self, World world, Ray ray, Primitive primitive, Point3D hit_point,
                                    bint exiting, Point3D inside_point, Point3D outside_point,
                                    Normal3D normal, AffineMatrix3D world_to_local, AffineMatrix3D local_to_world):

        cdef:
            Ray reflected
            Vector3D l_normal, l_tangent, l_bitangent
            Vector3D s_incident, s_random
            Normal3D s_normal
            AffineMatrix3D surface_to_local
            int attempt

        # generate an orthogonal basis about surface normal
        l_normal = normal.as_vector()
        l_tangent = normal.orthogonal()
        l_bitangent = l_normal.cross(l_tangent)

        # generate inverse surface transform matrix
        surface_to_local = new_affinematrix3d(l_tangent.x, l_bitangent.x, l_normal.x, 0.0,
                                              l_tangent.y, l_bitangent.y, l_normal.y, 0.0,
                                              l_tangent.z, l_bitangent.z, l_normal.z, 0.0,
                                              0.0, 0.0, 0.0, 1.0)

        local_to_surface = new_affinematrix3d(l_tangent.x, l_tangent.y, l_tangent.z, 0.0,
                                              l_bitangent.x, l_bitangent.y, l_bitangent.z, 0.0,
                                              l_normal.x, l_normal.y, l_normal.z, 0.0,
                                              0.0, 0.0, 0.0, 1.0)

        # convert ray direction to surface space
        s_incident = ray.direction.transform(world_to_local).transform(local_to_surface)

        # attempt to find a valid (intersectable by ray) surface perturbation
        s_normal = new_normal3d(0, 0, 1)
        for attempt in range(SAMPLE_ATTEMPTS):

            # Generate a new normal about the original normal by lerping between a random vector and the original normal.
            # The lerp strength is determined by the roughness. Calculation performed in surface space, so the original
            # normal is aligned with the z-axis.
            s_random = vector_hemisphere_cosine()
            s_normal.x = self.roughness * s_random.x
            s_normal.y = self.roughness * s_random.y
            s_normal.z = self.roughness * s_random.z + (1 - self.roughness)

            # Only accept the new normal if it does not change the side of the surface the incident ray is on.
            # An incident ray could not hit a surface facet that is facing away from it.
            # If (incident.normal) * (incident.perturbed_normal) < 0 the ray has swapped sides.
            # Note: normal in surface space is Normal3D(0, 0, 1), therefore incident.normal is just incident.z.
            if (s_incident.z * s_incident.dot(s_normal)) > 0:

                # we have found a valid perturbation, re-assign normal
                normal = s_normal.transform(surface_to_local).normalise()
                break

        return self.material.evaluate_surface(world, ray, primitive, hit_point, exiting, inside_point, outside_point,
                                              normal, world_to_local, local_to_world)

    cpdef Spectrum evaluate_volume(self, Spectrum spectrum, World world,
                                   Ray ray, Primitive primitive,
                                   Point3D start_point, Point3D end_point,
                                   AffineMatrix3D to_local, AffineMatrix3D to_world):

        return self.material.evaluate_volume(spectrum, world, ray, primitive, start_point, end_point, to_local, to_world)



