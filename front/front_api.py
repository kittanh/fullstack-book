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
    dbc.Row([dbc.Input(id="book_id", placeholder="ID du livre (int)"),
             dbc.Input(id='book_title', placeholder="Titre du livre (str)"),
             dbc.Input(id='book_authors', placeholder="Nom de l'autheur"),
             dbc.Input(id='book_average_rating', placeholder="Note moyenne du livre (float)"),
             dbc.Input(id='book_language_code', placeholder="Code de la langue du livre"),
             dbc.Input(id='book_num_pages', placeholder="Nombre de pages (int)"),
             dbc.Input(id='book_rating_count', placeholder="Nombre de notes (int)"),
             dbc.Input(id='book_review_count', placeholder="Nombre de revus du livre (int)"),
             dbc.Input(id='book_publication_date', placeholder="Date de publication du livre (int)"),]),
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
    State("book_id", "value"),
    State("book_title", "value"),
    State("book_authors", "value"),
    State("book_average_rating", "value"),
    State("book_language_code", "value"),
    State("book_num_pages", "value"),
    State("book_rating_count", "value"),
    State("book_review_count", "value"),
    State("book_publication_date", "value"),

    prevent_initial_call=True
)
def post_book(n, id, title, authors, average_rating, language_code, num_pages, rating_count,
               review_count, publication_date):
    r = requests.post("http://api:5000/books/",
                      json={"id": id, "title": title, "authors": authors,"average_rating": average_rating,
                            "language_code": language_code,"num_pages": num_pages,
                            "rating_count": rating_count,"text_review_count": review_count,
                            "publication_date": publication_date
                            })
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