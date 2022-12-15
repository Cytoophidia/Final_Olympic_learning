import time
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random
import base64

st.set_page_config(layout="wide")

@st.cache(suppress_st_warning=True)
def fetch_and_clean_data():
    st.experimental_set_query_params(number=0,answer_lists = ["Innsbruck","Vancouverxxx","Barcelona","Athina"])
    number = int(st.experimental_get_query_params()["number"][0])
    answers = st.experimental_get_query_params()["answer_lists"]
    res = [number, answers]
    return res

def add_bg_from_local(image):
    with open(image, "rb") as image:
        encoded_string = base64.b64encode(image.read())
    st.markdown(
        f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
        background-size: cover
    }}
    </style>
    """,
        unsafe_allow_html=True
    )

add_bg_from_local('bgpic.png')



athlete_data = pd.read_csv('athlete_events.csv')


# timeline data
year_city = athlete_data[["Year", "Season", "City"]]
year_city = year_city.drop_duplicates()
year_city.columns = year_city.columns.str.replace('Year', 'year')
# year_city

st.markdown("""
<style>
.fix_position {
    position: fixed; 
    bottom: 0; 
    width: 100%;
}
.small-font {
    font-size:20px;
}
</style>
""", unsafe_allow_html=True)


st.markdown("<h1 style='text-align: center; color: rgb(256,256,256); font-size: 25px; margin-top:-40px; margin-bottom:-80px'>Select The Time</h1>", unsafe_allow_html=True)
with st.container():
    year = st.select_slider(
         " ",
         options=(athlete_data.sort_values(by="Year").Year.unique()),
    )
    text = st.markdown("""
    <style>
    [data-testid="stMarkdownContainer"]{
        text-align: center;
        color: rgb(256,256,256);
        font-size:30px
    }
    </style>
    """,unsafe_allow_html=True)

    ColorMinMax = st.markdown(''' <style> div.stSlider > div[data-baseweb = "slider"] > div[data-testid="stTickBar"] > div {
        background: rgb(1 1 1 / 0%); color: rgb(256,256,256); font-size:25px} </style>''', unsafe_allow_html=True)

    Slider_Cursor = st.markdown(''' <style> div.stSlider > div[data-baseweb="slider"] > div > div > div[role="slider"]{
        background-color: rgba(14, 38, 74, 0); box-shadow: rgb(14 38 74 / 20%) 0px 0px 0px 0.2rem;} </style>''',
                                unsafe_allow_html=True)

    Slider_Number = st.markdown(''' <style> div.stSlider > div[data-baseweb="slider"] > div > div > div > div
                                    { color: rgb(256, 256, 256); font-size:33px; } </style>''', unsafe_allow_html=True)

    col = f''' <style> div.stSlider > div[data-baseweb = "slider"] > div > div {{
        background: linear-gradient(to right, rgb(1, 183, 158) 0%, 
                                    rgb(1, 183, 158) {year}%, 
                                    rgba(151, 166, 195, 0.25) {year}%, 
                                    rgba(151, 166, 195, 0.25) 100%); }} </style>'''

    ColorSlider = st.markdown(col, unsafe_allow_html=True)
    # st.write('You selected:', year)

# container_img = """
# <style>
# [data-testid="stVerticalBlock"]{
# background: rgba(72 122 180 / .2);
# }
# </style>
# """
# st.markdown(container_img, unsafe_allow_html=True)

df_selection = athlete_data.query(
    "Year == @year"
)

# get the column of countries that attend the game
countries = df_selection["NOC"]
countries_num = len(countries.drop_duplicates())
countries_list = countries.drop_duplicates()

# get the value in cell// The city hold the game
city = df_selection.iloc[-1]["City"]
season = df_selection.iloc[-1]["Season"]

# get the column of games
games = df_selection[["Sport","Event"]]
events = games.drop_duplicates()
events_num = len(events)
sports = games["Sport"].drop_duplicates()
sports_num = len(sports)

# Get the top 5 sports in that year
ranking_sport = games["Sport"].value_counts(sort=True)
top5 = ranking_sport.head(5)

# top5 fig
top5_sport_fig = go.Figure(go.Bar(
            x=top5.values,
            y=top5.index,
            orientation='h'))
top5_sport_fig.update_layout(
    title='Top5 Sports in number of participants',
    barmode='stack',
    template="ggplot2",
    font=dict(
        family="Courier New, monospace",
        size=18,
        color='white'),
    yaxis={'categoryorder':'total ascending'})
top5_sport_fig.update_layout({
    'plot_bgcolor':'rgba(0,0,0,0)',
    'paper_bgcolor':'rgba(0,0,0,0)'
})

# Male/Female ratio
# data
gender = df_selection["Sex"]
gender = gender.to_frame()
len_gender = len(gender)
i = 0
num = []
while i < len_gender:
    num.append(1)
    i += 1
gender.insert(1, "Num", num, True)

# make the fig
# gender_fig = px.pie(gender, values='Num', names="Sex", template="simple_white", title="Gender Ratio",labels={'M': "hello", 'F': "hi"})
gender_fig = go.Figure(data=[go.Pie(labels=gender["Sex"], values=gender["Num"], hole=.3)])
colors = ['mediumturquoise','gold']
gender_fig.update_traces(hoverinfo='label+percent', textfont_size=20,
                  marker=dict(colors=colors, line=dict(color='#FFFFFF', width=2)))

gender_fig.update_layout({
    'plot_bgcolor':'rgba(0,0,0,0)',
    'paper_bgcolor':'rgba(0,0,0,0)'
})
gender_fig.update_layout(
    font=dict(
        family="Courier New, monospace",
        size=18,
        color='white')
)
# medal data
medal = df_selection[["Event","NOC","Medal"]]
mask = ~medal["Medal"].isna()
medal = medal[mask]
medal = medal.drop_duplicates()

# Calculate the medal number for each team
medal_ranking = pd.DataFrame()
medal_ranking["Countries"] = countries_list
medal_ranking = medal_ranking.reset_index(drop=True)
medal_ranking.index += 1

medal_ranking["Gold"] = 0
medal_ranking["Silver"] = 0
medal_ranking["Bronze"] = 0

# Use for loop
for i in medal.index:
    countries_name = medal["NOC"][i]
    medal_type = medal["Medal"][i]
    index_num = medal_ranking.index[medal_ranking['Countries'] == countries_name].tolist()
    medal_ranking.at[index_num[0], medal_type] += 1
medal_ranking = medal_ranking.sort_values("Gold",ascending=False)
medal_ranking = medal_ranking.reset_index(drop=True)
medal_ranking.index += 1
medal_ranking = medal_ranking.head(10)
medal_table = go.Figure(data=[go.Table(
    columnwidth=100,
    header=dict(values=list(medal_ranking),
                line_color='rgb(256,256,256)',
                fill_color='rgb(204,51,0)',
                align='center',
                height=30),
    cells=dict(values=[medal_ranking["Countries"],
                       medal_ranking["Gold"], # 1st column
                       medal_ranking["Silver"], # 2nd column
                       medal_ranking["Bronze"]],
               line_color='rgb(256,256,256)',
               fill_color='rgb(255,153,102)',
               align='center',
               height=30))
])

medal_table.update_layout({
    'plot_bgcolor':'rgba(0,0,0,0)',
    'paper_bgcolor':'rgba(0,0,0,0)'
})
medal_table.update_layout(
    font=dict(
        family="Courier New, monospace",
        size=18,
        color='white'),
    width=500,
    height=800
)

# Layout
st.markdown("<h1 style='text-align: center; color: rgb(256,256,256); font-size: 100px; margin-top:-40px'>{0}, {1}</h1>".format(year,city), unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; color: rgb(256,256,256); font-size: 70px'>{0} Olympic Game</h1>".format(season), unsafe_allow_html=True)
st.write("#")


st.markdown("""
<style>
.medium-font {
    font-size:100px;
}
.small-font {
    font-size:40px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: rgb(256,256,256); font-size: 40px'>Hosted</h1>", unsafe_allow_html=True)
#st.write(cost_list)
# general info columns
col1, col2, col3 = st.columns([1,1,1])
with col1:
    st.write('#')
    st.markdown('<p class="medium-font" style="text-align: center; color:rgb(256,256,256)">  {0} <span style="font-size:40px">Countries</span></p>'.format(countries_num), unsafe_allow_html=True)

with col2:
    st.write('#')
    st.markdown('<p class="medium-font"style="text-align: center; color:rgb(256,256,256)">  {0} <span style="font-size:40px">Soprts</span></p>'.format(sports_num), unsafe_allow_html=True)
with col3:
    st.write('#')
    st.markdown('<p class="medium-font"style="text-align: center; color:rgb(256,256,256)">  {0} <span style="font-size:40px">Events</span></p>'.format(events_num), unsafe_allow_html=True)

gender_ratio,top5_soprt,medalRK = st.tabs(['Athletes','Sports','Medal Ranking'])
with gender_ratio:
    gender_fig
with top5_soprt:
    top5_sport_fig
with medalRK:
    medal_table

st.markdown("""
<style>
div[role="tablist"] > button[data-baseweb="tab"]{
    background-color: rgba(92,81,191,0.7);
}
div[data-baseweb="tab-panel"] > div > div[data-testid="stVerticalBlock"]{
    background-color: rgba(153,153,255,0.9);
}

</style>
""", unsafe_allow_html=True)

test = fetch_and_clean_data()
# games
# countries_list
# countries_num
# df_selection

question_year = athlete_data[["Year", "Season", "City"]]
question_year = question_year.drop_duplicates()
question_year = question_year.reset_index(drop=True)
city_list = question_year["City"].to_list()

question_size = len(question_year)
def change_question(question_year,city_list,question_size):
    random_num = random.randint(0, question_size)
    q1_question = question_year.at[random_num, "Year"]
    q1_correct_answer = question_year.at[random_num, "City"]
    answer_list = random.choices(city_list, k=3)
    answer_list.append(q1_correct_answer)
    random.shuffle(answer_list)
    st.experimental_set_query_params(number=random_num, answer_lists=answer_list)

# get a defalt question number

random_num = int(st.experimental_get_query_params()["number"][0])
answer_list = st.experimental_get_query_params()["answer_lists"]
q1_question = question_year.at[random_num, "Year"]
q1_correct_answer = question_year.at[random_num, "City"]



st.markdown("<h1 style='text-align: center; color: rgb(256,256,256); font-size: 60px'>Quiz Part</h1>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; color: rgb(256,256,256); font-size: 40px'>Where was the {0} Olympics held?</h1>".format(q1_question), unsafe_allow_html=True)

with st.form("question"):

    blank1,content,blank2 = st.columns([1,1,1])
    with content:
        q1_answer = st.radio(
            label="Make a choice!",
            options = answer_list
        )
        submit = st.form_submit_button("Check the Answer")
        st.markdown(""" 
        <style>
        div.stButton > button:first-child {
        background-color: #663399;color:white;font-size:20px;height:3em;width:20em;margin:0, auto;border-radius:10px 10px 10px 10px;
        }
        div[data-testid="column"] > div > div > div:first-child{
            background-color: rgba(153,153,255,0.9)
        }
        </style>
        """,unsafe_allow_html=True)

    if submit:
        if q1_answer == q1_correct_answer:
            st.warning("Correct!!")
        else:
            st.warning("Opps, the {0} Olympics held in {1}".format(q1_question,q1_correct_answer))

blank1,content,blank2 = st.columns([1,1,1])
with content:
    next = st.button("Next Question")
    if next:
        change_question(question_year,city_list,question_size)
        time.sleep(1)
        st.experimental_rerun()




