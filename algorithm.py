'''
source code: https://github.com/LeeMinNguyeen/distributed-database/blob/main/algorithm.py
log file: https://github.com/LeeMinNguyeen/distributed-database/blob/main/vertical_fragmentation.log
'''

import numpy as np
import logging as log

class VerticalFragmentation:
    def __init__(self, attributes, queries, acc):
        self.attributes = attributes
        self.queries = queries
        
        self.usage_matrix, self.columns_pos = self.attributes_usage_matrix(attributes, queries)
        self.access_freq(acc)
        self.AA = self.attribute_affinity_matrix()
        
        # self.BEA()
        
    def access_freq(self, acc):
        """
        Access Frequency Matrix: application access frequency for each query
        """
        self.acc = acc
        
        self.acc_sum = self.acc.sum(axis=1).tolist() # Sum of the access frequency for each query

    def aff(self, attribute1, attribute2):
        """
        Affinity between two attributes

        Parameters
        ----------
        attribute1 : str
            Attribute 1
        attribute2 : str
            Attribute 2
        """
                
        a1 = list(self.columns_pos.keys())[list(self.columns_pos.values()).index(attribute1)]
        
        a2 = list(self.columns_pos.keys())[list(self.columns_pos.values()).index(attribute2)]
        
        affinity = 0
        
        for q in range(self.usage_matrix.shape[0]):
            if self.usage_matrix[q, a1] == 1 and self.usage_matrix[q, a2] == 1:
                affinity += self.acc_sum[q] # Sum of the access frequency for each query
        
        return affinity                

    def attribute_affinity_matrix(self):
        """
        Attribute Affinity Matrix

        Parameters
        ----------
        attributes : list
            List of attributes
        """
        
        affinity_matrix = np.zeros((len(self.attributes), len(self.attributes)), dtype=int) # Create a matrix with the size of attributes x attributes
        
        for a1 in range(len(self.attributes)):
            for a2 in range(len(self.attributes)):
                affinity_matrix[a1, a2] = self.aff(self.attributes[a1], self.attributes[a2])
                
        return np.matrix(affinity_matrix)

    def attributes_usage_matrix(self, attributes, queries):
        """
        Attributes Usage Matrix

        Parameters
        ----------
        attributes : list
            List of attributes
        queries : list
            List of queries
        """
        
        usage = np.zeros((len(queries), len(attributes)), dtype=int) # Create a matrix with the size of queries x attributes
        
        attribute_columns = {idx: attribute for idx, attribute in enumerate(attributes)} # Create a dictionary with the index as keys and the attributes as values
        
        for i, query in enumerate(queries):
            for j, attribute in enumerate(attributes):
                if attribute in query: # If the attribute is used in the query, set the value to 1
                    usage[i, j] = 1
                    if attribute not in attribute_columns: # If the attribute is not in the dictionary, add it
                        attribute_columns[j] = attribute
        
        return np.matrix(usage), attribute_columns
    
    def BEA(self):
        """
        Bond Energy Algorithm   
        """
        log.info("----------------")
        log.info(f"BEA")
        log.info("----------------")
        CA = self.AA[:, :2] # Create a matrix with the first two columns of the affinity matrix
        
        new_columns_pos = [self.columns_pos[k] for k in list(self.columns_pos)[:2]]
        log.info(new_columns_pos)
        
        # Add zeros columns at the beginning and end of the CA matrix
        CA = np.append(np.zeros((self.AA.shape[0],1)), CA, axis=1)
        CA = np.append(CA,np.zeros((self.AA.shape[0],1)), axis=1)
        
        log.info(CA)
        
        index = 2 # Start from the third column

        while index < len(self.AA): # Iterate through the columns
            
            cont_score = [] # Create a list to store the contribution score
            
            j = 0
            
            for i in range(1, CA.shape[1]): # Iterate through the columns of the CA matrix
                cont = (2 * np.dot(CA[:, j:j+1].T, self.AA[:, index:index+1]) + 
                      2 * np.dot(self.AA[:, index:index+1].T, CA[:, i:i+1]) - 
                      2 * np.dot(CA[:, j:j+1].T, CA[:, i:i+1]))
                cont_score.append(cont) # Store the contribution score in the list
                j = i
                
            loc = np.argmax(cont_score) + 1 # Get the index of the maximum contribution score
            log.info(f"\nCont score: {[score.item() for score in cont_score]}")
            log.info(f"Best pos: {loc - 1}")
            
            temp = {loc: self.columns_pos[index]}
            new_columns_pos.insert(loc - 1, temp[loc])
            log.info(new_columns_pos)
            
            CA = np.insert(CA, loc, self.AA[index:index+1], axis=1) # Insert the column with the maximum contribution score to the CA matrix
            
            log.info(CA)
            
            index += 1
        
        # Remove the first and last columns of zeros the CA matrix
        CA = np.delete(CA, 0, axis=1)
        CA = np.delete(CA, CA.shape[1]-1, axis=1)
        
        # Order the rows of CA according to the relative position of columns
        ordered_CA = np.zeros_like(CA)
        for idx, col in enumerate(new_columns_pos):
            row_idx = list(self.columns_pos.values()).index(col) # Get the index of the column
            ordered_CA[idx, :] = CA[row_idx, :]
        
        self.CA = np.matrix(ordered_CA)
        
        self.CA_columns_pos = new_columns_pos
    
    def Split(self):
        """ 
        Split Algorithm
        """
        log.info("\n----------------")
        log.info(f"SPLIT")
        log.info("----------------")
        
        def usage(use):
            query = []
            for row in use:
                if 1 in row:    
                    query.append(1)
                else:
                    query.append(0)
            return query
        
        def partition_point():
            CTQ = 0
            CBQ = 0
            COQ = 0
            
            log.info(f"\nTA: {TA_columns_pos}\nBA: {BA_columns_pos}")
            
            TA_usage = self.attributes_usage_matrix(TA_columns_pos, self.queries)[0]
            BA_usage = self.attributes_usage_matrix(BA_columns_pos, self.queries)[0]
 
            TA_query = usage(TA_usage)
            BA_query = usage(BA_usage)
            
            log.info(f"\nTA: {TA_query}\nBA: {BA_query}")
            
            for i in range(len(TA_query)):
                if TA_query[i] and BA_query[i]:
                    COQ += self.acc_sum[i]
                elif TA_query[i] and not BA_query[i]:
                    CTQ += self.acc_sum[i]
                else:
                    CBQ += self.acc_sum[i]
            
            log.info(f"CTQ: {CTQ}, CBQ: {CBQ}, COQ: {COQ}\n result: {CTQ * CBQ - COQ**2}")
            return CTQ * CBQ - COQ**2
        
        split_columns = self.CA_columns_pos
        log.info(f"\n{split_columns}")
        
        TA_columns_pos = split_columns[:-1] # Create a list with all columns except the last column of the CA matrix
        BA_columns_pos = split_columns[-1:] # Create a list with the last column of the CA matrix
        
        best = [TA_columns_pos]
        best_score = partition_point()
        
        for i in range(len(split_columns)):
            for i in range(2, len(split_columns)):
                TA_columns_pos = split_columns[:-i] # Create a list with all columns except the last i columns of the CA matrix
                BA_columns_pos = split_columns[-i:] # Create a list with the last i columns of the CA matrix
                z = partition_point()
                if z > best_score:
                    best_score = z
                    best = [TA_columns_pos]
                elif z == best_score:
                    best.append(TA_columns_pos) # Save all TA of the highest score
            log.info("----------------\n")
            split_columns.append(split_columns.pop(0))
            log.info(f"{split_columns}")
        
        # Assuming the first attribute is the key
        key = list(self.columns_pos.values())[0]
        for ta in best:
            if key not in ta:
                ta.insert(0, key)
            else:
                ta.remove(key)
                ta.insert(0, key)
        
        self.best = best
        
if __name__ == "__main__":
    
    log.basicConfig(
        filename='vertical_fragmentation.log',
        encoding='utf-8',
        filemode='w',
        format='%(message)s',
        level=log.INFO
    )
    
    def fragment(columns, queries, acc):
        frag = VerticalFragmentation(columns, queries, acc)

        # USE
        print("-------- Use --------")
        print(list(frag.columns_pos.values()))
        use = frag.usage_matrix
        print(use)
        
        # AA
        print("\n-------- AA --------")
        AA = frag.AA
        print(list(frag.columns_pos.values()))
        print(AA)
        
        # BEA
        frag.BEA()
        BEA = frag.CA
        print("\n-------- CA --------")
        print(frag.CA_columns_pos)
        print(BEA)
        
        # Split
        frag.Split()
        split = frag.best
        print("\n-------- Split --------")
        for frag in split:
            print(frag)
    
    ##################### Proj ##########################
    """
    acc = np.array([[15, 20, 10],
                    [ 5,  0,  0],
                    [25, 25, 25],
                    [ 3,  0,  0]])    
    
    columns = ['PNO', 'PNAME', 'BUDGET', 'LOC']
    
    q1_query = "SELECT BUDGET FROM PROJ WHERE PNO = 'VALUE'"
    q2_query = "SELECT PNAME,BUDGET FROM PROJ"
    q3_query = "SELECT PNAME FROM PROJ WHERE LOC = 'VALUE'"
    q4_query = "SELECT SUM(BUDGET) FROM PROJ WHERE LOC = 'VALUE'"
    
    queries = [q1_query, q2_query, q3_query, q4_query]
    """
    ##################### Quá trình ##########################
    
    acc = np.array([[10, 20, 0],
                    [0, 20, 10]])

    columns = ['ENO', 'ENAME', 'PNO', 'DUR', 'RESP']
    
    q1_query = "CREATE VIEW EMPVIEW (ENO, ENAME, PNO, RESP) AS SELECT E.ENO, E.ENAME, ASG.PNO, ASG.RESP FROM EMP, ASG WHERE EMP.ENO=ASG.ENO AND DUR=24"
    q2_query = "SELECT ENO, DUR FROM ASG"
    
    queries = [q1_query, q2_query]
    
    fragment(columns, queries, acc)