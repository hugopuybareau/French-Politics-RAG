from sentence_transformers import SentenceTransformer

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def get_embedding(text: str):
    return model.encode([text])[0].tolist() #Wrap it in a list so the single string test vector doesn't
                                            #generate a float instead of a 1D-np.ndarray. 

