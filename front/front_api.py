# Importez les modules nécessaires
import requests
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

# Créer l'application Dash
app = dash.Dash(__name__)

# Mise en page de l'application Dash
app.layout = html.Div(children=[
    html.H1(children="Book Search Engine"),
    dbc.Row([
        dbc.Input(id="search_input", placeholder="Enter book title"),
        dbc.Button("Search", id="search_button", n_clicks=0),
    ]),
    html.H2(id="search_output"),
])

# Callback pour effectuer la recherche et afficher les résultats
@app.callback(
    Output("search_output", "children"),
    Input("search_button", "n_clicks"),
    State("search_input", "value"),
    prevent_initial_call=True
)
def search_books(n, title):
# Modifiez cette ligne dans le fichier front_api.py
    r = requests.get("http://api:5000/search_books/?title={title}")
    books = r.json()
    
    if not books:
        return "No books found with the given title"
    
    book_list = [
        f"{book.title} by {book.authors}, Rating: {book.average_rating}" 
        for book in books
    ]
    
    return html.Ul([html.Li(book) for book in book_list])

# Exécuter l'application Dash
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8050)
