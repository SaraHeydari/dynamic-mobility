def get_rcParams(fig_width_cm, fig_ratio = 0.8, font_sizes = None):
    """Set good parameters for LaTeX-figures.

    The idea is to set the figure width in centimeters to be the
    same as the final size in your LaTeX document. This way the font
    sizes will be correct also.

    Parameters
    ----------
    fig_width_cm: int or float
        The width of the final figure in centimeters.
    fig_ratio: float (between 0 and 1)
        The ratio height/width. < 1 is landscape, 1.0 is square and
        > 1.0 is portrait.
    font_sizes: dictionary
        The font sizes used in the figure. Default is size 8 for
        everything else expect 10 for the title. Possible keys are
        'default', 'label', 'title', 'text', 'legend' and 'tick'.
        'default' is used when the specific value is not defined,
        other keys should be self explanatory.
    """
    default_font_sizes = {'label':8, 'title':10, 'text':8, 'legend':8, 'tick':8}
    font_sizes = (font_sizes or {})
    for k in default_font_sizes:
        if k not in font_sizes:
            font_sizes[k] = (font_sizes.get('default') or default_font_sizes[k])

    inches_per_cm = 1/2.54
    fig_width = 1.0*fig_width_cm*inches_per_cm  # width in inches
    fig_height = 1.0*fig_width*fig_ratio        # height in inches
    fig_size =  [fig_width,fig_height]
    params = {'font.family':'serif',
              'font.serif':'Computer Modern Roman',
              'axes.labelsize': font_sizes['label'],
              'axes.titlesize': font_sizes['title'],
              #'text.fontsize': font_sizes['text'],
              'font.size': font_sizes['text'],
              'legend.fontsize': font_sizes['legend'],
              'xtick.labelsize': font_sizes['tick'],
              'ytick.labelsize': font_sizes['tick'],
              'text.usetex': True,
              'figure.figsize': fig_size,
              'legend.labelspacing': 0.0,
              'lines.markersize': 3,
              'lines.linewidth': 0.5}
    return params