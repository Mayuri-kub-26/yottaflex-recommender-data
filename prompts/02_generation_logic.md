# Data Generation Logic Notes

## The challenge

500k sessions + 100k orders is a lot to generate in pure Python without NumPy. My first instinct was to use Faker for names but the spec said no external deps, so everything had to come from random + a word list.

## Distributions I had to think through

**Sessions**: Not every customer sessions equally. Real users have power-law behavior - 15% of customers generate way fewer sessions (sparse users). Also 1-2% of traffic is bot-like (lots of pageviews, weird patterns). Had to model both.

**Products**: The spec specifically called out "cold-start" products. I set 10% of products with recent launch dates and flagged them `is_cold_start=True`. That way a recommender engineer can test fallback strategies on those.

**Categories**: Some categories (clothing, sports, toys) are seasonal. I added `is_seasonal` boolean on Category.

## Question I asked AI about the train/test split

I knew I needed to avoid data leakage but wasn't 100% sure on the right cutoff strategy. Asked:

> "Should I do a random 80/20 split or a time-based one for a recommendation dataset?"

AI explained that random splits in recommender systems cause future purchases to leak into training data, which inflates offline metrics but kills production performance. Chronological split by session timestamp is the right approach.

That made sense - if a customer buys something on Wednesday, the model shouldn't "learn" from that to recommend things they were browsing on Monday.

## What I settled on

- Sort sessions by session_start ascending
- Take first 80% as train, last 20% as test
- Propagate the split label to recommendations based on their session_id

## Another AI question - recommendation exclusion rules

Asked for a sanity check on whether "exclude purchased items" should use all historical purchases or only purchases before the recommendation timestamp. AI said strictly before - using future purchases would be leakage. I implemented it as: build the purchased set from order_lines at data generation time (which is fine since we're building a static dataset, not a live system).

