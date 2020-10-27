import math

def svg(display, style, content):
    if len(display) != 2:
        print('display must be a 2-tuple')
        raise ValueError
    
    return '''<?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{0}" height="{1}" viewBox="0 0 {0} {1}">
<style type="text/css" >
    <![CDATA[
        {2}
    ]]>
</style>
    <rect width="{0}" height="{1}" class="background"/>
    {3}
</svg>
    '''.format( * display , style, '\n    '.join(content))

def svg_path(points, classes = ()):
    head, * body = points 
    path = 'M {0},{1} '.format( * head ) + ' '.join('L {0},{1}'.format( * point ) for point in body)
    return '<path class="{0}" d="{1}"/>'.format(' '.join(classes), path)

def svg_text(text, position, classes = ()):
    return '<text x="{0}" y="{1}" class="{2}">{3}</text>'.format(
        * position , ' '.join(classes), text)

def kernel(x, center, width):
    return 1 / (width * math.sqrt(2 * math.pi)) * math.exp(-0.5 * ((x - center) / width) ** 2)

def transform(x, w, b):
    return tuple(x * w + b for x, w, b in zip(x, w, b))
    
def plot(series, bins = 40, smoothing = 1, 
    range_x = (0, 1), 
    range_y = (0, 1), 
    major   = (0.1, 0.1), 
    minor   = (2, 2),
    title   = None, 
    subtitle = None,
    label_x = None, 
    label_y = None,
    legend  = {},
    colors  = {}):
    
    resolution   = 10 * bins
    kernel_width = smoothing / bins
    
    display     = 800, 400
    margin_x    = 120, 120
    margin_y    =  80,  50 + 10 * (subtitle is not None) + 20 * (title is not None)
    
    area    = display[0] - sum(margin_x), sum(margin_y) - display[1]
    offset  = margin_x[0], display[1] - margin_y[0]
    
    start, end  = range_x 
    low, high   = range_y
    
    # epsilon deals with floating point error
    cells   = int((end - start) / major[0] * minor[0] + 1e-5), int((high - low) / major[1] * minor[1] + 1e-5)
    
    grid_minor  = []
    grid_major  = []
    ticks       = []
    labels      = []
    for i in range(cells[0] + 1):
        x      = i * major[0] / (minor[0] * (end - start))
        v      = i * major[0] /  minor[0]
        m      = i % minor[0] == 0
        
        screen = tuple(tuple(map(round, transform(x, area, offset))) for x in ((x, 0), (x, 1)))
        length = 12 if m else 6
        (grid_major if m else grid_minor).append(  
            svg_path(  (transform(screen[0], (1, 1), (0.5,  0)), 
                        transform(screen[1], (1, 1), (0.5, -1))), 
            classes = ('grid', 'grid-major' if m else 'grid-minor')))
        ticks.append( 
            svg_path(  (transform(screen[0], (1, 1), (0.5, 8)), 
                        transform(screen[0], (1, 1), (0.5, 8 + length))), 
            classes = ('tick',)))
        
        if m:
            labels.append(svg_text(str(round(v, 3)), 
                position    = transform(screen[0], (1, 1), (0, 16 + length)), 
                classes     = ('label-numeric', 'label-x')))
    
    for i in range(cells[1] + 1):
        y = i * major[1] / (minor[1] * (high - low))
        v = i * major[1] /  minor[1]
        m = i % minor[1] == 0
        
        screen = tuple(tuple(map(round, transform(y, area, offset))) for y in ((0, y), (1, y)))
        length = 12 if m else 6
        
        (grid_major if m else grid_minor).append( 
            svg_path(  (transform(screen[0], (1, 1), (0, -0.5)), 
                        transform(screen[1], (1, 1), (1, -0.5))), 
            classes = ('grid', 'grid-major' if m else 'grid-minor')))
        ticks.append( 
            svg_path(  (transform(screen[0], (1, 1), (-8, -0.5)), 
                        transform(screen[0], (1, 1), (-8 - length, -0.5))), 
            classes = ('tick',)))
        
        if m:
            labels.append(svg_text(str(round(v, 3)), 
                position    = transform(screen[0], (1, 1), (-16 - length, 0)), 
                classes     = ('label-numeric', 'label-y')))
    
    paths = []
    for name, series in series.items():
        scale   = 1 / (bins * len(series))
        curve   = tuple(
            (
                            x / resolution, 
                (sum(kernel(x / resolution, (point - start) / (end - start), kernel_width) 
                    for point in series) * scale - low) / (high - low)
            ) 
            for x in range(resolution + 1))
        
        paths.append(svg_path(map(lambda x: transform(x, area, offset), curve), 
            classes = (name, 'density-curve')))
    
    for i, (name, label) in enumerate(legend):
        base    = tuple(map(round, transform((1, 1), area, offset)))
        dy      = 20 * i
        paths.append(
            svg_path(  (transform(base, (1, 1), (10, dy)), 
                        transform(base, (1, 1), (25, dy))), 
            classes     = (name, 'density-curve')))
        labels.append(
            svg_text(label, 
            position    = transform(base, (1, 1), (32, dy)), 
            classes     = ('label-legend',)))
    
    if type(title) is str:
        screen = tuple(map(round, transform((0.5, 1), area, offset)))
        labels.append(svg_text(title, 
            position    = transform(screen, (1, 1), (0, -40)), 
            classes     = ('title',)))
    if type(subtitle) is str:
        screen = tuple(map(round, transform((0.5, 1), area, offset)))
        labels.append(svg_text(subtitle, 
            position    = transform(screen, (1, 1), (0, -20)), 
            classes     = ('subtitle',)))
    
    if type(label_x) is str:
        screen = tuple(map(round, transform((0.5, 0), area, offset)))
        labels.append(svg_text(label_x, 
            position    = transform(screen, (1, 1), (0, 50)), 
            classes     = ('label-axis', 'label-x')))
    if type(label_y) is str:
        screen = tuple(map(round, transform((0, 0.5), area, offset)))
        labels.append(svg_text(label_y, 
            position    = transform(screen, (1, 1), (-80, 0)), 
            classes     = ('label-axis', 'label-y', 'label-vertical')))
        
    style = '''
    rect.background 
    {
        fill:   white;
    }
    
    path.grid 
    {
        stroke-width: 1px;
        fill:   none;
    }
    path.grid-major 
    {
        stroke: #eeeeeeff;
    }
    path.grid-minor 
    {
        stroke: #f5f5f5ff;
    }
    
    path.tick 
    {
        stroke-width: 1px;
        stroke: #333333ff;
        fill:   none;
    }
    
    text
    {
        fill: #333333ff;
        font-family: 'SF Mono';
    }
    text.label-numeric 
    {
        font-size: 12px;
    }
    text.label-x 
    {
        text-anchor: middle; 
        dominant-baseline: hanging;
    }
    text.label-y 
    {
        text-anchor: end; 
        dominant-baseline: middle;
    }
    text.label-legend 
    {
        font-size: 12px;
        text-anchor: begin; 
        dominant-baseline: middle;
    }
    
    text.label-axis 
    {
        font-size: 14px;
        font-weight: 700;
    }
    text.label-vertical.label-y 
    {
        text-anchor: middle; 
        transform-box: fill-box;
        transform-origin: center;
        transform: rotate(-90deg);
    }
    
    text.title, text.subtitle 
    {
        text-anchor: middle; 
    }
    text.title 
    {
        font-size: 20px;
    }
    text.subtitle 
    {
        font-size: 12px;
    }
    
    path.density-curve 
    {
        stroke-linejoin: round;
        stroke-width: 2px;
        fill:   none;
    }
    
    ''' + ''.join('''
    path.{0} 
    {{
        stroke: {1};
    }}
    '''.format(name, color) for name, color in colors.items())
    
    return svg(display, style, grid_minor + grid_major + ticks + paths + labels)
