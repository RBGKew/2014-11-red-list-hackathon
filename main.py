import json
import csv

# Work from the Hack the IUCN Red List Conservation Hackathon: <http://conservationhackathon.org/hack-the-iucn-redlist/>
#
# See <http://rbgkew.github.io/2014-11-red-list-hackathon/>.
#
# Reads in data from the Sampled Red List Index of plants: <http://threatenedplants.myspecies.info/>.
# Outputs summarised data in JSON format for use in visualisation, keyed by ISO 3166-1 Numeric country code.

global isoCountryCodes

# def readCsv(file,header=False):
# 	with open(file,'r') as f:
# 		lines = f.readlines()
# 	if header:
# 		lines.pop(0)
# 	return [line.strip().split(',') for line in lines]

def readCsv(file,header=False,delimiter=','):
	result = []
	with open(file,'r') as f:
		reader = csv.reader(f, delimiter=delimiter)
		for row in reader:
			result.append(row)
	return result

# with open('some.csv') as f:
#     reader = csv.reader(f)
#     for row in reader:
#         print(row)

def createJsonCountries(data):
	column = [i[4] for i in data]
	countries = sorted(uniq(column))
	jData = createJson(countries)
	return jData

# remove duplicates
def uniq(seq):
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if not (x in seen or seen_add(x))]

# Convert list of possible country codes (alpha2) into JSON of numeric codes with name and alpha2 code,
# including only valid countries.
def createJson(countries):
	jData = {}
	for country in countries:
		isoData = isoCountryData(country)
		if (isoData):
			jData[isoData['numeric']] = {
				'name' : isoData['name'],
				'alpha2' : isoData['alpha2']
			}
	return jData

def extractSpeciesForCountry(country,cData):
	sData = []
	for row in cData:
		if country in row:
			sData.append(row)
	fData = filterEndangered(sData)
	return fData
	# return sData

def filterEndangered(sData):
	fData = []
	for row in sData:
		# print row
		tl = row[3]
		status1 = row[6]
		status2 = row[7]
		if (tl=='CR' or tl=='EN' or tl=='VU') and status1 == 'Extant' and status2 == 'Native':
			fData.append(row)
	return fData

def extractThreatTypes(speciesName,tData):
	selected = []
	for row in tData:
		if speciesName in row:
			selected.append(row)
	threatTypes = []
	for row in selected:
		threatTypes.append(row[8])
	return threatTypes

# Given an ISO Alpha-2 country code (e.g. GB) return the name, alpha2 code and numeric code (e.g. 826).
# (Inefficient, replace with pycountry.)
def isoCountryData(country):
	for row in isoCountryCodes:
		if (country == row[1]):
			isoData = {
				'name': row[0],
				'alpha2': row[1],
				'numeric': row[2]
			}
			return isoData

def writeJson(jData,jsonFile):
	json.dump(jData,open(jsonFile,'w'),indent=4,separators=(',', ': '))


if __name__ == "__main__":

	countryCSV = 'data/02_coo_published.csv'
	threatCSV = 'data/01_threats_species_published.csv'
	isoCountriesCSV = 'data/iso-countries.tsv'

	cData = readCsv(countryCSV)
	tData = readCsv(threatCSV)

	isoCountryCodes = readCsv(isoCountriesCSV, delimiter='\t')

	jData = createJsonCountries(cData)

	for countryCode, countryData in jData.iteritems():
		origCountry = countryData['alpha2']
		sData = extractSpeciesForCountry(origCountry,cData)
		species = {}
		speciesNames = [row[2] for row in sData]
		for name in speciesNames:
			species[name]=sorted(uniq(extractThreatTypes(name,tData)))
		jData[countryCode] = { 'country': countryData, 'species': species }

	writeJson(jData,'output/srli-data.json')
