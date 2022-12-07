import dash
import pymongo
from dash import dcc, html, callback, Output, Input
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd

dash.register_page(__name__, name='Further Analysis')

layout = html.Div(
    [
        dbc.Row(
            [
                dbc.Col([html.P(id="header_3", children="", style={'fontSize': 25})], width={"size": 3, "offset": 2}),
                dbc.Col([html.P(id="header_4", children="", style={'fontSize': 25})], width={"size": 3, "offset": 3})
            ]
        ),
        dbc.Row([
            dbc.Col([html.Label(" like,Comment Count Vs View counts ", className='bg-secondary')],
                    width={"size": 10, "offset": 5})
        ]), dbc.Row([html.Br()]),
        dbc.Row(
            [
                dbc.Col([dcc.RadioItems(id="rad_sca_1", options=[{'label': 'likes', 'value': 'likeCount'},
                                                                 {'label': 'Comments', 'value': 'commentCount'}],
                                        value='likeCount', inline=True)], width={"offset": 4}),
                dbc.Col([dcc.RadioItems(id="rad_sca_2", options=[{'label': 'likes', 'value': 'likeCount'},
                                                                 {'label': 'Comments', 'value': 'commentCount'}],
                                        value='likeCount', inline=True)], width={"offset": 4})
            ]),
        dbc.Row(
            [
                dbc.Col([dcc.Graph(id="scatter_1", config={'displayModeBar': False})], width={"size": 6}),
                dbc.Col([dcc.Graph(id="scatter_2", config={'displayModeBar': False})], width={"size": 6})
            ]
        ),
        dbc.Row([html.Br()]),
        dbc.Row([
            dbc.Col([html.Label("Publishedday Vs Average like,Comment and View counts", className='bg-secondary')],
                    width={"size": 10, "offset": 4})
        ]), dbc.Row([html.Br()]),

        dbc.Row(
            [
                dbc.Col([dcc.Graph(id="line_1", config={'displayModeBar': False})], width={"size": 6}),
                dbc.Col([dcc.Graph(id="line_2", config={'displayModeBar': False})], width={"size": 6})
            ]
        ), dbc.Row([html.Br()]),
        dbc.Row([
            dbc.Col([html.Label("Publishedday Vs like,Comment and View counts", className='bg-secondary')],
                    width={"size": 10, "offset": 4})
        ]), dbc.Row([html.Br()]),

        dbc.Row(
            [
                dbc.Col([dcc.RadioItems(id="rad_sun_1", options=[{'label': 'views', 'value': 'viewCount'},
                                                                 {'label': 'likes', 'value': 'likeCount'},
                                                                 {'label': 'Comments', 'value': 'commentCount'}],
                                        value='likeCount', inline=True)], width={"offset": 3}),
                dbc.Col([dcc.RadioItems(id="rad_sun_2", options=[{'label': 'views', 'value': 'viewCount'},
                                                                 {'label': 'likes', 'value': 'likeCount'},
                                                                 {'label': 'Comments', 'value': 'commentCount'}],
                                        value='likeCount', inline=True)], width={"offset": 4})
            ]),
        dbc.Row(
            [
                dbc.Col([dcc.Graph(id="sun_1", config={'displayModeBar': False})], width={"size": 5}),
                dbc.Col([dcc.Graph(id="sun_2", config={'displayModeBar': False})], width={"size": 5, "offset": 2})
            ]
        ), dbc.Row([html.Br()]),
        dbc.Row([
            dbc.Col([html.Label(" Tagcount,No Word's in Title,Length Title and Emoji Count Vs View counts",
                                className='bg-secondary')],
                    width={"size": 10, "offset": 4})
        ]), dbc.Row([html.Br()]),
        dbc.Row(
            [
                dbc.Col([dcc.Graph(id="scatter_3", config={'displayModeBar': False})], width={"size": 6}),
                dbc.Col([dcc.Graph(id="scatter_4", config={'displayModeBar': False})], width={"size": 6})
            ]
        )
    ]
)


@callback(
    Output('scatter_1', 'figure'),
    Output('scatter_2', 'figure'),
    Output('line_1', 'figure'),
    Output('line_2', 'figure'),
    Output('sun_1', 'figure'),
    Output('sun_2', 'figure'),
    Output('scatter_3', 'figure'),
    Output('scatter_4', 'figure'),
    Output('header_3', 'children'),
    Output('header_4', 'children'),
    Input('rad_sca_1', 'value'),
    Input('rad_sca_2', 'value'),
    Input('rad_sun_1', 'value'),
    Input('rad_sun_2', 'value'),

)
def update_graph_second(rad_but_1, rad_but_2, rad_but_3, rad_but_4):
    client = pymongo.MongoClient(
        "mongodb+srv://Amrpur:Amrith123@amr.byx5b8y.mongodb.net/?retryWrites=true&w=majority")

    def default_youtube_channel():
        db = client['youtube_channel_tracer']
        db_collecting = db['Channel'].find_one()
        return db_collecting['channel1'], db_collecting['channel2']

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

    def second_collection_db(ch_id_text_2):
        if ch_id_text_2 in client.list_database_names():
            dff2 = pd.DataFrame(list(collecting_mangodb(ch_id_text_2).find()))
            dff2 = dff2.iloc[:, 2:]
            return dff2

    def get_fig_scatter(rad_but, df):
        dff = df
        fig_scatter = px.scatter(dff, x=rad_but, y="viewCount", trendline='ols', trendline_color_override="grey")
        fig_scatter.update_xaxes(zeroline=False, showgrid=False)
        fig_scatter.update_yaxes(zeroline=False, showgrid=False)
        fig_scatter.update_layout(margin=dict(l=0, r=0, t=10, b=0))
        return fig_scatter

    def get_fig_line(df):
        day_df = df.groupby(['pushblishDayName']).mean()
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_df = day_df.reindex(weekdays)
        fig_line = px.line(data_frame=day_df, x=day_df.index, y=['commentCount', 'likeCount', 'viewCount'],
                           markers=True, labels={'value': 'variable'})
        fig_line.update_xaxes(showgrid=False, zeroline=False)
        fig_line.update_yaxes(showgrid=False, zeroline=False)
        fig_line.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="right", x=1))
        fig_line.update_layout(margin=dict(l=0, r=0, t=10, b=0))
        return fig_line

    def get_fig_sun(rad_but, df):
        dff = df
        fig_sunburst = px.sunburst(dff, path=['weekdayVsweekend', 'pushblishDayName', 'durationmins'],
                                   values=rad_but)
        fig_sunburst.update_layout(margin=dict(l=0, r=0, t=10, b=0))
        return fig_sunburst

    def get_fig_scatter_2(df):
        fig = px.scatter(df, x=["tagsCount", 'no_words_title', 'titleLength', 'emoji_counts']
                         , y="viewCount", labels={'value': 'variable'})
        fig.update_xaxes(zeroline=False, showgrid=False)
        fig.update_yaxes(zeroline=False, showgrid=False)
        fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), legend=dict(font=dict(size=11)))
        return fig

    retrive_youtuber_id = default_youtube_channel()

    df1 = first_collection_db(retrive_youtuber_id[0])
    df2 = second_collection_db(retrive_youtuber_id[1])

    fig_scatter_1 = get_fig_scatter(rad_but_1, df1)
    fig_scatter_2 = get_fig_scatter(rad_but_2, df2)

    fig_line_1 = get_fig_line(df1)
    fig_line_2 = get_fig_line(df2)

    fig_sun_1 = get_fig_sun(rad_but_3, df1)
    fig_sun_2 = get_fig_sun(rad_but_4, df2)

    fig_scatter_3 = get_fig_scatter_2(df1)
    fig_scatter_4 = get_fig_scatter_2(df2)

    first = df1.loc[0, "channelTitle"]
    second = df2.loc[0, "channelTitle"]

    return fig_scatter_1, fig_scatter_2, fig_line_1, fig_line_2, fig_sun_1, fig_sun_2, fig_scatter_3, fig_scatter_4, first.capitalize(), second.capitalize()
