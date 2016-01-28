# cython: language_level=3

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


import matplotlib.pyplot as plt
from numpy import pi as PI

from raysect.optical.observer.sensor import NonImaging
from raysect.optical.observer.point_generator import SinglePoint, Disk
from raysect.optical.observer.vector_generators import SingleRay, ConeUniform
from raysect.core import AffineMatrix3D, Point3D, Vector3D


# TODO: check normalisation of various random distributions
class BasicLineOfSight(NonImaging):
    """
    The most basic Line Of Sight observer in Raysect.

    Inherits arguments and attributes from the base sensor.NonImaging class. Fires a single ray oriented along the observer's
    z axis in world space.
    """
    def _generate_rays(self, ray_template):

        rays = []
        for n in range(self.pixel_samples):
            rays.append(ray_template.copy(Point3D(), Vector3D()))
        return rays


class OpticalFibre(NonImaging):
    """
    An optical fibre Line Of Sight observer.

    Inherits arguments and attributes from the base sensor.NonImaging class. Rays are sampled over a circular area at the fibre tip
    and a conical solid angle defined by the acceptance_angle parameter.

    :param float acceptance_angle: The angle in radians between the z axis and the cone surface which defines the fibres
    soild angle sampling area.
    :param float radius: The radius of the fibre tip in metres. This radius defines a circular area at the fibre tip
    which will be sampled over.
    """
    def __init__(self, acceptance_angle=10, radius=0.001, sensitivity=1.0, spectral_samples=512,
                 spectral_rays=1, pixel_samples=1, parent=None, transform=AffineMatrix3D(), name=""):

        super().__init__(sensitivity=sensitivity, spectral_samples=spectral_samples, spectral_rays=spectral_rays,
                         pixel_samples=pixel_samples, parent=parent, transform=transform, name=name)

        if not 0 <= acceptance_angle <= 90:
            raise RuntimeError("Acceptance angle {} for OpticalFibre must be between 0 and 90 degrees."
                               "".format(acceptance_angle))

        self.acceptance_angle = acceptance_angle
        self.radius = radius

    def _generate_rays(self, ray_template):

        point_generator = Disk(self.radius)
        origins = point_generator(self.pixel_samples)
        vector_generator = ConeUniform(self.acceptance_angle)
        directions = vector_generator(self.pixel_samples)

        # todo: add cos(theta).dA weighting Normal.Vector

        rays = []
        for n in range(self.pixel_samples):
            rays.append(ray_template.copy(origins[n], directions[n]))
        return rays
