import requests

#Get updated data from API
url = "https://api.football-data.org/v4/competitions/PD/matches"
headers = {"X-Auth-Token" : "33fd527cad68426fa1c899f3f6374504"}

response = requests.get(url, headers=headers)
data = response.json()

#Make all the names unified
alavesName = data['matches'][3]["homeTeam"]["shortName"]
barcaName = data['matches'][39]["homeTeam"]["shortName"]
nameMapping = {
	alavesName : "Alaves",
	"Alaves" : "Alaves",
	"Almeria" : "Almeria",
	"Ath Bilbao" : "Ath Bilbao",
	"Athletic" : "Ath Bilbao",
	"Ath Madrid" : "Ath Madrid",
	"Atleti" : "Ath Madrid",
	barcaName : "FC Barcelona",
	"Barcelona" : "FC Barcelona",
	"Betis" : "Real Betis",
	"Real Betis" : "Real Betis",
	"Cadiz" : "Cadiz",
	"Celta" : "Celta",
	"Elche" : "Elche",
	"Espanol" : "Espanyol",
	"Espanyol" : "Espanyol",
	"Getafe" : "Getafe",
	"Girona" : "Girona",
	"Granada" : "Granada",
	"Las Palmas" : "Las Palmas",
	"Leganes" : "Leganes",
	"Levante" : "Levante",
	"Mallorca" : "Mallorca",
	"Osasuna" : "Osasuna",
	"Rayo Vallecano" : "Rayo Vallecano",
	"Vallecano" : "Rayo Vallecano",
	"Real Madrid" : "Real Madrid",
	"Real Oviedo" : "Real Oviedo",
	"Real Sociedad" : "Real Sociedad",
	"Sevilla" : "Sevilla",
	"Sevilla FC" : "Sevilla",
	"Sociedad" : "Real Sociedad",
	"Valencia" : "Valencia",
	"Valladolid": "Valladolid",
	"Villarreal" : "Villarreal",
}