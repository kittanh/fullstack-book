import requests
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input
from dash.dependencies import Output
from dash.dependencies import State

app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1(children="Test API book"),
    dbc.Row([dbc.Input(id="book_name", placeholder="Nom du livre"),
             dbc.Input(id='book_price', placeholder="Prix du livre (entier)")]),
    dbc.Button("POST", id="post_button", n_clicks=0),
    html.H2(id="output_post"),
    dbc.Button("GET_ALL_BOOKS", id="all_books_button", n_clicks=0),
    html.H2(id="output_get"),
    dbc.Button("DELETE_ALL_BOOKS", id="delete_all_button", n_clicks=0),
    html.H2(id="output_delete")
])

@app.callback(
    Output("output_post", "children"),
    Input("post_button", "n_clicks"),
    State("book_price", "value"),
    State("book_name", "value"),
    prevent_initial_call=True

)
def post_book(n, price, name):
    r = requests.post("http://api:5000/books/", json={"name": name, "price": price})
    return str(r.json())

@app.callback(
    Output("output_get", "children"),
    Input("all_books_button", "n_clicks"),
    prevent_initial_call=True

)
def get_all_books(n):
    r = requests.get("http://api:5000/all_books")
    return str(r.json())

@app.callback(
    Output("output_delete", "children"),
    Input("delete_all_button", "n_clicks"),
    prevent_initial_call=True   
)
def delete_all(n):
    r = requests.delete("http://api:5000/delete_all")
    return str(r.json())

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8050)