<div align="center">

  <img src="assets/logo.png" alt="logo" width="200" height="auto" />
  <h1>Genrify</h1>
  
  <p>
    Free tool to get mp3 genre data using Spotify API 
  </p>
  
  
<!-- Badges -->
<p>
  <a href="https://github.com/mdenitz/genrify/graphs/contributors">
    <img src="https://img.shields.io/github/contributors/mdenitz/genrify" alt="contributors" />
  </a>
  
  <a href="">
    <img src="https://img.shields.io/github/last-commit/mdenitz/genrify" alt="last update" />
  </a>
  
  <a href="https://github.com/mdenitz/genrify/network/members">
    <img src="https://img.shields.io/github/forks/mdenitz/genrify" alt="forks" />
  </a>
  
  <a href="https://github.com/mdenitz/genrify/stargazers">
    <img src="https://img.shields.io/github/stars/mdenitz/genrify" alt="stars" />
  </a>
  
  <a href="https://github.com/mdenitz/genrify/issues/">
    <img src="https://img.shields.io/github/issues/mdenitz/genrify" alt="open issues" />
  </a>
  
  <!--
  <a href="https://github.com/couldbejake/awesome-readme-template/blob/master/LICENSE">
    <img src="https://img.shields.io/github/license/couldbejake/awesome-readme-template.svg" alt="license" />
  </a>-->
</p>
   
<h4>
    <a href="https://github.com/mdenitz/genrify/wiki">Documentation</a>
  <span> · </span>
    <a href="https://github.com/mdenitz/genrify/issues">Report Bug</a>
  <span> · </span>
    <a href="https://github.com/mdenitz/genrify/issues/new">Request Feature</a>
  </h4>
</div>

<!-- Getting Started -->
## 	:toolbox: Getting Started

<!-- Prerequisites -->
### :bangbang: Prerequisites

Please navigate to https://developer.spotify.com/dashboard and create app to acquire credentials  
Have Client ID and Client Secret ready before running script
<!-- Run Locally -->
### :running: Run Locally

Clone the project

`$ git clone https://github.com/mdenitz/genrify.git`

<!-- Installation -->
### :gear: Installation

Go to the project directory

`$ cd genrify `

Install desired packages using PIP

`$ pip install -r requirements.txt`

Please See 
Run the script

`$ python3 genrify.py`


## Spotify Credentials 

If you do not have a config.py file upon initial run you will be prompted to create one.  


Inside `config.py` please insert the following if script doesn't succesfully create one for you: 

- `client_id`: The spotify Client ID
- `client_secret`:The Client Secret 



## Getting Folder Path

The script will ask you for a folder that contains mp3s to be converted. Please get the folder path.

You can either:

1. `cd` into the folder directory and `pwd` once inside to get path. 
2. Drag the folder into the terminal window when prompted to provide the folder path.

Does not currently check in nested folders




## Troubleshooting

Within the Spotify API genres are assosciated with artists not with tracks so genrify will try and get the "artist" metadata from the file in order to perform the search for a genre. If file does not contain an artist then this will be logged.
