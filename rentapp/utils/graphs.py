import plotly
from plotly.offline import plot

def make_graph(refs):

    xaxis = [refs['price'],
             refs['refmaj'],
             refs['ref'],
             refs['refmin']]

    yaxis = ['Loyer proposé', 
             'Loyer majoré', 
             'Loyer de référence', 
             'Loyer minimum']

    marker = dict(color=['rgba(63,127,191,1)', 
                         'rgba(191,63,63,1)',
                         'rgba(191,191,63,1)', 
                         'rgba(127,191,63,1)'])

    annotations = []
    for x, y in zip(xaxis, yaxis):
        annotations.append(dict(x=x/2, y=y, text=y,
                                font=dict(size=16,
                                color='rgba(245, 246, 249, 1)'),
                                showarrow=False,))
    
    layout = dict(annotations=annotations,
                  yaxis=dict(showticklabels=False))
    
    bar = dict(x=xaxis, 
               y=yaxis, 
               type='bar',
               orientation='h',
               opacity=0.6,
               marker=marker,
               hoverinfo='x')

    fig = plotly.graph_objs.Figure(data=[bar], 
                                   layout=layout)

    div = plot(fig, 
               show_link=False, 
               output_type="div", 
               include_plotlyjs=True)

    return div
