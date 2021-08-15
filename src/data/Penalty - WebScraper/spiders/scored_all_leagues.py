import scrapy
from scrapy import Request
from scrapy import Selector
import requests
import re

general_url = "https://www.transfermarkt.de"

all_leagues = [
    #Germany
    "https://www.transfermarkt.de/bundesliga/elfmeterstatistik/wettbewerb/L1/saison_id/1963/plus/1",
    #England
    "https://www.transfermarkt.de/premier-league/elfmeterstatistik/wettbewerb/GB1/saison_id/1992/plus/1",
    #Spain
    "https://www.transfermarkt.de/laliga/elfmeterstatistik/wettbewerb/ES1/saison_id/1928/plus/1",
    #Italy
    "https://www.transfermarkt.de/serie-a/elfmeterstatistik/wettbewerb/IT1/saison_id/1929/plus/1",
    #France
    "https://www.transfermarkt.de/ligue-1/elfmeterstatistik/wettbewerb/FR1/saison_id/1980/plus/1"
    ]

country_and_year_urls = []

for url_per_league in all_leagues:
    html = requests.get(url_per_league, headers={'User-Agent': 'Mozilla/5.0'}).content
    page = Selector (text=html)
    all_years = page.xpath("//div[@class = 'inline-select']//option/@value").extract()

    for year in all_years:
        url_per_year = url_per_league.replace(re.search("\d{4}", url_per_league).group(), year)
        country_and_year_urls.append(url_per_year)



class PenaltyScraperSpider(scrapy.Spider):
    name = 'scored_all_leagues'
    start_urls = country_and_year_urls


    def parse(self, response):
        matchday = response.xpath("//div[@class = 'responsive-table'][2]//table[@class = 'items']//td[@class = 'zentriert'][1]/text()").extract()
        penalty_taker = response.xpath("//div[@class = 'responsive-table'][2]//table[@class = 'items']//table[@class = 'inline-table']//td[@class = 'hauptlink']/a/@title").extract()
        penalty_taker_position = response.xpath("//div[@class = 'responsive-table'][2]//table[@class = 'items']//table[@class = 'inline-table']/tr[2]/td/text()").extract()
        penalty_taker_club = response.xpath("//div[@class = 'responsive-table'][2]//table[@class = 'items']//td[@class = 'zentriert no-border-rechts'][1]//a//img/@alt").extract()
        goalkeeper = response.xpath("//div[@class = 'responsive-table'][2]//table[@class = 'items']//td[@class = 'links hauptlink no-border-links']/a/@title").extract()
        score_before_penalty = response.xpath("//div[@class = 'responsive-table'][2]//table[@class = 'items']//td[@class = 'zentriert no-border-rechts no-border-links']/text()").extract()
        minute = response.xpath("//div[@class = 'responsive-table'][2]//table[@class = 'items']//td[@class = 'zentriert'][2]/text()").extract()
        home_team = response.xpath("//div[@class = 'responsive-table'][2]//td[@class = 'zentriert no-border-rechts'][3]/a/img/@alt").extract()
        away_team = response.xpath("//div[@class = 'responsive-table'][2]//td[@class = 'zentriert no-border-links']/a/img/@alt").extract()
        final_score = response.xpath("//div[@class = 'responsive-table'][2]//td[@class = 'zentriert no-border-rechts no-border-links']/a/span/text()").extract()
        league = response.xpath("//div[@class = 'kartei-button-bar'][1]/a[1]/@href").extract()[0].split("/")[1]

        row_data=zip(matchday, penalty_taker, penalty_taker_position, penalty_taker_club, goalkeeper, score_before_penalty, minute, home_team, away_team, final_score)


        for item in row_data:
            
            scraped_info = {
                #key:value
                'matchday' : item[0],
                'penalty_taker' : item[1],
                'penalty_taker_position' : item[2],
                'penalty_taker_club' : item[3],
                'goalkeeper' : item[4],
                'score_before_penalty' : item[5],
                'minute' : item[6],
                'home_team' : item[7],
                'away_team' : item[8],
                'final_score' : item[9],
                'season' : response.xpath("//div[@class = 'inline-select']//option[@selected = 'selected']/text()").extract(),
                'league' : league.capitalize(),
                'scored' : 0
            }

            #yield or give the scraped info to scrapy
            yield scraped_info

            next_page = response.xpath("//div[@class = 'responsive-table'][1]//div[@class = 'pager']/ul//li[@class = 'naechste-seite']/a/@href").extract_first()
            if next_page:
                yield scrapy.Request(url=(general_url + next_page), callback=self.parse)