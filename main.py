from database import database
import algorithm as alg
import numpy as np

project = database("NGUYIN\\NGUYIN", "PROJECT")
project.connect()

columns, row = project.sql("SELECT top(1) * FROM PROJ", type = "table")
print(columns)

q1_query = "SELECT BUDGET FROM PROJ WHERE PNO = 'VALUE'"
q2_query = "SELECT PNAME,BUDGET FROM PROJ"
q3_query = "SELECT PNAME FROM PROJ WHERE LOC = 'VALUE'"
q4_query = "SELECT SUM(BUDGET) FROM PROJ WHERE LOC = 'VALUE'"

q1 = project.sql(q1_query, type = "array")
q2 = project.sql(q2_query, type = "array")
q3 = project.sql(q3_query, type = "array")
q4 = project.sql(q4_query, type = "array")


project.close()

