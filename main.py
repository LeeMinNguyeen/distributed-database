from database import database
from algorithm import VerticalFragmentation
import numpy as np

project = database("NGUYIN\\NGUYIN", "PROJECT")
project.connect()

def fragment(columns, queries, acc):
    frag = VerticalFragmentation(columns, queries, acc)
    
    # BEA
    frag.BEA()
    BEA = frag.CA
        
    # Split
    frag.Split()
    split = frag.best
        
    print("-------- BEA --------")
    print(frag.CA_columns_pos)
    print(BEA)
        
    print("\n-------- Split --------")
    for frag in split:
        print(frag)

acc = np.array([[10, 20, 0],
                [0, 20, 10]])

columns = ['ENO', 'ENAME', 'PNO', 'DUR', 'RESP']
    
q1_query = "CREATE VIEW EMPVIEW (ENO, ENAME, PNO, RESP) AS SELECT E.ENO, E.ENAME, ASG.PNO, ASG.RESP FROM EMP, ASG WHERE EMP.ENO=ASG.ENO AND DUR=24"
q2_query = "SELECT ENO, DUR FROM ASG"
    
queries = [q1_query, q2_query]
    
fragment(columns, queries, acc)

project.close()

