# Business case: Collaborative Filtering Movie Recommender

**"People who rate like you loved these", served from an API.**

## Who buys this

The buyer is a product lead at a small catalogue business (a niche streaming service, an online bookshop, a course platform) that has ratings or purchase history but no recommendation system. The users are the customers who see the suggestions and the product team that tunes them.

## The problem and what it costs

Large catalogues overwhelm people. Netflix's own engineers reported that recommendations influence **about 80% of hours streamed** on Netflix, and estimated that personalisation and recommendations save the company **more than US$1 billion a year**, mainly through lower churn ([Gomez-Uribe and Hunt, 2015, ACM TMIS](https://dl.acm.org/doi/10.1145/2843948)). A small business will not see numbers like that, but the mechanism is the same: help people find something they like before they leave.

## How the repo solves it

| Need | What in the repo does it |
|---|---|
| Find similar users | User-based collaborative filtering with cosine similarity over a user × movie matrix (`api/`), taken from `CollaborativeFiltering.ipynb` |
| Recommend unseen items | `GET /recommendations/{name}?k=&top_n=` ranks unseen movies by the mean rating of the k nearest users |
| Explain a suggestion | Each card shows the neighbour score, the overall average and the full rating distribution, next to the viewer's own top-rated films |
| Benchmark data | The MovieLens 100K ratings set: 100,000 ratings, 944 users, 1,682 movies ([GroupLens](https://grouplens.org/datasets/movielens/100k/)) |

## Use-case scenarios

All of these organisations are fictional.

1. **A niche film-streaming service** shows a "viewers like you watched" row on the home page.
2. **An independent online bookshop** recommends titles from rating and purchase history and checks each suggestion against the customer's own favourites.
3. **A training-course platform** suggests the next course from how similar learners rated the ones they finished.

## ROI: a worked model (illustrative)

These figures are **illustrative assumptions** unless a source is linked.

| Input | Value | Basis |
|---|---|---|
| Monthly active subscribers | 20,000 | Assumption |
| Monthly price | US$8 | Assumption |
| Monthly churn before | 5% | Assumption |
| Relative churn reduction from better discovery | 5% (5.00% to 4.75%) | Assumption, to be measured by A/B test |

Subscribers retained: 20,000 × 0.25% = 50 a month. If each stays about 12 more months: 50 × 12 × $8 × 12 months ≈ **US$58,000 a year** of retained revenue once the effect builds up. The churn reduction is the key unknown, which is why the path to production starts with an A/B test.

## Path to production

1. Replace the MovieLens data with your own ratings or implicit signals (views, purchases).
2. Precompute neighbours offline. In-memory user-based filtering does not scale to millions of users.
3. A/B test against a popularity baseline and measure retention, not just clicks.
4. Compare with item-based or matrix-factorisation models once data grows.

## Risks and limits

- New users and new items have no ratings (the cold-start problem), so a fallback such as popularity is needed.
- User-based similarity over a dense matrix is memory-heavy at scale.
- MovieLens is a 1998 benchmark, so results here say nothing about your catalogue.

**Case strength:** **Moderate.** The business value of recommendations is well documented, but this repo is a clear, small implementation of a classic algorithm, not a production recommender.

## Sources

- Gomez-Uribe, C. and Hunt, N. (2015), The Netflix Recommender System, ACM TMIS 6(4): https://dl.acm.org/doi/10.1145/2843948
- GroupLens, MovieLens 100K dataset: https://grouplens.org/datasets/movielens/100k/
