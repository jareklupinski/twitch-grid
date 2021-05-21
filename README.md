# twitch-grid

twitch-grid is a listing of currently live Twitch streams I created to help me find popular but under-appreciated games.

I know I can count on a gem when I see one or two people streaming to a total of hundreds or thousands 👐

![Screen Shot 2021-05-18 at 7 04 47 PM](https://user-images.githubusercontent.com/2049284/118734219-ed47f880-b80b-11eb-82f7-f3df07066ca6.png)

Give it a try! https://twitch-grid.herokuapp.com/ (please be patient, it may take a moment to load all 250 games per page from the Heroku Free Tier 🙂 )

Each row corresponds to a single game, with the channels currently streaming that game listed by viewer count.

The games themselved are listed in order of total viewers for that game among all streamers.

## Design

The app was engineered to fit inside the free-tier limits of Heroku and the Twitch API.

The Twitch API rate-limits to 800 calls per minute, and with 4000 games being played simultaneously sometimes, a cache is needed to render a page for everyone without running out of credits.

Heroku Scheduler runs a job every ten minutes to fetch the relevent data (slowly) from Twitch and stores it in a Postgres DB.

Django helps in quickly putting together a front-end for the cached results for page visitors.
