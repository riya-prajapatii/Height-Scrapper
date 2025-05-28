# scraping_teams.py

# This code is designed to scrape the names and player heights from multiple rosters in 4 sports:
# mens_swimming_teams, womens_swimming_teams, mens_volleyball_teams, womens_volleyball_teams

# The product is 4 pandas data frames, that includes a heading with the name of the sport,
# a list of the players' names and height in inches. Summary data for each sport also prints to screen.

# Important: This code prints results as proof of effectiveness of the base code. It loops through the
# list of teams and prints them one after the other.

# Each loop of this first-draft code have added some fuctionality to the following:
#     - It has the output of each data frame as a csv
#     - It analyzes each data frame for averages, although we could continue to use the .describe() method here
#     - It has the output data to a sql database file
#     - It prints the 8 tables of 5 shortest and tallest height in each sport
#     - It produces a bar graph for average height per team


import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

# Four dictionaries of teams and their web rosters divided by sport.
# Dictionary that included team names was chosen over a siple list of URLs in order to support debugging

mens_swimming_teams = {
  'CSI':'https://csidolphins.com/sports/mens-swimming-and-diving/roster/2023-2024',
  'York College CUNY':'https://yorkathletics.com/sports/mens-swimming-and-diving/roster',
  'Baruch College':'https://athletics.baruch.cuny.edu/sports/mens-swimming-and-diving/roster',
  'Ramapo College':'https://ramapoathletics.com/sports/mens-swimming-and-diving/roster',
  'SUNY Oneota':'https://oneontaathletics.com/sports/mens-swimming-and-diving/roster',
  'SUNY Binghamton':'https://bubearcats.com/sports/mens-swimming-and-diving/roster/2021-22',
  'Albright College':'https://albrightathletics.com/sports/mens-swimming-and-diving/roster/2021-22',
  'Lindenwood University - men':'https://lindenwoodlions.com/sports/mens-swimming-and-diving/roster/2021-22',
  'Mckendree University - men':'https://mckbearcats.com/sports/mens-swimming-and-diving/roster/2023-24',
  'Brooklyn College - men':'https://www.brooklyncollegeathletics.com/sports/mens-swimming-and-diving/roster/2019-20'
    }

womens_swimming_teams = {
  'College of Staten Island':'https://csidolphins.com/sports/womens-swimming-and-diving/roster/2023-2024',
  'York College':'https://yorkathletics.com/sports/womens-swimming-and-diving/roster' ,
  'Baruch':'https://athletics.baruch.cuny.edu/sports/womens-swimming-and-diving/roster/2021-22?view=2' ,
  'Ramapo College':'https://ramapoathletics.com/sports/womens-swimming-and-diving/roster?view=2' ,
  'Kean University':'https://keanathletics.com/sports/womens-swimming-and-diving/roster?view=2' ,
  'SUNY Oneota':'https://oneontaathletics.com/sports/womens-swimming-and-diving/roster/2021-22',
  'Queens College':'https://queensknights.com/sports/womens-swimming-and-diving/roster/2019-20',
  'Lindenwood University':'https://lindenwoodlions.com/sports/womens-swimming-and-diving/roster/2021-22',
  'Mckendree University':'https://mckbearcats.com/sports/womens-swimming-and-diving/roster',
  'Brooklyn College':'https://www.brooklyncollegeathletics.com/sports/womens-swimming-and-diving/roster/2022-23'
    }

mens_volleyball_teams = {
  'City College of New York':'https://ccnyathletics.com/sports/mens-volleyball/roster',
  'Lehman College':'https://lehmanathletics.com/sports/mens-volleyball/roster',
  'Brooklyn College':'https://www.brooklyncollegeathletics.com/sports/mens-volleyball/roster',
  'John Jay College':'https://johnjayathletics.com/sports/mens-volleyball/roster',
  'Baruch College CUNY':'https://athletics.baruch.cuny.edu/sports/mens-volleyball/roster',
  'Medgar Evers College':'https://mecathletics.com/sports/mens-volleyball/roster',
  'Hunter College':'https://www.huntercollegeathletics.com/sports/mens-volleyball/roster',
  'York CUNY':'https://yorkathletics.com/sports/mens-volleyball/roster',
  'Ball State':'https://ballstatesports.com/sports/mens-volleyball/roster'
      }

womens_volleyball_teams = {
  'York College':'https://yorkathletics.com/sports/womens-volleyball/roster',
  'Bronx CC':'https://bronxbroncos.com/sports/womens-volleyball/roster/2021',
  'Queens College':'https://queensknights.com/sports/womens-volleyball/roster',
  'Augusta College':'https://augustajags.com/sports/wvball/roster',
  'Flagler College':'https://flaglerathletics.com/sports/womens-volleyball/roster',
  'USC Aiken':'https://pacersports.com/sports/womens-volleyball/roster',
  'Penn State - Lock Haven':'https://www.golhu.com/sports/womens-volleyball/roster',
  'Hostos CC':'https://hostosathletics.com/sports/womens-volleyball/roster/2022-2023',
  'BMCC':'https://bmccathletics.com/sports/womens-volleyball/roster/2022'
    }


# headers Source: https://www.zenrows.com/blog/web-scraping-headers#user-agent
headers = {
  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
  'Accept-Language': 'en-US,en;q=0.9',
  'Connection': 'keep-alive'
  }

# since processing heights of players seemed the correct use of a class object
# Tallness was included as an experiment. In this context, it likely increased
# comlexity without much value added, but was worth it for the practice

class Tallness:

  def __init__(self, feet, inches):
    self.feet = feet
    self.inches = inches

  def __str__(self):
    return f"{self.feet}'{self.inches}"

  # custom class method to convert ft'&in" to inches
  def inchConvert(self):
    return self.feet * 12 + self.inches

# because 38 team pages were being scraped, several soup methods and methods of
# processing this soup data made combining much of the code into one or two functions
# somewhat awkward and hard to read.  As such, each steps in the process has been
# separated into its own funtion to call. This aided in debugging so many methods.

# feetToInches translates height text objects from soup into argument to apply in fuctions
# for example: 6-2 or 6'2 or 6'2" --> [6, 2]

def feetToInches(player_height,team):

    if player_height.find("-") == -1:
      item = player_height.split("'")
    else:
      item = player_height.split("-")

    feet = int(item[0].strip())
    inches = int(item[1].strip())
    tall = Tallness(feet,inches)            # produces class object
    height_in_inches = tall.inchConvert()   # performs class method
    return height_in_inches

# scrape_page is a standalone scrape function allows this to be called only once per team,
# rather than once each time a different soup mthod was required based on unique webpage designs

def scrape_page(url):
  page = requests.get(url, headers=headers)
  if page.status_code == 200:
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup
  else:
    return None                             # ignores schools with no working page (e.g. Medgar Evers)

# player_names builds list of roster names and varies by tags employed

def player_names(soup,team):
  roster_names = []
  if team == 'Ball State':
    names = soup.find_all('h3')
  else:
    names = soup.find_all('td', class_ ='sidearm-table-player-name')

  for name in names:
    roster_names.append(name.get_text().strip())
  return roster_names

# player_heights builds list of raw roster heights and varies by tags and format employed

def player_heights(soup,team):
  roster_heights = []
  if team == 'Ball State':
    heights = soup.find_all('span',class_='s-person-details__bio-stats-item')
    for height in heights:
      if height.get_text().startswith('Height'):
        player_height = height.get_text()[7:-3]
        roster_heights.append(feetToInches(player_height,team))
    return roster_heights
  else:
    heights = soup.find_all('td', class_ ='height')
    for height in heights:
      player_height = height.get_text()
      roster_heights.append(feetToInches(player_height,team))
    return roster_heights

# make_player_dictionary calls all the functions above to build the dictionary
# upon which the pandas dataframe will be based. Dataframe columns are simply name and
# height, and return a dictionary only for each sport called as a parameter of this funtion

def make_player_dictionary(sport):
  heights = []
  names = []
  for team in sport:
    url = sport[team]
    soup = scrape_page(url)
    if soup == None:
      continue
    else:
      heights.extend(player_heights(soup,team))
      names.extend(player_names(soup,team))
  player_dict = {'Name' : names,'Height' : heights}
  return player_dict


def main():

#creating file based database

  db_conn = sqlite3.connect("teams_heights.db")
  cursor = db_conn.cursor()

# sports is a dictionary to loop through team value as a parameter in the make_player_dictionary
# funtion call. The keys are used for the headers that print each dataframe.

  sports = {
      "Male Swimmers":mens_swimming_teams,
      "Female Swimmers":womens_swimming_teams,
      "Male Volleyball Players":mens_volleyball_teams,
      "Female Volleyball Players":womens_volleyball_teams
        }

#empty list to store avg height summary
  team_names = []
  avg_heights = []


  for sport in sports:

    print('\n'+'_'*len(sport)+'\n')                 # prints a header for each dataframe produced
    print (sport)
    print('_'*len(sport)+'\n')

    final = make_player_dictionary(sports[sport])   # function call to produce the name/height dictionary called final
    df = pd.DataFrame(final)                        # creates each dataframe based on the name/height dictionary

    df.to_csv(sport + ".csv", index=False)          #output as csv file
    print(df.describe())
    print(df)

#all team data to sql

    table_name = sport.lower().replace(" ", "_")
    df.to_sql(table_name, db_conn, if_exists='replace', index=False)


#output average height each team

    avg_height = df['Height'].mean()
    print(f'\nThe average height for {sport} is {avg_height}')

#update empty lists for summary
    team_names.append(sport)
    avg_heights.append(avg_height)

# 5 tallest each team
    top_heights = df['Height'].nlargest(5).unique()
    fifth_height = top_heights[-1]
    tallest = df[df['Height'] >= fifth_height]

# 5 shortest each team
    shortest_heights = df['Height'].nsmallest(5).unique()
    fifth_height = shortest_heights[-1]
    shortest = df[df['Height'] <= fifth_height]

#output tallest and shortest
    print(f"\nTallest in {sport}:\n")
    print(tallest)

    print(f"\nShortest in {sport}:\n")
    print(shortest)

    tallest_table = f"tallest_{table_name}"
    shortest_table = f"shortest_{table_name}"

#tallest and shortest to sql

    tallest.to_sql(tallest_table, db_conn, if_exists='replace', index=False)
    shortest.to_sql(shortest_table, db_conn, if_exists='replace', index=False)

#average height summary

  summary = {
      'team_name': team_names,
      'average_height': avg_heights
  }

  summary_df = pd.DataFrame(summary)
  print("\nSummary of Average Heights:\n")
  print(summary_df)

#average height summary to sql

  summary_df.to_sql("team_averages", db_conn, if_exists='replace', index=False)

  db_conn.commit()
  db_conn.close()
  print("\n\n")

  # Bar Chart to visualize Average height by team
  print("Bar Chart of Average Heights by Team:")
  summary_df.plot.bar(x='team_name', y='average_height', title='Average Height by Sport')
  plt.show()

main()
