import scrapy
import re


class FilmsSpider(scrapy.Spider):
    name = "films"
    allowed_domains = ["ru.wikipedia.org"]

    INFOBOX_XPATH = '//*[@class="infobox-above"]//text()'
    GENRE_XPATH = '//*[@data-wikidata-property-id="P136"]//text()'
    DIRECTOR_XPATH = '//*[@data-wikidata-property-id="P57"]//text()'
    COUNTRY_XPATH = '//*[@data-wikidata-property-id="P495"]//text()'
    YEAR_XPATH = '//*[@data-wikidata-property-id="P577"]//a[@title]//text() | //*[@class="dtstart"]//text()'

    def start_requests(self):
        URL = 'https://ru.wikipedia.org/wiki/Категория:Фильмы_по_алфавиту'
        yield scrapy.Request(url=URL, callback=self.parse_page)

    def exclude_special_notations(self, data):
        pattern = r'(\[|\()\w+.?(\]|\))|\xa0|\n|\d|рус.|англ.|\[*?\]|/|\*|\(|\)|\[|\]|\,\ |\,'
        almost_ready = [text.strip() for text in data if not re.search(pattern, text)]
        return ','.join(almost_ready).replace(',,,', ',').replace(',,', ',').split(',')

    def parse_film(self, response):
        title = response.xpath(self.INFOBOX_XPATH).getall()[-1] if response.xpath(self.INFOBOX_XPATH).getall() else None
        genre = response.xpath(self.GENRE_XPATH).getall()
        director = response.xpath(self.DIRECTOR_XPATH).getall()
        country_name = response.xpath(self.COUNTRY_XPATH).getall()
        year = response.xpath(self.YEAR_XPATH).getall()

        yield {
            'Название': title,
            'Жанр': self.exclude_special_notations(genre),
            'Режиссер': self.exclude_special_notations(director),
            'Страна': self.exclude_special_notations(country_name),
            'Год': year[-1] if year else None,
        }

    def parse_page(self, response):
        links = response.xpath('//div[@id="mw-pages"]//div[@class="mw-category-group"]//a/@href').getall()
        for link in links:
            yield response.follow(link, callback=self.parse_film)

        next_page = response.xpath('//a[contains(text(), "Следующая страница")]/@href').extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse_page)