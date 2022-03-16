import numpy as np
import matplotlib.pyplot as plt
import pickle


def read_commutters_data(data_path, text_encoding_format, number_of_header_lines,
                        number_of_coloumns, measure_coloumn):
    measure_book = {}
    line_counter = 0
    with open(data_path, 'r', encoding=text_encoding_format) as data:
        for line in data:
            line_counter += 1
            if line_counter > number_of_header_lines:
                #from IPython.core.debugger import Pdb
                #Pdb().set_trace()
                fields = line.strip().split(';')
                assert len(fields) == number_of_coloumns
                city = fields[0]
                measure = int(fields[measure_coloumn])
                measure_book[city] = measure
    return measure_book

import itertools
def calculate_distance_matrix(coordinates_book):
    ### aim: calculating the distance matrix between all the population centers 
    ### input: coordinates_book
    ###        a dictionary with population center names as keys and their (x,y) coordinates as values
    ### output: distance_book
    ###         a dictionary with (pop_cent_i, pop_cent_j) as keys and their distance as value
    distance_book = {}
    pairs = list(itertools.combinations(coordinates_book.keys(), 2))
    for city_pair in pairs:
        i = city_pair[0]
        j = city_pair[1]
        x_i, y_i = coordinates_book[i][0], coordinates_book[i][1]
        x_j, y_j = coordinates_book[j][0], coordinates_book[j][1]
        d = np.sqrt((x_i - x_j)**2+(y_i - y_j)**2)
        distance_book[(i,j)] = d
        distance_book[(j,i)] = d
    return distance_book

def population_sum_between_origin_and_destination(population_book, distance_book, origin, destination):
    d_ij = distance_book[(origin,destination)]
    ID_set = set(population_book.keys()).difference({origin, destination})
    sum_ij = 0
    for city in ID_set:
        #from IPython.core.debugger import Pdb
        #Pdb().set_trace()
        if distance_book[(city, origin)] < d_ij:
            sum_ij += population_book[city]
    return sum_ij
            
                                                
def flow_from_i_to_j(normalization_factor, workers_living_in_i, jobs_in_i, jobs_in_j, s_ij):
    p_ij = (normalization_factor*jobs_in_i*jobs_in_j)/((jobs_in_i+s_ij)*(jobs_in_i+jobs_in_j+s_ij)) 
    flow_ij = workers_living_in_i*p_ij
    return flow_ij

def number_of_workers_who_both_live_and_work_in_i (workers_living_in_i, outcommuters_of_i):
    n_ii = workers_living_in_i - out_commuters_from_i
    return n_ii


if __name__ == "__main__":
    
    #figuring out the path to the location where our script is saved
    import inspect, os.path
    filename = inspect.getframeinfo(inspect.currentframe()).filename
    dir_path = os.path.dirname(os.path.abspath(filename))
    
    ### Reading the data from statistics Finland on number of out-commuters of each municipality, "ni+"
    out_commutters_data_path = dir_path + "/data/population_data/out_degree_cleaned.csv"
    #out_commutters_data_path = "/m/cs/scratch/networks/heydars1/population_flow/data/population_data/out_degree_cleaned.csv"
    out_commuters_book = read_commutters_data(out_commutters_data_path, 'iso-8859-1', 4, 12, 3)
    
    ### Reading the data from statistics Finland on total number of workers living in each municipality, "ni:"
    num_workers_by_home_municipality_data_path = "/m/cs/scratch/networks/heydars1/population_flow/data/population_data/num_employed_by_home_municipality_cleaned.csv"
    workers_by_home_municipality_book = read_commutters_data(num_workers_by_home_municipality_data_path, 'iso-8859-1', 3, 11, 2)
    
    ### Reading the data from statistics Finland on total number of jobs located in each municipality, "n:i"
    num_jobs_in_each_muncipality_data_path = "/m/cs/scratch/networks/heydars1/population_flow/data/population_data/num_jobs_in_each_municipality_cleaned.csv"
    jobs_in_each_municipality_book = read_commutters_data(num_jobs_in_each_muncipality_data_path, 'iso-8859-1', 3, 11, 2)
    
    
    ### Reading the data and extracting poulation to calculate the center of population of each municipality
    data_path = "/m/cs/scratch/networks/heydars1/population_flow/data/population_data/population_2017_cleaned.csv"
    ## this function can be used to extrct population and coordinates info for "municipalities". In that case, population is sum of all the zipcode regions in the municipality and x ant y coordinate are coordinates of center of population of the municipality (weighted average)
    #_, coordinates_book = read_population_data_and_sum_in_municipality_level(data_path, ';', 'iso-8859-1', 5, 3)
    coordinates_book = pickle.load( open( dir_path + "/data/population_data/centre_of_populations_of_municiplaities.pkl", "rb" ) )
    
    ##Municipality Valtimo has been merged with Nurmes recently. Even if our both population data and commuter data are from 2017, Valimo exist in commuting data but not in population data. For convenience, we remove Valtimo from our dictionaries.
    del out_commuters_book['Valtimo']
    del jobs_in_each_municipality_book['Valtimo']
    del workers_by_home_municipality_book['Valtimo']
    

    
    #calculating distance between all pairs of population centers
    distance_book = calculate_distance_matrix(coordinates_book)
    total_num_jobs_in_country = sum(list(jobs_in_each_municipality_book.values()))

    ##printing the header of .csv file
    seperator = ','
    header_couloumns = ["origin","destination","workers living in i","jobs in i","jobs in j","jobs in between","estimated_population_flow"]
    path_for_saving_results = dir_path + "/results/radiation_model_number_of_commuters_as_prior.csv"
    print(path_for_saving_results)
    with open(path_for_saving_results, 'w') as outfile:
        outfile.write(seperator.join(header_couloumns) + "\n")
        
        for city_pair in distance_book.keys():
            i = city_pair[0]
            j = city_pair[1]
            d = distance_book[city_pair]
            ### Caculating s_ij, sum of population of all the regions which their distance to region i is less than d_ij
            s_ij = population_sum_between_origin_and_destination(jobs_in_each_municipality_book, distance_book, i, j)
            jobs_in_i = jobs_in_each_municipality_book[i]
            jobs_in_j = jobs_in_each_municipality_book[j]
            out_commuters_from_i = out_commuters_book[i]
            workers_living_in_i = workers_by_home_municipality_book[i]
            ### Calculating daily commuting flow from i to j based on the radiation model (number of people who live in region i but work in region j )
            normalization_factor = out_commuters_from_i/((workers_living_in_i)*(1-jobs_in_i/total_num_jobs_in_country))
            assert normalization_factor <= 1
            flow_ij = flow_from_i_to_j(normalization_factor, workers_living_in_i, jobs_in_i, jobs_in_j, s_ij) #estimated traffic flow from i to j
            #printing the results
            value_list = [city_pair[0], city_pair[1], str(workers_living_in_i), str(jobs_in_i), str(jobs_in_j), str(s_ij), str(flow_ij)]
            line_to_write = seperator.join(value_list) + "\n"
            #print(seperator.join(value_list))
            outfile.write(line_to_write)
