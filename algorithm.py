import numpy as np

class VerticalFragmentation:
    def __init__(self, attributes, queries):
        self.attributes = attributes
        self.queries = queries
        
        self.usage_matrix, self.columns_pos = self.attributes_usage_matrix(attributes, queries)
        self.access_freq()
        self.affinity_matrix = self.attribute_affinity_matrix()
        
        self.BEA()
        
    def access_freq(self):
        """
        Access Frequency Matrix: application access frequency for each query
        """
        self.acc = np.array([[15, 20, 10],
                             [5 , 0 , 0 ],
                             [25, 25, 25],
                             [3 , 0 , 0 ]])
        
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
        CA = self.affinity_matrix[:, :2] # Create a matrix with the first two columns of the affinity matrix

        # Add zeros columns at the beginning and end of the CA matrix
        CA = np.append(np.zeros((4,1)), CA, axis=1)
        CA = np.append(CA,np.zeros((4,1)), axis=1)
        
        index = 2 # Start from the third column

        while index < len(self.affinity_matrix): # Iterate through the columns
            
            cont_score = [] # Create a list to store the contribution score
            
            j = 0
            
            for i in range(1, CA.shape[1]): # Iterate through the columns of the CA matrix
                cont = (2 * np.dot(CA[:, j:j+1].T, self.affinity_matrix[:, index:index+1]) + 
                      2 * np.dot(self.affinity_matrix[:, index:index+1].T, CA[:, i:i+1]) - 
                      2 * np.dot(CA[:, j:j+1].T, CA[:, i:i+1]))  
                cont_score.append(cont) # Store the contribution score in the list
                j = i

            loc = np.argmax(cont_score) + 1 # Get the index of the maximum contribution score

            CA = np.insert(CA, loc, self.affinity_matrix[index:index+1], axis=1) # Insert the column with the maximum contribution score to the CA matrix
            
            index += 1
        
        # Remove the first and last columns of zeros the CA matrix
        CA = np.delete(CA, 0, axis=1)
        CA = np.delete(CA, CA.shape[1]-1, axis=1)
        
        self.CA = np.matrix(CA)
    
    def Split(self):
        """ 
        Split Algorithm
        """
        pass

if __name__ == "__main__":
    
    columns = ['PNO', 'PNAME', 'BUDGET', 'LOC']
    
    q1_query = "SELECT BUDGET FROM PROJ WHERE PNO = 'VALUE'"
    q2_query = "SELECT PNAME,BUDGET FROM PROJ"
    q3_query = "SELECT PNAME FROM PROJ WHERE LOC = 'VALUE'"
    q4_query = "SELECT SUM(BUDGET) FROM PROJ WHERE LOC = 'VALUE'"
    queries = [q1_query, q2_query, q3_query, q4_query]
    
    proj = VerticalFragmentation(columns, queries)
    
    print(proj.CA)