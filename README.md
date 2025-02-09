<div align="center">
  <a href="https://github
<div align="center">
  <a href="https://devpost.com/software/server-insights">
    <img src="https://github.com/user-attachments/assets/a6678e6d-d6ec-4326-ab10-7efa77a64d33" alt="Logo" width="80" height="80">
  </a>

<h3 align="center">Server Insights</h3>
  <p align="center">
    A Discord bot that analyzes server message data to provide insights on user activity, channel engagement, and more.
    <br />
     <a href="https://devpost.com/software/server-insights">devpost.com/software/server-insights</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#key-features">Key Features</a></li>
      </ul>
    </li>
    <li><a href="#architecture">Architecture</a></li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

## About The Project

Server Insights is a Discord bot designed to provide server administrators and members with valuable insights into server activity. By archiving and analyzing message data, the bot can generate various reports and visualizations to help understand user engagement, channel usage, and communication patterns.

### Key Features

- **Message Archiving:** Archives all messages in the server to a CSV file for analysis.
- **Server Breakdown Analysis:** Provides breakdowns of messages sent by users, channels, or based on keyword searches, displayed in various graph types (bar, pie, text).
- **User Overview:** Generates a summary of a specific user's activity, including message count, oldest message, and swear word usage.
- **Random Message Retrieval:** Sends a random message from the archive based on specified filters (swear words, channel, user).
- **Customizable Prefix:** Allows server administrators to change the bot's command prefix.

## Architecture

- **Frontend:**
  - Discord client interface via bot commands.
- **Backend:**
  - `discord.py` library for bot functionality.
  - `matplotlib` for generating graphs.
  - `csv` module for reading and writing message archives.
  - `json` module for managing bot prefixes.
  - `pytz` for timezone conversions.
- **Data Storage:**
  - CSV files stored locally in the `server_archives` directory.
  - `prefixes.json` file for storing custom prefixes for each guild.

## Getting Started

### Prerequisites

- Python 3.6 or higher
- `discord.py` library
  ```sh
  pip install discord.py
  ```
- `matplotlib` library
  ```sh
  pip install matplotlib
  ```
- `pytz` library
  ```sh
  pip install pytz
  ```

### Installation

Instructions for setting up the bot:

1. Clone the repository:
   ```sh
   git clone https://github.com/owengretzinger/server-insights.git
   ```
2. Navigate to the project directory:
   ```sh
   cd server-insights
   ```
3. Install the required packages:
   ```sh
   pip install -r requirements.txt
   ```
4. Create a `server_archives` directory:
   ```sh
   mkdir server_archives
   ```
5. Obtain a Discord bot token from the [Discord Developer Portal](https://discord.com/developers/applications).
6. Replace `"insert_token"` in `server_insights.py` with your bot token.
7. Run the bot:
   ```sh
   python server_insights.py
   ```

## Acknowledgments

- This README was generated with [README Generator](https://github.com/owengretzinger/readme-generator) — an AI tool that understands your entire codebase.
