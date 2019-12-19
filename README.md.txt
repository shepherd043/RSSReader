CS50 Final Project:    RSS Addict README Document

RSS Addict is a simple RSS feed reader that allows users to customize their own news feed only pulling news from sources they select. The app will also come with a few pre-made lists for different topics that the user can choose from as well.

What is an RSS Feed?

RSS stands for Really Simple Syndication and it is used as a way to convey information by converting the information to an XML file which can be easily read by a computer. This RSS reader will retrieve the XML data from every feed address that is provided by the user and store the information into  a database. When the user logins to their account all their associated feeds will be displayed in an easy to read form. Each article displayed for the user will also contain a link that will provide the user access to the full article from the originating website.  Different RSS feeds have different formats from each other depending on where they come from. This application should be able to pull all the information from at least 4 different formats but some news cards maybe missing images and/or descriptions.

Where can RSS Feeds be found?

	Many different websites and companies still use RSS feeds for any news and updates that they want to report. Many of these websites also make the feeds available and easy to find for people to be able to follow them and read the information using their favourite RSS feed reader.  If you see a  RSS symbol on a website then that should lead you to the RSS feed address.  Sometimes instead of the symbol companies may have the link to their feed in the footer of their website or in their contact page, it may take some searching to find it.  If you just want to find feeds for specific categories then Google is your friend and you should be able to find one or two feeds that you can follow in RSS Addict.

How to Use this Web Application:

Upon launching this web application the user will be brought to the login screen. If the user already holds an account then it is just a matter of typing in the username and password and hitting enter. If the user does not yet have an account then they can click the register button where they will be redirected to the registration page.

To register for an account all fields must be completed in order for the account to be created. Once the account is setup then the user will be automatically logged in and redirected to the home page of the application.

The Home Page:
	After the user is logged in they will be directed to the homepage. In the homepage there will be an application menu at the top that will contain a welcome message top centre, an add feed input bar on the left hand side, a pre-made news selection list and a logout button on the right hand side. The remainder of the screen will be empty for now until the user starts to input RSS Feeds.

To add an RSS Feed simply input the URL/web address of the feed you wish to follow into the "Add Feed bar" at the top left of the application. If there are no errors with the provided address then the main screen will populate with news cards for each individual article within the feed. There will also be a selection box on the right hand side so that you can choose to follow all of your feeds at once or read articles from specific feeds only.

If you do not know of any feeds you wish to follow right away then there are premade feed lists that can be chosen instead. There are feeds from 3 different sources within each category to give the users a few feeds that they can follow until they find others they wish to view.  Any feeds that are submitted are saved into a database and recalled and updated the next time the user logs in.  

