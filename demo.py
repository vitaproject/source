from raysect.core.acceleration import Unaccelerated
from raysect.optical import World, translate, rotate, Point, Vector, Ray, d65_white, ConstantSF, SampledSF
from raysect.optical.observer.pinholecamera import PinholeCamera
from raysect.optical.material.emitter import UniformVolumeEmitter, UniformSurfaceEmitter, Checkerboard
from raysect.optical.material.glass import Glass, Sellmeier
from raysect.optical.material.glass_libraries import schott
from raysect.primitive import Sphere, Box, Cylinder, Union, Intersect, Subtract
from matplotlib.pyplot import *
from numpy import array

# kludge to fix matplotlib 1.4 ion() idiocy
import sys
sys.ps1 = 'SOMETHING'

red_glass = Glass(index=Sellmeier(1.03961212, 0.231792344, 1.01046945, 6.00069867e-3, 2.00179144e-2, 1.03560653e2),
                  transmission=SampledSF([300, 490, 510, 590, 610, 800], array([0.0, 0.0, 0.0, 0.0, 1.0, 1.0])*0.7),
                  cutoff=1e-4)

green_glass = Glass(index=Sellmeier(1.03961212, 0.231792344, 1.01046945, 6.00069867e-3, 2.00179144e-2, 1.03560653e2),
                    transmission=SampledSF([300, 490, 510, 590, 610, 800], array([0.0, 0.0, 1.0, 1.0, 0.0, 0.0])*0.7),
                    cutoff=1e-4)

blue_glass = Glass(index=Sellmeier(1.03961212, 0.231792344, 1.01046945, 6.00069867e-3, 2.00179144e-2, 1.03560653e2),
                   transmission=SampledSF([300, 490, 510, 590, 610, 800], array([1.0, 1.0, 0.0, 0.0, 0.0, 0.0])*0.7),
                   cutoff=1e-4)

world = World()

cyl_x = Cylinder(1, 4.2, transform=rotate(90, 0, 0)*translate(0, 0, -2.1))
cyl_y = Cylinder(1, 4.2, transform=rotate(0, 90, 0)*translate(0, 0, -2.1))
cyl_z = Cylinder(1, 4.2, transform=rotate(0, 0, 0)*translate(0, 0, -2.1))
cube = Box(Point(-1.5, -1.5, -1.5), Point(1.5, 1.5, 1.5))
sphere = Sphere(2.0)

Intersect(sphere, Subtract(cube, Union(Union(cyl_x, cyl_y), cyl_z)), world, translate(-2.1,2.1,2.5)*rotate(30, -20, 0), schott("N-LAK9"))
Intersect(sphere, Subtract(cube, Union(Union(cyl_x, cyl_y), cyl_z)), world, translate(2.1,2.1,2.5)*rotate(-30, -20, 0), schott("SF6"))
Intersect(sphere, Subtract(cube, Union(Union(cyl_x, cyl_y), cyl_z)), world, translate(2.1,-2.1,2.5)*rotate(-30, 20, 0), schott("LF5G19"))
Intersect(sphere, Subtract(cube, Union(Union(cyl_x, cyl_y), cyl_z)), world, translate(-2.1,-2.1,2.5)*rotate(30, 20, 0), schott("N-BK7"))

#s1 = Sphere(1.0, transform=translate(0, 0, 1.0-0.01))
#s2 = Sphere(0.5, transform=translate(0, 0, -0.5+0.01))
#Intersect(s1, s2, world, translate(0,0,-7.6)*rotate(65,30,0), schott("N-BK7"))

Box(Point(-50, -50, 50), Point(50, 50, 50.1), world, material=Checkerboard(4, d65_white, d65_white, 0.4, 0.8))
Box(Point(-100, -100, -100), Point(100, 100, 100), world, material=UniformSurfaceEmitter(d65_white, 0.1))

ion()
camera = PinholeCamera(fov=45, parent=world, transform=translate(0, 0, -8) * rotate(0, 0, 0))
camera.ray_max_depth = 20
camera.rays = 25
camera.spectral_samples = 1
camera.pixels = (512, 512)
camera.display_progress = True
camera.display_update_time = 10
camera.observe()

ioff()
camera.save("render.png")
camera.display()
show()
