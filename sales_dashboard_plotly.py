import pandas as pd
import plotly.express as px
import dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from dash import dcc
from dash import html
import random
import numpy as np

####################### DATA CLEANING #######################
# Load the data
retail_data = pd.read_excel('Online Retail.xlsx')

# Clean the data
retail_data['CustomerID'] = retail_data['CustomerID'].fillna(0)
retail_data['Description'] = retail_data['Description'].fillna('OTHER')
retail_data['Sales'] = retail_data['Quantity'] * retail_data['UnitPrice']
retail_data["CustomerID"] = retail_data["CustomerID"].astype(int)

retail_clean = retail_data.query("Quantity >= 0 and UnitPrice >= 0").copy()
retail_clean['InvoiceDate'] = pd.to_datetime(retail_clean['InvoiceDate'])

'''# Filter data to create a sample dataframe for testing purposes
np.random.seed(10)
retail_clean = retail_clean.sample(n=100).copy()
retail_clean['Country'] = retail_clean['Country'].astype(str)'''

# Create dataframes for the graphs and country dropdown menus
monthly_sales_df = retail_clean.groupby(['Country', pd.Grouper(key='InvoiceDate', freq='M')])['Sales'].sum().reset_index()
'''monthly_customer_count = retail_clean.groupby(['Country', pd.Grouper(key='InvoiceDate', freq='M')])['CustomerID'].nunique().reset_index()
monthly_customer_count.rename(columns={'CustomerID': 'Count of Customers'}, inplace=True)'''

countries = retail_clean['Country'].unique()


####################### DEFINE KPIs and GRAPHS #######################

def get_sales(retail_clean):
    return '{0:,.0f}'.format(retail_clean['Sales'].sum())
        
def get_customers(retail_clean):
    return '{0:,}'.format(len(retail_clean['CustomerID'].unique()))

def get_sales_quantity(retail_clean):
    return '{0:,} Units'.format((retail_clean['Quantity'].sum()))

def create_chart(monthly_sales_df, country):
    retail_country = monthly_sales_df[monthly_sales_df['Country'] == country]
    return px.line(retail_country, x='InvoiceDate', y='Sales')

def revenue_country_viz(retail_clean):
    revenue_country = retail_clean.groupby("Country")["Sales"].sum().reset_index().sort_values('Sales', ascending = False).head(10)
    revenue_country_viz = px.bar(revenue_country, y="Country", x="Sales", text="Sales", 
                             hover_data={"Sales":":.2f"}, title="TOP 10 MARKETS IN SALES ".upper())
    revenue_country_viz.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    revenue_country_viz.update_layout(uniformtext_minsize=7, uniformtext_mode='hide', 
                                   hoverlabel={"bgcolor":"white", "font_size":16, "font_family":"Open Sans"},
                                   title={"y":0.9, "x":0.5, "xanchor":"center", "yanchor":"top",
                                          "font":{"size":16, "color":"#4a4a4a"}},
                                   paper_bgcolor="#f8f9fa")
    return revenue_country_viz

def viz_scatter(retail_clean): 
    scatter_df = retail_clean[['Country','Sales','Quantity']].groupby(['Country']).sum().reset_index().sort_values('Sales',ascending = False).head(10)
    viz_scatter = px.scatter(scatter_df, x="Quantity", y="Sales", size="Sales", color="Country",
                        hover_name="Sales", log_x=True, log_y=True,template="seaborn", size_max = 50, title='QUANTITY VS. SALES BY TOP 10 COUNTRY')
    viz_scatter.update_traces(mode="markers", hovertemplate="Quantity: %{x} <br>Sales: %{y}")
    viz_scatter.update_layout(yaxis_title = 'Log Sales', xaxis_title = 'Log Quantity', hoverlabel=dict(bgcolor="white", font_size=16, font_family="Open Sans"),font=dict(size=10, color="#4a4a4a"))
    return viz_scatter

def create_chart(data, country):
    line_chart = px.line(data[data['Country'] == country], x='InvoiceDate', y='Sales', title=f"MONTHLY REVENUES FOR {country}", template="seaborn")
    line_chart.update_layout(font=dict(size=10, color="#4a4a4a"), paper_bgcolor="#f8f9fa")
    return line_chart



####################### APP DASHBOARD ####################### 

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])


######################## APP BODY ####################### 

navbar = dbc.Navbar(id = 'navbar', children = [
    dbc.Row([
        dbc.Col(dbc.NavbarBrand("Retail Sales Dashboard", style = {'color':'white', 'fontSize':'30px','fontFamily':'Arial', 'margin-left':'15px'}))
        ],align = "center")], color = '#01080b',fixed="top")

card_content_dropdwn = [dbc.CardBody([html.H6('Select Country', style = {'textAlign':'center'}),
    dbc.Row([
        dbc.Col([html.H6('Markets'),dcc.Dropdown(id='country-dropdown', options=[{'label': c, 'value': c} for c in retail_clean['Country'].unique()], value=retail_clean['Country'].unique()[0]),
        dcc.Input(id='selected_country', value='', type='text', style={'display': 'none'})])])])
    ]

body_app = dbc.Container([
    
    html.Br(),
    html.Br(),

# First Row --------------------------------------------------------------------
    dbc.Row([
        dbc.Col([dbc.Card(card_content_dropdwn,style={'height':'150px'})],width = 4),

        dbc.Col([dbc.Card([dbc.CardBody(
            [
                html.H6('Total sales', style = {'fontWeight':'lighter', 'textAlign':'center'}),
                html.H3('${0}'.format(get_sales(retail_clean)), style = {'color':'rgb(64 165 193)','textAlign':'center'}),
                
            ])], style={'height':'150px'})]),
        dbc.Col([dbc.Card([dbc.CardBody(
            [
                html.H6('Total Customers', style = {'fontWeight':'lighter', 'textAlign':'center'}),
                html.H3('{0}'.format(get_customers(retail_clean)), style = {'color':'rgb(64 165 193)','textAlign':'center'}),
                
            ])],style={'height':'150px'})]),
        dbc.Col([dbc.Card([dbc.CardBody(
            [
                html.H6('Total Inventory Sold', style = {'fontWeight':'lighter', 'textAlign':'center'}),
                html.H3('{0}'.format(get_sales_quantity(retail_clean)), style = {'color':'rgb(64 165 193)','textAlign':'center'}),
                
            ])],style={'height':'150px'})])

        ]),  

    html.Br(),
    html.Br(),

# Second Row --------------------------------------------------------------------

    dbc.Row([
        dbc.Col(width = 6, children = [dbc.Card([dbc.CardBody(dcc.Graph(id = 'country_line_graph',figure= create_chart(monthly_sales_df,'selected_country')),style={'height':'500px'})])]),
        dbc.Col(width = 6, children = [dbc.Card([dbc.CardBody(dcc.Graph(figure=revenue_country_viz(retail_clean)),style={'height':'500px'})])]),
   ]),

    html.Br(),
    html.Br(),
# Third Row --------------------------------------------------------------------
    dbc.Row([dbc.Col(width = 12, children = [dbc.Card([dbc.CardBody(dcc.Graph(figure=viz_scatter(retail_clean),style={'height':'600px'}))])])])
], 
    style = {'backgroundColor':'#f7f7f7'},
    fluid = True)

######################## APP LAYOUT ####################### 
app.layout = html.Div(id = 'parent', children = [navbar,body_app], style = {'margin': '30px'})


######################## APP CALLBACKS ####################### 

@app.callback(
    dash.dependencies.Output('country_line_graph', 'figure'),
    [dash.dependencies.Input('country-dropdown', 'value')])

def update_chart(selected_country):
    return create_chart(monthly_sales_df, selected_country)

'''
@app.callback(
    Output("graph-title", "children"),
    [Input("country-dropdown", "value")]
)
def update_graph_title(selected_country):
    return f"Graph for {selected_country}"
'''

######################## RUN APP ####################### 
if __name__ == '__main__':
    app.run_server(port = 8080, debug=True)

