from embed import embed
def retrieve_from_pinecone(index, model, tokenizer, state, county, zip):
    prompts = [f"News about hurricanes, hurricane damage, hurricane preparedness, sea level rise, property values in {county}, {state} at zip code {zip}"]
    vectors = embed(prompts, model, tokenizer)
    response = index.query(
        vector = vectors.tolist(),
        top_k = 10,
        include_metadata = True
    )
    string_resp = ""
    sources = []
    print(response)
    for res in response['matches']:
        string_resp += res['metadata']["content"] + "\n\n\n"
        sources.append(res["metadata"]['url'])
    return string_resp, sources