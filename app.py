import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import mysql_utils as sqlDB
import neo4j_utils as neo4jDB
import mongodb_utils as mongoClass

# intialize the mongoDB connection... neo4j and SQL connections are initialized on query
mongoDB = mongoClass.MongoDBClient()
# commonly used query functions from various databases
def get_universities():
    query = "SELECT DISTINCT name FROM university"
    df = sqlDB.fetch_data(query)
    return df['name'].tolist()

# Function to get list of research interests
def get_research_interests():
    query = "SELECT DISTINCT name FROM keyword"
    df = sqlDB.fetch_data(query)
    return df['name'].tolist()

# Function to fetch the number of universities
def get_universities_count():
    query = "SELECT COUNT(DISTINCT name) as count FROM university"
    df = sqlDB.fetch_data(query)
    return df['count'][0]

def get_faculty_names():
    query = "MATCH (f:Faculty) RETURN f.name AS name"
    result = neo4jDB.run_query(query)
    return [record['name'] for record in result]

def get_publication_titles():
    query = {}
    projection = {"_id": 0, "title": 1}
    result = mongoDB.find("academicworld", "publications", query, projection)
    return [record["title"] for record in result]

def get_faculty_names_mongo():
    query = {}
    projection = {"_id": 0, "name": 1}
    result = mongoDB.find("academicworld", "faculty", query, projection)
    return [record['name'] for record in result]

def get_keywords():
    pipeline = [
        {"$unwind": "$keywords"},
        {"$group": {"_id": "$keywords.name"}}
    ]
    result = mongoDB.aggregate("academicworld", "publications", pipeline)
    keywords = [record["_id"] for record in result]
    return keywords

# Initialize the Dash app
app = dash.Dash(__name__)

# App layout
app.layout = html.Div([
    html.H1("Explore Research Impact", style={'textAlign': 'center'}),
    dcc.Interval(
        id='interval-component',
        interval=60*60*1000,  # in milliseconds, update every hour
        n_intervals=0
    ),
    html.Div([
        html.Div([
            html.Label('Select Range for Top Universities:', style={'fontWeight': 'bold'}),
            dcc.RangeSlider(
                id='range-slider',
                min=1,
                max=20,
                step=1,
                marks={1: '1', 5: '5', 10: '10', 15: '15', 20: '20'},
                value=[1, 10]
            )], style={'width': '60%', 'display': 'inline-block'}),
        html.Div([            
            html.Label('Select University:', style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='university-dropdown',
                options=[{'label': name, 'value': name} for name in get_universities()],
                value=get_universities()[0],
                style={'width': '100%'}
            )], style={'width': '30%', 'display': 'inline-block'})
    ], style={'display': 'flex', 'justify-content': 'space-between', 'marginBottom': 20}), 
    html.Div([
        html.Div([
            dcc.Graph(id='top-universities-publications-graph', style={'width': '100%'})],
            style={'width': '30%', 'display': 'inline-block'}),
        html.Div([    
            dcc.Graph(id='top-universities-citations-graph', style={'width': '100%'})], 
            style={'width': '30%', 'display': 'inline-block'}),
        html.Div([
            dcc.Graph(id='top-research-areas-pie', style={'marginTop': 20, 'height': 400})
        ], style={'width': '40%', 'display': 'inline-block', 'verticalAlign': 'top'})
    ], style={'display': 'flex', 'justify-content': 'space-between', 'marginBottom': 20}),
    html.Div([
        
        html.Div([
            html.H2("Explore What's Your Research Interest?", style={'textAlign': 'center'}),
            dcc.Dropdown(
                id='research-interest-input',
                options=[{'label': name, 'value': name} for name in get_research_interests()],
                placeholder='Enter or select research interest...',
                #style={'width': '80%', 'marginRight': 10},
                searchable=True
            ),
            html.Button('Search', id='research-interest-button', n_clicks=0)
        ], style={'width': '50%', 'display': 'inline-block'}),

        
        html.Div([
            html.H2("Search Faculty Contact Information", style={'textAlign': 'center'}),
            dcc.Dropdown(
                id='faculty-name-input',
                options=[{'label': name, 'value': name} for name in get_faculty_names()],
                placeholder='Select or search for faculty name...',
                #style={'width': '80%', 'marginRight': 10},
                searchable=True
            ),
            html.Button('Search', id='faculty-search-button', n_clicks=0)
        ], style={'width': '30%', 'display': 'inline-block'}),



    ], style={'display': 'flex', 'justify-content': 'space-between', 'marginBottom': 20}),
    html.Div([
        html.Div([
            html.Div([
                html.H3("Top Universities"),
                html.Table(id='top-universities-table')
            ], style={'width': '45%', 'display': 'inline-block', 'verticalAlign': 'top', 'paddingRight':'50px'}),
            html.Div([
                html.H3("Top Faculty Members"),
                html.Table(id='top-faculty-table')
            ], style={'width': '45%', 'display': 'inline-block', 'verticalAlign': 'top'})
        ], style={'width': '50%', 'display': 'inline-block'}),
        html.Div(id='faculty-contact-info', style={'width': '30%', 'display': 'inline-block'})
    ], style={'display': 'flex', 'justify-content': 'space-between', 'marginBottom': 20}),

    # mongo db widgets
    html.Div([
            html.Div([
                html.H1("Top Publications by Keyword", style={'textAlign': 'center'}),
                dcc.Dropdown(
                    id='keyword-dropdown',
                    options=[{'label': keyword, 'value': keyword} for keyword in get_keywords()],
                    placeholder='Select a keyword...',
                    style={'width': '80%', 'marginRight': 10},
                    searchable=True
                ),
                html.Button('Search', id='keyword-search-button', n_clicks=0),
                html.Div(id='top-publications-by-keyword', style={'textAlign': 'center'})],
            style={'width' : '30%', 'display' : 'inline-block'}),

            html.Div([
                html.H2("Update Faculty Contact Information", style={'textAlign': 'center'}),
                html.Div([
                    dcc.Dropdown(
                        id='faculty-dropdown',
                        options=[{'label': name, 'value': name} for name in get_faculty_names()],
                        placeholder='Select a faculty member...',
                        style={'width': '80%', 'marginRight': '10px', 'paddingRight': '20px'},
                        searchable=True
                    ),
                    html.Button('Select', id='faculty-select-button', n_clicks=0)
                ], style={'display': 'flex', 'justifyContent': 'center', 'marginBottom': 20}),
                #html.Div(id='faculty-contact-info', style={'textAlign': 'center'}),
                
            ], style={'width' : '30%', 'display' : 'inline-block'}),
            html.Div([
                html.H2("Update Faculty Email", style={'textAlign': 'center'}),
                html.Div([
                    html.Label('New Email:', style={'fontWeight': 'bold'}),
                    dcc.Input(id='email-input', type='email', style={'width': '80%', 'marginRight': '10px', 'paddingRight': '20px'}),
                    html.Button('Update Email', id='email-update-button', n_clicks=0)
                ], style={'display': 'flex', 'justifyContent': 'center', 'marginBottom': 20}),
                html.Div(id='email-update-status', style={'textAlign': 'center'}),
                html.H2("Update Faculty Phone", style={'textAlign': 'center'}),
                html.Div([
                    html.Label('New Phone:', style={'fontWeight': 'bold'}),
                    dcc.Input(id='phone-input', type='text', style={'width': '80%', 'marginRight': '10px', 'paddingRight': '20px'}),
                    html.Button('Update Phone', id='phone-update-button', n_clicks=0)
                ], style={'display': 'flex', 'justifyContent': 'center', 'marginBottom': 20}),
                html.Div(id='phone-update-status', style={'textAlign': 'center'})
            ], style={'width' : '30%', 'display' : 'inline-block'})

    ], style={'display': 'flex', 'justify-content': 'space-between', 'marginBottom': 20})

])
# Neo4j widgets 
# Callback to update faculty email
@app.callback(
    Output('email-update-status', 'children'),
    Input('email-update-button', 'n_clicks'),
    State('faculty-dropdown', 'value'),
    State('email-input', 'value')
)
def update_faculty_email(n_clicks, faculty_name, new_email):
    if n_clicks > 0 and faculty_name and new_email:
        query = """
        MATCH (f:Faculty {name: $name})
        SET f.email = $email
        RETURN f.name AS name, f.email AS email
        """
        result = neo4jDB.run_query(query, {'name': faculty_name, 'email': new_email})
        if result:
            info = result[0]
            return html.P(f"Updated email for {info['name']}: {info['email']}")
        else:
            return html.P("Failed to update email.")
    return html.Div()

# Callback to update faculty phone
@app.callback(
    Output('phone-update-status', 'children'),
    Input('phone-update-button', 'n_clicks'),
    State('faculty-dropdown', 'value'),
    State('phone-input', 'value')
)
def update_faculty_phone(n_clicks, faculty_name, new_phone):
    if n_clicks > 0 and faculty_name and new_phone:
        query = """
        MATCH (f:Faculty {name: $name})
        SET f.phone = $phone
        RETURN f.name AS name, f.phone AS phone
        """
        result = neo4jDB.run_query(query, {'name': faculty_name, 'phone': new_phone})
        if result:
            info = result[0]
            return html.P(f"Updated phone for {info['name']}: {info['phone']}")
        else:
            return html.P("Failed to update phone.")
    return html.Div()
# MongoDB Widgets
@app.callback(
    Output('top-publications-by-keyword', 'children'),
    Input('keyword-search-button', 'n_clicks'),
    State('keyword-dropdown', 'value')
)
def display_top_publications_by_keyword(n_clicks, keyword):
    if n_clicks > 0 and keyword:
        pipeline = [
            {"$match": {"keywords.name": keyword}},
            {"$unwind": "$keywords"},
            {"$match": {"keywords.name": keyword}},
            {"$sort": {"numCitations": -1}},
            {"$limit": 5},
            {"$project": {"title": 1, "numCitations": 1}}
        ]
        results = mongoDB.aggregate("academicworld", "publications", pipeline)
        if results:
            return html.Div([
                html.Table([
                    html.Tr([html.Th("Publication Title"), html.Th("#Citations")])
                ] + [
                    html.Tr([html.Td(pub['title']), html.Td(pub['numCitations'])])
                    for pub in results
                ])
            ])
        else:
            return html.P("No publications found for the selected keyword.")
    return html.Div()


@app.callback(
    Output('top-universities-publications-graph', 'figure'),
    Output('top-universities-citations-graph', 'figure'),
    Input('interval-component', 'n_intervals'),
    Input('range-slider', 'value')
)
def update_top_universities(n, range_values):
    start, end = range_values

    # Query for top universities by publications
    query_publications = """
    SELECT * FROM TopUniversitiesByPublications
    LIMIT %s OFFSET %s
    """
    df_publications = sqlDB.fetch_data(query_publications, params=(end - start + 1, start - 1))

    # Query for top universities by citations
    query_citations = """
    SELECT university.name, SUM(publication.num_citations) as total_citations 
    FROM university 
    JOIN faculty ON university.id = faculty.university_id 
    JOIN faculty_publication fp ON faculty.id = fp.faculty_Id 
    JOIN publication ON publication.id =  fp.publication_Id
    GROUP BY university.name 
    ORDER BY total_citations DESC
    LIMIT %s OFFSET %s
    """
    df_citations = sqlDB.fetch_data(query_citations, params=(end - start + 1, start - 1))

    fig_publications = {
        'data': [
            {
                'x': df_publications['total_publications'], 
                'y': df_publications['university_name'], 
                'type': 'bar', 
                'orientation': 'h',
                'name': 'Total Publications',
                'marker': {'color': '#1f77b4'},
                'hoverinfo': 'x+y'
            }
        ],
        'layout': {
            'title': 'Top Universities by Publications',
            'xaxis': {'title': 'Total Publications'},
            'yaxis': {'title': 'University', 'automargin': True, 'tickfont': {'size': 10}},
            'hovermode': 'closest',
            'margin': {'l': 150, 'r': 10, 't': 50, 'b': 50},
            'height': 400
        }
    }

    fig_citations = {
        'data': [
            {
                'x': df_citations['total_citations'], 
                'y': df_citations['name'], 
                'type': 'bar', 
                'orientation': 'h',
                'name': 'Total Citations',
                'marker': {'color': '#ff7f0e'},
                'hoverinfo': 'x+y'
            }
        ],
        'layout': {
            'title': 'Top Universities by Citations',
            'xaxis': {'title': 'Total Citations'},
            'yaxis': {'title': 'University', 'automargin': True, 'tickfont': {'size': 10}},
            'hovermode': 'closest',
            'margin': {'l': 150, 'r': 10, 't': 50, 'b': 50},
            'height': 400
        }
    }

    return fig_publications, fig_citations

@app.callback(
    Output('top-research-areas-pie', 'figure'),
    Input('university-dropdown', 'value')
)
def update_top_research_areas(selected_university):
    query = """
    SELECT k.name as research_area, COUNT(DISTINCT fp.publication_Id) as publication_count
    FROM university 
    JOIN faculty ON university.id = faculty.university_id 
    JOIN faculty_publication fp ON faculty.id = fp.faculty_Id 
    JOIN publication ON publication.id =  fp.publication_Id
    JOIN Publication_Keyword pk ON publication.id = pk.publication_id
    JOIN keyword k ON k.id = pk.keyword_id
    WHERE university.name = %s
    GROUP BY k.name
    ORDER BY publication_count DESC
    LIMIT 10
    """
    df = sqlDB.fetch_data(query, params=(selected_university,))
    fig = {
        'data': [
            {
                'labels': df['research_area'],
                'values': df['publication_count'],
                'type': 'pie',
                'hoverinfo': 'label+percent+value',
                'textinfo': 'percent',
                'marker': {
                    'colors': [
                        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', 
                        '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', 
                        '#bcbd22', '#17becf'
                    ]
                }
            }
        ],
        'layout': {
            'title': f'Top Research Areas for {selected_university}',
            'showlegend': True,
            'height': 400
        }
    }
    return fig

@app.callback(
    Output('top-universities-table', 'children'),
    Output('top-faculty-table', 'children'),
    Input('research-interest-button', 'n_clicks'),
    State('research-interest-input', 'value')
)
def update_research_interest(n_clicks, research_interest):
    if n_clicks > 0 and research_interest:
        # Query for top universities for the research interest
        query_universities = """
        SELECT university.name, COUNT(DISTINCT faculty.id) as num_faculty, COUNT(DISTINCT publication.id) as num_publications
        FROM university
        JOIN faculty ON university.id = faculty.university_id
        JOIN faculty_publication fp ON faculty.id = fp.faculty_Id
        JOIN publication ON publication.id = fp.publication_Id
        JOIN Publication_Keyword pk ON publication.id = pk.publication_id
        JOIN keyword k ON k.id = pk.keyword_id
        WHERE k.name = %s
        GROUP BY university.name
        ORDER BY num_publications DESC, num_faculty DESC
        LIMIT 10
        """
        df_universities = sqlDB.fetch_data(query_universities, params=(research_interest,))

        # Create the top universities table
        university_table = [
            html.Tr([html.Th("University"), html.Th("Number of Faculty"), html.Th("Number of Publications")])
        ] + [
            html.Tr([html.Td(row['name']), html.Td(row['num_faculty']), html.Td(row['num_publications'])])
            for _, row in df_universities.iterrows()
        ]

        # Query for top faculty members for the research interest
        query_faculty = """
        SELECT faculty.name, COUNT(DISTINCT publication.id) as num_publications, SUM(publication.num_citations) as num_citations
        FROM faculty
        JOIN faculty_publication fp ON faculty.id = fp.faculty_Id
        JOIN publication ON publication.id = fp.publication_Id
        JOIN Publication_Keyword pk ON publication.id = pk.publication_id
        JOIN keyword k ON k.id = pk.keyword_id
        WHERE k.name = %s
        GROUP BY faculty.name
        ORDER BY num_publications DESC, num_citations DESC
        LIMIT 10
        """
        df_faculty = sqlDB.fetch_data(query_faculty, params=(research_interest,))

        # Create the top faculty table
        faculty_table = [
            html.Tr([html.Th("Faculty Member"), html.Th("Number of Publications"), html.Th("Number of Citations")])
        ] + [
            html.Tr([html.Td(row['name']), html.Td(row['num_publications']), html.Td(row['num_citations'])])
            for _, row in df_faculty.iterrows()
        ]

        return university_table, faculty_table
    return [], []

def fetch_faculty_interests(faculty_name):
    query = """
    SELECT DISTINCT k.name as interest
    FROM faculty
    JOIN faculty_publication fp ON faculty.id = fp.faculty_Id
    JOIN publication ON publication.id = fp.publication_Id
    JOIN Publication_Keyword pk ON publication.id = pk.publication_id
    JOIN keyword k ON k.id = pk.keyword_id
    WHERE faculty.name = %s
    """
    df_interests = sqlDB.fetch_data(query, params=(faculty_name,))
    return df_interests['interest'].tolist()

@app.callback(
    Output('faculty-contact-info', 'children'),
    Input('faculty-search-button', 'n_clicks'),
    State('faculty-name-input', 'value')
)
def fetch_faculty_contact_info(n_clicks, faculty_name):
    if n_clicks > 0 and faculty_name:
        query = """
        MATCH (f:Faculty {name: $name})-[:AFFILIATION_WITH]->(i:Institute)
        RETURN f.name AS name, f.email AS email, f.phone AS phone, i.name AS institute
        """
        result = neo4jDB.run_query(query, {'name': faculty_name})

        if result:
            info = result[0]
            return html.Div([
                html.P(f"Name: {info['name']}"),
                html.P(f"Email: {info.get('email', 'N/A')}"),
                html.P(f"Phone: {info.get('phone', 'N/A')}"),
                html.P(f"Institute: {info['institute']}")
            ])
        else:
            return html.P("No contact information found for the specified faculty member.")
    return html.Div()

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
