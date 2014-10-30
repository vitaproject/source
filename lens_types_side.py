
from raysect.optical import World, translate, rotate, Point, d65_white
from raysect.optical.observer.pinholecamera import PinholeCamera
from raysect.optical.material.emitter import Checkerboard
from raysect.primitive import Box
from matplotlib.pyplot import *
import sys
sys.ps1 = 'SOMETHING'

# Import the new lens classes
from raysect.optical.optical_components.sphericalsinglets import planar_convex_lens

# Instantiate world object
world = World()

# Create a lens object
planar_convex_lens(15, 3, parent=world, transform=translate(0, 0, 0) * rotate(90.0, 0.0, 0.0))

# Background Checkerboard
Box(Point(-50.0, -50.0, 50.0), Point(50.0, 50.0, 50.1), world, material=Checkerboard(4.0, d65_white, d65_white, 0.4, 0.8))

# Instantiate camera object, and configure its settings.
ion()
camera = PinholeCamera(fov=45, parent=world, transform=translate(0, 0, -8) * rotate(0, 0, 0))
camera.ray_max_depth = 15
camera.rays = 1
camera.spectral_samples = 15
camera.pixels = (512, 512)
camera.display_progress = True
camera.display_update_time = 10

# Start ray tracing
camera.observe()

ioff()
camera.save("render.png")
camera.display()
show()