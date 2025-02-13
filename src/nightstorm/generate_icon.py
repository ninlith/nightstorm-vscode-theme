"""Icon generation."""

from importlib.resources import files
import skia
from shapely.geometry import box, Point
import nightstorm
from nightstorm.generate_themes import base_chromatic_palette

grid_size = 4  # pylint: disable=invalid-name
square_size = 49  # pylint: disable=invalid-name
spacing = 12  # pylint: disable=invalid-name
canvas_size = grid_size*square_size + (grid_size + 1)*spacing  # pylint: disable=invalid-name
assert canvas_size == 256
canvas_center = (canvas_size//2, canvas_size//2)
shapes = []
colors = []

# Background circles.
shapes.append(Point(canvas_center).buffer(canvas_size//2))
colors.append(skia.ColorSetARGB(0x40, 0x80, 0x80, 0x80))
shapes.append(Point(canvas_center).buffer(canvas_size//2 - spacing))
colors.append(skia.ColorSetRGB(0x20, 0x20, 0x20))

# Grid of squares intersected with a circle.
circle = Point(canvas_center).buffer(canvas_size//2 - 2*spacing)
for row in range(grid_size):
    for column in range(grid_size):
        x = spacing + column*(square_size + spacing)
        y = spacing + row*(square_size + spacing)
        square = box(x, y, x + square_size, y + square_size)
        shapes.append(square.intersection(circle).normalize().simplify(0.5))
order = [
    0,  2,  5,  9,
    1,  4,  8, 12,
    3,  7, 11, 14,
    6, 10, 13,  0,
]
colors.extend(
    skia.ColorSetRGB(*[int(x[i:i+2], 16) for i in (1, 3, 5)])
    for x in [base_chromatic_palette[o] for o in order]
)

# Draw.
recorder = skia.PictureRecorder()  # for saving to multiple formats
canvas = recorder.beginRecording(canvas_size, canvas_size)
for shape, color in zip(shapes, colors):
    # Convert Shapely shape to Skia path.
    path = skia.Path()
    for i, (x, y) in enumerate(shape.exterior.coords):
        (path.moveTo if i == 0 else path.lineTo)(x, y)
    path.close()

    # Draw the path with rounded corners.
    paint = skia.Paint(
        AntiAlias=True,
        Color=color,
        Style=skia.Paint.kFill_Style,
        PathEffect=skia.CornerPathEffect.Make(radius=10),
    )
    canvas.drawPath(path, paint)
picture = recorder.finishRecordingAsPicture()

output_dir = files(nightstorm).parent.parent/"images"
output_dir.mkdir(parents=True, exist_ok=True)

# Save as SVG.
stream = skia.FILEWStream(str(output_dir/"icon.svg"))
svg_canvas = skia.SVGCanvas.Make((canvas_size, canvas_size), stream)
svg_canvas.drawPicture(picture)
del svg_canvas
stream.flush()

# Save as PNG.
surface = skia.Surface(canvas_size, canvas_size)
image_canvas = surface.getCanvas()
image_canvas.drawPicture(picture)
image = surface.makeImageSnapshot()
image.save(str(output_dir/"icon.png"), skia.kPNG)
