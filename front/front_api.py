import requests
import dash
from dash import Dash, Input, Output, html, dcc, ctx, no_update, callback
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import dash_table
from datetime import datetime


# Ajoute le thème Bootstrap pour l'apparence
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP,dbc.themes.SPACELAB])

nom_user = "chatvoyou"
user_id = 0

app.layout = html.Div(style={'backgroundColor': '#EDF8F8'}, children=[
    
    html.Img(src='https://www.not-only-books.fr/wp-content/uploads/2023/02/livres-realisation-creation-externalisation-edition-812x1024.png',style={'width': '40px', 'float': 'left'}),

    html.H1(children=" BiblioTech", style={'color': '#01756C', "font-weight": "bold"}),

    html.H3(children=f" Bienvenue {nom_user} !", style={'color': '#01756C', 'display': 'inline-block', 'margin-left': '20px'}),

    
    html.Div(style={'margin': '20px'}),

    # DataTable pour afficher tous les livres

    html.Div(style={'margin': '20px'}),

    dcc.Interval(
    id="load_interval", 
    n_intervals=0, 
    max_intervals=0, 
    interval=1
    ),


    dash_table.DataTable(
        id='table',
        columns=[
            {'name': 'ID', 'id': 'id'},
            {'name': 'Titre', 'id': 'title'},
            {'name': 'Auteur', 'id': 'authors'},
            # Ajoute d'autres colonnes en fonction de tes besoins
        ],
        editable=True,
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        column_selectable="single",
        row_selectable="multi",
        selected_columns=[],
        selected_rows=[],
        page_action="native",
        page_current=0,
        page_size=10,
        style_cell={
                'backgroundColor': '#01756C',
                'color': 'white',
                'fontSize': '13px',
                'textAlign': 'left'
            },
        style_header={'backgroundColor': '#01756C'},

        style_filter={
            'backgroundColor': '#EDF8F8',
        },

        style_data_conditional=[
        {
            'if': {'state': 'selected'},
            'backgroundColor': '#01756C',
            'color': '#3C3C3C',
            'border': '1px solid #01756C',  # Bordure colorée
            'textAlign': 'left',  # Aligner le texte à gauche
        }
        ],
    ),

    
    html.Div(style={'margin': '20px'}),

    # DataTable pour afficher les favoris
    dash_table.DataTable(
        id='favorites-table',
        columns=[
            {'name': 'ID', 'id': 'id'},
            {'name': 'Titre', 'id': 'title'},
            {'name': 'Auteur', 'id': 'authors'},
        ],
        editable=True,
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        row_deletable=True,
        column_selectable="single",
        row_selectable="multi",
        selected_columns=[],
        selected_rows=[],
        page_action="native",
        page_current=0,
        page_size=10,
        style_cell={
                'backgroundColor': '#01756C',
                'color': 'white',
                'fontSize': '13px',
                'textAlign': 'left'
            },

        style_filter={
            'backgroundColor': '#EDF8F8',
        },
        style_data_conditional=[
        {
            'if': {'state': 'selected'},
            'backgroundColor': '#01756C',
            'color': '#3C3C3C',
            'border': '1px solid #01756C',  # Bordure colorée
            'textAlign': 'left',  # Aligner le texte à gauche
        }
        ],
    ),

    dbc.Modal(
            [
                dbc.ModalHeader("Vous avez ajouté un livre à votre liste de lecture"),
                dbc.ModalBody(id="modal-content"),
                dbc.ModalFooter(dbc.Button("Fermer", id="close", className="ml-auto", color="success")),
            ],
            id="modal",
    ),
    
])



@app.callback(
    Output("modal", "is_open"),
    Output("modal-content", "children"),
    Input('table', 'selected_rows'),
    Input("close", "n_clicks"),
)
def open_modal(selected_rows, _):
    if ctx.triggered_id == "close":
        return False, no_update
    if selected_rows:
        last_selected_row = selected_rows[-1]
        selected_book = books_data[last_selected_row]
        title = selected_book.get("title", "Unknown Title")
        return True, f"{title}"

    return no_update, no_update

@app.callback(
    Output('table', 'data'),
    Input(component_id="load_interval", component_property="n_intervals"),
)
def get_all_books_table(n_intervals):
    global books_data  # Utilise la variable globale
    r = requests.get("http://api:5000/all_books")
    books_data = r.json()
    return books_data

@app.callback(
    Output('favorites-table', 'data'),
    Input('table', 'selected_rows'),
    prevent_initial_call=True
)

def update_favorites(selected_rows):
    global books_data  # Utilise la variable globale

    # r = requests.get("http://api:5000/users_books/"+str(user_id))
    # users_books = r.json()

    # if not selected_rows:
    #     return dash.no_update

    # selected_books = [books_data[i] for i in selected_rows]
    # return users_books + selected_books

    if not selected_rows:
        return dash.no_update

    selected_books = [books_data[i] for i in selected_rows]

    for book in selected_books:
        usersbook = {
            "book_id": book["id"],
            "user_id": user_id
        }

        r = requests.post("http://api:5000/save_book/", json=usersbook)

        if r.status_code == 409:
            print(f"Book {book['title']} already exists in the user's favorites.")

    r = requests.get(f"http://api:5000/users_books/{user_id}")
    return r.json()

"""
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
                      json={"id": id, "title": title, "authors": authors, "average_rating": average_rating,
                            "language_code": language_code, "num_pages": num_pages,
                            "rating_count": rating_count, "text_review_count": review_count,
                            "publication_date": publication_date
                            })
    return str(r.json())

@app.callback(
    Output("output_delete", "children"),
    Input("delete_all_button", "n_clicks"),
    prevent_initial_call=True
)
def delete_all(n):
    r = requests.delete("http://api:5000/delete_all")
    return str(r.json())
"""
"""
    html.Div([
        dbc.Row([
            dbc.Input(id="book_id", placeholder="ID du livre (int)"),
            dbc.Input(id='book_title', placeholder="Titre du livre (str)"),
            dbc.Input(id='book_authors', placeholder="Nom de l'auteur"),
            dbc.Input(id='book_average_rating', placeholder="Note moyenne du livre (float)"),
            dbc.Input(id='book_language_code', placeholder="Code de la langue du livre"),
            dbc.Input(id='book_num_pages', placeholder="Nombre de pages (int)"),
            dbc.Input(id='book_rating_count', placeholder="Nombre de notes (int)"),
            dbc.Input(id='book_review_count', placeholder="Nombre de revues du livre (int)"),
            dbc.Input(id='book_publication_date', placeholder="Date de publication du livre (int)"),
        ]),
        dbc.Button("POST", id="post_button", n_clicks=0),
        html.H2(id="output_post"),
        dbc.Button("GET_ALL_BOOKS", id="all_books_button", n_clicks=0),
        html.H2(id="output_get"),

        dbc.Button("DELETE_ALL_BOOKS", id="delete_all_button", n_clicks=0),
        html.H2(id="output_delete"),

    ], style={'margin': '80px'})  # Ajoute de la marge à l'élément
    """

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8050)