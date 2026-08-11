from tempfile import TemporaryDirectory
from YoungLion import File, DDMTable
from models import Customer
with TemporaryDirectory() as tmp:
    f=File(tmp)
    f.csv_write("input.csv",[{"id":"1","name":" Alice ","country":"us","spend":"120.5"},{"id":"2","name":"Cavan","country":"az","spend":"410"},{"id":"3","name":"Bob","country":"de","spend":"75"}])
    customers=DDMTable(Customer(row) for row in f.csv_read("input.csv"))
    print("mean spend",customers.mean("spend"),"countries",customers.distinct("country"))
    f.csv_write("clean.csv",[{k:str(v) for k,v in row.items()} for row in customers.select("id","name","country","spend")])
    print(f.txt_read_str("clean.csv"))
