# Apprentice Clock

A web application for tracking apprentices' work hours. It requires the user to write a daily report for their training log before clocking out.

## Problem

Daily reports are easy to forget. Often nobody checks them right away, so apprentices end up writing the reports for several missing weeks at once. Apprentice Clock makes the report a condition for clocking out, so the training log stays up to date.

## Who it is for

- **Apprentices**, who have to clock in and out anyway and no longer need to remember the reports separately.
- **Companies**, who no longer need to ask apprentices for their reports. The reports are already in the database and can be signed quickly.

## Features (first version)

- Clock-in and clock-out functions
- A required daily report before clocking out
- Every user has their own unique ID

## Out of scope for now

- Login function (planned for a later phase)
- Generating a weekly report as a PDF from the daily reports
- Signing of reports by the company

## Stack

- Backend: Python 3.13 with FastAPI, managed with `uv`
- Database: PostgreSQL
- Frontend: Next.js with TypeScript
- Docker for running the backend as a container

## Data

The data is stored in a database. Each entry has these fixed fields:

- Entry ID
- Clock-in
- Clock-out
- User ID
- Daily report

## Run it locally

To be added.
