import pandas as pd 
import dash
import dash_html_components as html 
from dash.dependencies import Input, Output , State 
import dash_core_components as dcc 
import webbrowser
import plotly.graph_objects as go  
import plotly.express as px

app = dash.Dash()

def load_data():

    data_set = 'Global_terror.csv'
    global df
    df = pd.read_csv(data_set)

    month = {
            "January":1,
            "February": 2,
            "March": 3,
            "April":4,
            "May":5,
            "June":6,
            "July": 7,
            "August":8,
            "September":9,
            "October":10,
            "November":11,
            "December":12
            }

    global month_list
    month_list= [{"label":key, "value":values} for key,values in month.items()]

    global date_list
    date_list = [{"label":x, "value":x} for x in range(1, 32)] 


    global region_list
    region_list = [{"label": str(i), "value": str(i)}  for i in sorted( df['region_txt'].unique().tolist() ) ]

    global country_list
    country_list = df.groupby("region_txt")["country_txt"].unique().apply(list).to_dict()  

    global state_list
    state_list = df.groupby("country_txt")["provstate"].unique().apply(list).to_dict()

    global city_list
    city_list = df.groupby("provstate")["city"].unique().apply(list).to_dict()

    global attack_type_list
    attack_type_list = [{"label": str(i), "value": str(i)}  for i in df['attacktype1_txt'].unique().tolist()]

    global year_list
    year_list = sorted(df['iyear'].unique().tolist())

    global year_dict
    year_dict = {str(year): str(year) for year in year_list}

    print ('Loaded Data Successfully')

def open_browser():
    webbrowser.open_new('http://127.0.0.1:8050/')

def app_ui():
    dropdown_style={
        'font-family': 'Ranchers', 
        'background-color': '#5b5b3e',
        'width': '45%',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'margin-bottom': '5px',
        "padding-top": "4px",
        "padding-bottom": "2px",
        "border-radius":"50px"
    }    
    main_layout = html.Div(
        [
        html.H1( 'TERRORISM ANALYSIS', id='Heading' ,style= {'color':'#ffffff', 'text-align':'center','font-family': 'Ranchers'}),
        dcc.Dropdown(id='Month', options= month_list, placeholder='Select Month', multi=True ,style=dropdown_style),
        dcc.Dropdown(id='Date', options= date_list, placeholder='Select Date', multi=True,style=dropdown_style),
        dcc.Dropdown(id='Region', options= region_list, placeholder='Select Region', multi=True,style=dropdown_style),
        dcc.Dropdown(id='Country', options= country_list, placeholder='Select Country', multi=True,style=dropdown_style),
        dcc.Dropdown(id='State', options= state_list, placeholder='Select State', multi=True,style=dropdown_style),
        dcc.Dropdown(id='City', options= city_list, placeholder='Select City', multi=True,style=dropdown_style),
        dcc.Dropdown(id='Attack_type', options= attack_type_list, placeholder='Select Attack Type', multi=True,style=dropdown_style),
        html.H3('Select the Year' ,  id= 'Year_title',style={'color':'#ffffff','text-align':'center'}),
        dcc.RangeSlider(id='Range_slider', min=min(year_list), max=max(year_list), value=[min(year_list),max(year_list)], marks=year_dict ),
        html.Br(),
        dcc.Loading(children=[dcc.Graph(id='Graph_map',children = 'Loading')],type='graph',style={"position": "static","z-index":"1",})
        ],style={'background' : 'url(assets/unnamed.png)'}
    )
    return main_layout

@app.callback(
    dash.dependencies.Output('Graph_map' , 'figure'),
    [
        dash.dependencies.Input('Month' , 'value'),
        dash.dependencies.Input('Date' , 'value'),
        dash.dependencies.Input('Region' , 'value'),
        dash.dependencies.Input('Country' , 'value'),
        dash.dependencies.Input('State' , 'value'),
        dash.dependencies.Input('City' , 'value'),
        dash.dependencies.Input('Attack_type' , 'value'),
        dash.dependencies.Input('Range_slider' , 'value')
    ]
)
def update_ui(Month,Date,Region,Country,State,City,Attack_type,Range_slider):

    try:    
        # Year Filter
        year_range = range(Range_slider[0], Range_slider[1]+1)
        df1 = df[df["iyear"].isin(year_range)]

        # Month & Date Filter
        if Month == [] or Month == None:
            pass
        else:
            if Date == [] or Date == None:
                df1 = df1[df1["imonth"].isin(Month)]
            else:
                df1 = df1[(df1["imonth"].isin(Month)) & (df1['iday'].isin(Date))]

        # Place Filters
        if Region == [] or Region == None:
            pass
        else:
            df1 = df1[df1["region_txt"].isin(Region)] 
        if Country == [] or Country == None:
            pass
        else:
            df1 = df1[df1["country_txt"].isin(Country)] 
        if State == [] or State == None:
            pass
        else:
            df1 = df1[df1["provstate"].isin(State)]            
        if City == [] or City == None:
            pass
        else:
            df1 = df1[df1["city"].isin(City)]

        # Attack Type Filter

        if Attack_type == [] or Attack_type == None:
            pass
        else:
            df1 = df1[df1['attacktype1_txt'].isin(Attack_type)]

        # Printing Details of Data
        #print ("Data Matches To The Selected Fields",df1.shape[0])
        #print ("Selected Months : ",str(df1["imonth"].unique().tolist()))
        #print ("Selected Days : ",str(df1["iday"].unique().tolist()))
        #print ("Selected Years : ",str(year_range))
        #print ("Selected Regions : ",str(df1["region_txt"].unique().tolist()))
        #print ("Selected Countries : ",str(df1["country_txt"].unique().tolist()))
        #print ("Selected States : ",str(df1["provstate"].unique().tolist()))
        #print ("Selected Cities : ",str(df1["city"].unique().tolist()))
        #print ("Selected Attack Types : ",str(df1["attacktype1_txt"].unique().tolist()))



        figure = go.Figure()

        figure = px.scatter_mapbox(df1,
                                lat=df1["latitude"], 
                                lon=df1["longitude"],
                                hover_data=["region_txt", "country_txt", "provstate","city", "attacktype1_txt","nkill","iyear"],
                                color= "attacktype1_txt",
                                zoom=1
                    )                       
        figure.update_layout(mapbox_style="open-street-map",
                            autosize=True,
                            margin=dict(l=0, r=0, t=25, b=20),                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          
        )
    except KeyError:
        print ('im here')

        # Add images
        figure.add_layout_image(
                dict(
                    source="/home/pradeep/Desktop/Project_code/assets/facebookdown_3452194b.jpg",
                    xref="x",
                    yref="y",
                    x=0,
                    y=3,
                    sizex=2,
                    sizey=2,
                    sizing="stretch",
                    opacity=0.5,
                    layer="below")
        )


    return figure


@app.callback(
    Output('Country','options'),
    [Input('Region','value')])
def update_country(region_value):
    option = []
    if region_value == None or region_value == []:
        for var in country_list.keys():
            option.extend(country_list[var])      
        return [{'label':m , 'value':m} for m in option]
    else:
        for var in region_value:
            if var in country_list.keys():
                option.extend(country_list[var])
        return [{'label':m , 'value':m} for m in option]

@app.callback(
    Output('State','options'),
    [Input ('Region','value'),
    dash.dependencies.Input('Country','value')
    ])
def update_state(region_value,country_value):
    temp = []
    temp_country = []
    if country_value == None or country_value == []:
        if region_value == None or region_value == []:
            for var in state_list.keys():
                temp.extend(state_list[var])   
            option_state = set(temp)
            return [{'label':m , 'value':m} for m in option_state]
        else:
            for var in region_value:
                if var in country_list.keys():
                    temp_country.extend(country_list[var])
            for var in temp_country:
                if var in state_list.keys():
                    temp.extend(state_list[var])
                option_state = set(temp)
            return [{'label':m , 'value':m} for m in option_state]
    else:
        for var in country_value:
            if var in state_list.keys():
                temp.extend(state_list[var])
        option_state = set(temp)
        return [{'label':m , 'value':m} for m in option_state]

@app.callback(
    Output('City','options'),
    [Input('State','value'),
    dash.dependencies.Input('Country','value'),
    dash.dependencies.Input('Region','value')
    ])
def update_city(state_value,country_value,region_value):
    temp = []
    temp_state = []
    temp_country = []
    if state_value == None or state_value == []:
        if country_value == None or country_value == []:
            if region_value == None or region_value == []:
                for var in city_list.keys():
                    temp.extend(city_list[var])
                option = set(temp)
                return [{'label':m , 'value':m} for m in option]
            else:
                for var in region_value:
                    if var in country_list.keys():
                        temp_country.extend(country_list[var])
                for var in temp_country:
                    if var in state_list.keys():
                        temp_state.extend(state_list[var])
                for var in temp_state:
                    if var in city_list.keys():
                        temp.extend(city_list[var])
                option = set(temp)
                return [{'label':m , 'value':m} for m in option]
        else:
            for var in country_value:
                if var in state_list.keys():
                    temp_state.extend(state_list[var])
            for var in temp_state:
                if var in city_list.keys():
                    temp.extend(city_list[var])
            option = set(temp)
            return [{'label':m , 'value':m} for m in option]
    else:
        for var in state_value:
            if var in city_list.keys():
                temp.extend(city_list[var])
        option = set(temp)
        return [{'label':m , 'value':m} for m in option]

def main():
    global app
    load_data()
    open_browser()
    app.layout = app_ui()
    app.title = 'Terrorism Analysis'
    app.run_server()
    app = None
    df = None
    print ("\n____EXITED____")

if __name__ == '__main__':
    main()

