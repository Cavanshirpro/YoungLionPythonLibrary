from YoungLion import ListDDM, DDM

rows = ListDDM(DDM({"id":i,"metrics":{"score":float((i*13)%120),"bonus":1.0}}) for i in range(20000))
rows.multiply("metrics.score",1.075)
rows.increment("metrics.score",3)
rows.clamp("metrics.score",0,100)
print({"count":rows.numeric_count("metrics.score"),"mean":rows.mean("metrics.score"),"min":rows.min("metrics.score"),"max":rows.max("metrics.score")})
