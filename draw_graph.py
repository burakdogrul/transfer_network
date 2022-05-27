import pandas as pd
import networkx as nx
from pyvis.network import Network
import networkx.algorithms.community as nx_comm
import warnings
warnings.filterwarnings("ignore")

data=pd.read_csv("all_transfer.csv")


def prepare_data(dataframe, date_th='2012-01-01'):
    dataframe = dataframe[
        ~((dataframe.Date.isna()) | (dataframe.From == "x") | (dataframe.To == "x") | (dataframe.To == "Unknown"))]
    dataframe.Date = pd.to_datetime(dataframe.Date)
    dataframe = dataframe[dataframe.Date >= date_th]
    dataframe.loc[dataframe.Price == "Free", "Price"] = 0
    dataframe.Price = dataframe.Price.replace({'€': '', ' ': '', 'M': 'e+06', 'K': 'e+03'}, regex=True).astype(
        float).astype(int)
    dataframe.Age = dataframe.Age.astype("float", errors='ignore')
    dataframe = dataframe[((dataframe.Age >= 16) & (dataframe.Age <= 40)) | (dataframe.Age.isna())]

    dataframe2 = dataframe.groupby(["From", "To"]).agg({"Date": "count", "Price": "sum"}).reset_index().rename(
        columns={"Date": "Count", "Price": "Price_Sum"})

    return dataframe, dataframe2


data1,data2 = prepare_data(data)


G= nx.from_pandas_edgelist(data2,"From","To", edge_attr=["Count","Price_Sum"], create_using=nx.MultiGraph())

communities = nx_comm.louvain_communities(G,seed=42,resolution=10)

dct={}
for ind,item in enumerate(communities):
    dct[ind+1]=item

df_com =pd.DataFrame.from_dict(dct, orient='index').T.melt(var_name='CommunityID', value_name='Team').dropna(subset=['Team'])

data3 =data2.merge(df_com,left_on="From",right_on="Team",how="left").merge(df_com,left_on="To",right_on="Team",how="left")[["CommunityID_x","From","CommunityID_y","To","Count","Price_Sum"]].rename(columns={"CommunityID_x":"CommunityID_From","CommunityID_y":"CommunityID_To"})

data4 =data3[(data3["From"]=="Galatasaray")|(data3["To"]=="Galatasaray")|(data3["From"]=="Besiktas")|(data3["To"]=="Besiktas")|(data3["From"]=="Fenerbahce")|(data3["To"]=="Fenerbahce")|(data3["From"]=="Trabzonspor")|(data3["To"]=="Trabzonspor")]


gs_net = Network(height='1500px', width='100%', bgcolor='white', font_color='black')

gs_net.barnes_hut()

sources = data4['From']
targets = data4['To']
value = data4['Count']
weights = data4['Price_Sum']
grp1 = data4["CommunityID_From"]
grp2 = data4["CommunityID_To"]

edge_data = zip(sources, targets, value,weights,grp1,grp2)

for e in edge_data:
    src = e[0]
    dst = e[1]
    v = e[2]
    w = e[3]
    g1 = e[4]
    g2 = e[5]

    gs_net.add_node(src, src, title=src , group=g1)
    gs_net.add_node(dst, dst, title=dst, group=g1)
    gs_net.add_edge(src, dst, value=v , weight=w)

neighbor_map = gs_net.get_adj_list()

for node in gs_net.nodes:
    node['title'] += ' Neighbors: |' + '|'.join(neighbor_map[node['id']])
    node['value'] = len(neighbor_map[node['id']])

#gs_net.show_buttons(filter_=["nodes","physics"])
gs_net.toggle_physics(True)
gs_net.show('turkishcom.html')