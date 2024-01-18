# secure-lending-system  
A simple secure django app.  
Features:  
- Registering and setting two factor authorization using google authorizator,  
- Creating backup tokens (to login if you lose/don't have the device with google authorizator),  
- Logining in with 2FA,  
- Making transfers to another users,  
- Displaying secret informations in your profile (the data is actually encrypted in the database),  
- Blocking brute force attacks (block IP after too many failed logins),
- Viewing transfers history,  
- Changing your password while logged in,
- Resetting your password if your forget it by one-time-use link on your mail (doesn't reset the 2FA. If you've lost both 2FA device an admin will need to reset it),
- Configured to only utilize SSL connection (using a self-signed by me cerificate by default),  
- Dockerized and ready to deploy using nginx just by `docker compose up` - ing.

# Installation
Clone the repo  
`https://github.com/WojciechSzade/secure-lending-system.git`   
Change directory to config  
`cd config`  
Docker compose  
`docker compose up`  
Your app should be running on "https://localhost".  
Going to "http://localhost" will redirect to the safe connection "https://localhost".  
