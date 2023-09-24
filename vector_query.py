def get_semantically_close_text(question, client, model=None):
    query = (
       client.query
      .get("ServicePublic", ["text", "url", "subdomain", "title"])
    )

    if model:
        embedding = model.encode(question)
        nearVector = {"vector": embedding}
        query = query.with_near_vector(nearVector)
    else:
       query = query.with_near_text({"concepts": [question]})
       

    query = (
        query
        .with_limit(10)
        .with_additional(['certainty'])
    )

    response = query.do()

    print(response)

    if 'errors' in response["data"]["Get"].keys() and response["data"]["Get"]['errors'] is not None:
       raise RuntimeError('There is some error in weaviate for this query')

    return response
