import plotly.graph_objs as go
from plotly.offline import init_notebook_mode, iplot

import numpy as np

x = np.random.randn(200)
y = np.random.randn(200)
iplot([go.Histogram2dContour(x=x, y=y, contours=dict(coloring='heatmap')),
       go.Scatter(x=x, y=y, mode='markers', marker=dict(color='white', size=3, opacity=0.3))], show_link=False)