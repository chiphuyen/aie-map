# aie-map

I want to create a map to track where the 2 books AI Engineering (AIE) and Designing Machine Learning Systems (DMLS) are being read.

## Frontend
When users visit the website, there's a page with a world map, where every time a review is posted in a city, you add a pin to that city on the map. AI Engineering's pin is red. DMLS's pin is green.

When you zoom out, you show the number of pins for each book in each city.

When users click on the number, it shows all the reviews in that city in a list. Each review contains the following information, though not all reviews have all the information.
1. The book the review is about. A review can be about both books. If a review is about both books, create 2 separate pins (one for each book)
2. The date the review is added
3. The review
4. The name of the person writing that review
5. The company that person is at
6. The role of that person at the company
7. Source of the review (e.g. GoodReads, Amazon, O'Reilly, LinkedIn, X, Substack, Reddit, ...)
8. Link to the original review (if any)
9. Social media link of the reviewer (if any)
10. Assets associated with the review (e.g. the screenshot of the review)
11. The time when the review is uploaded

Make the location optional. If no location is chosen, default to Antartica.

If users click on a review, there can be a link to the person's original post.

### See all reviews
When I click on a book's name, I can see a list of all reviews for that book. Each review in the list should be compact (with options to read more) and with city tag next to it.

When I click on the city/country name from each review, I can see all reviews for that city/country.

When I click on the company name from each review, I can see all reviews from that company.

## Upload a review

When I visit the link [homepage]/upload, I can upload a review by potentially uploading a screenshot of the review.

If a screenshot is uploaded, automatically extract all the information you can.

If an information is missing, there's an option for me to add the missiong detail.

### Auto-extract information from each screenshot
Use a better model for information extraction from image, ideally an open source LLM.
1. Choose a model for it.
2. Write the prompt to extract the data.
3. Write test to make sure the extraction is correct.