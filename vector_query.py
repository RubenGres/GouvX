def get_semantically_close_text(question, client, model=None):
    query = (
       client.query
      .get("ServicePublic", ["text", "url", "subdomain", "title", "paragraph", "line_n"])
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

    if 'errors' in response["data"]["Get"].keys() and response["data"]["Get"]['errors'] is not None:
       raise RuntimeError('There is some error in weaviate for this query')

    return response


def get_page(client, url):
  url_filter = {
    "path": ["url"],
    "operator": "Equal",
    "valueText": url,
  }

  sort_order = [
    {
      'path': ['line_n'],
      'order': 'asc'
    },
  ]

  response = (
    client.query
    .get("ServicePublic", ["text", "url"])
    .with_where(url_filter)
    .with_sort(sort_order)
    .do()
  )

  page = [result['text'] for result in response["data"]["Get"]["ServicePublic"]]

  return "\n".join(page)


def get_paragraph(client, url, paragrah_number):
  url_filter = {
    "path": ["url"],
    "operator": "Equal",
    "valueText": url,
  }

  paragraph_filter = {
    "path": ["paragraph"],
    "operator": "Equal",
    "valueNumber": paragrah_number,
  }

  total_filter = {
      "operator": "And",
      "operands": [url_filter, paragraph_filter]
  }

  sort_order = [
    {
      'path': ['line_n'],
      'order': 'asc'
    },
  ]

  response = (
    client.query
    .get("ServicePublic", ["text", "url"])
    .with_where(total_filter)
    .with_sort(sort_order)
    .do()
  )

  page = [result['text'] for result in response["data"]["Get"]["ServicePublic"]]

  return "\n".join(page)


def get_around_paragraph(client, url, paragrah_number, line_n, n_lines_around=3):
  url_filter = {
    "path": ["url"],
    "operator": "Equal",
    "valueText": url,
  }

  paragraph_filter = {
    "path": ["paragraph"],
    "operator": "Equal",
    "valueNumber": paragrah_number,
  }

  line_n_filter_gte = {
    "path": ["line_n"],
    "operator": "GreaterThanEqual",
    "valueNumber": line_n - n_lines_around,
  }

  line_n_filter_lte = {
    "path": ["line_n"],
    "operator": "LessThanEqual",
    "valueNumber": line_n + n_lines_around,
  }

  total_filter = {
      "operator": "And",
      "operands": [url_filter, paragraph_filter, line_n_filter_gte, line_n_filter_lte]
  }

  sort_order = [
    {
      'path': ['line_n'],
      'order': 'asc'
    },
  ]

  response = (
    client.query
    .get("ServicePublic", ["text", "url"])
    .with_where(total_filter)
    .with_sort(sort_order)
    .do()
  )

  page = [result['text'] for result in response["data"]["Get"]["ServicePublic"]]

  return "\n".join(page)

