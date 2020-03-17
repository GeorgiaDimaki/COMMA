import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from dateutil import parser
from db_helpers import  *
from pandas.tools.plotting import table


# given a collected category result od a week with summaries for each day of the week
# it creates its summary for this week
def summarizeCOMMA(category):
        pos = np.array([day['pos'] for day in category['days']])
        dates = [parser.parse(day['date']) for day in category['days']]
        neg = np.array([day['neg'] for day in category['days']])
        describe = {}
        describe["total"] = np.array([day['total_unfiltered'] for day in category['days']]).sum()
        describe["total filtered"] = np.array([day['total_filtered'] for day in category['days']]).sum()
        describe["pos"] = pos.sum()
        describe["AvgPos"] = pos.mean()
        describe["StdPos"] = pos.std()
        describe["neg"] = neg.sum()
        describe["AvgNeg"] = neg.mean()
        describe["StdNeg"] = neg.std()
        return pos, neg, dates, describe

# given a week it creates a plot of its summary
def summarize_week(week):

    matplotlib.style.use('ggplot')
    dfPos = pd.DataFrame()
    dfNeg = pd.DataFrame()
    descf = pd.DataFrame()
    for comma in week['collected']:
        pos ,neg, dates, describe = summarizeCOMMA(comma)
        dfPos = dfPos.join(pd.DataFrame(data=pos, index=dates, columns=[comma['category']]), how='outer')
        dfNeg = dfNeg.join(pd.DataFrame(data=neg, index=dates, columns=[comma['category']]), how='outer')
        descf = descf.join(pd.DataFrame(data=np.round(describe.values(),2), index=describe.keys(), columns=[comma['category']]), how='outer')

    fig, axes = plt.subplots(3, 1)

    titles_dict = {'fontsize': 14,'fontweight' :8, 'verticalalignment': 'baseline','horizontalalignment': 'center'}
    dfPos.plot.area(stacked=False,ax=axes[0])
    axes[0].set_title("Tweets week "+str(week['_id']), fontdict=titles_dict )
    axes[0].set_ylabel('Positive')
    axes[0].legend(fontsize = 'xx-small')
    axes[0].get_xaxis().set_visible(False)

    dfNeg.plot.area(stacked=False,ax=axes[1], figsize=(6,9))
    axes[1].set_ylabel('Negative')
    axes[1].legend(fontsize = 'xx-small')
    axes[1].set_xlabel('Weekly Summary')
    axes[1].set_xticklabels(dfNeg.index.values, rotation='horizontal')
    import matplotlib.dates as dates
    axes[1].get_xaxis().set_major_locator(dates.DayLocator(interval=1))
    axes[1].get_xaxis().set_minor_formatter(dates.DateFormatter(''))
    axes[1].get_xaxis().set_major_formatter(dates.DateFormatter('%b %d\n'))

    axes[2].axis('tight')
    axes[2].axis('off')
    t = table(axes[2],descf,  gid=str(' Weekly Summary\n'), cellLoc = 'center', loc='center')
    t.auto_set_font_size(False)
    t.set_fontsize(7)

    # figManager = plt.get_current_fig_manager()
    # figManager.window.showMaximized()
    fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0)
    # plt.savefig("week_"+str(week['_id'])+".png",bbox_inches='tight')
    return fig

# asks for summary of a specific week
def summarize_specific_week(weekNum, memory_db):

        def get_week_memory_db(weekNum, memory_db):
            for w in memory_db:
                if w['_id'] == weekNum:
                    return w

        return summarize_week(get_week_memory_db(weekNum, memory_db))

# creates an intertemporal summary of positive and negative averages for the given category
def summarize_intertemporal(category, memory_db):

        def get_category_summary(weeks, category):
            week_ids = []
            neg_avgs = []
            pos_avgs = []
            for w in weeks:
                for c in w['collected']:
                    if c['category'] == category:
                        week_ids.append(w['_id'])
                        pos ,neg, dates, describe = summarizeCOMMA(c)
                        pos_avgs.append(describe["AvgPos"])
                        neg_avgs.append(describe["AvgNeg"])

            return  week_ids, neg_avgs, pos_avgs

        return get_category_summary(memory_db, category)

# creates the plot of an intertemporal summary
def plot_intertemporal(category, memory_db):
    week_ids, neg_avgs, pos_avgs = summarize_intertemporal(category, memory_db)
    df_pos = pd.DataFrame(data=pos_avgs, index=week_ids, columns=['pos_avgs'])
    df_neg = pd.DataFrame(data=neg_avgs, index=week_ids, columns=['neg_avgs'])

    matplotlib.style.use('ggplot')

    fig, axes = plt.subplots(2, 1)

    titles_dict = {'fontsize': 14,'fontweight' :8, 'verticalalignment': 'baseline','horizontalalignment': 'center'}
    df_pos.plot.bar(ax=axes[0], color='g')
    axes[0].set_title("Category "+category, fontdict=titles_dict )
    axes[0].set_ylabel('Positive Averages')
    axes[0].get_xaxis().set_visible(False)

    plt.gca().invert_yaxis()
    df_neg.plot.bar(ax = axes[1], color='r')
    axes[1].set_ylabel('Negative Averages')
    axes[1].legend(fontsize = 'xx-small')
    axes[1].set_xlabel('Weeks')
    axes[1].set_xticklabels(df_pos.index.values, rotation='horizontal')

    # figManager = plt.get_current_fig_manager()
    # figManager.window.showMaximized()
    fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0)
    # plt.savefig("category_"+category+".png",bbox_inches='tight')
    plt.subplots_adjust(hspace=0)
    return fig