import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import calendar
import seaborn as sns
import plotly.express as px  # pip install plotly-express
from sklearn.preprocessing import LabelEncoder
import streamlit.components.v1 as components



st.set_page_config(page_title="FARAH", page_icon=":bar_chart:",layout="wide")

# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)


st.set_option('deprecation.showPyplotGlobalUse', False)

# ---- MAINPAGE ----
st.title(":bar_chart: Tableau de bord des ventes")
st.markdown("##")

# Afficher le sélecteur de fichiers pour importer le fichier CSV
uploaded_file = st.file_uploader("Importez votre fichier CSV", type="csv")


if uploaded_file is not None:
    # Lire le fichier CSV en utilisant Pandas
    sales = pd.read_csv(uploaded_file)
    def preprocess_data(data):
        # Removing variables from the data which don't have any predictive power
        sales = data.drop(columns=["Invoice ID", "Date", "Time", "gross margin percentage"])

        # One-hot encoding for categorical features
        categorical_features = ["Branch", "City", "Customer type", "Gender", "Product line", "Payment"]
        sales = pd.get_dummies(sales, columns=categorical_features)

        # Detecting correlations between variables
        data_corr = sales.corr()

        # Removing highly correlated variables
        sales_clean = sales.drop(
            columns=["Tax 5%", "cogs", "gross income", "City_Mandalay", "City_Naypyitaw", "City_Yangon"])

        return sales_clean, data_corr

    # Prétraitement des données
    sales_clean, data_corr = preprocess_data(sales)

    # Afficher les données prétraitées
    # st.write("Données prétraitées :", sales_clean)
    # st.write("Matrice de corrélation :", data_corr)

    st.sidebar.header("Filtrez :")
    city = st.sidebar.multiselect(
        "Selectionner la ville:",
        options=sales["City"].unique(),
        default=sales["City"].unique()
    )

    customer_type = st.sidebar.multiselect(
        "Selectionner le type de client:",
        options=sales["Customer type"].unique(),
        default=sales["Customer type"].unique(),
    )

    gender = st.sidebar.multiselect(
        "Selectionner le genre:",
        options=sales["Gender"].unique(),
        default=sales["Gender"].unique()
    )
    df_selection = sales.query("City == @city and `Customer type` == @customer_type and Gender == @gender")





    # TOP KPI's
    total_sales = int(df_selection["Total"].sum())
    average_rating = round(df_selection["Rating"].mean(), 1)
    star_rating = ":star:" * int(round(average_rating, 0))
    average_sale_by_transaction = round(df_selection["Total"].mean(), 2)


    with st.expander("📜 Données importées :"):
        shwdata = st.multiselect('Filter :', df_selection.columns, default=[])
        st.dataframe(df_selection[shwdata],use_container_width=True)

    sub_option = st.selectbox("Selectionner une sous-option",["Vue générale", "Vue selon les branches", "Vue selon les produits","Vue selon le type de client", "Vue selon le temps"])
    st.markdown(f"<h1 style='font-weight: bold;'>{sub_option}</h1>", unsafe_allow_html=True)
    if sub_option == "Vue générale":

        left_column, middle_column, right_column = st.columns(3)
        with left_column:
            st.subheader("Total des ventes:")
            st.subheader(f"US $ {total_sales:,}")
        with middle_column:
            st.subheader("Note moyenne:")
            st.subheader(f"{average_rating} {star_rating}")
        with right_column:
            st.subheader("Ventes moyennes par transaction:")
            st.subheader(f"US $ {average_sale_by_transaction}")

        st.markdown("""---""")

        # SALES BY PRODUCT LINE [BAR CHART]
        sales_by_product_line = (
            df_selection.groupby(by=["Product line"]).sum()[["Total"]].sort_values(by="Total")
        )
        fig_product_sales = px.bar(
            sales_by_product_line,
            x="Total",
            y=sales_by_product_line.index,
            orientation="h",
            title="<b>Sales by Product Line</b>",
            color_discrete_sequence=["#0083B8"] * len(sales_by_product_line),
            template="plotly_white",
        )
        fig_product_sales.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=(dict(showgrid=False))
        )

        # number of categories in each column
        # unique_counts = sales.select_dtypes('object').apply(pd.Series.nunique, axis=0)
        # Afficher le résultat sur la page Streamlit
        # st.write("Décompte des valeurs uniques pour les colonnes de type 'object':")
        # st.write(unique_counts)


        # checking if the data is imbalanced and the distribution of categorical data
        def vcounts(sales, colname):
            a = sales[colname].value_counts()
            return a


        vcounts(sales, "Branch")
        vcounts(sales, "Customer type")
        vcounts(sales, "Gender")
        vcounts(sales, "Product line")
        vcounts(sales, "Payment")

        # dealing with date and time
        sales['Date'] = pd.to_datetime(sales['Date'])
        sales['Day'] = sales['Date'].dt.day
        sales['Month'] = sales['Date'].dt.month
        sales['Month'] = sales['Month'].apply(lambda x: calendar.month_name[x])

        # Afficher les premières lignes du DataFrame
        st.write("Description du dataset:")
        st.dataframe(sales.describe())

        # Select numeric columns for mean calculation
        numeric_columns = sales.select_dtypes(include='number')

        # Calculate the mean of the numeric columns
        means = numeric_columns.mean()

        # Afficher la moyenne des colonnes du DataFrame
        st.write("La Moyenne des colonnes :", means)
        st.markdown("""---""")
        st.write("Les histogrammes des variables continues :")

        # Sélectionnez les attributs à afficher dans les histogrammes
        attributes = ["Unit price", "Quantity", "Tax 5%", "Total", "cogs", "gross margin percentage", "gross income",
                      "Rating"]

        # Calculez le nombre total de sous-graphiques
        num_plots = len(attributes)

        # Calculez la hauteur totale de la figure en fonction du nombre de sous-graphiques
        total_height = 5 * num_plots

        # Créez la figure avec la hauteur ajustée
        fig, axes = plt.subplots(nrows=num_plots, ncols=1, figsize=(10, total_height))

        # Générez les histogrammes
        for i, attribute in enumerate(attributes):
            axes[i].hist(sales[attribute], bins=50)
            axes[i].set_xlabel(attribute)
            axes[i].set_ylabel("Frequency")

        # Ajustez l'espacement vertical entre les sous-graphiques
        fig.tight_layout(pad=3.0)
        st.pyplot(fig)


    if sub_option == "Vue selon les branches":

        # Calculer la distribution des branches
        st.write("La distribution des branches :")
        branch = sales["Branch"].value_counts()
        # Créer le graphique en camembert
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.pie(branch, labels=branch.index, autopct='%1.1f%%')
        ax.set_title("Distribution des branches")
        st.pyplot(fig)
        st.markdown("""---""")
        st.write("Répartition des sexes par branche :")
        # Group the data by branch and gender
        grouped_data = sales.groupby(['Branch', 'Gender']).size()
        # Unstack the data
        unstacked_data = grouped_data.unstack(0)
        # Plot the data
        st.bar_chart(unstacked_data)
        quote_text = " Un nombre plus élevé de femmes achètent des produits de la branche C par rapport aux hommes qui achètent la plupart des produits des branches A et B. Cela implique que la branche C est plus populaire chez les femmes et que les branches A et B sont plus populaires chez les hommes."
        quote_color = "#FFFFFF"
        st.markdown(f'<blockquote style="color:{quote_color};">{quote_text}</blockquote>', unsafe_allow_html=True)
        st.markdown("""---""")
        st.write("Les notes des branches :")
        # Create a boxplot of the ratings by branch
        fig = sns.boxplot(x="Branch", y="Rating", data=sales)
        # Add a title to the plot
        fig.set_title("Les notes des branches :")
        # Display the plot
        st.pyplot(fig.figure)
        quote_text = "La branche B a la note la plus basse parmi toutes les autres directions et les branches A et C ont la même notation."
        quote_color = "#FFFFFF"
        st.markdown(f'<blockquote style="color:{quote_color};">{quote_text}</blockquote>', unsafe_allow_html=True)
        st.markdown("""---""")
        # Distribution of Customer type across branches
        st.write("Répartition du type de client entre les succursales :")
        # Create a DataFrame
        data = {
            'Branch': ['A', 'B', 'C'],
            'Customer type': ['Retail', 'Commercial', 'Government'],
            'Size': [10, 20, 30]
        }
        df = pd.DataFrame(data)
        # Group the DataFrame by Branch and Customer type
        df = df.groupby(['Branch', 'Customer type']).size().unstack(0)
        # Plot a bar chart
        st.bar_chart(df)
        quote_text = "Les clients membres achètent la plupart de leurs produits de la branche C et le moins de la branche B tandis que les clients normaux achètent beaucoup de la branche A puis de la branche B, mais moins de la branche C."
        quote_color = "#FFFFFF"
        st.markdown(f'<blockquote style="color:{quote_color};">{quote_text}</blockquote>', unsafe_allow_html=True)

    if sub_option == "Vue selon les produits":
        # Calculer la distribution des lignes de produits
        st.write("La distribution des lignes de produits :")
        productline = sales["Product line"].value_counts()

        # Créer le graphique en camembert
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.pie(productline, labels=productline.index, autopct='%1.1f%%')
        ax.set_title("Distribution des lignes de produits")
        st.pyplot(fig)

        quote_text = "D'après le diagramme circulaire, il a été observé que les accessoires de mode étaient le produit le plus populaire dans toutes les branches, la nourriture et les boissons occupent la deuxième place, et les accessoires électroniques arrivent en troisième position dans la catégorie des produits."
        quote_color = "#FFFFFF"
        st.markdown(f'<blockquote style="color:{quote_color};">{quote_text}</blockquote>', unsafe_allow_html=True)
        st.markdown("""---""")

        st.write("Ventes de différents produits :")
        fig, ax = plt.subplots()
        sns.boxenplot(y='Product line', x='Total', data=sales, ax=ax)
        st.pyplot(fig)
        quote_text = "D’après le visuel ci-dessus, la santé et la beauté, les sports et les voyages génèrent plus de ventes totales que les accessoires électroniques, la maison et le style de vie, la nourriture et les boissons et les accessoires de mode."
        quote_color = "#FFFFFF"
        st.markdown(f'<blockquote style="color:{quote_color};">{quote_text}</blockquote>', unsafe_allow_html=True)
        st.markdown("""---""")

        st.write("Ventes de différents produits selon le genre :")
        # Définissez les valeurs pour les variables x, hue et y
        x = 'Total'
        hue = 'Gender'
        y = 'Product line'
        # Créez le graphique à barres avec Seaborn
        fig = sns.barplot(x=x, y=y, hue=hue, data=sales)
        # Affichez le graphique dans Streamlit
        st.pyplot(fig.figure)
        quote_text = "Les femmes préfèrent acheter des articles pour la maison et le style de vie et génèrent des ventes maximales d'environ 380 dollars, tandis que les hommes sont plus enclins à acheter des produits de santé et de beauté et ont généré des ventes maximales d'environ 350 dollars."
        quote_color = "#FFFFFF"
        st.markdown(f'<blockquote style="color:{quote_color};">{quote_text}</blockquote>', unsafe_allow_html=True)

    if sub_option == "Vue selon le type de client":
        st.write("Quantité de produits répartis par type de client:")
        # Définissez les valeurs pour les variables x, hue et y
        x = 'Quantity'
        hue = 'Customer type'
        y = 'Product line'
        # Créez le graphique à barres avec Seaborn
        fig = sns.barplot(x=x, y=y, hue=hue, data=sales)
        # Affichez le graphique dans Streamlit
        st.pyplot(fig.figure)
        quote_text = "Les membres préfèrent acheter plus de produits de santé et de beauté et de produits pour la maison et le style de vie, tandis que les clients normaux préfèrent les accessoires électroniques."
        quote_color = "#FFFFFF"
        st.markdown(f'<blockquote style="color:{quote_color};">{quote_text}</blockquote>', unsafe_allow_html=True)
        st.markdown("""---""")

        st.write("Total des ventes de produits pour chaque type de paiement:")
        # Définissez les valeurs pour les variables x, hue et y
        x = 'Total'
        hue = 'Payment'
        y = 'Product line'
        # Créez le graphique à barres avec Seaborn
        fig = sns.barplot(x=x, y=y, hue=hue, data=sales)
        # Affichez le graphique dans Streamlit
        st.pyplot(fig.figure)
        quote_text = " La plupart des clients achètent des accessoires électroniques en utilisant un portefeuille électronique qui génère des ventes maximales d'environ 350 dollars. Les clients préfèrent acheter des produits pour la maison et le style de vie en espèces et génèrent des ventes maximales d'environ 360 dollars. La carte de crédit est surtout utilisée pour l'achat d'accessoires électroniques et de produits sportifs et de voyage, et génère un maximum de ventes pour ces produits grâce à l'achat par carte de crédit."
        quote_color = "#FFFFFF"
        st.markdown(f'<blockquote style="color:{quote_color};">{quote_text}</blockquote>', unsafe_allow_html=True)
        st.markdown("""---""")

        st.write("Ventes générées par le genre par le biais de types de paiement:")
        # Définissez les valeurs pour les variables x, hue et y
        y = 'Total'
        hue = 'Payment'
        x = 'Gender'
        # Créez le graphique à barres avec une orientation horizontale
        fig = sns.barplot(x=y, y=x, hue=hue, data=sales, orient='h')
        # Affichez le graphique dans Streamlit
        st.pyplot(fig.figure)
        quote_text = "Les femmes préfèrent acheter des articles en utilisant un portefeuille électronique et génèrent des ventes maximales d'environ 348 dollars, tandis que les hommes préfèrent faire leurs achats par carte de crédit et génèrent des ventes maximales d'environ 330 dollars."
        quote_color = "#FFFFFF"
        st.markdown(f'<blockquote style="color:{quote_color};">{quote_text}</blockquote>', unsafe_allow_html=True)

    if sub_option == "Vue selon le temps":
        st.write("Ventes horaires:")
        # Convert Date and Time columns to datetime
        sales['Date'] = pd.to_datetime(sales['Date'])
        sales['Time'] = pd.to_datetime(sales['Time'])
        # Extract day, month, and hour
        sales['Day'] = sales['Date'].dt.day
        sales['Month'] = sales['Date'].dt.month.apply(lambda x: calendar.month_name[x])
        sales['Hour'] = sales['Time'].dt.hour
        # Create a figure and axes
        fig, ax = plt.subplots()
        # Create the line plot
        sns.lineplot(x='Hour', y='Total', data=sales, ax=ax)
        # Set the title of the plot
        ax.set_title("Hourly Sales")
        # Display the plot in Streamlit
        st.pyplot(fig)
        st.markdown("""---""")

        st.write("Ventes quotidiennes:")
        # Convert Date column to datetime
        sales['Date'] = pd.to_datetime(sales['Date'])
        # Extract day
        sales['Day'] = sales['Date'].dt.day
        # Create a figure and axes
        fig, ax = plt.subplots()
        # Create the line plot
        sns.lineplot(x='Day', y='Total', data=sales, ax=ax)
        # Set the title of the plot
        ax.set_title("Daily Sales")
        # Display the plot in Streamlit
        st.pyplot(fig)
        st.markdown("""---""")

        st.write("Ventes mensuelles:")
        # Convert Date column to datetime
        sales['Date'] = pd.to_datetime(sales['Date'])
        # Extract month and convert it to month name
        sales['Month'] = sales['Date'].dt.month.apply(lambda x: calendar.month_name[x])
        # Create a figure and axes
        fig, ax = plt.subplots()
        # Create the line plot
        sns.lineplot(x='Month', y='Total', data=sales, ax=ax)
        # Set the title of the plot
        ax.set_title("Monthly Sales")
        # Display the plot in Streamlit
        st.pyplot(fig)
        quote_text = "Les ventes maximales sont générées au mois de janvier avec une forte baisse en mars et une légère augmentation en février."
        quote_color = "#FFFFFF"
        st.markdown(f'<blockquote style="color:{quote_color};">{quote_text}</blockquote>', unsafe_allow_html=True)

footer = """<style>


a:hover,  a:active {
color: red;
background-color: transparent;
text-decoration: underline;
}

.footer {
position: fixed;
left: 0;
height:5%;
bottom: 0;
width: 100%;
background-color: #00172B;
color: white;
text-align: center;
}
</style>
<div class="footer">
<p>Developed with  ❤ by Farah <a style='display: block; text-align: center;' href="https://www.heflin.dev/" target="_blank">Samir.s.s</a></p>
</div>
"""
st.markdown(footer, unsafe_allow_html=True)