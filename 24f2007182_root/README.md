# placement-portal-application
This is my IITM MAD -1 Project Repository

Made changes to the job positions and users tables to better fit the requiremets. 
The seed data file generates data to insert into the db.

Company table was being displayed even if there were no on going drives. Rectified it by sorting the drives in the backend before sending it.

The flash message wasn't closing and was showing older messages as well.Debugged it by clearing the cache after each flash message.

The rendering of drives that were active wasnt working properly fixed that by adding proper filtering parameters in the queries to ensure they run correctly.