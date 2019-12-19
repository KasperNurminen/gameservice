# WSD Project plan
### Project members
* Kasper Nurminen 602486
* Sanni Lares 647984
* Atte Mäkinen 596925
### General description
We are planning to implement all mandatory and some optional requirements. We will go through each requirement one by one.
 
__Authentication:__
We will implement a Django authentication with email validation using Django’s Console backend. We will not configure a real SMTP-server. Our user-model can have multiple roles, each user is either a player, developer or both. We use django.contrib.auth.roles to accomplish this. We use Django’s default django.contrib.auth user-model for this.
 
__Basic player functionalities:__
Every user who has the role of player is able to purchase games from the course’s mockup payment service. Players are also able to play the purchased games, but not any non-purchased titles. 
 
Players are able to find games via a search (by at least name) or via a category that the developer decided. A game must have exactly one category. The search can also filter by games that the player own, so that no non-purchased titles are visible. The filter can use the payments-model and filter it by player. 
 
__Basic developer functionalities:__
A developer can add and edit their titles from the same view. The functionalities are the same, only the texts are different with editing and creating new. A developer also has a “my games” -view, which displayes sales statistics and game inventory for each game. Game-model has a developer-attribute, so that each game knows who is allowed to edit or remove the game and who isn’t.
 
__Game/service interaction:__
When player has finished playing a game (or presses submit score), the game sends a postMessage to the parent window containing the current score. This score is saved to the Score-model. The highscores are displayed on the same page as the game. A player can view their personal high scores from their own profile page. The scores are transmitted using postMessage.
  
__Save/load and resolution feature:__
The service supports saving and loading for games with the simple message protocol described in Game Developer Information. A saved game data is saved to the savedata-object. Each time a game sends the LOAD_REQUEST -message, the service checks whether a save data exists. If it does, it sends the save data to the game. The game can also send the SETTINGS-command, which for example sets the resolution. This is not saved to the service, as the game should send the command each time it has loaded.
 
__RESTful API__
We are planning on implementing a RESTful API for at least some of the services. We have not yet decided which ones, but the authentication should come “for free” with django auth. It sets the access token as a cookie, so that we can require that the access token cookie exists for any API. We are not planning to implement any other access methods, so OAuth etc is not supported.
 
__Mobile Friendly__
We are planning to create a mobile-friendly game service. It should work on all size devices. We will use Bootstrap to accomplish this.
 
 
### Models
We will (initially) use these models:

__User__
The users are extended from django.contrib.auth.user. Each user can have 2 possible groups: developer and player. Each group has their own set of permissions. Therefore we only need to specify the group when creating a new user, and the permissions will then be handled automatically.

We use the following fields:
* username
* password
* email
* groups
* first_name
* last_name

__Score__
A score object relates a numerical score with a game and a player. It has the following fields:

* player:  ForeignKey(User)
* score:  IntegerField
* game:  ForeignKey(Game)

__Game__
A game object holds all the relevant information about a game title.
It has the following fields:
* title: Charfield
* developer: ForeignKey(User)
* price:  DecimalField 
* url: URLField

The prices are saved as DecimalFields to prevent floating point errors. We don't want any cents to go missing because of our lousy programming.

__Savedata__
A player might play a game a bit, and return to it later. Therefore a game can save it’s progress and we need a model for that. This model has the following fields:
* player:  ForeignKey(User)
* data:  Charfield
* game:  ForeignKey(Game)

Data is saved as a string, as it is not useful for django to store it as JSON.

__Payment:__
We use https://tilkkutakki.cs.aalto.fi/payments/ as a payment processor. Sid and pid are required in tilkkutäkki. Pid is our own identifier for a payment, and sid is calculated from the username.

* player:  ForeignKey(User)
* price:  DecimalField
* game:  ForeignKey(Game)
* sid: Charfield
* pid: Charfield

### Initial view proposal

* Login  (Atte, done by 9.1.2020)
    *  login
    *  register (as player)

* "Main view" (Kasper, done by 9.1.2020)
    * search and purchase games
    * filter to show only purchased
    * text search and category filtering

* Game view (Sanni, done by 9.1.2020)
    * playing each game
    * saving and loading data
    * high scores

* Developer inventory
    * list of developer's games, sales information and edit and remove buttons
  
* Add/edit game
    * possibility to modify name, price, url
	
* Profile
    * name
    * high scores for all games
    * payment history


### Project management

We are planning on meeting weekly and using Trello (or similar) for a Kanban-like workflow. We create issues, assign them to project members and complete them one by one. We will also use good git practices - all development is done in feature branches, and the changes are merged to master only after a team member has reviewed the changes. We will try to create as many tests as we think is necessary.
 
For version control, we use git with version.aalto.fi. 


__Project schedule__

* 10.12-20.12.2019 project planning
* 2.1.2020 ->  implementation
	*  weekly meetings
* initial heroku deployment goal by 1.2.2020
* release testing up until 13.2.2020
* 14.2.2020 final submission deadline

Unit tests are created for critical business functionality alongside coding, whenever we feel the need.





