# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

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

# Input field for smoothie name
name_on_order = st.text_input("Name on smoothie:")
st.write("The name on your smoothie will be:", name_on_order)

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch fruit options from Snowflake table
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# Multiselect for choosing ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections=5
)

# Process selected ingredients
if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        # Retrieve nutrition information from Fruityvice API
        try:
            fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + fruit_chosen)
            fruityvice_response.raise_for_status()  # Raise an error for bad response status
            fv_data = fruityvice_response.json()
            st.subheader(fruit_chosen + ' Nutrition Information')
            st.json(fv_data)
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

