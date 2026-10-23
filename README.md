<!-- PROJECT LOGO -->
<br />
<div align="center">
  <h1 align="center">monocle</h1>

  <p align="center">
    <h2>1,000+ Job and Internship postings in one singular no bloat email</h2>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#So... what is monocle?">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## So... what is monocle?
"monocle" watches new-grad and internship postings so a student only reads what they qualify for. It condenses thousands of postings into one singular email. No filler, no bloat, no BS.

# The Problem
One community list holds thousands of active new-grad software postings, with 100+ of them added in the last 7 days (New-Grad-Positions). Its internship list adds 1,300+ software internships (Summer2027-Internships); both counts are from Oct 23, 2026. Many "entry-level" postings quietly ask for 3+ years of experience, and many internships require you to return to school afterward. So most of the reading goes to jobs you can't get, and by the time a good one turns up, it is days old or already closed.

# Who has it?
Students who are graduating in 2027 who want an entry role with the computer science degree they worked hard for for 4+ years, which is describing me as well.

# 10x claim
Finding a posting that fits my resume takes me about 30 minutes to an hour daily; monocle turns this into a 2 minute email with only new postings that fits waht I want.

# Core features
1. Profile and company watchlist: target levels (new grad, internship or both), degree and graduation date, a planned master's start if any, locations, remote, stack, max years of experience.
2. Ingest from both community lists (new grad and internships) plus Greenhouse, Ashby and Lever feeds; each posting saved once, vanished ones marked closed.
3. Extract facts from each posting with an LLM; plain Python rules decide pass or fail.
4. Daily 8:00 digest email of new postings that passed, with a full-time section and an internship section.
5. Application tracker (saved, applied, interviewing, rejected, offer) and a weekly PDF of the pipeline.

# Concepts used
|Concept|Where in monicle|
|-|-|
|API Endpoints|Watchlist, postings feed, application status, job status (202 Accepted for slow work)|
|Database|Postgres: postings, extractions, matches, jobs, LLM cost log|
|Authentication|Register and log in with JWT; every route except /health is protected and scoped to its user|
|Background and cron jobs|A worker container: ingest every 6 hours, extraction queue, 8:00 digest, Sunday report|
|Reporting|Daily digest email (Mailpit locally) and a weekly PDF of your applications|
|Caching|Extractions stored by a hash of the posting text, so each text costs one LLM call ever|
|LLM Integration|One job: posting text to validated JSON facts, every call logged with tokens, latency and cost|

## Non-goals
- No auto applying
- No sites that forbid scrapping (LinkedIn, Indeed, etc.)
- No fetching descriptions from Workday pages; those postings use the community list's fields only.
- No front end beyond Swagger UI and the emails.

Data. Public job postings only. No résumé is needed: the rules read your profile fields, and the demo seeds a made-up profile.
<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Built With

SOON

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
# Getting Started

SOON

## Prerequisites

SOON

## Installation

SOON

# Roadmap

SOON

See the [open issues](https://github.com/tutruong8/monocle/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTACT -->
# Contact

Travis Tú Trương - travistu8@icloud.com

Project Link: [https://github.com/tutruong8/monocle](https://github.com/tutruong8/monocle)

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<p align="right">(<a href="#readme-top">back to top</a>)</p>