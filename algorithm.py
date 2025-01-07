import numpy as np

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
        CA = self.AA[:, :2] # Create a matrix with the first two columns of the affinity matrix
        
        new_columns_pos = [self.columns_pos[k] for k in list(self.columns_pos)[:2]]
        print(new_columns_pos)
        
        # Add zeros columns at the beginning and end of the CA matrix
        CA = np.append(np.zeros((self.AA.shape[0],1)), CA, axis=1)
        CA = np.append(CA,np.zeros((self.AA.shape[0],1)), axis=1)
        
        print(CA)
        
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
            print(f"\nCont score: {[score.item() for score in cont_score]}")
            print(f"Best pos: {loc - 1}")
            
            temp = {loc: self.columns_pos[index]}
            new_columns_pos.insert(loc - 1, temp[loc])
            print(new_columns_pos)
            
            CA = np.insert(CA, loc, self.AA[index:index+1], axis=1) # Insert the column with the maximum contribution score to the CA matrix
            
            print(CA)
            
            index += 1
        
        # Remove the first and last columns of zeros the CA matrix
        CA = np.delete(CA, 0, axis=1)
        CA = np.delete(CA, CA.shape[1]-1, axis=1)
        
        # Order the rows of CA according to the relative position of columns
        ordered_CA = np.zeros_like(CA)
        for idx, col in enumerate(new_columns_pos):
            row_idx = list(self.columns_pos.values()).index(col) # Get the index of the column
            ordered_CA[idx, :] = CA[row_idx, :]
        
        CA = np.matrix(ordered_CA)
        
        return CA
    
    def Split(self):
        """ 
        Split Algorithm - chưa làm
        """
        pass

if __name__ == "__main__":
    
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
    
    
    acc = np.array([[10, 20, 0],
                   [0, 20, 10]])
    
    columns = ['ENO', 'ENAME', 'PNO', 'DUR', 'RESP']
    
    q1_query = "CREATE VIEW EMPVIEW (ENO, ENAME, PNO, RESP) AS SELECT E.ENO, E.ENAME, ASG.PNO, ASG.RESP FROM EMP, ASG WHERE EMP.ENO=ASG.ENO AND DUR=24"
    q2_query = "SELECT ENO, DUR FROM ASG"
    
    queries = [q1_query, q2_query]
    
    
    proj = VerticalFragmentation(columns, queries, acc)
    
    print("----------------\n")
    print("Original Attributes")
    print(proj.attributes)
    print("\n----------------\n")
    print("USE")
    print(proj.usage_matrix)
    print("\n----------------\n")
    print("AA")
    print(proj.AA)
    print("\n----------------\n")
    print("BAE")
    result = proj.BEA()
    print("-------- Result --------")
    print(result)