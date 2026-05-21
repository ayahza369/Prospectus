Welcome to Prospectus! This is for analyzing financial information from some past SEC documents for Tesla, Berkshire Hathaway, Amazon, and Eli Lilly.

 This application was made with Photon Code and RocketRide with access to Claude API.

Be sure to include the following environment info:

1. `prospectus-app/.env.local' (Photon project ID, Photon project secret key, user phone number (in form "+1##########"))

```
PROJECT_ID=...
PROJECT_SECRET=...
USER_PHONE_NUMBER=...
```

2. `ANTHROPIC_API_KEY` --- add this to the environment with the following Shell command:

```
echo "ANTHROPIC_API_KEY=their-key-here" > .env
```

Then, run the following code in three separate terminals:

1. `./start.sh`
2. `./start_2.sh`
3. Go to the `prospectus-app` directory, and then run `npm run bot`