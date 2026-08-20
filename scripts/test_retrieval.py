from app.rag.retriever import retrieve

print(retrieve("heart specialist doctor cardiac catheterization", doc_type="job", profession="Doctor")[0]["metadata"])
print(retrieve("ventilator ICU critical care nurse", doc_type="job", profession="Nurse")[0]["metadata"])
print(retrieve("how many consecutive night shifts are allowed", doc_type="knowledge")[0]["metadata"])