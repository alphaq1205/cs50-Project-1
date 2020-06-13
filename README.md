# Project 1

This is a website on which one can search for different books can rate and review particular book searched for. This website is built on flask with postgresql. Goodreads api is used in this project to mention the work_ratings_count and average_rating so user can get more accurate reviews count.

The sections of this website are:-

### Front Page
This is sort of a welcome page which contain login and signup navigation buttons each buttons will take user to particular page which are either login page or registration page.

### Registration
Users is able to register on this website by providing a username, email and password.

### Login
Users, once registered, is able to log in to website with their email and password. 

### Logout
User is able to logout from the website once user is loged in by click the logout button on the inner pages.

### Homepage
This is first page which occur after loging in to website. It contain a search-bar, sidebar, table.
1. Sidebar - This sidebar is static in all pages of the website. It contain homepage and logout buttons so that user can logout or can navigate to homepage from any page of the website.

2. Search - Through this search-bar user can search for a book. Users can type in the ISBN number of a book, the title of a book, or the author of a book. After performing the search, the data is display a table form of possible matching results, or shows sort of message if there were no matches. User can also type in only part of a title, ISBN, or author name, and search page will find matches for those as well. 

3. Table - This table contain four section which are isbn, title, author and year of publication. After performing the search, the data is display a table form of possible matching results. The data of title section contain a navigation link which will take user to  book details page and The data of isbn section contain a navigatin link which gives access to api of book details in JSON form.


4. API Access - If users make a GET request to this website’s /api/<isbn> route, where <isbn> is an ISBN number, website returns a JSON response containing the book’s title, author, publication date, ISBN number, review count, and average score. The resulting JSON should follow the format.

### Book Page
When users click on a book from the results of the search page, they are taken to this page, with details about the book: its title, author, publication year, ISBN number, average rating(goodreads), number of ratings(goodreads) and any reviews that users have left for the book on your website. This page contain :-

1. Review Submission- On this page, users are be able to submit a review: consisting of a rating on a scale of 1 to 5, as well as a text component to the review where the user can write their opinion about a book. Users are not be able to submit multiple reviews for the same book. users can update their review and also can delete there review if they want to.

2. Goodreads Review Data- On this page, website also display (if available) the average rating and number of ratings the work has received from Goodreads.
