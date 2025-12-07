# Envelopes
a budgeting system based on the principals of holding cash in envelopes earmarked for certain categories

# Prerequisites
1. postgresql deployment

# Deployment
on your preferred postgres instance enter the shell and create a database named envelopes, as well as a user with name and password to match your ENV Variables

psql:
- psql -U postgres
- CREATE DATABASE envelopes;
- CREATE USER envelopes WITH PASSWORD 'envelopes';
- GRANT ALL PRIVILEGES ON DATABASE envelopes TO envelopes;
- \c envelopes
- GRANT CREATE ON SCHEMA public TO envelopes;
- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO envelopes;
- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO envelopes;