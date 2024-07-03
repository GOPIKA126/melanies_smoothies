import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd  # Import Pandas for DataFrame handling
from urllib.parse import quote  # Import quote function from urllib.parse

# Set title for the Streamlit app
st.title("My Parents New Healthy Dinner")

# Display breakfast menu
st.title("Breakfast Menu")
st.write(
    """Omega 3 & Blueberry Oatmeal
       Kale, Spinach & Rocket Smoothie
       Hard-Boiled Free-Range Egg
    """
)

name_on_order = st.text_input("Name on smoothie:")
st.write("The name on your smoothie will be:", name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        search_on=pd_df.loc[pd_df['FRUIT_NAME']==fruit_chosen,'SEARCH_ON'.iloc[0]
        st.write('the search value for',fruit_chosen,'is',search_on,'.')
        
        st.subheader(fruit_chosen + ' Nutrition Information')
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + fruit_chosen)
        try:
            fruit_chosen_encoded = quote(fruit_chosen)  # URL encode the fruit name
            fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{fruit_chosen_encoded}")
            fruityvice_response.raise_for_status()  # Raise an error for bad response status
            
            if fruityvice_response.status_code == 200:
                fv_data = fruityvice_response.json()
                fv_df = pd.DataFrame([fv_data])  # Convert JSON to DataFrame
                st.dataframe(fv_df, use_container_width=True)  # Display DataFrame
            else:
                st.error(f"Error fetching data for {fruit_chosen}: Status Code {fruityvice_response.status_code}")
        
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching data for {fruit_chosen}: {e}")
            continue  # Skip to the next fruit

    # Insert order into Snowflake table
    if ingredients_string and name_on_order:
        my_insert_stmt = f"""INSERT INTO smoothies.public.orders(ingredients, name_on_order)
                            VALUES ('{ingredients_string.strip()}', '{name_on_order}')"""
        
        time_to_insert = st.button('SUBMIT ORDER')
        
        if time_to_insert:
            try:
                session.sql(my_insert_stmt).collect()
                st.success('Your Smoothie order has been placed!', icon="✅")
            except Exception as e:
                st.error(f"Error inserting order: {e}")

st.write(my_insert_stmt)  # This line is outside the 'if time_to_insert' block
