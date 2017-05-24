from urllib.request import urlopen
from bs4 import BeautifulSoup
import os

#collect all team roster urls
def collect_teams():
	confrence_url = "http://www.espn.com/nba/teams"

	print("let the script run until you see 'finished'\n")
	#downloads a webpage
	client = urlopen(confrence_url)
	html_source = client.read()
	client.close()

	#find team roster urls
	soup = BeautifulSoup(html_source, "html.parser")
	confrence = soup.body.div.find_all("ul", class_ = "medium-logos")

	#list of team roster urls
	teams = []
	teams_url = []
	for x in confrence:
		temp = x.find_all("li")
		teams = teams + temp
		pass

	print("collecting team urls\n")

	for x in teams:
		x = x.div.span.a.next_sibling.next_sibling.next_sibling.next_sibling.get("href")
		x = "http://www.espn.com" + x
		teams_url.append(x)

	return teams_url

#function that collects player urls from a team roster website
def collect_players(url):
	#downloads a webpage
	client = urlopen(url)
	html_source = client.read()
	client.close()

	#find player link
	soup = BeautifulSoup(html_source, "html.parser")
	players = soup.body.div.find_all("td", class_ = "sortcell")

	#saves player url and also creates a folder
	print("collecting player urls\n")
	players_url = []
	for x in players:
		#make folder
		rpath = x.a.contents[0]
		rpath = rpath.strip()
		makefolder("players\\" + rpath)

		#save url
		x = x.a.get("href")
		x = x[:31] + "gamelog/" + x[31:]
		players_url.append(x)
		pass

	return players_url

#collects urls to previous seasons
def collect_seasons(soup):
	#find urls
	print("collecting\n")
	raw_list = soup.find_all("select")[0]
	links = []

	for x in raw_list.contents:
		temp = x.get("value")
		if(temp != ""):
			links.append("http:" + temp)
		pass
	return links

#function that collects data for a single player
def player_data(soup, name):
	#extract data
	data = soup.find_all("table", class_ = "tablehead")[0]
	data = data.find_all("tr")
	table = ""
	season = ""
	totals = ""

	for x in data:
		if (x.get("class")[0] == "stathead"):
			if (table != ""):
				path = os.getcwd() + "\\players\\" + name + "\\" + season + ".txt"
				f = open(path, "w")
				f.write(table)
				f.close()
				pass
			season = get_entry_from_table(x)
			table = ""
		elif (x.get("class")[0] == "total"):
			totals = totals + get_entry_from_table(x) + "\n"
		elif (x.get("class")[0] != "colhead"):
			table = table + get_entry_from_table(x) + "\n"

	path = os.getcwd() + "\\players\\" + name + "\\" + season + ".txt"
	f = open(path, "w")
	f.write(table)
	f.close()

	year = season.split()[0]
	path = os.getcwd() + "\\players\\" + name + "\\" + year + " TOTALS.txt"
	f = open(path, "w")
	f.write(totals)
	f.close()
	pass

#grabs a players gamelog and bio
def preview_player(url):
	client = urlopen(url)
	html_source = client.read()
	client.close()
	soup = BeautifulSoup(html_source, "html.parser")
	return soup

#writes player bio to bio.txt
def update_bio(soup):
	all_info = soup.body.div.find_all("div", class_ = "mod-content")[0]
	general = all_info.div.next_sibling.next_sibling.next_sibling.ul
	meta = general.next_sibling

	name = all_info.h1.string

	buff_age = meta.li.next_element.next_element.next_element.split(":", 2)
	age = buff_age[1][1:3]

	general = general.li
	buff_position = general.string.split(" ", 2)
	position = buff_position[1]
	general = general.next_sibling
	ht_wt = general.string.split(",", 2)
	ht = ht_wt[0]
	wt = ht_wt[1].strip()
	general = general.next_sibling
	team = general.string
	temp = name + ", " + position + ", " + ht + ", " + wt + ", " + team + ", " + age

	path = os.getcwd() + "\\players\\" + name + "\\BIO.txt"
	f = open(path, "w")
	f.write(temp)
	f.close()
	return name

#returns the date of the last time the player was active
def get_last_game(soup):
	data = soup.find_all("table", class_ = "tablehead")[0]
	data = data.find_all("tr")

	for x in data:
		if ((x.get("class")[0] != "stathead") and (x.get("class")[0] != "colhead") and (x.get("class")[0] != "total")):
			str_entry = get_entry_from_table(x).split(",")

			#if player was active 
			if (str_entry[5] != "0"):
				return str_entry[0]

	lastgame = "has not played this season"
	return lastgame

#takes an entry from a table and returns a string version
def get_entry_from_table(entry):
	str_entry = ""

	for x in entry.stripped_strings:
		if (x == "vs"):
			x = "Home"
			pass
		elif (x == "@"):
			x = "Away"

		str_entry = str_entry + x + ", "
		pass

	return str_entry.rstrip(", ")

#internal function that creates a folder
def makefolder(rpath):
	path = os.getcwd() + "\\" + rpath
	try:
		os.mkdir(path)
		print("new player, creating a folder\n")

	except FileExistsError as e:
		print("old player, folder already exists\n")

#read_metadata has three return codes 0, 1, 2
#return code 0 means player is up to date
#return code 1 means current season is out of date
#return code 2 means this is a new player thats not in the data base
def read_metadata(name, most_recent_game):
	path = os.getcwd() + "\\players\\" + name + "\\metadata.txt"
	try:
		f = open(path, "r")
		lastgame = f.readline()
		lastgame = lastgame.strip()
		f.close()
		print("old player, reading from metadata file\n")

		if (lastgame == most_recent_game):
			#stats are up to date
			return 0
		elif (lastgame == "has not played this season"):
			return 0
		else:
			#stats are outdated
			f = open(path, "w")
			f.write(most_recent_game)
			f.close()
			return 1

		pass
	except FileNotFoundError as e:
		#brand new player
		print("new player, creating metadata file\n")
		f = open(path, "w")
		f.write(most_recent_game)
		f.close()
		return 2
	pass

#adds a player to database
def new_player(preveiw, name):
	season_urls = collect_seasons(preveiw)
	for x in season_urls:
		cURL = preview_player(x)
		print("working\n")
		player_data(cURL, name)
		pass
	pass

def main():
	team_urls = collect_teams()

	#empty list of player urls
	player_url = []

	#creates a folder for players
	makefolder("players")

	#vist each roster page and collect player urls
	for x in team_urls:
		player_url = player_url + collect_players(x)
		pass

	for x in player_url:
		#open webpage
		preview = preview_player(x)
		#write to bio
		name = update_bio(preview)
		
		lastgame = get_last_game(preview)
		#read metadata
		exitcode = read_metadata(name, lastgame)

		if (exitcode == 0):
			#dont do anything player is up to date
			print(name + " up to date\n")
			pass
		elif (exitcode == 1):
			#update current season
			print("updating " + name + "\n")
			player_data(preview, name)
			pass
		elif (exitcode == 2):
			#brand new player read entire player history
			print("retrieving " + name +"'s full player history\n")
			new_player(preview, name)
			pass

		pass
		#update metadata

	print("finished with no error")