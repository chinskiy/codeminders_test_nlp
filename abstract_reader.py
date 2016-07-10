import pandas as pd
import datetime
import calendar

from nltk.corpus import stopwords
from lxml import etree


def parse_date(time):
    time = time.getchildren()
    cal = dict((v, k) for k, v in enumerate(calendar.month_abbr))
    try:
        date = datetime.date(int(time[0].text),
                             int(time[1].text),
                             int(time[2].text))
    except Exception:
        date = datetime.date(int(time[0].text),
                             int(cal[time[1].text.strip()]),
                             int(time[2].text))
    return date


def create_df(articlelist, xml_elements):
    findelems = lambda arr, elem: [item[1] for item in arr if item[0] == elem]
    stripelems = lambda arr: [item.text.strip().lower() for item in arr]
    stopwords_rem = lambda arr, lang: ' '.join([item for item in arr.split() if item not in stopwords.words('english')])

    d_lang = {'eng': 'english', 'spa': 'spanish', 'dut': 'german',
              'fre': 'french', 'dan': 'danish', 'chi': 'english'}

    df = pd.DataFrame(columns=xml_elements)

    for article in range(len(articlelist)):
        # print article, articlelist[article]
        article_d = dict()

        context = list(etree.iterparse(articlelist[article],
                                       events=("end",),
                                       tag=xml_elements))

        context = [(_[1].tag, _[1]) for _ in context]

        try:
            article_d['datecreated'] = parse_date(findelems(context, 'datecreated')[0])
        except Exception:
            article_d['datecreated'] = 'not available'

        try:
            article_d['country'] = stripelems(findelems(context, 'country'))[0]
            if article_d['country'] == 'unknown' or article_d['country'] == '':
                raise Exception
        except Exception:
            article_d['country'] = 'not available'
        article_d['title'] = ' '.join(stripelems(findelems(context, 'title')))
        article_d['language'] = stripelems(findelems(context, 'language'))[0]
        article_d['publicationstatus'] = ' '.join(stripelems(findelems(context, 'publicationstatus')))

        article_d['articletitle'] = stopwords_rem(' '.join(stripelems(findelems(context, 'articletitle'))), d_lang[article_d['language']])
        article_d['abstracttext'] = stopwords_rem(' '.join(stripelems(findelems(context, 'abstracttext'))), d_lang[article_d['language']])

        for key in article_d.keys():
            df.loc[article, key] = article_d[key]
    return df