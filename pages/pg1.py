import dash
import pymongo
from dash import dcc, html, callback, Output, Input, State
import plotly.express as px
import dash_bootstrap_components as dbc
from assets import youtube_dff as yd
import pandas as pd

dash.register_page(__name__, path='/', name='Home General stats')  # '/' is home page

# page 1 data


layout = html.Div(
    [
        dbc.Row([dbc.Col(
            [html.Label("Enter channel-id", className="mt-4"),
             dcc.Input(id="input-handle", type="text", placeholder="insert youtubers channel id")
             ], width=3),
            dbc.Col(
                [html.Label("Enter channel-id", className="mt-4"),
                 dcc.Input(id="input-handle-2", type="text", placeholder="insert youtubers channel id")
                 ], width={"size": 2, "offset": 6})
        ]),
        dbc.Row(
            [
                dbc.Col(
                    [html.Button(id="hit-button", n_clicks=0, children="Submit",
                                 style={"background-color": "blue", "color": "white"}, className="mt-2"
                                 )], width=2)

            ]
        ),
        dbc.Row(
            [
                dbc.Col([html.P(id="header", children="", style={'fontSize': 25})], width={"size": 3, "offset": 2}),
                dbc.Col([html.P(id="header_2", children="", style={'fontSize': 25})], width={"size": 3, "offset": 3})
            ]
        ),

        dbc.Row([
            dbc.Col(
                [html.Label("Duration of video's Vs like ,View and Comment counts", className='bg-secondary')],
                width={"size": 10, "offset": 4})
        ]), dbc.Row([html.Br()]),
        dbc.Row(
            [
                dbc.Col([dcc.RadioItems(id="rad_v_bar_2", options=[{'label': 'likes', 'value': 'likeCount'},
                                                                   {'label': 'Views', 'value': 'viewCount'},
                                                                   {'label': 'Comments', 'value': 'commentCount'}],
                                        value='likeCount', inline=True)], width={"offset": 3}),
                dbc.Col([dcc.RadioItems(id="rad_v_bar_3", options=[{'label': 'likes', 'value': 'likeCount'},
                                                                   {'label': 'Views', 'value': 'viewCount'},
                                                                   {'label': 'Comments', 'value': 'commentCount'}],
                                        value='likeCount', inline=True)], width={"offset": 3})
            ]),
        dbc.Row(
            [
                dbc.Col([dcc.Graph(id="bar_v_1", config={'displayModeBar': False})], width={"size": 6}),
                dbc.Col([dcc.Graph(id="bar_v_2", config={'displayModeBar': False})], width={"size": 6})
            ]
        ), dbc.Row([html.Br()]),

        dbc.Row([
            dbc.Col([html.Label("Video count based on duration of video in seconds", className='bg-secondary')],
                    width={"size": 10, "offset": 4})
        ]), dbc.Row([html.Br()]),

        dbc.Row(
            [
                dbc.Col([dcc.Graph(id="hist_th", config={'displayModeBar': False})], width={"size": 6}),
                dbc.Col([dcc.Graph(id="hist_th_2", config={'displayModeBar': False})], width={"size": 6})
            ]
        ), dbc.Row([html.Br()]),

        dbc.Row([
            dbc.Col([html.Label("Video count based on published day", className='bg-secondary')],
                    width={"size": 10, "offset": 4})
        ]), dbc.Row([html.Br()]),
        dbc.Row(
            [
                dbc.Col([dcc.Graph(id="bar_v_3", config={'displayModeBar': False})], width={"size": 6}),
                dbc.Col([dcc.Graph(id="bar_v_4", config={'displayModeBar': False})], width={"size": 6, "offset": 0})
            ]
        )
    ]
)


@callback(
    # Output('table-div', 'children'),
    # Output('table-div-2', 'children'),
    Output('bar_v_1', 'figure'),
    Output('bar_v_2', 'figure'),
    Output('hist_th', 'figure'),
    Output('hist_th_2', 'figure'),
    Output('bar_v_3', 'figure'),
    Output('bar_v_4', 'figure'),
    Output('header', 'children'),
    Output('header_2', 'children'),
    Input('hit-button', 'n_clicks'),
    State('input-handle', 'value'),
    State('input-handle-2', 'value'),
    Input('rad_v_bar_2', 'value'),
    Input('rad_v_bar_3', 'value')

)
def update_graph(nclicks, ch_id_text, ch_id_text_2, radio_but_1, radio_but_2):
    client = pymongo.MongoClient(
        "mongodb+srv://Amrpur:Amrith123@amr.byx5b8y.mongodb.net/?retryWrites=true&w=majority")

    def collecting_mangodb(id_text):
        db = client[id_text]
        collections_name = db.list_collection_names()[0]
        collection = db[collections_name]
        return collection
    
    def first_collection_db(ch_id_text):

        if ch_id_text in client.list_database_names():
            dff1 = pd.DataFrame(list(collecting_mangodb(ch_id_text).find()))
            dff1 = dff1.iloc[:, 2:]
            return dff1

        else:
            object_1 = yd.youtube_creator_dataframe(ch_id_text)
            object_1.save_data_mangodb()
            dff1 = pd.DataFrame(list(collecting_mangodb(ch_id_text).find()))
            dff1 = dff1.iloc[:, 2:]
            return dff1

    def second_collection_db(ch_id_text_2):

        if ch_id_text_2 in client.list_database_names():
            dff2 = pd.DataFrame(list(collecting_mangodb(ch_id_text_2).find()))
            dff2 = dff2.iloc[:, 2:]
            return dff2

        else:
            object_2 = yd.youtube_creator_dataframe(ch_id_text_2)
            object_2.save_data_mangodb()
            dff2 = pd.DataFrame(list(collecting_mangodb(ch_id_text_2).find()))
            dff2 = dff2.iloc[:, 2:]
            return dff2


    def nclicks_fig_v_bar(dff, rad_but):
        dff['viewCount'] = dff['viewCount'].apply(lambda x: 0 if x is None else int(x))
        dff['likeCount'] = dff['likeCount'].apply(lambda x: 0 if x is None else int(x))
        dff['commentCount'] = dff['commentCount'].apply(lambda x: 0 if x is None else int(x))
        dff_durationmins = dff.groupby(['durationmins']).sum()
        fig_v_bar = px.bar(data_frame=dff_durationmins, x=dff_durationmins.index, y=rad_but)
        fig_v_bar.update_xaxes(categoryorder='total descending')
        fig_v_bar.update_layout(margin=dict(l=0, r=0, t=10, b=0))
        return fig_v_bar

    def nclicks_fig_hist(df):
        dff = df
        fig_hist = px.histogram(data_frame=dff, x="durationSecs", nbins=50)
        fig_hist.update_layout(margin=dict(l=0, r=0, t=10, b=0))
        return fig_hist

    #
    def nclicks_fig_v_bar_2(df):
        dff = df
        day_df = pd.DataFrame(dff['pushblishDayName'].value_counts())
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_df = day_df.reindex(weekdays)
        fig_v_bar = px.bar(data_frame=day_df, x=day_df.index, y='pushblishDayName',
                           labels={"index": "pushblishday", "pushblishDayName": "count"})
        fig_v_bar.update_layout(margin=dict(l=0, r=0, t=10, b=0))
        return fig_v_bar

    def youtube_channel_tracer(ch_id_text, ch_id_text_2):

        if 'youtube_channel_tracer' in client.list_database_names():
            db = client['youtube_channel_tracer']
            db['Channel'].drop()
            db = client['youtube_channel_tracer']
            collection = db['Channel']
            collection.insert_one({'_id': 'Channel',"channel1": ch_id_text, "channel2": ch_id_text_2})
        else:
            db = client['youtube_channel_tracer']
            collection = db['Channel']
            collection.insert_one({"_id": "Channel", "channel1": ch_id_text, "channel2": ch_id_text_2})

    def default_youtube_channel():
        db = client['youtube_channel_tracer']
        db_collecting=db['Channel'].find_one()
        return db_collecting['channel1'],db_collecting['channel2']

    if nclicks > 0:
        df1 = first_collection_db(ch_id_text)
        df2 = second_collection_db(ch_id_text_2)

        first = df1.loc[0, "channelTitle"]
        second = df2.loc[0, "channelTitle"]

        fig_v_bar_1 = nclicks_fig_v_bar(df1, radio_but_1)
        fig_v_bar_2 = nclicks_fig_v_bar(df2, radio_but_2)

        fig_hist_1 = nclicks_fig_hist(df1)
        fig_hist_2 = nclicks_fig_hist(df2)

        fig_v_bar_3 = nclicks_fig_v_bar_2(df1)
        fig_v_bar_4 = nclicks_fig_v_bar_2(df2)


        youtube_channel_tracer(ch_id_text, ch_id_text_2)

        return fig_v_bar_1, fig_v_bar_2, fig_hist_1, fig_hist_2, fig_v_bar_3, fig_v_bar_4, first, second

    elif nclicks == 0:

        retrive_youtuber_id = default_youtube_channel()

        df1 = first_collection_db(retrive_youtuber_id[0])
        df2 = second_collection_db(retrive_youtuber_id[1])

        first = df1.loc[0, "channelTitle"]
        second = df2.loc[0, "channelTitle"]

        fig_v_bar_1 = nclicks_fig_v_bar(df1, radio_but_1)
        fig_v_bar_2 = nclicks_fig_v_bar(df2, radio_but_2)

        fig_hist_1 = nclicks_fig_hist(df1)
        fig_hist_2 = nclicks_fig_hist(df2)

        fig_v_bar_3 = nclicks_fig_v_bar_2(df1)
        fig_v_bar_4 = nclicks_fig_v_bar_2(df2)


        return fig_v_bar_1, fig_v_bar_2, fig_hist_1, fig_hist_2, fig_v_bar_3, fig_v_bar_4, first, second
