import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from textwrap import dedent
import pandas as pd

# https://docs.google.com/spreadsheets/d/1i_tDmppgYFRVL0JvS4jfevR2FmQ6FZrBfaUThhMo3fQ/edit?usp=sharing
# https://docs.google.com/spreadsheets/d/1i_tDmppgYFRVL0JvS4jfevR2FmQ6FZrBfaUThhMo3fQ/edit?usp=sharing

list_name = ['data_id', 'address','days_on_streeteasy', 'price','scrape_date', 
		'sq_ft', 'unit_type', 'neighborhood',
       'realtor', 'rooms', 'beds', 'baths', 'bike room',
       'board approval required', 'cats and dogs allowed',
       'central air conditioning', 'concierge', 'cold storage',
       'community recreation facilities', "children's playroom", 'deck',
       'dishwasher', 'doorman', 'elevator', 'full-time doorman', 'furnished',
       'garage parking', 'green building', 'guarantors accepted',
       'laundry in building', 'live-in super', 'loft', 'package room',
       'parking available', 'patio', 'pets allowed', 'roof deck', 'smoke-free',
       'storage available', 'sublet', 'terrace', 'virtual doorman',
       'washer/dryer in-unit', 'waterview', 'waterfront', 'A', 'C', 'E', 'B',
       'D', 'F', 'M', 'G', 'L', 'J', 'Z', 'N', 'Q', 'R', '1', '2', '3', '4',
       '5', '6', '7', 'S', 'LIRR', 'PATH', 'price_percentile', 'borough',
       'min_subway_distance']
important_amenities = ['elevator','smoke-free','waterview','pets allowed','doorman','dishwasher','patio','terrace','garage parking','furnished']
df = pd.read_csv(
	'https://docs.google.com/spreadsheets/d/1i_tDmppgYFRVL0JvS4jfevR2FmQ6FZrBfaUThhMo3fQ/gviz/tq?tqx=out:csv',names = list_name)
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
application = app.server


app.layout = html.Div([
	html.Div([
    	dcc.Graph(id='graph-with-slider'),
    	dcc.RangeSlider(
        	id='size-slider',
        	min=int(0),
        	max=int(6000),
        	value=[0,500],
        	marks={str(size): str(size) for size in [0,250,500,750,1000,1250,1500,1750,2000,3000,
                                                    4000,5000]},
        	step=None
    	)
    ],
    style={'width':'80%', 'float':'right','display':'inline-block','padding': '10px 5px 5px 5px'}),

    html.Div([
        html.Div('''select type of size axis (sq.ft.)''',
            style = {'paddingTop':10, 'paddingBottom':5}),
    	dcc.RadioItems(
    		id = 'xaxis-type',
    		options =[{'label' : i, 'value': i} for i in ['Linear','Log']],
    		value='Linear',
    		labelStyle={'display':'inline-block'}
    	),
        html.Div([
            html.Div('''slide to adjust price''', style={'paddingTop':2.5,'paddingBottom':5}),
            dcc.RangeSlider(id='price-slider',
            min = int(0),
            max = int(12000),
            value = [0,2000],
            marks={str(price): '$' + str(price) for price in [0,1000,2000,3000,4000,5000,6000,7000,8000,9000,
                                                    10000,11000,12000]},
            vertical=True),
        ],
        style={'height': '300px', 'width': '100%','display': 'inline-block','padding': '20px 0px 0px 0px'}
	)],
	style = {'width' : '10%', 'float':'left','padding': '10px 10px 10px 10px','display':'inline-block'}),

    html.Div([  # Holds the heatmap & barchart (60:40 split) 
        html.Div([  # Holds the heatmap
            dcc.Graph(
                id="survival-graph",
            ),
        ],
        style={
            "width" : '40%', 'float' : 'left', 'display' : 'inline-block', 'padding': '40px 10px 10px 10px','boxSizing' : 'border-box'} # padding = top,right,bottom,left
        ),
        html.Div([  # Holds the barchart
            dcc.Graph(id="Boxplot"),
            dcc.Checklist(
                id='amenities-list',
                options = [{'label':sev,'value':sev} for sev in important_amenities],
                values = [sev for sev in important_amenities],
                labelStyle = {'display':'inline-block','padding': '10px 10px 20px 10px','boxSizing' : 'border-box'}
            )
            #style={'height' : '50%'})
        ],
        style={
            "width" : '60%', 'float' : 'right', 'display' : 'inline-block','padding': '50px 10px 1px 10px','boxSizing' : 'border-box'})
    ]),
    html.Div([
        dcc.Markdown(dedent('''
            ## Infographic of NYC renting
            ###### the data is from Nov 2016 - FEB 2017
            ###### collected by Braden Purcell, Ph.D. 
            [Purcell Github here](https://github.com/purcelba/streeteasy_scrape)
            '''))
    ],
    style = {"width" : '60%', 'float' : 'left', 'display' : 'inline-block','padding': '0px 10px 150px 0px','boxSizing' : 'border-box'})
])

def update_by_size(data,size,price):
    data2 = data[(data['sq_ft'] > size[0]) & (data['sq_ft'] <= size[1]) & (data['price'] > price[0]) &(data['price'] <= price[1])]
    return data2

@app.callback(
    Output('graph-with-slider', 'figure'),
    [Input('xaxis-type','value'),
    Input('size-slider', 'value'),
    Input('price-slider','value')])
def update_figure(xaxis_type,size,price):
    filtered_df = update_by_size(df,size,price)
    traces = []
    for i in filtered_df.borough.unique():
        df_by_borough = filtered_df[filtered_df['borough'] == i]
        traces.append(go.Scatter(
            x=df_by_borough['sq_ft'],
            y=df_by_borough['price'],
            text=df_by_borough['address'],
            mode='markers',
            opacity=0.7,
            marker={
                'size': 5, # use small marker size maybe like 5
                'line': {'width': 0.5, 'color': 'white'}
            },
            name=i
        ))

    return {
        'data': traces,
        'layout': go.Layout(title='size of apartment and price',
            xaxis={'type': 'linear' if xaxis_type =='Linear' else 'log', 
            		'title': 'sq ft'
            		},
            yaxis={'title': 'price', 'range': [0, filtered_df['price'].max()]},
            margin={'l': 40, 'b': 40, 't': 25, 'r': 0},
            legend={'x': 0, 'y': 1},
            hovermode='closest'
        )
    }

def gross_survival(sold_data):
    count_days_listing = sold_data.groupby(['days_on_streeteasy']).count().reset_index()
    count_days_listing['survival_fraction'] = (sold_data.shape[0]-count_days_listing['data_id'].cumsum())/sold_data.shape[0]
    return count_days_listing

@app.callback(
 	Output('survival-graph', 'figure'),
    [Input('size-slider', 'value'),
    Input('price-slider','value')])
def update_survival(size,price):
    filtered_df = update_by_size(df,size,price)
    traces = []
    for i in ['Manhattan','Brooklyn','Queens','Bronx']:
        survive_by_borough = gross_survival(filtered_df[filtered_df['borough'] == i])
        traces.append(go.Scatter(
            x=survive_by_borough['days_on_streeteasy'],
            y=survive_by_borough['survival_fraction'],
            mode='lines',
            name=i
        ))

    return {
        'data': traces,
        'layout': go.Layout(title='how long house listings stay on the web',
            xaxis={'title': 'days_on_streeteasy', 'range': [-1,200]},
            yaxis={'title': 'survival_fraction', 'range': [-0.1, 1]},
            margin={'l': 40, 'b': 120, 't': 30, 'r': 0},
            legend={'x': 0.8, 'y': 1}
        )
    }

@app.callback(
    Output('Boxplot', 'figure'),
    [Input('size-slider', 'value'),
    Input('amenities-list','values'),
    Input('price-slider','value')])
def update_Boxplot(size,amenities,price):
    filtered_df = update_by_size(df,size,price)
    traces = []

    # next step put checklist as input to this step. avoiding hard-code the list to look at
    for i in amenities:
        traces.append(go.Box(y=filtered_df[filtered_df[i]==0]['price'],name='No ' + str(i),marker={"size": 1}))
        traces.append(go.Box(y=filtered_df[filtered_df[i]==1]['price'],name='Have ' + str(i),marker={"size": 1}))
    #traces.append(go.Box(y=filtered_df[filtered_df['dishwasher']==0]['price'],name='No dishwasher',marker={"size": 2}))
    #traces.append(go.Box(y=filtered_df[filtered_df['dishwasher']==1]['price'],name='have dishwasher',marker={"size": 2}))

    return {
        'data': traces,
        'layout': go.Layout(title='breaking down the price of amenities',
            margin={'l': 50, 'b': 90, 't': 30, 'r': 0},yaxis={'title': 'price', 'range': [0, filtered_df['price'].max()]}
        )
    }

if __name__ == '__main__':
    application.run(debug=True)
