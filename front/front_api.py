import requests
import dash
from dash import Dash, Input, Output, html, dcc, ctx, no_update, callback
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import dash_table
import os
from os.path import join, dirname, realpath
from flask import Flask, session
from flask_oidc import OpenIDConnect
from keycloak.keycloak_openid import KeycloakOpenID
import time

######################on attend que keycloak soit lancé##########
def wait_for_keycloak(keycloak_url, timeout=600):
    start_time = time.time()
    while True:
        try:
            response = requests.get(f"{keycloak_url}/realms/master", timeout=5)
            response.raise_for_status()

            if response.status_code == 200:
                print("Keycloak is ready!")
                time.sleep(5)
                break
        except requests.exceptions.RequestException as e:
            # Ignorer les erreurs de connexion pendant l'attente
            print(f"Keycloak n'est pas encore prêt. Attente... ({e})")

        time.sleep(1)

        if time.time() - start_time >= timeout:
            print("Timeout waiting for Keycloak.")
            break
wait_for_keycloak("http://host.docker.internal:8080/auth")
########################################################################

##########A ne faire que lors du premier appel#########################
keycloak_url = "http://host.docker.internal:8080/auth"
admin_username = "admin"
admin_password = "admin"

# Obtain an admin access token
token_url = f"{keycloak_url}/realms/master/protocol/openid-connect/token"
token_data = {
    "grant_type": "password",
    "client_id": "admin-cli",
    "username": admin_username,
    "password": admin_password,
}
token_response = requests.post(token_url, data=token_data)
token_response.raise_for_status()
admin_access_token = token_response.json()["access_token"]
headers = {
    "Authorization": f"Bearer {admin_access_token}",
    "Content-Type": "application/json",
}

# Create a new realm
def create_realm(realm_name):
    realm_url = f"{keycloak_url}/admin/realms"
    realm_data = {
        "realm": realm_name,
        "enabled": True,
        "displayName": realm_name,
        "registrationAllowed": True
    }
    requests.post(realm_url, headers=headers, json=realm_data)

# Create a new client in the realm
def create_client(client_name, realm_name, url):
    client_url = f"{keycloak_url}/admin/realms/{realm_name}/clients"
    client_data = { 
        "id": client_name,
        "clientId": client_name,
        "protocol": "openid-connect",
        "publicClient": False,
        "directAccessGrantsEnabled": True,
        "redirectUris": [url],
        "clientAuthenticatorType": "client-secret",
        "secret": "MyOwnSecret"
    }
    requests.post(client_url, headers=headers, json=client_data)
    

if requests.get(f"{keycloak_url}/admin/realms/app_realm", headers=headers).json()=={'error': 'Realm not found.'}:
    create_realm("app_realm")
    create_client("Front", "app_realm", "http://localhost:8050*")
###################################

UPLOADS_PATH = join(dirname(realpath(__file__)), 'client_secrets.json')

server = Flask(__name__)

server.config.update({
    'SECRET_KEY': 'SomethingNotEntirelySecret',
    'TESTING': True,
    'DEBUG': True,
    'OIDC_CLIENT_SECRETS': UPLOADS_PATH,
    'OIDC_OPENID_REALM': 'app_realm',
    'OIDC_SCOPES': ['openid'],
    'OIDC_INTROSPECTION_AUTH_METHOD': 'client_secret_post'
})

keycloak_openid = KeycloakOpenID(server_url=keycloak_url,
                                 client_id="Front",
                                 realm_name="app_realm",
                                 client_secret_key="MyOwnSecret")

oidc = OpenIDConnect(server)

@server.route("/")
def public_la():
    return 'Bonjour veuillez vous connecter, <a href="/dash"> CONNEXION</a>'

@server.route("/disconnect")
def logout():
    if oidc.user_loggedin:
        session.clear()
        oidc.logout()
        return'<a href="http://host.docker.internal:8080/auth/realms/app_realm/protocol/openid-connect/logout" target="_blank">Déconnecte toi ici</a>' + '\n'+ '<a href="/"> RETOUR AU LOGIN</a>'
    else:
        return"Tu n'étais pas connecté <a href=\"/\"> RETOUR AU LOGIN</a>"

@server.route("/dash")
@oidc.require_login
def show_dash():
    return app.index() +'\nPour se déconnecter, <a href="/disconnect"> DECONNEXION</a>'


# Ajoute le thème Bootstrap pour l'apparence
app = dash.Dash(server=server, routes_pathname_prefix="/dash/", add_log_handler=True,
                external_stylesheets=[dbc.themes.BOOTSTRAP,dbc.themes.SPACELAB])

rating_data = [{'average_rating': i} for i in range(0, 6)]

app.layout = html.Div(style={'backgroundColor': '#EDF8F8'}, children=[
    
    html.Div(style={'display': 'flex', 'alignItems': 'center'}, children=[
        html.Img(src='https://www.not-only-books.fr/wp-content/uploads/2023/02/livres-realisation-creation-externalisation-edition-812x1024.png', style={'width': '40px', 'float': 'left'}),
        html.H1(children=" BiblioTech", style={'color': '#01756C', "font-weight": "bold", 'margin-left': '10px'}),
        html.H4(children="", id="user-output", style={'color': '#01756C', 'margin-left': 'auto'}),
    ]),
    
    html.Div(style={'margin': '20px'}),
    
    html.H4(children="Recherchez vos prochaines lectures ", style={'color': '#01756C', 'margin-left': '10px'}),

    dcc.Input(id='dummy-input', value='', style={'display': 'none'}),

    dash_table.DataTable(
        id='table',
        columns=[
            {'name': 'ID', 'id': 'id'},
            {'name': 'Titre', 'id': 'title'},
            {'name': 'Auteur', 'id': 'authors'},
            {'name': 'Note', 'id': 'average_rating'},
            # Ajoute d'autres colonnes en fonction de tes besoins
        ],
        #editable=True,
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        column_selectable="single",
        row_selectable="single",
        selected_columns=[],
        selected_rows=[],
        page_action="native",
        page_current=0,
        page_size=10,
        style_cell={
                'backgroundColor': '#01756C',
                'color': 'white',
                'fontSize': '13px',
                'textAlign': 'left',
                'overflow': 'hidden',  # Masquer le contenu dépassant de la cellule
                'textOverflow': 'ellipsis',
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


    html.Div(style={'width': '30%', 'padding': '20px'}, children=[
            dash_table.DataTable(
                id='rating-table',
                data=rating_data,
                columns=[
                    {'name': 'Livres notés plus de ', 'id': 'average_rating'}
                ],
                filter_action="native",
                sort_action="native",
                sort_mode="multi",
                row_selectable="single",
                column_selectable="single",
                selected_columns=[],
                selected_rows=[0],
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
                        'border': '1px solid #01756C',
                        'textAlign': 'left',
                    }
                ],
            ),
        ]), #width=3  # Adjust the width as needed


    html.Div(style={'margin': '20px'}),


    html.H4(children="Votre liste de lecture ", style={'color': '#01756C', 'margin-left': '10px'}),

    # DataTable pour afficher les favoris
    dash_table.DataTable(
        id='favorites-table',
        columns=[
            {'name': 'ID', 'id': 'id'},
            {'name': 'Titre', 'id': 'title'},
            {'name': 'Auteur', 'id': 'authors'},
            # {'name': 'Statut', 'id': 'status'},
            # {'name': 'Note', 'id': 'personal_rating'}
        ],
        #editable=True,
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        row_deletable=True,
        column_selectable="single",
        #row_selectable="multi",
        selected_columns=[],
        selected_rows=[],
        page_action="native",
        page_current=0,
        page_size=10,
        style_cell={
                'backgroundColor': '#01756C',
                'color': 'white',
                'fontSize': '13px',
                'textAlign': 'left',
                'overflow': 'hidden',  # Masquer le contenu dépassant de la cellule
                'textOverflow': 'ellipsis',
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

    html.Div(style={'margin': '20px'}),

    html.H4(children="Consultez les lectures des autres utilisateurs", style={'color': '#01756C', 'margin-left': '10px'}),

    dbc.Row([
        dbc.Col(
            html.Div(style={'width': '100%', 'padding': '20px', 'float': 'right'}, children=[
                dash_table.DataTable(
                    id='users-table',
                    columns=[
                        {'name': 'Utilisateur', 'id': 'id'}
                    ],
                    filter_action="native",
                    sort_action="native",
                    sort_mode="multi",
                    row_selectable="single",
                    column_selectable="single",
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
                            'border': '1px solid #01756C',
                            'textAlign': 'left',
                        }
                    ],
                ),
            ]), width=3  # Adjust the width as needed
        ),

        dbc.Col(
            html.Div(style={'width': '100%', 'padding': '20px', 'float': 'right'}, children=[
                dash_table.DataTable(
                    id='usersbooks-table',
                    columns=[
                        {'name': 'ID', 'id': 'id'},
                        {'name': 'Titre', 'id': 'title'},
                        {'name': 'Auteur', 'id': 'authors'},
                    ],
                    filter_action="native",
                    sort_action="native",
                    sort_mode="multi",
                    column_selectable="single",
                    selected_columns=[],
                    selected_rows=[],
                    page_action="native",
                    page_current=0,
                    page_size=10,
                    style_cell={
                        'backgroundColor': '#01756C',
                        'color': 'white',
                        'fontSize': '13px',
                        'textAlign': 'left',
                        'overflow': 'hidden',  # Masquer le contenu dépassant de la cellule
                        'textOverflow': 'ellipsis',
                    },
                    style_filter={
                        'backgroundColor': '#EDF8F8',
                    },
                    style_data_conditional=[
                        {
                            'if': {'state': 'selected'},
                            'backgroundColor': '#01756C',
                            'color': '#3C3C3C',
                            'border': '1px solid #01756C',
                            'textAlign': 'left',
                        }
                    ],
                ),
            ]), width=9  # Adjust the width as needed
        ),
    ]),

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
    Output(component_id='user-output', component_property='children'),
    Input('dummy-input', 'value'),
    prevent_initial_call=False
)
def update_output_div(n):
    global username 
    username = oidc.user_getfield('preferred_username')
    user = {"id": username}
    requests.post("http://host.docker.internal:5000/users/", json=user)
    return f'Bienvenue {username} !'

 

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
    #Input('dummy-input', 'value'),
    Input('rating-table', 'selected_rows'),
    prevent_initial_call=False
)

def get_all_books_table(selected_rows):
    
    max_retries = 3
    retries = 0

    global books_data  # Utilise la variable globale

    avg_rating = selected_rows[0]
    while retries < max_retries:
        try:
            # r = requests.get("http://api:5000/all_books")
            
            r = requests.get(f"http://host.docker.internal:5000/books_avg_sup/{avg_rating}")
            r.raise_for_status()
            books_data = r.json()
            # Process the data as needed
            return books_data
        except requests.exceptions.RequestException:
            retries += 1

    return []


@app.callback(
    Output('favorites-table', 'data'),
    [#Input('dummy-input', 'value'),
     Input('table', 'selected_rows'),
     Input('favorites-table', 'data_previous')],
    [State('favorites-table', 'data')],
    prevent_initial_call=True,
    allow_duplicate=True 
)

def update_favorites(selected_rows, data_previous, data_current): #value,
    #global books_data  # Utilise la variable globale
    ctx = dash.callback_context

    if not ctx.triggered_id:
        raise dash.exceptions.PreventUpdate

    # Check which input triggered the callback
    triggered_component_id = ctx.triggered_id.split(".")[0]

    # if triggered_component_id == "dummy-input":
    #     r = requests.get(f"http://api:5000/users_books/{username}")
    #     return r.json()
    
    if triggered_component_id == "table":
        # Logic for updating favorites
        if not selected_rows:
            return dash.no_update
        

        selected_books = [books_data[i] for i in selected_rows]

        for book in selected_books:
            usersbook = {
                "book_id": book["id"],
                "user_id": username
            }

            r = requests.post("http://host.docker.internal:5000/save_book/", json=usersbook)

            if r.status_code == 409:
                print(f"Book {book['title']} already exists in the user's favorites.")

        r = requests.get(f"http://host.docker.internal:5000/users_books/{username}")
        return r.json()

    elif triggered_component_id == "favorites-table":
        # Logic for deleting a book row
        if data_previous:
            print("Deleting book row...")

            book =  [i for i in data_previous if i not in data_current]
            if book is not None:
                delete_book_from_usersbooks(book[0]["id"])
                # data_previous.pop(book)
                # return data_previous

    return dash.no_update

def delete_book_from_usersbooks(book_id):

    if book_id is not None:
        # Make a request to the API or use your database deletion logic
        usersbook_id = str(book_id) + "_" + str(username)  
        requests.delete(f"http://host.docker.internal:5000/unfav_book/{usersbook_id}")
        print(f"Deleted book with ID {book_id}")

@app.callback(

    Output('users-table', 'data'),
    Input('dummy-input', 'value'),
    prevent_initial_call=False
)

def get_all_users_table(n):
    global users_data
    max_retries = 3
    retries = 0
    while retries < max_retries:
        try:
            r = requests.get("http://host.docker.internal:5000/all_users")
            r.raise_for_status()
            users_data = r.json()
            # Process the data as needed
            return users_data
        except requests.exceptions.RequestException:
            retries += 1

    return []


@app.callback(
    Output('usersbooks-table', 'data'),
    Input('users-table', 'selected_rows'),
    prevent_initial_call=True,
    allow_duplicate=True 
)

def update_favorites(selected_rows):
    user_id = [users_data[i] for i in selected_rows][0]["id"]
    r = requests.get(f"http://host.docker.internal:5000/users_books/{user_id}")
    r.raise_for_status()
    return r.json()


if __name__ == '__main__':
    server.run(debug=True, host="0.0.0.0", port=8050)