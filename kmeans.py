"""
file: HW10_kmeans.py
authors: Dyangelo Grullon, Joseph Ville, Meridangela Gutierrez
"""

from math import sqrt
import csv
import random
#import matplotlib.pyplot as plt

"""
Cluster Class to encapsualte cluster data and define methods to manipulate and analyze the data
"""
class Cluster:

    """
    The Constructor class.  Adds a key-value pair to the instance object representing the cluster id.
    @param cid the cluster id number
    @param instance the dictionary representing an instance. 
    """
    def __init__(self, cid, instance):
        self.cid = cid 
        self.members = [] 
        self.members.append(instance) #add instance to the array of members
        self.COM = {} #a dictionary representing the center of mass of all members
        for attribute in instance.keys(): #initialize the center of mass to the lone member in cluster
            self.COM[attribute] = instance[attribute]
        instance['cid'] = cid #reference this cluster id in the instance

    """
    Determine the euclidean distance from a cluster to a data point
    @param instance - the data point to find the distance to
    @returns the euclidean distance between this cluster and a data point
    """
    def euclidDistance(self, instance):
        summation = 0
        for attribute in self.COM.keys():
            summation += pow(self.COM[attribute] - instance[attribute], 2)
        return sqrt(summation)

    """
    Merges the data point to the cluster and updates the center of mass of the cluster
    @param instance - the data point to merge
    """
    def merge(self, instance):
        self.members.append(instance)
        instance['cid'] = self.cid
        for attribute in self.COM.keys():
            summation = 0
            total = 0
            for member in self.members:
                summation += member[attribute]
                total += 1
            self.COM[attribute] = summation/total
    """
    Finds the sse of the cluster. Sum these across clusters to find
    the total sse.
    @returns the sse of the cluster
    """
    def sse(self):
        summation = 0
        for instance in self.members:
            summation += pow(self.euclidDistance(instance), 2)
        return summation
    """
    Finds the string representation of the cluster
    @returns the string representation of this cluster
    """
    def __str__(self):
        return "cid: " + str(self.cid) + '\n COM: ' + str(self.COM) + '\n Size: ' + str(len(self.members)) + '\n -----------------------\n'

"""
Retrieves and formats flight data in a dictionary
@param filename the name of the csv file to open
@returns a tuple representing the (data, attributes) pair
"""
def getData(filename):
    data = {}
    with open(filename) as csvfile:
        reader= csv.reader(csvfile)
        attributes = next(reader)
        for row in range(1, 52):
            data[row] = {} #for future reference, data is dereferenced at the first level with a row
            for aisle in range(1, 11):
                instance = {} #and the second level uses the aisle number to dereference the instance
                raw = next(reader) #raw data from the file
                cur = 0 #current attribute position for the instance in raw
                for attribute in attributes: #for every attribute except the space in the end
                    instance[attribute] = float(raw[cur]) #convert the attribute value to a float
                    cur += 1 #go to the next attribute
                data[row][aisle] = instance #add the new data point
   
    return (data, attributes) 

"""
Clusters flight data into k clusters using any optional seeds provided
@param k the number of clusters desired
@param data the dictionary of datapoints in a data[row][aisle] format
@param seeds a set of seeds in the format [[row, aisle], ...]
@returns a tuple representing a (clusters, SSE) pair. The array of clusters and the sse.
"""
def kmeans(k, data, seeds=None):
    if seeds is None: #if there are no seeds
        seeds = [] #instantiate the array
    totalSeeds = len(seeds) #total number of seeds
    if totalSeeds > k:
        seeds = seeds[:k]
    if totalSeeds < k: #if we don't have enough seeds
        conflict = {row: {aisle: False for aisle in range(1, 11)} for row in range(1, 52)} #used to check if seed found
        for seed in seeds:
            conflict[seed[0]][seed[1]] = True #set all previously found seeds to found in the conflict dict
        seedCount = k #find more seeds until total seeds + random seeds = k
        while seedCount > totalSeeds: #find more seeds until total seeds + random seeds = k
            row = random.randint(1, 51) #random int between 1 and 51
            aisle = random.randint(1, 10) #random int between 1 and 10
            if not conflict[row][aisle]: #if there is no conflict
                conflict[row][aisle] = True #set the conflict to True for finding future seeds
                seeds.append([row, aisle]) # add the new [row, aisle] pair to the seeds
                seedCount -= 1 # lower the seedCount
    clusters = [] #the array that holds the clusters
    cid = 0 #set the first cluster id to 0
    for seed in seeds: #for every seed
        row = seed[0] #get the row
        aisle = seed[1] #get the aisle
        clusters.append(Cluster(cid, data[row][aisle])) #make a cluster using the seed data point
        cid += 1 #increase the cluster id. Also represents the position in the 'clusters' array
    change = True #used to determine if any data points have moved
    SSE = None #instantiate the SSE
    while change:
        change = False # set the change boolean to false so that we can change to True if there is a change
        for row in range(1,52): 
            for aisle in range(1, 11): #visit every data point
                best = None #instantiate the best distance metric
                cid = None #instantiate the best cid value
                instance = data[row][aisle] #get the current instance
                for cluster in clusters: #for every cluster find the best cluster distance to data point
                    distance = cluster.euclidDistance(instance) 
                    if best == None or distance < best:
                        best = distance
                        cid = cluster.cid
                if instance not in clusters[cid].members: #if the instance is not already a member of the cluster
                    clusters[cid].merge(instance)#merge the data point to the cluster
                    change = True #record the change to continue running k-means
        curSSE = 0 #initialize the current SSE calculation
        for cluster in clusters:
            curSSE += cluster.sse() #find the sse of all clusters and sum them to find total sse
        if SSE is None or curSSE < SSE: #if the current is lower then the best sse
            SSE = curSSE #update the best sse
    return (clusters, SSE)

"""
Displays the set of passengers in their respective clusters based on the
cid that has been assigned to them during insertion to a cluster
@param data the formated data set 
"""
def graphCluster(data):
    header = '\t'
    for aisle in range(1, 10):
        header += '0' + str(aisle) + '  '
    header += '10\n'
    print(header)
    for row in range(1,52):
        if row < 10: #if less than two digits fill a zero before the row 
            result = str(0) + str(row) + '\t'
        else: #don't need to fill 0 in
            result = str(row) + '\t'
        for aisle in range(1, 11):#for every aisle
            cid = data[row][aisle]['cid'] #retrieve the cluster id
            if cid < 10: #if cluster id is less than two digits
                result += str(0) + str(cid) + '  ' #fill a zero in
            else: #otherwise just display the unmodified cid
                result += str(cid) + '  '
        print (result)#print each line

"""
Creates a csv holding the data points with the cid attribute. To be used for data
visualization.
@param filename the name of the file you want to export
@param data the data you wish to export
@param attributes the attributes you wish to include in this table
"""
def exportClusters(filename, data, attributes):
    with open(filename, 'w', newline='') as csvfile:
        export = csv.writer(csvfile, delimiter=',')
        export.writerow(attributes)
        for row in range(1, 52):
            for aisle in range(1, 11):
                export.writerow([data[row][aisle][attribute] for attribute in attributes])
    
"""
def getGraphData(filename):
    graphData = []
    with open(filename) as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            info = []
            inx = 0
            for elem in range(len(row)):
                if elem in (0,1,len(row)-1):
                    info.append(float(row[elem]))
                    inx += 1
            graphData.append(info)
    return graphData


def plottingGraph(K, filename):
    data = getGraphData(filename)
    colors = []
    for i in range(0,K):
        r = random.randint(0,255)/255
        g = random.randint(0,255)/255
        b = random.randint(0,255)/255
        color = (r,g,b)
        colors.append(color)

    fig = plt.figure()
    ax1 = fig.add_subplot(211)
    ax2 = fig.add_subplot(212)
    colorPalette ={}
    colorIndex = 0

    for row in data:
        cid = row[2]
        if cid not in colorPalette:
            colorPalette[row[2]] = colors[colorIndex]
            colorIndex += 1
        ax1.scatter(row[0], row[1], c=colorPalette.get(cid), marker='s', edgecolors='none')
    ax1.set_title('Infectious K-means ')
    ax1.axis('tight')
    ax1.grid(True)

    for key in colorPalette:
        ax2.scatter(key, 1, c=colorPalette[key], marker='s', edgecolors='none')
    ax2.set_ylim([0.5,1.5])
    ax2.grid(True)

    plt.show()
"""
#The following main methods display results for all of the questions we must answer
                
def main_raw_9():
    sample = [[7, 8],[42, 3], [1,1], [2, 9], [13, 2], [18, 9], [33, 2], [38, 9], [51, 10]]
    fileData = getData("QANTAS420_DATA__v043_temp_for_class.csv")
    data = fileData[0]
    attributes = fileData[1]
    attributes.append('cid')
    clusterData = kmeans(9, data, sample)
    for cluster in clusterData[0]:
        print(cluster)
    print("SSE: " + str(clusterData[1]))
    graphCluster(data)
    exportClusters('QANTAS_Clustered_raw_9.csv', data, attributes)

def main_normalized_9():
    sample = [[7, 8],[42, 3], [1,1], [2, 9], [13, 2], [18, 9], [33, 2], [38, 9], [51, 10]]
    fileData = getData("QANTAS_Normalized.csv")
    data = fileData[0]
    attributes = fileData[1]
    attributes.append('cid')
    clusterData = kmeans(9, data, sample)
    for cluster in clusterData[0]:
        print(cluster)
    print("SSE: " + str(clusterData[1]))
    graphCluster(data)
    exportClusters('QANTAS_Clustered_normalized_9.csv', data, attributes)

def main_raw_39():
    sample = [[7, 8],[42, 3], [1,1], [2, 9], [13, 2], [18, 9], [33, 2], [38, 9], [51, 10]]
    fileData = getData("QANTAS420_DATA__v043_temp_for_class.csv")
    data = fileData[0]
    attributes = fileData[1]
    attributes.append('cid')
    clusterData = kmeans(39, data, sample)
    for cluster in clusterData[0]:
        print(cluster)
    print("SSE: " + str(clusterData[1]))
    graphCluster(data)
    exportClusters('QANTAS_Clustered_raw_39.csv', data, attributes)
    
def main_normalized_39():
    sample = [[7, 8],[42, 3], [1,1], [2, 9], [13, 2], [18, 9], [33, 2], [38, 9], [51, 10]]
    fileData = getData("QANTAS_Normalized.csv")
    data = fileData[0]
    attributes = fileData[1]
    attributes.append('cid')
    clusterData = kmeans(39, data, sample)
    for cluster in clusterData[0]:
        print(cluster)
    print("SSE: " + str(clusterData[1]))
    graphCluster(data)
    exportClusters('QANTAS_Clustered_normalized_39.csv', data, attributes)
    
def main_normalized_v5_9():
    sample = [[7, 8],[42, 3], [1,1], [2, 9], [13, 2], [18, 9], [33, 2], [38, 9], [51, 10]]
    fileData = getData("QANTAS_Normalized_05.csv")
    data = fileData[0]
    attributes = fileData[1]
    attributes.append('cid')
    clusterData = kmeans(9, data, sample)
    for cluster in clusterData[0]:
        print(cluster)
    print("SSE: " + str(clusterData[1]))
    graphCluster(data)
    exportClusters('QANTAS_Clustered_v5.csv', data, attributes)

def main_normalized_v25_9():
    sample = [[7, 8],[42, 3], [1,1], [2, 9], [13, 2], [18, 9], [33, 2], [38, 9], [51, 10]]
    fileData = getData("QANTAS_Normalized_025.csv")
    data = fileData[0]
    attributes = fileData[1]
    attributes.append('cid')
    clusterData = kmeans(9, data, sample)
    for cluster in clusterData[0]:
        print(cluster)
    print("SSE: " + str(clusterData[1]))
    graphCluster(data)
    exportClusters('QANTAS_Clustered_v25.csv', data, attributes)
    
def main_normalized_v125_9():
    sample = [[7, 8],[42, 3], [1,1], [2, 9], [13, 2], [18, 9], [33, 2], [38, 9], [51, 10]]
    fileData = getData("QANTAS_Normalized_0125.csv")
    data = fileData[0]
    attributes = fileData[1]
    attributes.append('cid')
    clusterData = kmeans(9, data, sample)
    for cluster in clusterData[0]:
        print(cluster)
    print("SSE: " + str(clusterData[1]))
    graphCluster(data)
    exportClusters('QANTAS_Clustered_v125.csv', data, attributes)
"""
def findBestK(filename):
    fileData = getData(filename)
    sample = [[7, 8],[42, 3], [1,1], [2, 9], [13, 2], [18, 9], [33, 2], [38, 9], [51, 10]]
    data = fileData[0]
    attributes = fileData[1]
    attributes.append('cid')
    k = 2
    best = None
    bestK = None
    while k < 40:
        clusterData = kmeans(k, data, sample)
        SSE = clusterData[1]
        if best is None or SSE < best:
            bestK = k
            best = SSE
        k+=1
    return bestK
"""
"""
def main(filename, k):
    sample = [[7, 8],[42, 3], [1,1], [2, 9], [13, 2], [18, 9], [33, 2], [38, 9], [51, 10]]
    fileData = getData(filename)
    data = fileData[0]
    attributes = fileData[1]
    attributes.append('cid')
    clusterData = kmeans(k, data, sample)
    for cluster in clusterData[0]:
        print(cluster)
    print("SSE: " + str(clusterData[1]))
    graphCluster(data)
    exportClusters('QANTAS_Best.csv', data, attributes)
"""
print("-----------------0.5-----------------")    
main_normalized_v5_9()
print("-----------------0.25-----------------")
main_normalized_v25_9()
print("-----------------0.125-----------------")
main_normalized_v125_9()
print("-----------------------------------")
main_normalized_9()


#main("QANTAS_Normalized.csv", 9)

