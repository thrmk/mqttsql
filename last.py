import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import sqlite3
from dash.dependencies import Input, Output, State
import paho.mqtt.client as mqtt
import time
import pandas as pd
import sqlite3
import os
import base64
from six.moves.urllib.parse import quote
from sqlalchemy import create_engine
from datetime import datetime,timedelta


FA ="https://use.fontawesome.com/releases/v5.8.1/css/all.css"

server = Flask(__name__)
#server.config['DEBUG'] = True
server.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///test.db')

#server.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(server)
db_URI = os.environ.get('DATABASE_URL', 'sqlite:///test.db')
engine = create_engine(db_URI)

class User(db.Model):
    __tablename__ = 'datatable'

    id = db.Column(db.Integer, primary_key=True)
    stamp = db.Column(db.String(26))
    devId = db.Column(db.String(15))
    SPA = db.Column(db.String(10))
    TA = db.Column(db.String(10))

    def __repr__(self):
        return '<User %r %r  %r %r>' % (self.stamp, self.devId, self.SPA, self.TA)
db.create_all()
def on_connect(client, userdata, flags, rc):
    print("Connected!", rc)

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed:", str(mid), str(granted_qos))

def on_unsubscribe(client, userdata, mid):
    print("Unsubscribed:", str(mid))

def on_publish(client, userdata, mid):
    print("Publish:", client)

def on_log(client, userdata, level, buf):
    print("log:", buf)

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")

def on_message(client, userdata, message):

    payload = str(message.payload.decode("utf-8"))
    print("payload=",payload)
    data = dict(x.split(": ") for x in payload.split(" , "))
    admin = User(stamp=str(datetime.now()+timedelta(minutes=330)),devId=data['devId'],SPA=data['SPA'],TA=data['TA'])
    db.session.add(admin)
    db.session.commit()
client = mqtt.Client()
print("client=",client)

client.on_subscribe = on_subscribe
client.on_unsubscribe = on_unsubscribe
client.on_connect = on_connect
client.on_message = on_message
time.sleep(1)

subtop="tracker/device/sub"
pubtop="tracker/device/pub"
client.username_pw_set("cbocdpsu", "3_UFu7oaad-8")
client.connect('soldier.cloudmqtt.com', 14035,60)
client.loop_start()
client.subscribe(subtop)
client.loop()

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "15rem",
    "padding": "2rem 2rem",
    "fontSize":"30rem"
}



navbar = dbc.Navbar(
           html.Div(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.NavbarBrand(
                                html.H2("Logo or Title",style={"align":"center"}),style={"fontSize":"60px","padding-left":"10rem"})),
                        #dbc.NavbarToggler(id="navbar-toggler"),
                        # dbc.Collapse(sidebar,id="sidebar-collapse",navbar=True),
                        # dbc.Collapse(button,id="button-collapse",navbar=True)
                        ],
                    align="center",
                    no_gutters=True,
                ),
             ),
          )

content = html.Div(id="page-content")#, style=CONTENT_STYLE)



app = dash.Dash(__name__,server=server,external_stylesheets=[dbc.themes.BOOTSTRAP, FA])

app.config['suppress_callback_exceptions']=True


app.layout = html.Div([navbar,content,
    dcc.Location(id='url', refresh=False),

#    html.Div([
        html.Div([
            
            dcc.Tabs(id="tabs", children=[
                dcc.Tab(label='Graph', value='/page-1'),
                dcc.Tab(label='Table', value='/page-2'),
                dcc.Tab(label='Read', value='/page-3'),
                dcc.Tab(label='Write', value='/page-4'),
],value='/page-1')
 #           ]),
  #      ])#,value='/page-1'
    ]),
#    html.Div(id='page-content'),
])    

page_2_graph = html.Div([
    html.H3('Graph'),
    dcc.Dropdown(
        id='devices',
        options=[
            {'label': 'R1', 'value': 'R1 '},
            {'label': 'G2', 'value': 'G2 '},
            {'label': 'R2', 'value': 'R2 '}
        ],
        value='R1 ', style={"width":"auto"}),
html.Div(id='dd-output-container'),
    dcc.Graph(id='graph-with-slider'),
    dcc.Interval(
            id='interval-component',
            interval=1*1000, # in milliseconds
            n_intervals=0
        ),
    dcc.Link(href='/page-1'),
])

page_1_table = html.Div([
                html.H3('Table Data'),
#               html.Table(id="live-update-text"),
               html.A(
                   dbc.Button(
            "Download CSV",
            id='download-link',color="primary"),
            style={"padding": "auto"},#"1000px"},

            download="rawtable.csv",
            href="",target="_blank")
            ,
 
            dcc.Link(href='/page-2'),
            html.Div([
            html.Table(id="live-update-text")],style={"overflowY":"scroll"})

])

         

page_3_read = html.Div([
    html.H4('You can read the data using these dropdown buttons'),
    dcc.Dropdown(
        id='devices1',
        options=[
            {'label': 'R1', 'value': 'R1'},
            {'label': 'G2', 'value': 'G2'},
            {'label': 'R2', 'value': 'R2'}
        ],
        value='', style={"width":"auto"}),
    dcc.Dropdown(
        id='options1',
        options=[
            {'label': 'GETALL', 'value': 'GETALL'},
            {'label': 'LAT', 'value': 'LAT'},
            {'label': 'LONGITUDE', 'value': 'LONGITUDE'},
            {'label': 'RTC', 'value': 'RTC'},
            {'label': 'SUN', 'value': 'SUN'},
            {'label': 'TRACKER', 'value': 'TRACKER'},
            {'label': 'ZONE', 'value': 'ZONE'},
            {'label': 'MODE', 'value': 'MODE'},
            {'label': 'HR', 'value': 'HR'},
            {'label': 'MIN', 'value': 'MIN'},
            {'label': 'SEC', 'value': 'SEC'},
            {'label': 'DATE', 'value': 'DATE'},
            {'label': 'MONTH', 'value': 'MONTH'},
            {'label': 'YEAR', 'value': 'YEAR'},
                    ],
        value='', style={"width":"auto"}),
    #inline=True,
    dbc.Button("Read", id="buttons1"),

html.Div(id='display'),
     dcc.Link(href='/page-3'),

])

page_4_write=html.Div([
    html.H4('Using these you can write the commands for setting the values in the device'),
    dcc.Dropdown(
        id='device',
        options=[
            {'label': 'R1 ', 'value': 'R1'},
            {'label': 'G2 ', 'value': 'G2'},
            {'label': 'R2 ', 'value': 'R2'}
        ],
        value='',style={"width":"auto"}
    ),
    #html.H4(''),
    dcc.Dropdown(
        id='options',
        options=[
            {'label': 'LAT', 'value': 'LAT'},
            {'label': 'LONGITUDE', 'value': 'LONGITUDE'},
            {'label': 'SEC', 'value': 'SEC'},
            {'label': 'MIN', 'value': 'MIN'},
                        {'label': 'HOUR', 'value': 'HR'},
            {'label': 'DATE', 'value': 'DATE'},
            {'label': 'MONTH', 'value': 'MONTH'},
            {'label': 'YEAR', 'value': 'YEAR'},
            {'label': 'EAST', 'value': 'EAST'},
            {'label': 'WEST', 'value': 'WEST'},
            {'label': 'TIMEZONE', 'value': 'TIMEZONE'},
            {'label': 'REVLIMIT', 'value': 'REVLIMIT'},
            {'label': 'FWDLIMIT', 'value': 'FWDLIMIT'},
            {'label': 'AUTOMODE', 'value': 'AUTOMODE'},
            {'label': 'MANUALMODE', 'value': 'MANUALMODE'},
        ],
        value='',style={"width":"auto"}
    ),
  dcc.Input(id="input2", type="text"),
  html.Div(id="output"),
        dbc.Button("Write", id="write button"),
            dcc.Link(href='/page-4'),

        ],
)
def table(rows):

    table_header=[
        html.Thead(html.Tr([html.Th('Id'),html.Th('stamp'),html.Th('devId'),html.Th('sun angle') ,html.Th('tracker angle')#, html.Th('motor status') ,
         ]))]
    table_body=[
        html.Tbody(html.Tr([html.Td(dev.id),html.Td(dev.stamp),html.Td(dev.devId),html.Td(dev.SPA),html.Td(dev.TA)]))for dev in rows]
    table=dbc.Table(table_header+table_body,bordered=True,striped=True,hover=True,style={"backgroundColor":"white"})
    return table

@app.callback(
        Output('display', 'children'),
        [Input('devices1', 'value'),Input('options1', 'value'),Input('buttons1','n_clicks')])

def output(val1,val2,n):
    if n:
        client.publish(pubtop,"{} READ:{}".format(val1,val2))
        return "published for getting {}".format(val2)

@app.callback(
        Output('output', 'children'),
        [Input('device', 'value'),Input('options', 'value'),Input('input2','value'),Input('write button', 'n_clicks')])

def update_output(valueDEV,valueOP,value2,x):
    print("dev=",valueDEV,"options=",valueOP,"value=",value2)
    list1=["EAST","WEST","AUTOMODE","MANUALMODE","STOP"]
    if ((valueOP in list1) and (x is not None)):
        client.publish(pubtop,"{} WRITE:{}".format(valueDEV,valueOP))


        print("executing")
        return 'You have published "{} write {}"'.format(valueDEV,valueOP)

    elif((value2 != None) and (x is not None)):
        client.publish(pubtop,"{} WRITE:{}_{}".format(valueDEV,valueOP,value2))


        return 'You have published "{} {} write {}"'.format(valueDEV,valueOP,value2)
@app.callback(
    Output('graph-with-slider', 'figure'),
    [Input('devices', 'value')])

def update_figure(selected_device):
    connection1 = engine#.connnect()
    df=pd.read_sql("select * from datatable",connection1)
    filtered_df = df[df.devId == selected_device]
    print("filtered df=",filtered_df)

    return {
                                'data': [
                                    {'x': filtered_df.stamp, 'y':filtered_df.SPA
                                    #.where(df.devname=='dev_01')
                                    , 'name': 'SPA'},
                                    {'x': filtered_df.stamp, 'y':filtered_df.TA
                                                                  , 'name': 'TA'}, ],
            'layout': {
                'title': 'SPA and TA'
                }}


@app.callback(Output("live-update-text", "children"),
              [Input("live-update-text", "className")])
def update_output_div(input_value):

    rows = User.query.all()
    return [html.Table(table(rows)
        )]


#@app.callback(Output("download-link", "url"),
@app.callback(Output("download-link", "url"),
              [Input("downoad-link", "className")])
def update_download_link(input_value):
    connection1 = engine
    df=pd.read_sql("select * from datatable",connection1)
    cv = df.to_csv(index=False, encoding='utf-8')
    cv = "data:text/csv;charset=utf-8,%EF%BB%BF" + quote(cv)
    return cv

@app.callback(dash.dependencies.Output('url', 'pathname'),
              [dash.dependencies.Input('tabs', 'value')])
def tab_updates_url(value):
    return value
    
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')],
              )
def display_page(pathname):
    if pathname == '/page-2':
        return page_1_table
    elif pathname == '/page-1':
        return page_2_graph
    elif pathname == '/page-3':
        return page_3_read
    elif pathname =='/page-4':
        return page_4_write
    #else:
     #   pathname == '/page-1'
      #  return page_2_graph

        

#@app.callback(dash.dependencies.Output('url', 'pathname'),
#              [dash.dependencies.Input('tabs', 'value')])
def tab_updates_url(value):
    return value


if __name__ == '__main__':
    app.run_server(debug=True,threaded=False)#, **flask_run_options)#False)

