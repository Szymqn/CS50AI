def transition_model(corpus, page, damping_factor):
    num_pages_corpus = len(corpus)
    num_links_page = len(corpus[page])

    link_prob = damping_factor * (1 / num_links_page)
    rand_page_prob = (1 - damping_factor) * (1 / num_pages_corpus)

    prob_distribution = {}

    for p in corpus:
        prob_distribution[p] = rand_page_prob

    for link in corpus[page]:
        prob_distribution[link] += link_prob

    return prob_distribution

# Example usage:
corpus = {
    '4.html': {'2.html'},
    '2.html': {'3.html', '1.html'},
    '1.html': {'2.html'},
    '3.html': {'2.html', '4.html'}
}

page = '4.html'
damping_factor = 0.85

result = transition_model(corpus, page, damping_factor)
print(result)
