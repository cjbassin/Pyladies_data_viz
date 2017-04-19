import math
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
from bokeh.charts import Scatter, Bar, color
from bokeh.plotting import figure, output_file, show, ColumnDataSource
from bokeh.models import HoverTool





def load_clean_data(filename):
    animals = pd.read_csv(filename)
    animals.drop_duplicates(inplace = True)
    animals['ZIP Code'].replace(" ",'unknown',inplace = True)
    animals['ZIP Code'][animals['ZIP Code'].isnull()]='unknown'
    animals['ZIP Code'] = animals['ZIP Code'].apply(lambda x: x.split('-')[0])
    animals['ZIP Code'][animals['ZIP Code'].apply(lambda x: len(x)<5)] = 'unknown'
    animals['ZIP Code'][animals['ZIP Code'].apply(lambda x: x[0] ==' ' or x[0] == '*')] = 'unknown'
    animals["Animal's Name"][animals["Animal's Name"].isnull()]='unknown'
    animals.rename(columns ={"Animal's Name":"Name","ZIP Code":"ZipCode"}, inplace = True)

    return animals


def setup_bar_names(animals):
    anim = animals.groupby("Name").count().reset_index()
    anim.sort_values('License Number',inplace=True)
    return anim.tail(30)


def setup_scatter(animals):
    ag= animals.groupby(['ZipCode','Species']).count()
    ag.reset_index(inplace=True)
    ag2 = ag.pivot(index = 'ZipCode',columns = 'Species',values ="License Number")
    ag2.Livestock.replace(np.nan, 0, inplace = True)
    ag2.sort_values('Livestock',inplace=True)
    ag2.reset_index(inplace=True)
    return ag2


def write_to_altair_data(anidatadf, cols):
    #turn pandas dataframe into altair style data
    alt_data =[anidatadf[cols].T.iloc[:,x].to_dict() for x in range(len(anidatadf))]
    
    return alt_data


def bokeh_high_level_scatter(ag2):
    pal =['#7fc97f', '#beaed4', '#fdc086', '#ffff99','#386cb0', '#f0027f', '#bf5b17']
    tooltips=[
                ("Cat", "@Cat"),
                ("Dog", "@Dog"),
                ("Livestock", "@Livestock"),
                ("ZipCode", "@ZipCode")
            ]
    s= Scatter(ag2,x='Cat',y='Dog',color = color('Livestock', palette =pal), tooltips = tooltips)
    output_file('bokeh_high_scatter.html')
    show(s)



def bokeh_high_level_bar(ani):
    b = Bar(ani.tail(30), label="Name", values='License Number')
    output_file('bokeh_high_level_bar.html')
    show(b)


def matplot_scatter(ag2):
    plt.scatter(ag2.Cat.tolist(), ag2.Dog.tolist(), c = ag2.Livestock.tolist())
    plt.show()


def matplot_bar(anig):
    names1= anig.Name.values
    x= 4*np.arange(0,len(names1),1)
    y = anig['License Number'].values
    width = 1 
    plt.bar(x, y, width)
    plt.xticks(x+ width / 2, names1, rotation = 45)
    plt.show()


def bokeh_low_level_bar(ani):
    p = figure(x_range = ani.Name.tolist(), title = "Names")
    p.vbar(x=ani.Name, width=0.5, bottom=0,
       top=ani['License Number'], color="firebrick")
    p.xaxis.major_label_orientation = math.pi/4
    p.xaxis.axis_label = "Name"
    p.yaxis.axis_label = "Count"
    output_file('bokeh_low_bar.html')
    show(p)


def bokeh_low_level_scatter(ag2):
    pal =['#7fc97f', '#beaed4', '#fdc086', '#ffff99','#386cb0', '#f0027f', '#bf5b17']
    numliv = ag2.Livestock.unique()
    colormap = {numliv[i]:e for i,e in enumerate(pal)}
    ag2['color'] = ag2.Livestock.map(lambda x: colormap[x])


    columns = ag2.columns
    p = figure(title = "Cats vs Dogs")
    p.xaxis.axis_label =  ag2.columns[0]
    p.yaxis.axis_label = ag2.columns[1]

    p.circle(ag2.Cat, ag2.Dog,
            color=ag2.color, fill_alpha=0.2, size=10, )
    output_file("bokeh_low_level_scatter.html", title="Cats vs. Dogs")
    show(p)


def bokeh_low_scatter_with_hover(ag2):
    pal =['#7fc97f', '#beaed4', '#fdc086', '#ffff99','#386cb0', '#f0027f', '#bf5b17']
    ag2_b = ag2.reset_index()
    numliv = ag2_b .Livestock.unique()
    colormap = {numliv[i]:e for i,e in enumerate(pal)}
    ag2_b ['color'] = ag2_b .Livestock.map(lambda x: colormap[x])



    source = ColumnDataSource(
            data=ag2_b 
        )

    hover = HoverTool(
            tooltips=[
                ("Cat", "@Cat"),
                ("Dog", "@Dog"),
                ("Livestock", "@Livestock"),
                ("Zip Code", "@ZipCode")
            ]
        )

    p = figure( tools=[hover], title="Cats vs Dogs")

    p.circle('Cat', 'Dog', color ='color',fill_alpha =0.2, size=10, source=source)
    output_file("bokeh_with_hover.html")
    show(p)

###fun stuff
def setupnamesearch(animals):
    animals['lowname'] = animals.Name.apply(lambda x: x.lower())
    ani=animals.groupby('lowname').count()
    animals_dict = ani.T.to_dict()
    return animals_dict

def check_name(name):
    import pprint
    if name in animals_dict.keys():
        pprint.pprint(animals_dict[name])
    else:
        print ('Sorry no one by that name here')


def main():
    filename  = 'Seattle_Pet_Licenses.csv'
    animals = load_clean_data(filename)

    
    
    #BAR PLOTS-BOKEH
    bar_animals = setup_bar_names(animals)
    bokeh_high_level_bar(bar_animals)
    bokeh_low_level_bar(bar_animals)

    #SCATTER PLOTS-BOKEH
    scatter_animals = setup_scatter(animals)  
    bokeh_high_level_scatter(scatter_animals)
    bokeh_low_level_scatter(scatter_animals)  
    bokeh_low_scatter_with_hover(scatter_animals)

    #BAR_MATPLOTLIB
    matplot_bar(bar_animals)


    #SCATTER-MATPLOTLIB
    matplot_scatter(scatter_animals)

    #fun
    


if __name__ == '__main__':
    main()



