import pandas as pd
import datetime
import calendar
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

    df = pd.DataFrame(columns=xml_elements)

    for article in range(len(articlelist)):
        # print article, articlelist[article]
        article_dict = dict()

        context = list(etree.iterparse(articlelist[article],
                                       events=("end",),
                                       tag=xml_elements))

        context = [(_[1].tag, _[1]) for _ in context]

        article_dict['abstracttext'] = ' '.join(stripelems(findelems(context, 'abstracttext')))
        try:
            article_dict['datecreated'] = parse_date(findelems(context, 'datecreated')[0])
        except Exception:
            article_dict['datecreated'] = 'not available'

        try:
            article_dict['country'] = stripelems(findelems(context, 'country'))[0]
            if article_dict['country'] == 'unknown' or article_dict['country'] == '':
                raise Exception
        except Exception:
            article_dict['country'] = 'not available'
        article_dict['title'] = ' '.join(stripelems(findelems(context, 'title')))
        article_dict['articletitle'] = ' '.join(stripelems(findelems(context, 'articletitle')))
        article_dict['language'] = stripelems(findelems(context, 'language'))[0]
        article_dict['publicationstatus'] = ' '.join(stripelems(findelems(context, 'publicationstatus')))

        for key in article_dict.keys():
            df.loc[article, key] = article_dict[key]
    return df