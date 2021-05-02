<div align='center'>

![GitHub](https://img.shields.io/github/license/firminoneto11/wow-arena-leaderboards?style=for-the-badge)
![GitHub repo size](https://img.shields.io/github/repo-size/firminoneto11/wow-arena-leaderboards?style=for-the-badge)
![GitHub top language](https://img.shields.io/github/languages/top/firminoneto11/wow-arena-leaderboards?style=for-the-badge)
![GitHub language count](https://img.shields.io/github/languages/count/firminoneto11/wow-arena-leaderboards?style=for-the-badge)
![GitHub last commit](https://img.shields.io/github/last-commit/firminoneto11/wow-arena-leaderboards?style=for-the-badge)

</div>

<div align='center'><h1>World of Warcraft Arena Leader Boards</h1></div>
<div align='center'><h3>A web page dedicated to show the best brazilians players of World of Warcraft</h3></div>
<hr/>

<div align='center'><h2>🕹 World of Warcraft 🕹</h2></div>
<p>World of Warcraft is a MMORPG game developed back in 2004 and one of my favorites games of all time. I started playing it back in 2012 and didn't stopped ever since. Within this game, there are a lot of activities to do, and one of them is to play competitive matches against other players. Basically there are 3 types of player versus player (PvP) content and are divided by the amount of players in it. For example, there are 2v2 matches, 3v3 matches and 10v10. If you wanna know more about this game, you can visit the <a href='https://worldofwarcraft.com/en-us/'>World of Warcraft</a> website.</p>
<hr/>

<div align='center'><h2>🤔 What does the webpage? 🤔</h2></div>
<p>As i mentioned before, there are 3 types of PvP content and they are 2v2, 3v3 and 10v10. Until this moment, i designed and built this webpage to only display the best brazilian players at the 3v3 bracket.</p>
<hr/>

<div align='center'><h2>💻 How it works 💻</h2></div>
<p>So, basically, when the 'Show Players' button is pressed, a request is sent to the Blizzard's API and the JSON file returned is read and filters for the brazilian realms. After the data is returned and filtered, a table is created to display the data and that's it.
Keep in mind that this process takes a little while, because it's making requests to another platform and also filtering the massive data that is returned.
Also, i did not posted this code in any hosting services such as Netlify or Github pages, because since it works with an API that needs an access token, i need to keep that access token hidden. As soon as i find a way to hide that access token i'll publish this code into a hosting service.
</p>
<hr/>

<div align='center'><h2>📁 Downloading the repository 📁</h2></div>
<p>To download this repository you will need the following elements:</p>

- [x] [Git](https://git-scm.com/);
- [x] A source code editor. I use [VSCode](https://code.visualstudio.com/), but feel free to use any other;

<p>Now, with Git installed, type the following code into any directory of your preference:</p>

```git
git clone https://github.com/firminoneto11/wow-arena-leaderboards.git
```

<p>With the repository already on your machine, open up the source code editor inside the repository folder, and create a 'config.js' file, because there, you are going to insert your own access token from the Blizzard's API. Check the sample that there is inside the <a href='https://github.com/firminoneto11/wow-arena-leaderboards/blob/main/config_sample.js'>config_sample.js</a> file.
Now that you know what to do, just create your account in the Blizzard's website and go to this <a href='https://develop.battle.net/access/'>page</a> to create your API access token.
After everything is done, you can open the 'index.html' file and see for yourself.
</p>
<hr/>

<div align='center'><h2>✔ The webpage ✔</h2></div>
<p>When you open the 'index.html' file, there will be some information about the search and the 'Show Players' button. When pressed, it will make the request for the Blizzard's API and display the returned data filtered by the brazilian players.</p>

![Working gif](https://github.com/firminoneto11/wow-arena-leaderboards/blob/main/readme_content/working.gif)

<p>If any errors occur while trying to get the data, the page will display a message saying that it happened, and ask to try again later.</p>

![Not working gif](https://github.com/firminoneto11/wow-arena-leaderboards/blob/main/readme_content/not%20working.gif)

<hr/>

<div align='center'><h2>Author</h2></div>
<p>Made with ❤ by <a href='https://github.com/firminoneto11'>Firmino Neto</a>.</p>

<!--
<div align='center'></div>
-->
