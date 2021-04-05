import csv
import json
import requests

import sys; print(sys.version)

# Grab the whole lists of sites for snakehead fishing from MDs Angler Access site
class AnglerAccessScraper(object):
    def __init__(self):
        self.url = 'https://gisapps.dnr.state.md.us/arcgis2/rest/services/fisheries/PublicFishingAccessSites/MapServer/0/query'
        self.session = requests.Session()
        self.params = {
            'f': 'json',
            'where': """ (FishTypes LIKE '%Snakehead%') AND 
                          Waterbody LIKE '%%' AND 
                          County LIKE '%%' AND 
                          LicenseTyp LIKE '%%' AND 
                          Ramp LIKE '%%' AND 
                          (ShoreFishi LIKE '%%' OR Piers LIKE '%%') AND 
                          AccessibleSp LIKE '%%' AND 
                          Complete = 'complete' """,
            'returnGeometry': 'true',
            'spatialRel': 'esriSpatialRelIntersects',
            'geometry': """ {"xmin":-8766409.89997295,  "ymin":4383204.949988967,
                             "xmax":-8140237.764260951, "ymax":5009377.085700965,
                             "spatialReference": { "wkid":102100,"latestWkid":3857 }} """,
            'geometryType': 'esriGeometryEnvelope',
            'inSR': 102100,
            'outFields': '*',
            'outSR': 102100,
        }

    def csv_save(self, data, filename):
        with open(filename, 'w', newline='') as fp:
            writer = csv.writer(fp, quoting=csv.QUOTE_NONNUMERIC)

            for row in data:
                writer.writerow(row)
        
    def scrape(self):
        locations = []

        resp = self.session.get(self.url, params=self.params)
        data = resp.json()

        def maplink(lat, lng):
            return f"https://www.bing.com/maps?q={lat}%2C{lng}"
        
        for f in data['features']:
            attribs = f['attributes']
            lat,lng = attribs['DNRAIMSv3.DBO.PublicFishingAccessSites.Y'], attribs['DNRAIMSv3.DBO.PublicFishingAccessSites.X']
            
            entry = {}
            entry['name'] = attribs['DNRAIMSv3.DBO.PublicFishingAccessSites.Name']
            entry['county'] = attribs['DNRAIMSv3.DBO.PublicFishingAccessSites.County']
            entry['website'] = attribs['DNRAIMSv3.DBO.PublicFishingAccessSites.WebLink']
            entry['latlng'] = f'{lat}, {lng}'
            entry['maplink'] = maplink(lat, lng)
            entry['parking'] = attribs['DNRAIMSv3.DBO.PublicFishingAccessSites.ParkingTyp']
            entry['season open'] = attribs['DNRAIMSv3.DBO.PublicFishingAccessSites.SeasonalOp']

            locations.append(entry)

        return locations
    
if __name__ == '__main__':
    scraper = AnglerAccessScraper()
    locations = scraper.scrape()
    scraper.csv_save(locations, 'snakeheads.csv')
