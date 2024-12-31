import numpy as np

class VerticalFragmentation:
    def __init__(self, attributes, queries):
        self.attributes = attributes
        self.queries = queries
        
        self.usage_matrix, self.columns_pos = self.attributes_usage_matrix(attributes, queries)
        self.access_freq()
        self.affinity_matrix = self.attribute_affinity_matrix()
        
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
    
class ClusteringAlg(VerticalFragmentation):
    def __init__(self, attributes, queries):
        super().__init__(attributes, queries)
    
    def bond(self, attribute1, attribute2):
        """
        Bond between two attributes
        """
        result = 0
        for row in range(self.affinity_matrix.shape[0]):
            try:
                a1 = list(self.columns_pos.keys())[list(self.columns_pos.values()).index(attribute1)]
            except ValueError:
                continue
            try:
                a2 = list(self.columns_pos.keys())[list(self.columns_pos.values()).index(attribute2)]
            except ValueError:
                continue
            result += self.affinity_matrix[row, a1] * self.affinity_matrix[row, a2]
        
        return result
    
    def cont(self, attribute1, attribute2, attribute3):
        """
        Contribution to Global Affinity Measure - AM
        """
        print(attribute1, attribute2, attribute3)
        return (2*self.bond(attribute1, attribute2) + 2*self.bond(attribute2, attribute3) - 2*self.bond(attribute1, attribute3))
    
    def BEA(self):
        """
        Bond Energy Algorithm   
        """
        CA = np.zeros((self.affinity_matrix.shape[0], self.affinity_matrix.shape[1])) # Create a matrix with the size of attributes x attributes
        
        # Copy the first two columns of the affinity matrix to the CA matrix
        CA[:, 0] = self.affinity_matrix[:, 0].reshape(-1)
        CA[:, 1] = self.affinity_matrix[:, 1].reshape(-1)
        
        index = 2 # Start from the third column

        while index <= self.affinity_matrix.shape[1]: # Iterate through the columns
            
            cont_score = {} # Create a dictionary to store the contribution score
            
            '''
            BUG: nó lấy toàn bộ attribute của AA thay vì là các Attributes đang có CA
            eg:
            While lần đầu CA có 2 cột: PNO và PNAME -> chèn vào BUDGET
            Lặp while lần đầu tính:
                cont(0 BUDGET PNO)
                cont(PNO BUDGET PNAME)
                cont(PNAME BUDGET LOC)
            thay vì là:
                cont(0 BUDGET PNO)
                cont(PNO BUDGET PNAME)
                cont(PNAME BUDGET 0) -> LOC lúc này ko tồn tại trong CA
            '''
            
            for i in range(index): # Iterate through the columns of the CA matrix
                try:
                    cont = self.cont(self.columns_pos[i - 1], self.columns_pos[index], self.columns_pos[i]) # Calculate the contribution between the columns
                    cont_score[i] = cont # Store the contribution score in the dictionary
                except KeyError:
                    try:
                        cont = self.cont(0, self.columns_pos[index], self.columns_pos[i]) # Calculate the contribution between the columns
                        cont_score[i] = cont # Store the contribution score in the dictionary
                    except KeyError:
                        cont = self.cont(0, 0, self.columns_pos[i]) # Calculate the contribution between the columns
                        cont_score[i] = cont
            
            try:
                cont = self.cont(self.columns_pos[index - 1], self.columns_pos[index], self.columns_pos[index + 1]) # Calculate the contribution between the last column and the next column
            except KeyError:
                try:
                    cont = self.cont(self.columns_pos[index - 1], self.columns_pos[index], 0)
                except KeyError:
                    cont = self.cont(self.columns_pos[index - 1], 0, 0)
            cont_score[i + 1] = cont
            
            print(cont_score)
            
            loc = max(cont_score, key=cont_score.get) # Get the location with the maximum contribution score

            for j in range(index, loc, -1):
                CA[:, j] = CA[:, j - 1] # Shift the columns to the right
            
            CA[:, loc] = self.affinity_matrix[:, index].reshape(-1)
            index += 1
            
            print(np.matrix(CA))
        
        # Reorder the rows to match the relative position of the columns
        ordered_CA = np.zeros_like(CA)
        for i in range(CA.shape[0]):
            ordered_CA[i, :] = CA[self.columns_pos.index(self.attributes[i]), :]
        
        return np.matrix(ordered_CA)
        
if __name__ == "__main__":
    
    columns = ['PNO', 'PNAME', 'BUDGET', 'LOC']
    
    q1_query = "SELECT BUDGET FROM PROJ WHERE PNO = 'VALUE'"
    q2_query = "SELECT PNAME,BUDGET FROM PROJ"
    q3_query = "SELECT PNAME FROM PROJ WHERE LOC = 'VALUE'"
    q4_query = "SELECT SUM(BUDGET) FROM PROJ WHERE LOC = 'VALUE'"
    queries = [q1_query, q2_query, q3_query, q4_query]
    
    proj = ClusteringAlg(columns, queries)
    
    print(proj.BEA())
    
    

